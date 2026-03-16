
import sys
import os
import random
import json
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Now import backend modules
try:
    from backend.utils.db_connection import get_database
    from backend.config import Config
except ImportError:
    from utils.db_connection import get_database
    from config import Config
import pymysql

def seed_database():
    print("=" * 60)
    print("HEALTHCARE SYSTEM - DATA SEEDER")
    print("=" * 60)

    db = get_database()
    if not db:
        print("✗ Failed to connect to database. Check .env")
        return

    cursor = db.cursor()
    
    # 1. Get Doctor ID
    print("[1] Verifying Doctor Account...")
    cursor.execute("SELECT id FROM users WHERE email = %s", ('doctor@healthcare.com',))
    doctor = cursor.fetchone()
    
    if not doctor:
        print("    ! Doctor account not found. Please run init_db.py first or register.")
        # Try to find ANY user
        cursor.execute("SELECT id FROM users LIMIT 1")
        doctor = cursor.fetchone()
        if not doctor:
             print("    ✗ No users found. Cannot link data.")
             return
        print(f"    ! Using existing user ID: {doctor['id']} as fallback.")
    
    doctor_id = doctor['id'] if isinstance(doctor, dict) else doctor[0]
    print(f"    ✓ Using User ID: {doctor_id}")

    # 2. Seed Patients
    print("\n[2] Seeding Patients...")
    
    patients_data = [
        ("John Doe", 45, "Male", "High"),
        ("Jane Smith", 32, "Female", "Low"),
        ("Robert Johnson", 58, "Male", "High"),
        ("Emily Davis", 29, "Female", "Low"),
        ("Michael Wilson", 52, "Male", "Medium"),
        ("Sarah Brown", 41, "Female", "Medium"),
        ("David Miller", 63, "Male", "High"),
        ("Jennifer Taylor", 35, "Female", "Low")
    ] # Name, Age, Gender, Expected Risk (just for flavor)

    added_count = 0
    patient_ids = []

    for name, age, gender, _ in patients_data:
        # Check if exists
        cursor.execute("SELECT patient_id FROM patients WHERE name = %s AND created_by = %s", (name, doctor_id))
        existing = cursor.fetchone()
        
        if existing:
            pid = existing['patient_id'] if isinstance(existing, dict) else existing[0]
            patient_ids.append(pid)
            continue

        # Create new
        pid = f"P{random.randint(10000000, 99999999)}"
        cursor.execute("""
            INSERT INTO patients (patient_id, name, age, gender, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (pid, name, age, gender, doctor_id, datetime.now()))
        
        patient_ids.append(pid)
        added_count += 1
    
    db.commit()
    print(f"    ✓ Added {added_count} new patients (Total: {len(patient_ids)})")

    # 3. Seed Predictions
    print("\n[3] Seeding Predictions...")
    
    predictions_added = 0
    
    risk_map = {
        'High': ['Heart Disease', 'High Risk'],
        'Medium': ['Heart Disease', 'Medium Risk'],
        'Low': ['No Disease', 'Low Risk']
    }
    
    diseases = ['Heart Disease', 'Diabetes']
    
    for i, pid in enumerate(patient_ids):
        # Generate 1-2 predictions per patient
        num_preds = random.randint(1, 2)
        
        # Get patient name for the record
        cursor.execute("SELECT name FROM patients WHERE patient_id = %s", (pid,))
        p_name_res = cursor.fetchone()
        p_name = p_name_res['name'] if isinstance(p_name_res, dict) else p_name_res[0]

        for _ in range(num_preds):
            disease = random.choice(diseases)
            
            # Weighted risk based on index (simulating variety)
            if i % 3 == 0:
                risk_level = 'High'
                prob = random.uniform(75.0, 95.0)
            elif i % 3 == 1:
                risk_level = 'Medium'
                prob = random.uniform(40.0, 74.0)
            else:
                risk_level = 'Low'
                prob = random.uniform(10.0, 39.0)

            # Check if prediction exists closely (avoid dupes for this run)
            # Simplified: just insert
            
            input_features = json.dumps({"age": 50, "cp": 2, "trestbps": 140}) # Dummy info
            
            cursor.execute("""
                INSERT INTO predictions 
                (patient_id, patient_name, disease_type, risk_percentage, risk_level, input_features, predicted_by, prediction_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (pid, p_name, disease, prob, risk_level, input_features, doctor_id, datetime.now() - timedelta(days=random.randint(0, 30))))
            
            predictions_added += 1

    db.commit()
    print(f"    ✓ Added {predictions_added} predictions")
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)
    cursor.close()
    db.close()

if __name__ == "__main__":
    seed_database()
