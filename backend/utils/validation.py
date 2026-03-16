"""
Input Validation Utility
Validates user inputs and medical parameters
"""
import re
from datetime import datetime

class Validator:
    """Input validation class"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        return True, ""
    
    @staticmethod
    def validate_age(age):
        """Validate age range"""
        try:
            age = int(age)
            if age < 0 or age > 120:
                return False, "Age must be between 0 and 120"
            return True, ""
        except ValueError:
            return False, "Age must be a number"
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        # Remove common separators
        phone = re.sub(r'[-()\s]', '', phone)
        if len(phone) < 10:
            return False, "Phone number must be at least 10 digits"
        return True, ""
    
    @staticmethod
    def validate_heart_disease_params(params):
        """
        Validate heart disease prediction parameters
        
        Expected parameters:
        - age: 0-120
        - sex: 0 or 1
        - cp (chest pain type): 0-3
        - trestbps (resting blood pressure): 50-200
        - chol (cholesterol): 100-600
        - fbs (fasting blood sugar): 0 or 1
        - restecg: 0-2
        - thalach (max heart rate): 60-220
        - exang (exercise induced angina): 0 or 1
        - oldpeak: 0-10
        - slope: 0-2
        - ca (number of vessels): 0-4
        - thal: 0-3
        """
        validations = [
            ('age', params.get('age'), 0, 120),
            ('sex', params.get('sex'), 0, 1),
            ('cp', params.get('cp'), 0, 3),
            ('trestbps', params.get('trestbps'), 50, 200),
            ('chol', params.get('chol'), 100, 600),
            ('fbs', params.get('fbs'), 0, 1),
            ('restecg', params.get('restecg'), 0, 2),
            ('thalach', params.get('thalach'), 60, 220),
            ('exang', params.get('exang'), 0, 1),
            ('oldpeak', params.get('oldpeak'), 0, 10),
            ('slope', params.get('slope'), 0, 2),
            ('ca', params.get('ca'), 0, 4),
            ('thal', params.get('thal'), 0, 3)
        ]
        
        for name, value, min_val, max_val in validations:
            if value is None:
                return False, f"Missing parameter: {name}"
            try:
                value = float(value)
                if value < min_val or value > max_val:
                    return False, f"{name} must be between {min_val} and {max_val}"
            except ValueError:
                return False, f"{name} must be a number"
        
        return True, ""
    
    @staticmethod
    def validate_diabetes_params(params):
        """
        Validate diabetes prediction parameters
        
        Expected parameters:
        - pregnancies: 0-20
        - glucose: 0-300
        - blood_pressure: 0-200
        - skin_thickness: 0-100
        - insulin: 0-900
        - bmi: 0-70
        - diabetes_pedigree: 0-3
        - age: 0-120
        """
        validations = [
            ('pregnancies', params.get('pregnancies'), 0, 20),
            ('glucose', params.get('glucose'), 0, 300),
            ('blood_pressure', params.get('blood_pressure'), 0, 200),
            ('skin_thickness', params.get('skin_thickness'), 0, 100),
            ('insulin', params.get('insulin'), 0, 900),
            ('bmi', params.get('bmi'), 0, 70),
            ('diabetes_pedigree', params.get('diabetes_pedigree'), 0, 3),
            ('age', params.get('age'), 0, 120)
        ]
        
        for name, value, min_val, max_val in validations:
            if value is None:
                return False, f"Missing parameter: {name}"
            try:
                value = float(value)
                if value < min_val or value > max_val:
                    return False, f"{name} must be between {min_val} and {max_val}"
            except ValueError:
                return False, f"{name} must be a number"
        
        return True, ""
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate that all required fields are present"""
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, ""

# Global validator instance
validator = Validator()
