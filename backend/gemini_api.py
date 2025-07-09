import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check if the key is present
if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

genai.configure(api_key=api_key)

def analyze_text_with_gemini(resume_text):
    prompt = f"""
    You are a resume analysis expert.

    Analyze the following resume:
    -----
    {resume_text}
    -----

    1. List the top 5 skills in the resume.
    2. Suggest 3 job roles based on these skills.
    3. Mention 2 missing skills for top tech jobs and recommend courses to learn them.

    Respond ONLY in JSON format like:
    {{
        "skills": [...],
        "job_roles": [...],
        "missing_skills": [...],
        "courses": [...]
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Response was not valid JSON", "raw": response.text}
    except Exception as e:
        return {"error": str(e)}
