# Synkrone

Synkrone is an AI-powered resume analysis and job matching platform. It allows users to upload their resume (PDF format), then intelligently extracts skills, recommends job roles, identifies missing skills for a target role (e.g., Data Scientist), and suggests relevant online courses. The application leverages the Google Gemini API for natural language understanding of resume content.

---

## Features

- Resume upload through a web interface (PDF format)
- Text extraction from uploaded resume
- AI-powered skill extraction using Google Gemini API
- Automatic job role suggestions based on extracted skills
- Missing skill detection for a target job role
- Online course recommendations to fill identified skill gaps
- React-based frontend interface
- Flask-based backend API

---

## Tech Stack Used

### Frontend

- React
- Axios
- JavaScript
- CSS Modules or plain CSS

### Backend

- Python
- Flask
- Flask-CORS
- PyMuPDF (for PDF text extraction)
- dotenv (for environment variable management)

### AI Integration

- Google Gemini API (via `google-generativeai` Python SDK)
