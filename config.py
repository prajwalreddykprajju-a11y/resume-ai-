
import os
from datetime import timedelta

_secret_key = os.environ.get("SECRET_KEY")

# Detect production deployment
IS_PRODUCTION = (
    os.environ.get("RENDER") == "true"
    or os.environ.get("VERCEL") == "1"
)

if IS_PRODUCTION and not _secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable must be configured in production."
    )

class Config:
    SECRET_KEY = _secret_key or "local-development-only-change-this-key"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Configure DATA_DIR to your persistent Render disk mount path.
    DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)

    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
    SAMPLE_FOLDER = os.path.join(BASE_DIR, "sample_data")
    DATABASE_PATH = os.path.join(
        DATA_DIR, "instance", "resumeready.db"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Persistent visitor session
    PERMANENT_SESSION_LIFETIME = timedelta(days=90)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    SESSION_COOKIE_SAMESITE = "Lax"

    SCORING_WEIGHTS = {
        "structure": 15,
        "skills": 25,
        "education": 15,
        "projects_experience": 25,
        "role_keywords": 10,
        "achievements": 10
    }
