from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf_reader import extract_text_from_pdf
from gemini_api import analyze_text_with_gemini
import os

app = Flask(__name__)
CORS(app)  # allows frontend to call backend

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        "message": "Resume Analyzer API is running!",
        "endpoints": {
            "upload_resume": "/upload_resume (POST)",
            "health": "/health (GET)"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Resume analyzer is running"})

@app.route('/upload_resume', methods=['POST'])
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

        # Step 1: Validate and extract text
        try:
            # First validate the file
            from pdf_reader import validate_pdf_file
            validate_pdf_file(file)
            
            # Then extract text
            text = extract_text_from_pdf(file)
            if not text.strip():
                return jsonify({"error": "No text could be extracted from the PDF"}), 400
            
            print(f"Extracted text length: {len(text)}")  # Debug info
            
        except Exception as e:
            print(f"PDF processing error: {str(e)}")  # Debug info
            return jsonify({"error": f"PDF processing failed: {str(e)}"}), 500

        # Step 2: Analyze with Gemini
        try:
            analysis = analyze_text_with_gemini(text)
            
            # Check if analysis contains error
            if "error" in analysis:
                return jsonify({"error": f"Analysis failed: {analysis['error']}"}), 500
            
            return jsonify(analysis)
            
        except Exception as e:
            return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server will be available at:")
    print("  - http://127.0.0.1:5000")
    print("  - http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the app
    app.run(
        debug=True,
        host='127.0.0.1',  # Use 127.0.0.1 instead of 0.0.0.0 for local development
        port=5000,
        use_reloader=True
    )