
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from backend.app import app

def test_add_patient_flow():
    client = app.test_client()
    
    # 1. Login/Register
    email = "doctor@healthcare.com"
    password = "doctor123"
    
    print(f"Logging in as {email}...")
    resp = client.post('/api/auth/login', json={
        "email": email, 
        "password": password
    })
    
    if resp.status_code != 200:
        print("Login failed, trying to register...")
        resp = client.post('/api/auth/register', json={
            "name": "Test Doctor",
            "email": email,
            "password": password,
            "role": "doctor"
        })
        print(f"Register status: {resp.status_code}")
        # Login again
        resp = client.post('/api/auth/login', json={
            "email": email, 
            "password": password
        })
        if resp.status_code != 200:
            print("Login failed after registration")
            print(resp.get_json())
            return

    print("Login successful")
    
    # 2. Add Patient
    print("Adding patient...")
    resp = client.post('/api/patients/', json={
        "name": "Test Patient API",
        "age": 50,
        "gender": "Male",
        "phone": "555-1234",
        "email": "api@test.com"
    })
    print(f"Add Patient Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    
    if resp.status_code == 201:
        print("Patient added successfully!")
    else:
        print("Failed to add patient")

    # 3. Check Stats
    print("Checking stats...")
    resp = client.get('/api/patients/stats')
    print(f"Stats Status: {resp.status_code}")
    print(f"Stats: {resp.get_json()}")

if __name__ == "__main__":
    test_add_patient_flow()
