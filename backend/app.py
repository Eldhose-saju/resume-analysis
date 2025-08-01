from flask import Flask, request, jsonify, session, render_template_string
from flask_cors import CORS
from pdf_reader import extract_text_from_pdf
from gemini_api import analyze_text_with_gemini
from auth_db import UserAuthDB  # Import our authentication database
import os
from functools import wraps

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable credentials for sessions
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')  # Change this in production

# Initialize authentication database
auth_db = UserAuthDB("resume_analyzer.db")

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session token in headers or session
        session_token = request.headers.get('Authorization') or session.get('session_token')
        
        if not session_token:
            return jsonify({"error": "Authentication required"}), 401
        
        # Remove 'Bearer ' prefix if present
        if session_token.startswith('Bearer '):
            session_token = session_token[7:]
        
        # Validate session
        valid, user_info = auth_db.validate_session(session_token)
        if not valid:
            return jsonify({"error": "Invalid or expired session"}), 401
        
        # Add user info to request context
        request.current_user = user_info
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or request.current_user['role'] != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/')
def home():
    return jsonify({
        "message": "Resume Analyzer API with Authentication is running!",
        "endpoints": {
            "register": "/api/register (POST)",
            "login": "/api/login (POST)",
            "logout": "/api/logout (POST)",
            "profile": "/api/profile (GET) - requires auth",
            "upload_resume": "/api/upload_resume (POST) - requires auth",
            "health": "/health (GET)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Resume analyzer with auth is running"})

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'user')  # default to 'user', admin can be set manually
        
        # Validation
        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        # Create user
        success, message = auth_db.create_user(username, email, password, role)
        
        if success:
            return jsonify({"message": message}), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        # Get client IP
        ip_address = request.remote_addr
        
        # Authenticate user
        success, result = auth_db.authenticate_user(username, password, ip_address)
        
        if success:
            # Store session token in session (optional, for web-based auth)
            session['session_token'] = result['session_token']
            session['user_id'] = result['user_id']
            
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": result['user_id'],
                    "username": result['username'],
                    "role": result['role']
                },
                "session_token": result['session_token'],
                "expires_at": result['expires_at']
            }), 200
        else:
            return jsonify({"error": result}), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    try:
        session_token = request.headers.get('Authorization') or session.get('session_token')
        
        if session_token and session_token.startswith('Bearer '):
            session_token = session_token[7:]
        
        if session_token:
            success, message = auth_db.logout_user(session_token)
            
            # Clear session
            session.clear()
            
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": "No active session found"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        user_id = request.current_user['user_id']
        success, user_info = auth_db.get_user_info(user_id)
        
        if success:
            return jsonify({"user": user_info}), 200
        else:
            return jsonify({"error": user_info}), 404
            
    except Exception as e:
        return jsonify({"error": f"Failed to get profile: {str(e)}"}), 500

# Protected Resume Analysis Route
@app.route('/api/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file part in request"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Check file size
        if request.content_length and request.content_length > MAX_FILE_SIZE:
            return jsonify({"error": "File too large. Maximum size is 10MB"}), 400

        # Step 1: Extract text from PDF
        try:
            from pdf_reader import validate_pdf_file
            validate_pdf_file(file)
            
            text = extract_text_from_pdf(file)
            if not text.strip():
                return jsonify({"error": "No text could be extracted from the PDF"}), 400
            
            print(f"User {request.current_user['username']} uploaded resume - text length: {len(text)}")
            
        except Exception as e:
            print(f"PDF processing error for user {request.current_user['username']}: {str(e)}")
            return jsonify({"error": f"PDF processing failed: {str(e)}"}), 500

        # Step 2: Analyze with Gemini
        try:
            analysis = analyze_text_with_gemini(text)
            
            if "error" in analysis:
                return jsonify({"error": f"Analysis failed: {analysis['error']}"}), 500
            
            # Add user info to response (optional)
            analysis['analyzed_by'] = request.current_user['username']
            analysis['analysis_timestamp'] = datetime.now().isoformat()
            
            return jsonify(analysis)
            
        except Exception as e:
            return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Admin Routes
@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def get_all_users():
    """Admin route to get all users"""
    try:
        conn = sqlite3.connect(auth_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": bool(row[4]),
                "created_at": row[5],
                "last_login": row[6]
            })
        
        conn.close()
        return jsonify({"users": users}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get users: {str(e)}"}), 500

@app.route('/api/admin/create-admin', methods=['POST'])
@login_required
@admin_required
def create_admin_user():
    """Admin route to create another admin"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({"error": "Username, email, and password required"}), 400
        
        success, message = auth_db.create_admin(username, email, password)
        
        if success:
            return jsonify({"message": message}), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to create admin: {str(e)}"}), 500

# Initialize default admin user
def init_default_admin():
    """Create default admin user if none exists"""
    try:
        conn = sqlite3.connect(auth_db.db_path)
        cursor = conn.cursor()
        
        # Check if any admin exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Create default admin
            success, message = auth_db.create_admin("admin", "admin@synkrone.com", "admin123")
            if success:
                print("✅ Default admin created:")
                print("   Username: admin")
                print("   Email: admin@synkrone.com")
                print("   Password: admin123")
                print("   ⚠️  Please change the default password after first login!")
            else:
                print(f"❌ Failed to create default admin: {message}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error initializing default admin: {str(e)}")

if __name__ == '__main__':
    print("🚀 Starting Resume Analyzer with Authentication...")
    
    # Initialize default admin
    init_default_admin()
    
    print("\n📡 Server will be available at:")
    print("  - http://127.0.0.1:5000")
    print("  - http://localhost:5000")
    print("\n🔐 API Endpoints:")
    print("  - POST /api/register - Register new user")
    print("  - POST /api/login - User login")
    print("  - POST /api/logout - User logout")
    print("  - GET /api/profile - Get user profile (auth required)")
    print("  - POST /api/upload_resume - Analyze resume (auth required)")
    print("  - GET /api/admin/users - Get all users (admin only)")
    print("  - POST /api/admin/create-admin - Create admin user (admin only)")
    print("\n⛔ Press Ctrl+C to stop the server")
    
    # Run the app
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=True
    )