"""
End-to-End Test Suite for Fake Review Trap Full-Stack Application.
Verifies frontend serving, API endpoints, and SQLite integration.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import init_db

TEST_DB = os.path.join(BASE_DIR, "data", "test_fullstack.db")


class FullStackTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def setUp(self):
        init_db(TEST_DB)

    def test_serve_frontend_index(self):
        """Verify root URL serves the frontend index.html."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fake Review Trap", response.data)
        self.assertIn(b"reviewInput", response.data)

    def test_serve_frontend_css(self):
        """Verify style.css is served correctly."""
        response = self.client.get("/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"--genuine-color", response.data)

    def test_serve_frontend_js(self):
        """Verify script.js is served correctly."""
        response = self.client.get("/script.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"API_BASE", response.data)

    def test_full_analysis_and_history_lifecycle(self):
        """Verify full round-trip: analyze review, verify response, check history."""
        payload = {
            "review": "I bought this mechanical keyboard after researching for 2 weeks. The switches have great tactile feedback and the aluminum frame feels very durable. The only slight drawback is that the USB-C cable is somewhat stiff.",
            "rating": 5
        }
        res = self.client.post("/api/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["verdict"], "Genuine")
        self.assertLessEqual(data["score"], 34)

        # Check history
        hist_res = self.client.get("/api/history?limit=10")
        self.assertEqual(hist_res.status_code, 200)
        hist_data = hist_res.get_json()
        self.assertGreaterEqual(len(hist_data["reviews"]), 1)
        self.assertEqual(hist_data["reviews"][0]["verdict"], "Genuine")


if __name__ == "__main__":
    unittest.main()
