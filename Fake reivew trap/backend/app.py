"""
Flask application for Fake Review Trap.
Provides RESTful APIs to analyze reviews, store results in SQLite, and fetch history.
"""

import os
import sys
import io
import csv
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

# Add local directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from database import init_db, save_review, get_history, clear_history
from detector import analyze_review

# Optional rate limiter
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False

# Paths
FRONTEND_DIR = os.path.abspath(os.path.join(current_dir, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR)

# Enable CORS for all routes and origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure rate limiting
if HAS_LIMITER:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["120 per minute"],
        storage_uri="memory://",
    )
else:
    limiter = None

# Initialize SQLite database on startup
init_db()


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": getattr(error, "description", "Invalid request parameters.")
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint was not found."
    }), 404


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "error": "Too Many Requests",
        "message": "Rate limit exceeded. Please wait a moment before submitting more reviews."
    }), 429


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred while processing the request."
    }), 500


# Static Frontend Routes
@app.route("/")
def serve_index():
    """Serve frontend index.html if accessed through Flask server."""
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({"message": "Fake Review Trap Backend is running."})


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve frontend static assets."""
    if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"error": "File not found"}), 404


# API Routes
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "healthy",
        "service": "Fake Review Trap API",
        "version": "1.0.0"
    }), 200


@app.route("/api/analyze", methods=["POST"])
def analyze_endpoint():
    """
    POST /api/analyze
    Accepts JSON:
        {
            "review": "string" (required, 1-5000 chars),
            "rating": 1-5 (optional integer)
        }
    Returns:
        {
            "id": int,
            "verdict": "Fake" | "Suspicious" | "Genuine",
            "score": int (0-100),
            "reasons": [list of strings],
            "details": {...}
        }
    """
    if not request.is_json:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body must be valid JSON with 'Content-Type: application/json'."
        }), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "error": "Bad Request",
            "message": "Payload must be a JSON object."
        }), 400

    # Review text validation
    if "review" not in payload:
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'review' is required."
        }), 400

    review = payload.get("review")
    if not isinstance(review, str):
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'review' must be a string."
        }), 400

    review = review.strip()
    if not review:
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'review' cannot be empty or whitespace only."
        }), 400

    if len(review) > 5000:
        return jsonify({
            "error": "Bad Request",
            "message": "Review text exceeds maximum allowed length of 5000 characters."
        }), 400

    # Rating validation (optional)
    raw_rating = payload.get("rating")
    rating = None
    if raw_rating is not None and raw_rating != "":
        try:
            rating = int(raw_rating)
            if rating < 1 or rating > 5:
                return jsonify({
                    "error": "Bad Request",
                    "message": "Field 'rating' must be an integer between 1 and 5."
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "error": "Bad Request",
                "message": "Field 'rating' must be an integer between 1 and 5, or null."
            }), 400

    # Run detection logic
    analysis = analyze_review(review, rating=rating)

    # Save to SQLite
    review_id = save_review(
        review=review,
        rating=rating,
        verdict=analysis["verdict"],
        score=analysis["score"],
        reasons=analysis["reasons"],
        details=analysis["details"]
    )

    response_data = {
        "id": review_id,
        "verdict": analysis["verdict"],
        "score": analysis["score"],
        "reasons": analysis["reasons"],
        "details": analysis["details"]
    }

    return jsonify(response_data), 200


@app.route("/api/history", methods=["GET"])
def history_endpoint():
    """
    GET /api/history
    Returns the last 20 analyzed reviews from SQLite.
    """
    limit_param = request.args.get("limit", 20)
    try:
        limit = min(100, max(1, int(limit_param)))
    except (ValueError, TypeError):
        limit = 20

    records = get_history(limit=limit)
    return jsonify({
        "count": len(records),
        "reviews": records
    }), 200


@app.route("/api/history", methods=["DELETE"])
def clear_history_endpoint():
    """
    DELETE /api/history
    Clears all saved review analyses from SQLite.
    """
    deleted_count = clear_history()
    return jsonify({
        "status": "success",
        "message": f"Successfully deleted {deleted_count} historical review(s).",
        "deleted_count": deleted_count
    }), 200


@app.route("/api/history/export", methods=["GET"])
def export_history_csv():
    """
    GET /api/history/export
    Exports review history as a downloadable CSV file.
    """
    records = get_history(limit=100)
    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV header
    writer.writerow(["ID", "Timestamp", "Rating", "Verdict", "Risk Score", "Review Text", "Reasons Flagged", "Word Count", "Polarity"])

    for item in records:
        details = item.get("details", {})
        reasons_str = " | ".join(item.get("reasons", []))
        writer.writerow([
            item.get("id"),
            item.get("created_at"),
            item.get("rating", "N/A"),
            item.get("verdict"),
            item.get("score"),
            item.get("review"),
            reasons_str,
            details.get("word_count", "N/A"),
            details.get("sentiment_polarity", "N/A")
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=fake_review_trap_history.csv"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Fake Review Trap backend starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
