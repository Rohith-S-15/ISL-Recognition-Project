"""
Flask app configuration for ISL Similarity App
"""

import os
from datetime import datetime

# Base directory of the project (one level above app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    """Base configuration"""
    # Flask config
    SECRET_KEY = 'isl-similarity-app-secret-key-2026'
    DEBUG = True
    TESTING = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max video size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'results.db')
    
    # Sign Templates directory (where .npy template files are stored)
    SIGN_TEMPLATES_DIR = os.path.join(BASE_DIR, 'Sign_Templates')
    
    # Test videos folder
    TEST_VIDEOS_FOLDER = os.path.join(BASE_DIR, 'test_videos')
    
    # Gemini API Key (for AI sentence formation)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key')
    
    # OpenRouter API Key (free models - get from https://openrouter.ai/keys)
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-openrouter-api-key')

    # Ensure required folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(SIGN_TEMPLATES_DIR, exist_ok=True)
    os.makedirs(TEST_VIDEOS_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
