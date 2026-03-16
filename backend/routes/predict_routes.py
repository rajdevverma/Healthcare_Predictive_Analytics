"""
Prediction Routes - Pure MySQL
Handles ML-based disease predictions (Heart Disease & Diabetes)
"""
from flask import Blueprint, request, jsonify, session
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.model_loader import get_model_loader
from utils.auth import login_required
from utils.validation import validator
from utils.db_connection import get_database

predict_bp = Blueprint('predict', __name__, url_prefix='/api/predict')
model_loader = get_model_loader()

@predict_bp.route('/heart', methods=['POST'])
@login_required
def predict_heart_disease():
    """Predict heart disease risk"""
    from datetime import datetime
    try:
        data = request.get_json()
        
        # Validate heart disease parameters
        is_valid, message = validator.validate_heart_disease_params(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Extract features in correct order
        features = [
            float(data['age']), float(data['sex']), float(data['cp']),
            float(data['trestbps']), float(data['chol']), float(data['fbs']),
            float(data['restecg']), float(data['thalach']), float(data['exang']),
            float(data['oldpeak']), float(data['slope']), float(data['ca']),
            float(data['thal'])
        ]
        
        # Make prediction
        result = model_loader.predict('heart', features)
        
        # Prepare input features for JSON storage
        input_features = {k: v for k, v in data.items() if k not in ['patient_id', 'patient_name']}
        
        # Get database connection
        db = get_database()
        cursor = db.cursor()
        
        # Verify patient ownership
        user_id = session.get('user_id')
        patient_id = data.get('patient_id')
        if patient_id:
            cursor.execute("SELECT id FROM patients WHERE patient_id = %s AND created_by = %s", (patient_id, user_id))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({'success': False, 'message': 'Invalid patient ID or access denied'}), 404

        # Save to database
        cursor.execute(
            """INSERT INTO predictions 
            (patient_id, patient_name, disease_type, risk_percentage, risk_level, 
            model_used, input_features, predicted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (patient_id, data.get('patient_name'), 'heart_disease',
             result['risk_percentage'], result['risk_level'], 'random_forest',
             json.dumps(input_features), user_id)
        )
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Prediction generated successfully',
            'prediction': {
                'disease_type': 'Heart Disease',
                'risk_percentage': result['risk_percentage'],
                'risk_level': result['risk_level'],
                'recommendation': get_heart_recommendation(result['risk_level']),
                'prediction_date': datetime.now().isoformat()
            }
        }), 200
        
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'ML model not found. Please train the model first.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Prediction failed: {str(e)}'}), 500

@predict_bp.route('/diabetes', methods=['POST'])
@login_required
def predict_diabetes():
    """Predict diabetes risk"""
    from datetime import datetime
    try:
        data = request.get_json()
        
        # Validate diabetes parameters
        is_valid, message = validator.validate_diabetes_params(data)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Extract features
        features = [
            float(data['pregnancies']), float(data['glucose']), float(data['blood_pressure']),
            float(data['skin_thickness']), float(data['insulin']), float(data['bmi']),
            float(data['diabetes_pedigree']), float(data['age'])
        ]
        
        # Make prediction
        result = model_loader.predict('diabetes', features)
        
        # Prepare input features
        input_features = {k: v for k, v in data.items() if k not in ['patient_id', 'patient_name']}
        
        # Get database connection
        db = get_database()
        cursor = db.cursor()
        
        # Verify patient ownership
        user_id = session.get('user_id')
        patient_id = data.get('patient_id')
        if patient_id:
            cursor.execute("SELECT id FROM patients WHERE patient_id = %s AND created_by = %s", (patient_id, user_id))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({'success': False, 'message': 'Invalid patient ID or access denied'}), 404

        # Save to database
        cursor.execute(
            """INSERT INTO predictions 
            (patient_id, patient_name, disease_type, risk_percentage, risk_level, 
            model_used, input_features, predicted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (patient_id, data.get('patient_name'), 'diabetes',
             result['risk_percentage'], result['risk_level'], 'random_forest',
             json.dumps(input_features), user_id)
        )
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Prediction generated successfully',
            'prediction': {
                'disease_type': 'Diabetes',
                'risk_percentage': result['risk_percentage'],
                'risk_level': result['risk_level'],
                'recommendation': get_diabetes_recommendation(result['risk_level']),
                'prediction_date': datetime.now().isoformat()
            }
        }), 200
        
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'ML model not found.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Prediction failed: {str(e)}'}), 500

def get_heart_recommendation(risk_level):
    recommendations = {
        'Low': 'Your heart disease risk is low. Maintain a healthy lifestyle.',
        'Medium': 'Your heart disease risk is moderate. Consider consulting a cardiologist.',
        'High': 'Your heart disease risk is high. Immediate medical consultation is recommended.'
    }
    return recommendations.get(risk_level, 'Please consult with a healthcare professional.')

def get_diabetes_recommendation(risk_level):
    recommendations = {
        'Low': 'Your diabetes risk is low. Maintain healthy eating habits.',
        'Medium': 'Your diabetes risk is moderate. Monitor your blood sugar levels.',
        'High': 'Your diabetes risk is high. Immediate medical evaluation is recommended.'
    }
    return recommendations.get(risk_level, 'Please consult with a healthcare professional.')

@predict_bp.route('/history', methods=['GET'])
@login_required
def get_prediction_history():
    """Get prediction history"""
    try:
        patient_id = request.args.get('patient_id')
        limit = int(request.args.get('limit', 50))
        
        # Get database connection
        db = get_database()
        cursor = db.cursor()
        
        user_id = session.get('user_id')
        if patient_id:
            # First verify patient ownership
            cursor.execute("SELECT id FROM patients WHERE patient_id = %s AND created_by = %s", (patient_id, user_id))
            if not cursor.fetchone():
                cursor.close()
                return jsonify({'success': False, 'message': 'Patient not found or access denied'}), 404
                
            cursor.execute(
                "SELECT * FROM predictions WHERE patient_id = %s AND predicted_by = %s ORDER BY prediction_date DESC LIMIT %s",
                (patient_id, user_id, limit)
            )
        else:
            cursor.execute("SELECT * FROM predictions WHERE predicted_by = %s ORDER BY prediction_date DESC LIMIT %s", (user_id, limit))
        
        predictions = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
