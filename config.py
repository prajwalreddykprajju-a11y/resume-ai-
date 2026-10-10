import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'resumeready-secret-key-2026-college-project')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    SAMPLE_FOLDER = os.path.join(BASE_DIR, 'sample_data')
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'resumeready.db')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # Explainable Scoring Weights (Total = 100%)
    SCORING_WEIGHTS = {
        'structure': 15,          # Document structure, formatting, sections
        'skills': 25,             # Relevant technical & domain skills detected
        'education': 15,          # Education, degree, year-wise CGPA complete
        'projects_experience': 25, # Practical projects, internships, work exp
        'role_keywords': 10,       # Match against target job role keywords
        'achievements': 10        # Certifications, metrics, measurable outcomes
    }
