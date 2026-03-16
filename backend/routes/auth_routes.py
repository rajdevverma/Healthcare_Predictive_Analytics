"""
Authentication Routes - Pure MySQL
Handles user registration, login, and authentication
"""
from flask import Blueprint, request, jsonify, session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_connection import get_database
from utils.validation import validator
from config import Config
import bcrypt
import jwt
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new doctor/admin user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        is_valid, message = validator.validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Validate email
        is_valid, message = validator.validate_email(data['email'])
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Validate password
        is_valid, message = validator.validate_password(data['password'])
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Get database
        db = get_database()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (data['name'], data['email'], password_hash, data.get('role', 'doctor'))
        )
        db.commit()
        user_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and generate JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        db = get_database()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        user_id = str(user['id'])
        user_name = user['name']
        user_role = user['role']
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': data['email'],
            'role': user_role,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        # Set session
        session['user_id'] = user_id
        session['user_name'] = user_name
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_id,
                'name': user_name,
                'email': data['email'],
                'role': user_role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'message': 'No token provided'}), 401
        
        # Verify token
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        
        return jsonify({
            'success': True,
            'user': {
                'id': payload['user_id'],
                'email': payload['email'],
                'role': payload['role']
            }
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
