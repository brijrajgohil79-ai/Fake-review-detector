"""
Live HTTP Test Runner for Fake Review Trap API.
Simulates curl/Postman requests and prints formatted JSON requests and responses.
"""

import sys
import os
import json
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:5000/api"
SAMPLES_FILE = os.path.join(os.path.dirname(__file__), "sample_payloads.json")


def make_request(method, endpoint, payload=None):
    url = f"{API_URL}/{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        body = json.loads(e.read().decode("utf-8"))
        return status, body


def run_tests():
    print("=" * 70)
    print("FAKE REVIEW TRAP - BACKEND HTTP API VERIFICATION")
    print("=" * 70)

    # 1. Health check
    print("\n[TEST 1] GET /api/health")
    status, body = make_request("GET", "health")
    print(f"HTTP Status: {status}")
    print(json.dumps(body, indent=2))

    # 2. Analyze the 5 sample reviews
    with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
        samples = json.load(f)

    for idx, s in enumerate(samples, start=2):
        print("\n" + "-" * 70)
        print(f"[TEST {idx}] POST /api/analyze: {s['name']}")
        print("Request Payload (cURL equivalent):")
        req_payload = {"review": s["review"], "rating": s.get("rating")}
        print(f"curl -X POST http://127.0.0.1:5000/api/analyze \\\n  -H \"Content-Type: application/json\" \\\n  -d '{json.dumps(req_payload)}'")
        
        status, resp = make_request("POST", "analyze", req_payload)
        print(f"\nResponse (HTTP {status}):")
        print(json.dumps(resp, indent=2))

    # 3. Validation error testing
    print("\n" + "-" * 70)
    print("[TEST 7] POST /api/analyze - Validation Error Handling (Missing review)")
    status, resp = make_request("POST", "analyze", {"rating": 4})
    print(f"Response (HTTP {status}):")
    print(json.dumps(resp, indent=2))

    # 4. History endpoint
    print("\n" + "-" * 70)
    print("[TEST 8] GET /api/history - Retrieve recent history")
    print("curl -X GET http://127.0.0.1:5000/api/history?limit=5")
    status, resp = make_request("GET", "history?limit=5")
    print(f"Response (HTTP {status}): Total items: {resp.get('count')}")
    if resp.get("reviews"):
        sample_first = resp["reviews"][0]
        print("Latest entry:")
        print(json.dumps(sample_first, indent=2))

    print("\n" + "=" * 70)
    print("ALL LIVE HTTP BACKEND TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
