import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cogno.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI/ML Configuration
    AI_MODEL_NAME = "google/flan-t5-small"
    USE_LOCAL_MODELS = True
    MODEL_CACHE_DIR = "data/ai_models"
    
    # TTS Configuration
    TTS_ENGINE = 'browser'  # Use browser's built-in TTS for now
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Production Configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
