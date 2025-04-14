from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from app.models import User, Booking, ClientTask
from app.forms import TaskForm, CompleteTaskForm
from datetime import datetime, timedelta
from app import db
from werkzeug.utils import secure_filename
import os

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/psy_add_tasks')
def psy_add_tasks():
    if 'user_id' not in session:
        flash('🔐 Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Access denied. Only psychologists can assign tasks.", 'danger')
        return redirect(url_for('main_routes.home'))

    today = datetime.utcnow()

    recent_clients = (
        db.session.query(User)
        .join(Booking, Booking.client_id == User.id)
        .filter(
            Booking.psychologist_id == user.id,
            Booking.status == 'confirmed',
            Booking.appointment_time.between(today - timedelta(days=60), today)
        )
        .distinct()
        .all()
    )

    upcoming_clients = (
        db.session.query(User)
        .join(Booking, Booking.client_id == User.id)
        .filter(
            Booking.psychologist_id == user.id,
            Booking.status == 'confirmed',
            Booking.appointment_time > today
        )
        .distinct()
        .all()
    )

    return render_template(
        'tasks/psy_add_tasks.html',
        user=user,
        recent_clients=recent_clients,
        upcoming_clients=upcoming_clients,
        now=today
    )

@task_bp.route('/create-task/<int:client_id>', methods=['GET', 'POST'])
def psy_create_task(client_id):
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("Access denied.", "danger")
        return redirect(url_for('main_routes.home'))

    client = User.query.get(client_id)
    if not client:
        flash("Client not found.", "danger")
        return redirect(url_for('tasks.psy_add_tasks'))

    form = TaskForm()

    if form.validate_on_submit():
        new_task = ClientTask(
            client_id=client.id,
            psychologist_id=user.id,
            description=form.description.data,
            due_date=form.due_date.data,
            score=form.score.data
        )
        db.session.add(new_task)
        db.session.commit()
        flash(f"✅ Task assigned to {client.name}!", "success")
        return redirect(url_for('tasks.psy_add_tasks'))

    return render_template('tasks/psy_create_task.html', user=user, client=client, form=form)

@task_bp.route('/cli-tasks-view')
def cli_tasks_view():
    if 'user_id' not in session:
        flash("🔐 Faça login primeiro.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    today = datetime.utcnow().date()

    tasks_to_complete = ClientTask.query.filter_by(client_id=user.id, is_completed=False)\
        .filter(ClientTask.due_date >= today).all()

    tasks_completed = ClientTask.query.filter_by(client_id=user.id, is_completed=True).all()

    tasks_expired = ClientTask.query.filter_by(client_id=user.id, is_completed=False)\
        .filter(ClientTask.due_date < today).all()

    form = CompleteTaskForm()

    return render_template(
        'tasks/cli_tasks_view.html',
        tasks_to_complete=tasks_to_complete,
        tasks_completed=tasks_completed,
        tasks_expired=tasks_expired,
        complete_form=form
    )

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@task_bp.route('/complete-task/<int:task_id>', methods=['POST'])
def cli_complete_task(task_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    task = ClientTask.query.get(task_id)

    if not task:
        flash("❌ Task not found.", "danger")
        return redirect(url_for('dashboard.cli_dashboard'))

    file = request.files.get('task_photo')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'tasks')
        
        if not os.path.exists(upload_folder):
            flash("📂 Directory does not exist. Creating it...", "info")
            os.makedirs(upload_folder, exist_ok=True)
        else:
            flash("📂 Directory already exists.", "info")

        upload_path = os.path.join(upload_folder, filename)
        
        flash(f"📁 Full upload path: {upload_path}", "info")
        
        try:
            file.save(upload_path)
            task.client_photo = f'tasks/{filename}' 
        except Exception as e:
            print(f"Error saving file: {e}")
            flash(f"❌ Error saving file: {str(e)}", "danger")
            return redirect(url_for('dashboard.cli_dashboard'))
    elif file:
        flash("❌ Invalid file type. Please upload an image file.", "danger")
        return redirect(url_for('dashboard.cli_dashboard'))

    task.is_completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()

    flash("✅ Task marked as completed!", "success")
    return redirect(url_for('dashboard.cli_dashboard'))
