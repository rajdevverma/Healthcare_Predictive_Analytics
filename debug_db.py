
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from backend.utils.db_connection import get_database
from backend.config import Config

print(f"Connecting to {Config.MYSQL_HOST}...")
db = get_database()
if not db:
    print("Failed to connect")
    sys.exit(1)

cursor = db.cursor()
cursor.execute("SELECT * FROM patients")
patients = cursor.fetchall()
print(f"Total patients in DB: {len(patients)}")
for p in patients:
    print(f"ID: {p['patient_id']}, CreatedBy: {p['created_by']}")

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
print(f"Total users: {len(users)}")
for u in users:
    print(f"User: {u['email']}, ID: {u['id']}")

print("Done.")
