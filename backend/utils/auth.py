"""
Authentication & Authorization Utilities
Provides decorators for securing routes
"""
from functools import wraps
from flask import request, jsonify, session
import jwt
from config import Config

def login_required(f):
    """
    Decorator to ensure user is authenticated
    Checks for JWT in headers or user_id in session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        user_id = None
        
        # 1. Check for JWT Token in Header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if token:
            try:
                payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                # Inject into session if not present (for compatibility)
                if 'user_id' not in session:
                    session['user_id'] = user_id
            except jwt.ExpiredSignatureError:
                return jsonify({'success': False, 'message': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        # 2. Check for Session (Web Frontend)
        if not user_id and 'user_id' in session:
            user_id = session['user_id']
            
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
            
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to ensure user has admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We assume login_required is called before this or we check session/token here
        # For simplicity, this utility depends on login_required or checks session
        role = session.get('role')
        
        # If not in session, we might need to verify token again or use a g.user object
        # For this audit, we'll focus on doctor isolation.
        if role != 'admin':
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    
    return decorated_function
