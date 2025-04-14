from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import User, AvailabilityDay, Booking, ClientTask
from app.forms import CompleteTaskForm
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/psy-dashboard')
def psy_dashboard():
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user:
        flash("❌ User not found. Please log in again.", "danger")
        return redirect(url_for('auth.login'))

    if user.role != 'psychologist':
        flash("Access denied.", "danger")
        return redirect(url_for('main_routes.home'))

    available_days = AvailabilityDay.query.filter_by(psychologist_id=user.id).all()

    events = []
    for day in available_days:
        slots = day.slots
        total = len(slots)

        if not slots:
            color = "gray"
            title = "Unavailable"
        elif all(slot.is_booked for slot in slots):
            color = "red"
            title = "Fully Booked"
        elif any(slot.is_pending for slot in slots):
            color = "yellow"
            title = "Pending Requests"
        else:
            color = "green"
            title = "Available"

        events.append({
            "title": title,
            "start": str(day.date),
            "color": color
        })

    return render_template('dashboard/psy_dashboard.html', user=user, events=events)

@dashboard_bp.route('/cli-dashboard')
def cli_dashboard():
    if 'user_id' not in session:
        flash("🔐 Debug: No user_id in session. Redirecting to login.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user:
        flash("❌ Debug: User not found in DB.", "danger")
        return redirect(url_for('auth.login'))

    if user.role != 'client':
        flash(f"⛔ Debug: Access denied. Logged in as {user.role}, not 'client'.", "danger")
        return redirect(url_for('main_routes.home'))

    confirmed = Booking.query.filter_by(client_id=user.id, status='confirmed')\
        .order_by(Booking.appointment_time).all()

    pending = Booking.query.filter_by(client_id=user.id, status='pending')\
        .order_by(Booking.appointment_time).all()

    tasks = ClientTask.query.filter_by(client_id=user.id)\
        .order_by(ClientTask.due_date).all()

    complete_form = CompleteTaskForm()

    return render_template(
        'dashboard/cli_dashboard.html',
        user=user,
        confirmed=confirmed,
        pending=pending,
        tasks=tasks,
        today=datetime.utcnow().date(),
        complete_form=complete_form
    )
