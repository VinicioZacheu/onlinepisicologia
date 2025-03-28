import os

class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')

    # Enable CSRF protection for Flask-WTF
    WTF_CSRF_ENABLED = True

    # SQLite database location
    SQLALCHEMY_DATABASE_URI = 'sqlite:///onlinepsy.db'

    # Turn off SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
