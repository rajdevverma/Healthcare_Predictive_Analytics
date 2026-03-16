"""
Patient Management Routes - Pure MySQL
Handles patient data CRUD operations
"""
from flask import Blueprint, request, jsonify, session
import sys
import os
import random
import string
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.auth import login_required
from utils.db_connection import get_database
from utils.validation import validator
from config import Config

patient_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

def generate_patient_id():
    return 'P' + ''.join(random.choices(string.digits, k=8))

@patient_bp.route('/', methods=['POST'])
@login_required
def add_patient():
    """Add a new patient"""
    try:
        data = request.get_json()
        
        # Validations
        required_fields = ['name', 'age', 'gender']
        is_valid, message = validator.validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        patient_id = generate_patient_id()
        db = get_database()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO patients 
            (patient_id, name, age, gender, phone, email, address, medical_history, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (patient_id, data['name'], int(data['age']), data['gender'],
             data.get('phone', ''), data.get('email', ''), data.get('address', ''),
             data.get('medical_history', ''), session.get('user_id'))
        )
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Patient added successfully',
            'patient': {'patient_id': patient_id, 'name': data['name']}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to add patient: {str(e)}'}), 500

@patient_bp.route('/', methods=['GET'])
@login_required
def get_patients():
    """Get all patients with pagination and search"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', Config.ITEMS_PER_PAGE))
        search = request.args.get('search', '')
        offset = (page - 1) * limit
        
        db = get_database()
        cursor = db.cursor()
        
        user_id = session.get('user_id')
        if search:
            search_query = f"%{search}%"
            cursor.execute("SELECT COUNT(*) as count FROM patients WHERE created_by = %s AND (name LIKE %s OR patient_id LIKE %s)", (user_id, search_query, search_query))
            total = cursor.fetchone()['count']
            cursor.execute(
                "SELECT * FROM patients WHERE created_by = %s AND (name LIKE %s OR patient_id LIKE %s) ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (user_id, search_query, search_query, limit, offset)
            )
        else:
            cursor.execute("SELECT COUNT(*) as count FROM patients WHERE created_by = %s", (user_id,))
            total = cursor.fetchone()['count']
            cursor.execute("SELECT * FROM patients WHERE created_by = %s ORDER BY created_at DESC LIMIT %s OFFSET %s", (user_id, limit, offset))
        
        patients = cursor.fetchall()
        cursor.close()
        
        return jsonify({'success': True, 'total': total, 'page': page, 'limit': limit, 'patients': patients}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@patient_bp.route('/<patient_id>', methods=['GET'])
@login_required
def get_patient(patient_id):
    """Get specific patient details"""
    try:
        db = get_database()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s AND created_by = %s", (patient_id, session.get('user_id')))
        patient = cursor.fetchone()
        cursor.close()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        return jsonify({'success': True, 'patient': patient}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@patient_bp.route('/<patient_id>/predictions', methods=['GET'])
@login_required
def get_patient_predictions(patient_id):
    """Get predictions for a specific patient"""
    try:
        user_id = session.get('user_id')
        # First verify patient ownership
        cursor.execute("SELECT id FROM patients WHERE patient_id = %s AND created_by = %s", (patient_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Patient not found or access denied'}), 404
            
        cursor.execute("SELECT * FROM predictions WHERE patient_id = %s AND predicted_by = %s ORDER BY prediction_date DESC", (patient_id, user_id))
        predictions = cursor.fetchall()
        cursor.close()
        return jsonify({'success': True, 'count': len(predictions), 'predictions': predictions}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@patient_bp.route('/stats', methods=['GET'])
@login_required
def get_statistics():
    """Get system statistics"""
    try:
        db = get_database()
        cursor = db.cursor()
        
        user_id = session.get('user_id')
        
        cursor.execute("SELECT COUNT(*) as count FROM patients WHERE created_by = %s", (user_id,))
        total_patients = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE predicted_by = %s", (user_id,))
        total_predictions = cursor.fetchone()['count']
        
        cursor.execute("SELECT risk_level, COUNT(*) as count FROM predictions WHERE predicted_by = %s GROUP BY risk_level", (user_id,))
        risk_data = cursor.fetchall()
        risk_dist = {
            'low': 0,
            'medium': 0,
            'high': 0
        }
        for row in risk_data:
            risk_dist[row['risk_level'].lower()] = row['count']
        
        cursor.execute("SELECT disease_type, COUNT(*) as count FROM predictions WHERE predicted_by = %s GROUP BY disease_type", (user_id,))
        disease_data = cursor.fetchall()
        disease_dist = {
            'heart_disease': 0,
            'diabetes': 0
        }
        for row in disease_data:
            disease_dist[row['disease_type']] = row['count']
        
        cursor.close()
        return jsonify({
            'success': True,
            'statistics': {
                'total_patients': total_patients,
                'total_predictions': total_predictions,
                'risk_distribution': risk_dist,
                'disease_distribution': disease_dist
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
