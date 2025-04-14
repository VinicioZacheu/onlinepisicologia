from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import User, Booking, ClientNote
from app.forms import NoteForm
from datetime import datetime, timedelta
from app import db

note_bp = Blueprint('notes', __name__)

@note_bp.route('/psychologist-notes')
def psy_notes_dashboard():
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Access denied. Only psychologists can view notes.", "danger")
        return redirect(url_for('main_routes.home'))

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
        "notes/psy_notes_dashboard.html",
        user=user,
        active_clients=active_clients,
        inactive_clients=[],
        today=today
    )

@note_bp.route('/add-note/<int:client_id>', methods=['GET', 'POST'])
def psy_add_note(client_id):
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    psychologist = User.query.get(session['user_id'])
    client = User.query.get(client_id)

    if not client or psychologist.role != 'psychologist':
        flash("⚠️ Invalid access.", "danger")
        return redirect(url_for('notes.psy_notes_dashboard'))

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
        return redirect(url_for('notes.psy_notes_dashboard'))

    return render_template('notes/psy_add_note.html', form=form, client=client)

@note_bp.route('/client-notes/<int:client_id>')
def psy_client_notes_history(client_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    psychologist = User.query.get(session['user_id'])
    if psychologist.role != 'psychologist':
        flash("⛔ Access denied.", "danger")
        return redirect(url_for('main_routes.home'))

    client = User.query.get(client_id)
    if not client:
        flash("❌ Client not found.", "danger")
        return redirect(url_for('notes.psy_notes_dashboard'))

    notes = ClientNote.query.filter_by(client_id=client.id, psychologist_id=psychologist.id)\
                            .order_by(ClientNote.created_at.desc()).all()

    return render_template('notes/psy_client_notes_history.html', client=client, notes=notes, user=psychologist)

@note_bp.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
def psy_edit_note(note_id):
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    note = ClientNote.query.get_or_404(note_id)

    if request.method == 'POST':
        new_content = request.form.get('content')
        note.content = new_content
        db.session.commit()
        flash("📝 Note updated successfully.", "success")
        return redirect(url_for('notes.psy_client_notes_history', client_id=note.client_id))

    return render_template('notes/psy_edit_note.html', note=note)

@note_bp.route('/delete-note/<int:note_id>', methods=['POST'])
def psy_delete_note(note_id):
    if 'user_id' not in session:
        flash("🔐 Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    note = ClientNote.query.get_or_404(note_id)
    client_id = note.client_id
    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note deleted successfully.", "success")
    return redirect(url_for('notes.psy_client_notes_history', client_id=client_id))

@note_bp.route('/my-notes', methods=['GET', 'POST'])
def cli_notes_dashboard():
    if 'user_id' not in session:
        flash("🔐 Please log in to access your notes.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'client':
        flash("⛔ Access restricted to clients only.", "danger")
        return redirect(url_for('main_routes.home'))

    psy_notes_dashboard = ClientNote.query.filter(
        ClientNote.client_id == user.id,
        ClientNote.psychologist_id.isnot(None)
    ).order_by(ClientNote.created_at.desc()).all()

    psy_client_notes_history = ClientNote.query.filter(
        ClientNote.client_id == user.id,
        ClientNote.psychologist_id.is_(None)
    ).order_by(ClientNote.created_at.desc()).all()

    return render_template(
        "notes/cli_notes_dashboard.html",
        user=user,
        psy_notes_dashboard=psy_notes_dashboard,
        psy_client_notes_history=psy_client_notes_history)

@note_bp.route('/submit-client-note', methods=['POST'])
def cli_submit_note():
    if 'user_id' not in session:
        flash("🔐 Please log in to submit notes.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'client':
        flash("⛔ Only clients can submit personal notes.", "danger")
        return redirect(url_for('main_routes.home'))

    content = request.form.get('content')
    if not content:
        flash("✏️ Please write something before submitting.", "warning")
        return redirect(url_for('notes.cli_notes_dashboard'))

    new_note = ClientNote(
        client_id=user.id,
        psychologist_id=None,  
        content=content
    )

    db.session.add(new_note)
    db.session.commit()

    flash("📝 Your note has been saved.", "success")
    return redirect(url_for('notes.cli_notes_dashboard'))

@note_bp.route('/edit-client-note/<int:note_id>', methods=['GET', 'POST'])
def cli_edit_note(note_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    note = ClientNote.query.get_or_404(note_id)
    user = User.query.get(session['user_id'])

    if note.client_id != user.id or user.role != 'client':
        flash("⛔ You cannot edit this note.", "danger")
        return redirect(url_for('notes.cli_notes_dashboard'))

    if request.method == 'POST':
        note.content = request.form.get('content')
        db.session.commit()
        flash("📝 Note updated!", "success")
        return redirect(url_for('notes.cli_notes_dashboard'))

    return render_template('notes/cli_edit_note.html', note=note)

@note_bp.route('/delete-client-note/<int:note_id>', methods=['POST'])
def cli_delete_note(note_id):
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    note = ClientNote.query.get_or_404(note_id)
    user = User.query.get(session['user_id'])

    if note.client_id != user.id or user.role != 'client':
        flash("⛔ You cannot delete this note.", "danger")
        return redirect(url_for('notes.cli_notes_dashboard'))

    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note deleted.", "success")
    return redirect(url_for('notes.cli_notes_dashboard'))

