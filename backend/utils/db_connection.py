"""
Database Connection Utility - PyMySQL Version
Using PyMySQL for better compatibility on macOS
"""
import os
import pymysql
from config import Config

class DatabaseConnection:
    """Singleton database connection manager for MySQL using PyMySQL"""
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db is None:
            self.connect()
    
    def connect(self):
        """Establish MySQL database connection using PyMySQL"""
        try:
            self._db = pymysql.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                connect_timeout=10
            )
            print("✓ Successfully connected to MySQL via PyMySQL")
        except Exception as e:
            print(f"✗ MySQL connection failed: {str(e)}")
            # Don't raise on init to allow app startup even if DB is down initially
            # but heal_check will fail
            self._db = None
    
    def get_db(self):
        """Get database connection"""
        try:
            if self._db is None or not self._db.open:
                self.connect()
            return self._db
        except:
            self.connect()
            return self._db
    
    def close(self):
        """Close database connection"""
        if self._db and self._db.open:
            self._db.close()
    
    def health_check(self):
        """Check database connection health"""
        try:
            db = self.get_db()
            if not db:
                return False
            with db.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False

# Global database instance
db_connection = DatabaseConnection()

def get_database():
    """Helper function to get database instance"""
    return db_connection.get_db()
