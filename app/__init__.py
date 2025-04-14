from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/onlinepsy.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object('config.Config')

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)


    with app.app_context():
        from app.models import User
        from app.routes.auth_routes import auth_bp
        from app.routes.dashboard_routes import dashboard_bp
        from app.routes.booking_routes import book_bp
        from app.routes.note_routes import note_bp
        from app.routes.profile_routes import profile_bp
        from app.routes.task_routes import task_bp
        from app.routes.main_routes import main_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(book_bp)
        app.register_blueprint(note_bp)
        app.register_blueprint(profile_bp)
        app.register_blueprint(task_bp)
        app.register_blueprint(main_bp)

    @app.context_processor
    def inject_user_model():
        return dict(User=User)

    return app

