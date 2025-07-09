import os
import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

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
    Respond in JSON format like:
    {{
        "skills": [...],
        "job_roles": [...],
        "missing_skills": [...],
        "courses": [...]
    }}
    """

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    try:
        return eval(response.text)  # only if the response is JSON
    except:
        return {"error": "Gemini response could not be parsed", "raw": response.text}
import os
import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

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
    Respond in JSON format like:
    {{
        "skills": [...],
        "job_roles": [...],
        "missing_skills": [...],
        "courses": [...]
    }}
    """

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    try:
        return eval(response.text)  # only if the response is JSON
    except:
        return {"error": "Gemini response could not be parsed", "raw": response.text}
