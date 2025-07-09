from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf_reader import extract_text_from_pdf
from gemini_api import analyze_text_with_gemini

app = Flask(__name__)
CORS(app)  # allows frontend to call backend

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Step 1: Extract text
    text = extract_text_from_pdf(file)

    # Step 2: Analyze with Gemini
    analysis = analyze_text_with_gemini(text)

    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)
