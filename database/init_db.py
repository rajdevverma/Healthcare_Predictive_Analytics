"""
MySQL Database Initialization - PyMySQL Version
Creates database, tables, and seeds initial data
"""
import pymysql
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path) if os.path.exists(dotenv_path) else load_dotenv()

# MySQL connection configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'healthcare_db')

print("=" * 70)
print("MYSQL DATABASE INITIALIZATION (PyMySQL)")
print("=" * 70)

try:
    # Connect to MySQL (initially without database)
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=True,
        connect_timeout=5
    )
    cursor = conn.cursor()
    
    print(f"\n✓ Connected to MySQL at {MYSQL_HOST}")
    
    # Create database if not exists
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
    cursor.execute(f"USE {MYSQL_DATABASE}")
    print(f"✓ Using database: {MYSQL_DATABASE}")
    
    # Read and execute schema from healthcare.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'healthcare.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Split by semicolon and execute each command
    for command in schema_sql.split(';'):
        if command.strip():
            cursor.execute(command)
    
    print("✓ Tables created successfully")
    
    # Check if admin user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@healthcare.com',))
    if not cursor.fetchone():
        print("\n[Seeding] Creating default admin user...")
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ('Admin User', 'admin@healthcare.com', password_hash, 'admin')
        )
        print("  ✓ Admin user created")
        
    conn.commit()
    print("\n" + "=" * 70)
    print("DATABASE INITIALIZATION COMPLETED SUCCESS!")
    print("=" * 70)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Database initialization failed: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Ensure MySQL is running on port 3306")
    print("  2. Check credentials in .env file")
