from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password_hash == form.password.data:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Logged in successfully!', 'success')
            if user.role == 'psychologist':
                return redirect(url_for('dashboard.psy_dashboard'))
            else:
                return redirect(url_for('dashboard.cli_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/auth_login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'warning')
        else:
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password_hash=form.password.data,
                role=form.role.data
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            flash('Account created successfully!', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/auth_signup.html', form=form)