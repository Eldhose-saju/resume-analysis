import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check if the key is present
if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

def clean_json_response(text):
    """Clean and extract JSON from the response text"""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Find JSON object in the text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text

def analyze_text_with_gemini(resume_text):
    """Analyze resume text using Gemini API"""
    
    # Limit text length to avoid token limits
    if len(resume_text) > 8000:
        resume_text = resume_text[:8000] + "..."
    
    prompt = f"""
    You are a resume analysis expert. Analyze the following resume and provide feedback.

    Resume Content:
    -----
    {resume_text}
    -----

    Please provide your analysis in the following JSON format (respond with ONLY valid JSON):
    {{
        "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
        "job_roles": ["role1", "role2", "role3"],
        "missing_skills": ["missing_skill1", "missing_skill2"],
        "courses": ["course1", "course2"]
    }}

    Instructions:
    1. Extract the top 5 most important skills from the resume
    2. Suggest 3 job roles that match these skills
    3. Identify 2 skills that are missing but would be valuable for top tech jobs
    4. Recommend 2 courses or learning resources for the missing skills
    
    Respond ONLY with valid JSON, no additional text.
    """

    # Try different models in order of preference
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-2.0-flash-exp',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro'
    ]
    
    for model_name in models_to_try:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if not response.text:
                print(f"Empty response from model {model_name}")
                continue
            
            # Clean the response text
            cleaned_text = clean_json_response(response.text.strip())
            
            # Parse JSON
            try:
                analysis = json.loads(cleaned_text)
                
                # Validate required fields
                required_fields = ['skills', 'job_roles', 'missing_skills', 'courses']
                for field in required_fields:
                    if field not in analysis:
                        print(f"Missing field {field} in response from {model_name}")
                        raise ValueError(f"Missing required field: {field}")
                
                # Ensure all fields are lists
                for field in required_fields:
                    if not isinstance(analysis[field], list):
                        analysis[field] = [str(analysis[field])]
                
                print(f"Successfully got analysis from model: {model_name}")
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error with model {model_name}: {str(e)}")
                continue
                
        except Exception as e:
            print(f"Error with model {model_name}: {str(e)}")
            continue
    
    # If all models failed
    return {
        "error": "All Gemini models failed. Please check your API key and try again.",
        "attempted_models": models_to_try
    }

def list_available_models():
    """List all available Gemini models for your API key"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        return {"status": "success", "models": available_models}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def test_gemini_connection():
    """Test if Gemini API is working"""
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-2.0-flash-exp',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro'
    ]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello' in JSON format: {\"message\": \"Hello\"}")
            return {"status": "connected", "model": model_name, "response": response.text}
        except Exception as e:
            print(f"Model {model_name} failed: {str(e)}")
            continue
    
    return {"status": "error", "error": "No working models found"}