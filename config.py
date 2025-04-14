import os

class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')

    # Enable CSRF protection for Flask-WTF
    WTF_CSRF_ENABLED = False

    # SQLite database location
    SQLALCHEMY_DATABASE_URI = 'sqlite:///onlinepsy.db'

    # Turn off SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔽 Diretório de uploads
    UPLOAD_FOLDER = os.path.join('static', 'uploads') 
    
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_pics') 