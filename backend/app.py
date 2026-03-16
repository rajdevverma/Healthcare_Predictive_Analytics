"""
Healthcare Predictive Analytics System - Main Flask Application
Production-ready Flask backend with RESTful API
"""
from flask import Flask, render_template, jsonify, session, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables FIRST
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

from config import config
from routes.auth_routes import auth_bp
from routes.predict_routes import predict_bp
from routes.patient_routes import patient_bp
from utils.db_connection import db_connection

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Load configuration
from config import Config
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, supports_credentials=True)

# Register blueprints (API routes)
app.register_blueprint(auth_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(patient_bp)

# ============ WEB ROUTES (Frontend) ============

@app.route('/')
def index():
    """Home page - redirects to login if not authenticated"""
    if 'user_id' in session:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('dashboard.html')

@app.route('/predict')
def predict_page():
    """Patient prediction form page"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('patient_form.html')

@app.route('/result')
def result_page():
    """Prediction result page"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('prediction.html')

@app.route('/history')
def history_page():
    """Patient history page"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('history.html')

# ============ API UTILITY ROUTES ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db_status = db_connection.health_check()
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db_status else 'disconnected',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Endpoint not found'}), 404
    return render_template('login.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({'success': False, 'message': 'Bad request'}), 400

# ============ CONTEXT PROCESSORS ============

@app.context_processor
def inject_user():
    """Inject user info into templates"""
    return {
        'user_name': session.get('user_name', ''),
        'user_id': session.get('user_id', '')
    }

# ============ APPLICATION STARTUP ============

if __name__ == '__main__':
    print("=" * 70)
    print("HEALTHCARE PREDICTIVE ANALYTICS SYSTEM")
    print("=" * 70)
    print("\n🏥 Starting Flask Application...")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"   Debug Mode: {app.config.get('DEBUG', True)}")
    print(f"   Database: {app.config.get('DB_TYPE', 'mysql')}")
    
    # Test database connection
    try:
        if db_connection.health_check():
            print("   ✓ Database connected successfully")
        else:
            print("   ✗ Database connection failed")
    except Exception as e:
        print(f"   ✗ Database error: {str(e)}")
    
    print("\n📡 API Endpoints:")
    print("   Authentication:")
    print("     POST /api/auth/register")
    print("     POST /api/auth/login")
    print("     POST /api/auth/logout")
    print("     GET  /api/auth/verify")
    print(f"\n   Predictions:")
    print("     POST /api/predict/heart")
    print("     POST /api/predict/diabetes")
    print("     GET  /api/predict/history")
    print("\n   Patient Management:")
    print("     POST /api/patients/")
    print("     GET  /api/patients/")
    print("     GET  /api/patients/<id>")
    print("     GET  /api/patients/<id>/predictions")
    print("     GET  /api/patients/stats")
    
    print("\n🌐 Web Pages:")
    print("     /          - Home/Dashboard")
    print("     /login     - Login page")
    print("     /register  - Registration page")
    print("     /dashboard - Analytics dashboard")
    print("     /predict   - Prediction form")
    print("     /result    - Prediction results")
    print("     /history   - Patient history")
    
    print("\n" + "=" * 70)
    print("✓ Server starting on http://127.0.0.1:5001")
    print("=" * 70 + "\n")
    
    # Debug: Print loaded DB config (mask password)
    print(f"DEBUG: DB_HOST={app.config.get('MYSQL_HOST')}")
    print(f"DEBUG: DB_USER={app.config.get('MYSQL_USER')}")
    db_pass = app.config.get('MYSQL_PASSWORD')
    print(f"DEBUG: DB_PASS={'*' * len(db_pass) if db_pass else 'NONE'}")

    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5001)
