import sys
import os
from pathlib import Path

# Add the project directory to sys.path
sys.path.append(r"c:\Users\nirva\OneDrive\Projects\culinary-atlas\culinary-atlas")

from app import app


def test_routes():
    client = app.test_client()
    results = []

    # Test 1
    response = client.get("/dish/jollof-rice/?from=rice")
    if response.status_code == 200:
        results.append("Test 1 (Valid): PASS")
    else:
        results.append(f"Test 1 (Valid): FAIL {response.status_code}")

    # Test 2
    response = client.get("/dish/jollof-rice/?from=burger")
    if response.status_code == 200:
        results.append("Test 2 (Fallback): PASS")
    else:
        results.append(f"Test 2 (Fallback): FAIL {response.status_code}")

    # Test 3
    response = client.get("/dish/doner-kebab/?from=burger")
    if response.status_code == 404:
        results.append("Test 3 (Invalid): PASS")
    else:
        results.append(f"Test 3 (Invalid): FAIL {response.status_code}")

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))


if __name__ == "__main__":
    test_routes()
