
import sys
import os
import json

# Add project root and backend to path
sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.path.insert(0, os.path.join(os.path.abspath(os.getcwd()), 'backend'))

from dotenv import load_dotenv
load_dotenv('.env')

from backend.app import app

def verify_dashboard():
    print("=" * 70)
    print("VERIFYING DASHBOARD DATA FIX")
    print("=" * 70)
    
    with app.test_client() as client:
        # 1. Login
        print("\n[1] Logging in as doctor@healthcare.com...")
        login_resp = client.post('/api/auth/login', json={
            "email": "doctor@healthcare.com",
            "password": "doctor123"
        })
        
        if login_resp.status_code != 200:
            print(f"    ✗ Login failed: {login_resp.status_code}")
            return
            
        print("    ✓ Login successful")
        
        # 2. Get Stats
        print("\n[2] Fetching Dashboard Statistics...")
        stats_resp = client.get('/api/patients/stats')
        
        if stats_resp.status_code == 200:
            data = stats_resp.get_json()
            stats = data.get('statistics', {})
            
            print("\n" + "-" * 40)
            print("CURRENT DASHBOARD DATA:")
            print("-" * 40)
            print(f"Total Patients:      {stats.get('total_patients')}")
            print(f"Total Predictions:   {stats.get('total_predictions')}")
            print("-" * 40)
            
            if stats.get('total_patients', 0) > 0:
                print("\n✅ VERIFICATION PASSED: Data is verified and visible.")
            else:
                print("\n❌ VERIFICATION FAILED: Total Patients is still 0.")
        else:
            print(f"    ✗ API Request failed: {stats_resp.status_code}")

if __name__ == "__main__":
    verify_dashboard()
