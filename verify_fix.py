import sys
import os
from pathlib import Path

# Add the project directory to sys.path to import app
sys.path.append(r"c:\Users\nirva\OneDrive\Projects\culinary-atlas\culinary-atlas")

from app import app


def test_routes():
    client = app.test_client()

    print("--- Test 1: Valid Dish and Valid From ---")
    # jollof_rice exists, rice.json exists inside it
    response = client.get("/dish/jollof-rice/?from=rice")
    if response.status_code == 200:
        print("SUCCESS: Got 200 OK for valid dish/file")
    else:
        print(f"FAILURE: Expected 200, got {response.status_code}")
        print(response.data.decode("utf-8"))

    print("\n--- Test 2: Valid Dish and Invalid (Missing) From (Fallback) ---")
    # jollof_rice exists, burger.json DOES NOT exist
    # Should fallback to rice.json (the only file there)
    response = client.get("/dish/jollof-rice/?from=burger")
    if response.status_code == 200:
        print("SUCCESS: Got 200 OK for valid dish/missing file (fallback triggered)")
        # Ideally check content to see if it loaded the fallback, but status 200 is the main fix for the 500 error
    else:
        print(f"FAILURE: Expected 200 (fallback), got {response.status_code}")
        print(response.data.decode("utf-8"))

    print("\n--- Test 3: Invalid Dish ---")
    # doner-kebab does not exist
    response = client.get("/dish/doner-kebab/?from=burger")
    if response.status_code == 404:
        print("SUCCESS: Got 404 Not Found for non-existent dish")
    else:
        print(f"FAILURE: Expected 404, got {response.status_code}")
        print(response.data.decode("utf-8"))


if __name__ == "__main__":
    test_routes()
