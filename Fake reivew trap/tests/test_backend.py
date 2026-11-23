"""
Automated Test Suite for Fake Review Trap Backend.
Tests API endpoints, detection logic rules, validation, and database operations.
"""

import sys
import os
import unittest
import json

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import init_db, get_history, get_db_connection
from detector import analyze_review

TEST_DB_PATH = os.path.join(BASE_DIR, "data", "test_reviews.db")


class FakeReviewTrapBackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def setUp(self):
        # Ensure fresh clean test database
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        init_db(TEST_DB_PATH)

    def tearDown(self):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    # 1. Health check test
    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "healthy")

    # 2. Input validation tests
    def test_analyze_missing_review(self):
        response = self.client.post("/api/analyze", json={"rating": 5})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_analyze_empty_review(self):
        response = self.client.post("/api/analyze", json={"review": "   ", "rating": 5})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_analyze_invalid_rating_range(self):
        response = self.client.post("/api/analyze", json={"review": "Nice phone", "rating": 6})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_analyze_invalid_rating_type(self):
        response = self.client.post("/api/analyze", json={"review": "Nice phone", "rating": "stars"})
        self.assertEqual(response.status_code, 400)

    # 3. Detection logic tests
    def test_fake_generic_and_caps(self):
        payload = {
            "review": "BEST PRODUCT EVER BUY NOW!!! MUST BUY DO NOT HESITATE TO BUY 10/10 FIVE STARS!!!",
            "rating": 5
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["verdict"], "Fake")
        self.assertGreaterEqual(data["score"], 65)
        self.assertTrue(any("ALL CAPS" in r for r in data["reasons"]))
        self.assertTrue(any("exclamation" in r.lower() for r in data["reasons"]))
        self.assertTrue(any("generic" in r.lower() for r in data["reasons"]))

    def test_fake_promotional_link(self):
        payload = {
            "review": "Great quality! Get 50% off with promo code DISCOUNT50 at https://cheap-deals.shop contact whatsapp 9876543210",
            "rating": 5
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["verdict"], ["Fake", "Suspicious"])
        self.assertTrue(any("promotional" in r.lower() for r in data["reasons"]))

    def test_fake_rating_mismatch(self):
        payload = {
            "review": "This is the most amazing, flawless, wonderful product I have ever seen in my life! Truly perfect and exceptional quality!",
            "rating": 1
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["verdict"], ["Fake", "Suspicious"])
        self.assertTrue(any("conflict" in r.lower() for r in data["reasons"]))

    def test_suspicious_short_repetition(self):
        payload = {
            "review": "good good good good item",
            "rating": 5
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["verdict"], ["Suspicious", "Fake"])
        self.assertTrue(any("repeated" in r.lower() or "brief" in r.lower() for r in data["reasons"]))

    def test_genuine_detailed_review(self):
        payload = {
            "review": "I have been using these wireless headphones daily for 3 weeks. The sound quality is crisp and the bass is solid for this price point. Battery life lasts about 28 hours on a single charge. However, the plastic ear cushions can get slightly warm after 2 hours of continuous use. Overall, a great upgrade from my previous model.",
            "rating": 4
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["verdict"], "Genuine")
        self.assertLessEqual(data["score"], 34)
        self.assertIn("details", data)
        self.assertGreaterEqual(data["details"]["word_count"], 25)

    # 4. History endpoint test
    def test_history_endpoint(self):
        # Insert a sample review
        self.client.post("/api/analyze", json={
            "review": "Solid keyboard with tactile switches, typing feels responsive.",
            "rating": 5
        })
        response = self.client.get("/api/history?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("reviews", data)
        self.assertGreaterEqual(len(data["reviews"]), 1)
        first = data["reviews"][0]
        self.assertIn("id", first)
        self.assertIn("verdict", first)
        self.assertIn("score", first)
        self.assertIn("reasons", first)


if __name__ == "__main__":
    unittest.main()
