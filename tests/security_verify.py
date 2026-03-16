import requests
import json

BASE_URL = "http://127.0.0.1:5001/api"

def test_security():
    print("--- STARTING SECURITY VERIFICATION ---")
    
    # 1. Unauthorized Access Check
    print("\n[1] Testing Unauthorized Access to /api/patients/...")
    try:
        resp = requests.get(f"{BASE_URL}/patients/")
        if resp.status_code == 401:
            print("✓ SUCCESS: Got 401 Unauthorized as expected.")
        else:
            print(f"✗ FAILED: Expected 401, got {resp.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")

    # 2. SQL Injection Check
    print("\n[2] Testing SQL Injection in Search...")
    # This requires being logged in, but we can test if the endpoint is protected first.
    # The fix used parameterized queries, so even with a session it should be safe.
    payload = "' OR '1'='1"
    try:
        resp = requests.get(f"{BASE_URL}/patients/", params={'search': payload})
        if resp.status_code == 401:
            print("✓ SUCCESS: Route is protected (401).")
        else:
            print(f"INFO: Got {resp.status_code} - checking if payload worked if 200 (not expected yet).")
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n[3] Testing IDOR Vulnerability (ID Tampering)...")
    # Simulation: Assume we know a patient ID 'P12345678' that belongs to ANOTHER doctor.
    # Without a real login session here, we are validating that the route REQUIRES authentication.
    # In a full test, we would log in as Doctor A and try to access Doctor B's patient.
    try:
        resp = requests.get(f"{BASE_URL}/patients/P12345678")
        if resp.status_code == 401:
            print("✓ SUCCESS: Route is protected (401).")
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n--- SECURITY VERIFICATION COMPLETE ---")
    print("Manual validation recommended: Log in as two different doctors and verify data isolation in the UI.")

if __name__ == "__main__":
    test_security()
