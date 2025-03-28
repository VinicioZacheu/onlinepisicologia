from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()               # Initialize SQLAlchemy for database access
csrf = CSRFProtect()            # Enable CSRF protection for forms

def create_app():
    app = Flask(__name__)       # Create the Flask app instance

    # App configuration
    app.config.from_object('config.Config')  # Load config from config.py

    db.init_app(app)            # Initialize database with app
    csrf.init_app(app)          # Initialize CSRF protection with app

    from .routes import bp      # Import routes (views)
    app.register_blueprint(bp)  # Register routes using a blueprint

    return app                  # Return the configured app instance
