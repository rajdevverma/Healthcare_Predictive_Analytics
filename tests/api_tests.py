#!/usr/bin/env python3
"""
API Test Suite for Healthcare Predictive Analytics System
Automated testing of all backend endpoints
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
session = requests.Session()

# Test results storage
test_results = []

def log_test(test_id, description, passed, details=""):
    """Log test result"""
    result = {
        'test_id': test_id,
        'description': description,
        'status': 'PASS' if passed else 'FAIL',
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    test_results.append(result)
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_id} | {description}")
    if details and not passed:
        print(f"    Details: {details}")

def test_health_check():
    """Test API health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/api/health", timeout=5)
        passed = response.status_code == 200 and response.json().get('status') == 'healthy'
        log_test("API-000", "Health check endpoint", passed, 
                f"Status: {response.status_code}, Response: {response.json()}")
        return passed
    except Exception as e:
        log_test("API-000", "Health check endpoint", False, str(e))
        return False

def test_register_user():
    """Test user registration"""
    test_data = {
        "name": f"Test User {int(time.time())}",
        "email": f"test{int(time.time())}@example.com",
        "password": "test123456",
        "role": "doctor"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=test_data)
        passed = response.status_code == 201 and response.json().get('success') == True
        log_test("API-001", "Register new user with valid data", passed,
                f"Status: {response.status_code}")
        return passed, test_data['email']
    except Exception as e:
        log_test("API-001", "Register new user with valid data", False, str(e))
        return False, None

def test_register_duplicate():
    """Test duplicate email registration"""
    test_data = {
        "name": "Doctor Test",
        "email": "doctor@healthcare.com",  # Existing user
        "password": "test123",
        "role": "doctor"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=test_data)
        passed = response.status_code == 400
        log_test("API-002", "Register with duplicate email (should fail)", passed,
                f"Status: {response.status_code}, Message: {response.json().get('message', 'N/A')}")
        return passed
    except Exception as e:
        log_test("API-002", "Register with duplicate email", False, str(e))
        return False

def test_login_valid():
    """Test login with valid credentials"""
    test_data = {
        "email": "doctor@healthcare.com",
        "password": "doctor123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", json=test_data)
        passed = response.status_code == 200 and response.json().get('success') == True
        data = response.json()
        token = data.get('token', '') if passed else None
        log_test("API-005", "Login with valid credentials", passed,
                f"Token received: {bool(token)}")
        return passed, token
    except Exception as e:
        log_test("API-005", "Login with valid credentials", False, str(e))
        return False, None

def test_login_invalid():
    """Test login with invalid credentials"""
    test_data = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", json=test_data)
        passed = response.status_code == 401
        log_test("API-006", "Login with invalid credentials (should fail)", passed,
                f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("API-006", "Login with invalid credentials", False, str(e))
        return False

def test_predict_heart_disease():
    """Test heart disease prediction"""
    test_data = {
        "patient_name": "Test Patient Heart",
        "age": 55,
        "sex": 1,
        "cp": 2,
        "trestbps": 140,
        "chol": 250,
        "fbs": 1,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 1.5,
        "slope": 1,
        "ca": 0,
        "thal": 2
    }
    
    try:
        response = session.post(f"{BASE_URL}/predict/heart", json=test_data)
        data = response.json()
        passed = (response.status_code == 200 and 
                 data.get('success') == True and
                 'prediction' in data)
        
        prediction = data.get('prediction', {})
        details = f"Risk: {prediction.get('risk_percentage')}%, Level: {prediction.get('risk_level')}"
        log_test("API-009", "Heart disease prediction with valid data", passed, details)
        return passed
    except Exception as e:
        log_test("API-009", "Heart disease prediction", False, str(e))
        return False

def test_predict_heart_missing_field():
    """Test heart disease prediction with missing field"""
    test_data = {
        "patient_name": "Test Patient",
        "age": 55,
        # Missing other required fields
    }
    
    try:
        response = session.post(f"{BASE_URL}/predict/heart", json=test_data)
        passed = response.status_code == 400
        log_test("API-010", "Heart disease prediction with missing fields (should fail)", passed,
                f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("API-010", "Heart disease prediction with missing fields", False, str(e))
        return False

def test_predict_diabetes():
    """Test diabetes prediction"""
    test_data = {
        "patient_name": "Test Patient Diabetes",
        "pregnancies": 3,
        "glucose": 150,
        "blood_pressure": 85,
        "skin_thickness": 25,
        "insulin": 150,
        "bmi": 28.5,
        "diabetes_pedigree": 0.8,
        "age": 45
    }
    
    try:
        response = session.post(f"{BASE_URL}/predict/diabetes", json=test_data)
        data = response.json()
        passed = (response.status_code == 200 and 
                 data.get('success') == True and
                 'prediction' in data)
        
        prediction = data.get('prediction', {})
        details = f"Risk: {prediction.get('risk_percentage')}%, Level: {prediction.get('risk_level')}"
        log_test("API-012", "Diabetes prediction with valid data", passed, details)
        return passed
    except Exception as e:
        log_test("API-012", "Diabetes prediction", False, str(e))
        return False

def test_get_statistics():
    """Test patient statistics endpoint"""
    try:
        response = session.get(f"{BASE_URL}/patients/stats")
        data = response.json()
        passed = (response.status_code == 200 and 
                 data.get('success') == True and
                 'statistics' in data)
        
        stats = data.get('statistics', {})
        details = f"Patients: {stats.get('total_patients')}, Predictions: {stats.get('total_predictions')}"
        log_test("API-023", "Get patient statistics", passed, details)
        return passed
    except Exception as e:
        log_test("API-023", "Get patient statistics", False, str(e))
        return False

def test_add_patient():
    """Test adding a new patient"""
    test_data = {
        "name": f"Test Patient {int(time.time())}",
        "age": 45,
        "gender": "Male",
        "phone": "1234567890",
        "email": f"patient{int(time.time())}@example.com"
    }
    
    try:
        response = session.post(f"{BASE_URL}/patients/", json=test_data)
        data = response.json()
        passed = response.status_code == 201 and data.get('success') == True
        
        patient_id = data.get('patient', {}).get('patient_id', 'N/A')
        log_test("API-015", "Add new patient", passed, f"Patient ID: {patient_id}")
        return passed
    except Exception as e:
        log_test("API-015", "Add new patient", False, str(e))
        return False

def test_get_patients():
    """Test getting all patients"""
    try:
        response = session.get(f"{BASE_URL}/patients/")
        data = response.json()
        passed = response.status_code == 200 and data.get('success') == True
        
        total = data.get('total', 0)
        log_test("API-018", "Get all patients (paginated)", passed, f"Total: {total}")
        return passed
    except Exception as e:
        log_test("API-018", "Get all patients", False, str(e))
        return False

def run_all_tests():
    """Run complete test suite"""
    print("=" * 70)
    print("HEALTHCARE PREDICTIVE ANALYTICS - API TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 70)
    print()
    
    # Run tests
    test_health_check()
    test_register_user()
    test_register_duplicate()
    test_login_valid()
    test_login_invalid()
    test_predict_heart_disease()
    test_predict_heart_missing_field()
    test_predict_diabetes()
    test_add_patient()
    test_get_patients()
    test_get_statistics()
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in test_results if r['status'] == 'PASS')
    failed = sum(1 for r in test_results if r['status'] == 'FAIL')
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ({(passed/total*100):.1f}%)")
    print(f"Failed: {failed}")
    print()
    
    if failed > 0:
        print("Failed Tests:")
        for r in test_results:
            if r['status'] == 'FAIL':
                print(f"  - {r['test_id']}: {r['description']}")
                print(f"    {r['details']}")
    
    print("=" * 70)
    print(f"✅ Test execution completed!" if failed == 0 else f"⚠️  {failed} test(s) failed")
    print("=" * 70)
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"Results saved to: test_results.json")

if __name__ == "__main__":
    run_all_tests()
