from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    ana = User.query.filter_by(email="ana@example.com").first()
    if ana:
        print(f"Current role for Ana: {ana.role}")
        ana.role = "client"
        db.session.commit()
        print("✅ Ana's role updated to client.")
    else:
        print("❌ Ana not found.")
