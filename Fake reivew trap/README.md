# 🛡️ Fake Review Trap

A full-stack web application designed to detect whether an e-commerce product review is likely **Fake**, **Suspicious**, or **Genuine** using a hybrid linguistic, heuristic, and rule-based scoring engine.

---

## 🌟 Key Features

- **Hybrid Detection Engine (Rules + Machine Learning)**:
  - **Calibrated ML Model**: Pre-trained TF-IDF vectorizer + Logistic Regression pipeline (`review_classifier.joblib`) calculating synthetic probability.
  - **ALL CAPS & Excessive Punctuation**: Flags aggressive promotional yelling (`100% CAPS`, `!!!+`).
  - **Generic Praise Clichés**: Detects fabricated bot clichés like *"best product ever"*, *"must buy"*, *"life changer"*, *"works like magic"*.
  - **Promotional Links & Spam**: Identifies external URLs, discount/promo codes, Telegram/WhatsApp handles, and phone numbers.
  - **Rating-Sentiment Conflict**: Detects bots misaligning star ratings with review text (e.g., 1-star rating for an overwhelmingly positive glowing review).
  - **Text Repetition & Low Lexical Diversity**: Detects repeated keyword stuffing and copy-paste patterns.
  - **Product Feature Grounding**: Rewards authentic reviews that mention specific physical components (*battery life, cable, materials, dimensions*) and realistic usage durations (*"used for 3 weeks", "after 2 months"*).
- **Interactive Modern Frontend**:
  - Single-page application built with **Vanilla HTML5, CSS3, and JavaScript** (zero dependencies or heavy frameworks).
  - Dynamic **Score Meter** (0–100 risk score) with animated color coding:
    - 🟢 **Genuine** (0–34)
    - 🟡 **Suspicious** (35–64)
    - 🔴 **Fake** (65–100)
  - Interactive **Star Rating Selector** (1 to 5 stars, with click-to-clear).
  - **Quick Test Preset Buttons**: Test fake, promotional, rating mismatch, and genuine reviews with one click.
  - **Diagnostic Metrics Grid**: Live display of word count, caps ratio, exclamation count, sentiment polarity, vocabulary diversity, and detection engine mode.
  - **Persistent History & CSV Export**:
    - View the last 20 analyzed reviews stored in SQLite.
    - Click any historical review card to reload its full breakdown into the analyzer.
    - **Download CSV**: One-click export of analyzed reviews to spreadsheet-compatible CSV.
    - **Clear History**: Wipe past records with confirmation.
  - **Dark / Light Mode**: Smooth theme toggling with preference stored in `localStorage`.
- **One-Click Windows Launcher**:
  - Double-click `run.bat` to launch the backend server and open the web browser automatically.

---

## 📂 Project Structure

```text
Fake Review Trap/
├── backend/
│   ├── app.py               # Flask application server, endpoints, CORS, rate limiting
│   ├── detector.py          # Hybrid linguistic, heuristic, and ML fake detection engine
│   ├── database.py          # SQLite database interface & schema management
│   ├── train_model.py       # Scikit-learn TF-IDF & Logistic Regression training script
│   ├── review_classifier.joblib # Serialized ML pipeline artifact
│   └── requirements.txt     # Python dependencies (Flask, scikit-learn, joblib, etc.)
├── frontend/
│   ├── index.html           # Modern single-page user interface
│   ├── style.css            # Responsive styles, themes (Dark/Light), meters, badges
│   └── script.js            # Vanilla JS: API calls, DOM manipulation, presets, history
├── data/
│   └── reviews.db           # SQLite database storing analysis history (auto-created)
├── tests/
│   ├── test_backend.py      # Automated unit test suite (11 unit tests)
│   ├── test_fullstack.py    # End-to-end integration test suite (4 tests)
│   ├── curl_test_runner.py  # Live HTTP test runner simulating curl/Postman
│   └── sample_payloads.json # 5 sample test payloads (fake, suspicious, genuine)
├── run.bat                  # One-click Windows server and browser launcher
└── README.md                # Documentation and run instructions
```

---

## 🚀 Step-by-Step Run Instructions

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies
Open your terminal inside the project directory:
```bash
pip install -r backend/requirements.txt
```

### 3. Run the Backend Server
Start the Flask application:
```bash
python backend/app.py
```
*The backend server will start on `http://127.0.0.1:5000`.*

### 4. Open the Frontend
You can access the frontend in either of two ways:
- **Directly in your browser**: Open `http://127.0.0.1:5000` in Google Chrome, Microsoft Edge, or Firefox.
- **Or open the static file**: Double-click `frontend/index.html` to open it locally. It will automatically connect to the backend running at `http://127.0.0.1:5000`.

---

## 🧪 Testing the Backend

### Run Automated Unit Tests
```bash
python -m unittest tests/test_backend.py
```

### Run End-to-End Tests
```bash
python -m unittest tests/test_fullstack.py
```

### Run Live cURL / Postman Simulation
With the server running in another terminal window:
```bash
python tests/curl_test_runner.py
```

---

## 📡 API Reference & Sample cURL / Postman Requests

### 1. Analyze Review
- **Endpoint**: `POST /api/analyze`
- **Headers**: `Content-Type: application/json`

#### Example 1: Excessive Hype & ALL CAPS (Fake)
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "review": "BEST PRODUCT EVER BUY NOW!!! MUST BUY DO NOT HESITATE TO BUY 10/10 FIVE STARS WORKS LIKE MAGIC LIFE CHANGER!!!",
    "rating": 5
  }'
```
**Response (HTTP 200)**:
```json
{
  "id": 1,
  "verdict": "Fake",
  "score": 84,
  "reasons": [
    "Excessive ALL CAPS detected (100.0% of letters are capitalized).",
    "Excessive exclamation marks (6 exclamation mark(s) detected).",
    "Multiple generic hype clichés detected (e.g., 'BEST PRODUCT EVER', 'MUST BUY').",
    "Lacks specific product details: mentions no physical features, usage conditions, or distinct experience."
  ],
  "details": {
    "caps_percentage": 100.0,
    "char_count": 110,
    "exclamation_count": 6,
    "features_detected": [],
    "has_usage_context": false,
    "lexical_diversity": 0.86,
    "rating_conflict": false,
    "sentiment_polarity": 1.0,
    "word_count": 21
  }
}
```

#### Example 2: Promotional Link & Coupon Code (Fake)
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "review": "Superb quality item! Don'\''t miss out, use promo code DISCOUNT50 for 50% cashback on https://super-deals-shop.online or contact WhatsApp +1-555-0199 for bulk discounts!",
    "rating": 5
  }'
```
**Response (HTTP 200)**:
```json
{
  "id": 2,
  "verdict": "Fake",
  "score": 70,
  "reasons": [
    "Contains generic promotional praise cliché: 'Superb quality'.",
    "Contains promotional link, contact info, or voucher code ('https://super-deals-shop.online').",
    "Lacks specific product details: mentions no physical features, usage conditions, or distinct experience."
  ]
}
```

#### Example 3: Rating-Sentiment Conflict (Fake/Bot Mistake)
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "review": "This is hands down the most amazing, flawless, and wonderful product I have ever purchased. Absolute perfection in every detail and brilliant craftsmanship!",
    "rating": 1
  }'
```
**Response (HTTP 200)**:
```json
{
  "id": 3,
  "verdict": "Suspicious",
  "score": 51,
  "reasons": [
    "Severe rating-sentiment conflict: Rated 1-star but text expresses glowing praise (positive polarity 1.0).",
    "Lacks specific product details: mentions no physical features, usage conditions, or distinct experience."
  ]
}
```

#### Example 4: Detailed & Balanced Review (Genuine)
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "review": "I have been using these wireless headphones daily for about 3 weeks. The sound quality is crisp and the bass is solid for this price point. Battery life comfortably lasts 28 hours on a single charge. However, the plastic ear cups can get slightly warm after 2 hours of continuous wear. Overall, very satisfied with this upgrade compared to my previous pair.",
    "rating": 4
  }'
```
**Response (HTTP 200)**:
```json
{
  "id": 4,
  "verdict": "Genuine",
  "score": 0,
  "reasons": [
    "Authentic pattern: Mentions concrete product characteristics (sound, bass, charge).",
    "Authentic pattern: Includes realistic real-world usage duration or balanced critique.",
    "Authentic pattern: High vocabulary diversity and natural syntactic variation."
  ]
}
```

---

### 2. Retrieve History
- **Endpoint**: `GET /api/history?limit=20`

```bash
curl -X GET "http://127.0.0.1:5000/api/history?limit=5"
```

---

### 3. Export History to CSV
- **Endpoint**: `GET /api/history/export`

```bash
curl -X GET "http://127.0.0.1:5000/api/history/export" -o review_history.csv
```

---

### 4. Clear History
- **Endpoint**: `DELETE /api/history`

```bash
curl -X DELETE "http://127.0.0.1:5000/api/history"
```

---

### 5. Health Check
- **Endpoint**: `GET /api/health`

```bash
curl -X GET http://127.0.0.1:5000/api/health
```
**Response (HTTP 200)**:
```json
{
  "service": "Fake Review Trap API",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 📝 5 Test Reviews Included for Instant Testing

| # | Type | Star Rating | Sample Review Text | Primary Flag Triggered |
|---|---|---|---|---|
| **1** | **Fake** | 5 ★ | `BEST PRODUCT EVER BUY NOW!!! MUST BUY DO NOT HESITATE TO BUY 10/10 FIVE STARS WORKS LIKE MAGIC LIFE CHANGER!!!` | 100% ALL CAPS, excessive `!`, generic hype clichés |
| **2** | **Fake** | 5 ★ | `Superb quality item! Don't miss out, use promo code DISCOUNT50 for 50% cashback on https://super-deals-shop.online or contact WhatsApp +1-555-0199 for bulk discounts!` | URL links, promo codes, WhatsApp contact details |
| **3** | **Fake/Bot** | 1 ★ | `This is hands down the most amazing, flawless, and wonderful product I have ever purchased. Absolute perfection in every detail and brilliant craftsmanship!` | Critical rating-sentiment mismatch (1-star with glowing praise) |
| **4** | **Suspicious** | 5 ★ | `good good good product very nice nice nice good item fast fast delivery good` | Low lexical diversity, repetitive keyword spam |
| **5** | **Genuine** | 4 ★ | `I have been using these wireless headphones daily for about 3 weeks. The sound quality is crisp and the bass is solid for this price point. Battery life comfortably lasts 28 hours on a single charge. However, the plastic ear cups can get slightly warm after 2 hours of continuous wear. Overall, very satisfied with this upgrade compared to my previous pair.` | Concrete product attributes (*battery, sound, bass, plastic*), usage duration (*3 weeks*), balanced nuance (*"however"*), high lexical diversity |
