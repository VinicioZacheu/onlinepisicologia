from flask import Blueprint, render_template
from app.models import PsychologistProfile

main_bp = Blueprint('main_routes', __name__)

@main_bp.route('/')
def home():
    return render_template('main/home.html')

@main_bp.route('/psychologists')
def psychologists():
    profiles = PsychologistProfile.query.all()
    return render_template('main/main_psychologists.html', profiles=profiles)
