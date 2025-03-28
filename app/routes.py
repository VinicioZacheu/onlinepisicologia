from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, session, flash

from . import db
from .forms import (
    AvailabilityForm,
    LoginForm,
    RegistrationForm,
    TaskForm,
    CompleteTaskForm,
    NoteForm
)

from .models import (
    AvailabilityDay,
    AvailabilitySlot,
    Booking,
    ClientEvaluation,
    ClientTask,
    PsychologistProfile,
    User,
    ClientNote
)



bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password_hash == form.password.data:  # TEMP: plain text check
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Logged in successfully!', 'success')
            if user.role == 'psychologist':
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.client_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('main.home'))
    return render_template('signup.html', form=form)

@bp.route('/psychologists')
def psychologists():
    profiles = PsychologistProfile.query.all()
    return render_template('psychologists.html', profiles=profiles)

@bp.route('/add-availability', methods=['GET', 'POST'])
def add_availability():
    if 'user_id' not in session:
        flash("You must be logged in as a psychologist.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if user.role != 'psychologist':
        flash("Access denied: only psychologists can set availability.", "danger")
        return redirect(url_for('main.home'))

    form = AvailabilityForm()

    if form.validate_on_submit():
        # Create the day record
        day = AvailabilityDay(
            psychologist_id=user.id,
            date=form.date.data
        )
        db.session.add(day)
        db.session.commit()

        # Add time slots
        for slot_form in form.slots:
            if slot_form.time.data:
                slot = AvailabilitySlot(day_id=day.id, time=slot_form.time.data)
                db.session.add(slot)

        db.session.commit()
        flash("✅ Availability added successfully.", "success")

        if form.add_another.data:
            flash("🔁 You chose to add another one.", "info")
            return redirect(url_for('main.add_availability'))
        else:
            flash("🔙 Redirecting to your dashboard.", "info")
            return redirect(url_for('main.dashboard'))

    return render_template('add_availability.html', form=form)

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("Access denied.", "danger")
        return redirect(url_for('main.home'))

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

    print("📆 DEBUG EVENTS:", events)
    return render_template('dashboard.html', user=user, events=events)

@bp.route('/client-dashboard')
def client_dashboard():
    if 'user_id' not in session:
        flash("🔐 Debug: No user_id in session. Redirecting to login.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if not user:
        flash("❌ Debug: User not found in DB.", "danger")
        return redirect(url_for('main.login'))

    if user.role != 'client':
        flash(f"⛔ Debug: Access denied. Logged in as {user.role}, not 'client'.", "danger")
        return redirect(url_for('main.home'))

    confirmed = Booking.query.filter_by(client_id=user.id, status='confirmed')\
        .order_by(Booking.appointment_time).all()

    pending = Booking.query.filter_by(client_id=user.id, status='pending')\
        .order_by(Booking.appointment_time).all()

    # 💡 New: Fetch client tasks
    tasks = ClientTask.query.filter_by(client_id=user.id)\
        .order_by(ClientTask.due_date).all()

    flash(f"✅ Debug: Loaded client dashboard for {user.name}. Confirmed: {len(confirmed)}, Pending: {len(pending)}, Tasks: {len(tasks)}", "info")

    complete_form = CompleteTaskForm()

    return render_template(
        'client_dashboard.html',
        user=user,
        confirmed=confirmed,
        pending=pending,
        tasks=tasks,
        today=datetime.utcnow().date(),
        complete_form=complete_form
    )

@bp.route('/pending-bookings')
def pending_bookings():
    if 'user_id' not in session:
        flash("🔐 Debug: No user_id in session. Redirecting to login.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("❌ Debug: User not found.", "danger")
        return redirect(url_for('main.login'))

    if user.role != 'psychologist':
        flash(f"⛔ Debug: Access denied for role '{user.role}'. Redirecting to home.", "danger")
        return redirect(url_for('main.home'))

    bookings = Booking.query.filter_by(psychologist_id=user.id, status='pending').order_by(Booking.appointment_time).all()
    flash(f"🧠 Debug: Loaded {len(bookings)} pending bookings for {user.name}.", "info")

    return render_template('pending_bookings.html', bookings=bookings, user=user)

@bp.route('/handle-booking/<int:booking_id>/<string:action>')
def handle_booking(booking_id, action):
    user_id = session.get('user_id')
    booking = Booking.query.get(booking_id)

    if not booking:
        flash(f"❌ Debug: Booking ID {booking_id} not found.", "danger")
        return redirect(url_for('main.pending_bookings'))

    if booking.psychologist_id != user_id:
        flash(f"🚫 Debug: Booking {booking_id} does not belong to logged-in psychologist (ID {user_id}).", "danger")
        return redirect(url_for('main.pending_bookings'))

    if action == 'accept':
        booking.status = 'confirmed'
        flash(f"✅ Debug: Booking {booking_id} confirmed.", "success")
    elif action == 'reject':
        booking.status = 'canceled'
        flash(f"❌ Debug: Booking {booking_id} rejected.", "info")
    else:
        flash(f"⚠️ Debug: Invalid action '{action}' attempted on booking {booking_id}.", "warning")

    db.session.commit()
    flash("💾 Debug: Changes committed to database.", "info")

    return redirect(url_for('main.pending_bookings'))

@bp.route('/book-session')
def book_session():
    if 'user_id' not in session:
        flash("🔐 Please log in to book a session.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if user.role != 'client':
        flash("⛔ Access denied. Only clients can book sessions.", "danger")
        return redirect(url_for('main.home'))

    # Get all availability from psychologists
    available_days = AvailabilityDay.query.all()

    return render_template('book_session.html', user=user, available_days=available_days)

@bp.route('/request-booking/<int:slot_id>')
def request_booking(slot_id):
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('main.login'))

    client = User.query.get(session['user_id'])
    slot = AvailabilitySlot.query.get(slot_id)

    if not slot or slot.is_booked or slot.is_pending:
        flash("⚠️ Slot not available.", "danger")
        return redirect(url_for('main.book_session'))

    # Create Booking
    booking = Booking(
        client_id=client.id,
        psychologist_id=slot.day.psychologist_id,
        appointment_time=datetime.combine(slot.day.date, slot.time),
        status='pending'
    )
    db.session.add(booking)

    # Mark slot as pending
    slot.is_pending = True
    db.session.commit()

    flash("✅ Booking request submitted. Waiting for psychologist approval.", "success")
    return redirect(url_for('main.client_dashboard'))

@bp.route('/add_tasks')
def add_tasks():
    if 'user_id' not in session:
        flash('🔐 Please log in first.', 'warning')
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Access denied. Only psychologists can assign tasks.", 'danger')
        return redirect(url_for('main.home'))

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
        'add_tasks.html',
        user=user,
        recent_clients=recent_clients,
        upcoming_clients=upcoming_clients,
        now=today
    )

@bp.route('/create-task/<int:client_id>', methods=['GET', 'POST'])
def create_task(client_id):
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("Access denied.", "danger")
        return redirect(url_for('main.home'))

    client = User.query.get(client_id)
    if not client:
        flash("Client not found.", "danger")
        return redirect(url_for('main.add_tasks'))

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
        return redirect(url_for('main.add_tasks'))

    return render_template('create_task.html', user=user, client=client, form=form)

@bp.route('/complete-task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('main.login'))

    task = ClientTask.query.get(task_id)

    if not task:
        flash("❌ Task not found.", "danger")
        return redirect(url_for('main.client_dashboard'))

    task.is_completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()

    flash("✅ Task marked as completed!", "success")
    return redirect(url_for('main.client_dashboard'))

@bp.route('/psychologist-notes')
def psychologist_notes():
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Access denied. Only psychologists can view notes.", "danger")
        return redirect(url_for('main.home'))

    today = datetime.utcnow()

    active_clients_raw = (
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

    active_clients = []
    for client in active_clients_raw:
        latest_note = (
            ClientNote.query
            .filter_by(client_id=client.id, psychologist_id=user.id)
            .order_by(ClientNote.created_at.desc())
            .first()
        )
        active_clients.append({
            'client': client,
            'latest_note': latest_note
        })

    return render_template(
    "psychologist_notes.html",
    user=user,
    active_clients=active_clients,
    inactive_clients=[],  # keep this or build similar logic if needed
    today=today
)

@bp.route('/add-note/<int:client_id>', methods=['GET', 'POST'])
def add_note(client_id):
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('main.login'))

    psychologist = User.query.get(session['user_id'])
    client = User.query.get(client_id)

    if not client or psychologist.role != 'psychologist':
        flash("⚠️ Invalid access.", "danger")
        return redirect(url_for('main.psychologist_notes'))

    form = NoteForm()
    if form.validate_on_submit():
        new_note = ClientNote(
            client_id=client.id,
            psychologist_id=psychologist.id,
            content=form.content.data
        )
        db.session.add(new_note)
        db.session.commit()
        flash(f"📝 Note added for {client.name}", "success")
        return redirect(url_for('main.psychologist_notes'))

    return render_template('add_note.html', form=form, client=client)

@bp.route('/client-notes/<int:client_id>')
def client_notes(client_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('main.login'))

    psychologist = User.query.get(session['user_id'])
    if psychologist.role != 'psychologist':
        flash("⛔ Access denied.", "danger")
        return redirect(url_for('main.home'))

    client = User.query.get(client_id)
    if not client:
        flash("❌ Client not found.", "danger")
        return redirect(url_for('main.psychologist_notes'))

    notes = ClientNote.query.filter_by(client_id=client.id, psychologist_id=psychologist.id)\
                            .order_by(ClientNote.created_at.desc()).all()

    return render_template('client_notes_history.html', client=client, notes=notes, user=psychologist)
