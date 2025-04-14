from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from app.models import User, Booking, ClientNote, ClientTask, PsychologistProfile, AvailabilitySlot, AvailabilityDay
from datetime import datetime, date
from app import db
from app.forms import PsyProfileForm, CliProfileForm
from werkzeug.utils import secure_filename
import os

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/client-profile')
def cli_profile_view():
    if 'user_id' not in session:
        flash("🔐 Please log in to access your profile.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'client':
        flash("⛔ Only clients can view this profile.", "danger")
        return redirect(url_for('main_routes.home'))

    last_note = ClientNote.query.filter_by(client_id=user.id)\
        .order_by(ClientNote.created_at.desc()).first()

    last_consult = Booking.query.filter_by(client_id=user.id, status='confirmed')\
        .filter(Booking.appointment_time < datetime.utcnow())\
        .order_by(Booking.appointment_time.desc()).first()

    next_consult = Booking.query.filter_by(client_id=user.id, status='confirmed')\
        .filter(Booking.appointment_time >= datetime.utcnow())\
        .order_by(Booking.appointment_time.asc()).first()

    last_task = ClientTask.query.filter_by(client_id=user.id)\
        .order_by(ClientTask.created_at.desc()).first()

    return render_template(
        'profile/cli_profile_view.html',
        user=user,
        last_note=last_note,
        last_task=last_task,
        last_consult=last_consult,
        next_consult=next_consult
    )

@profile_bp.route('/client-profile/edit', methods=['GET', 'POST'])
def cli_profile_edit():
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'client':
        flash("⛔ Only clients can edit this profile.", "danger")
        return redirect(url_for('main_routes.home'))

    form = CliProfileForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        # user.birth_date = form.birth_date.data
        user.bio = form.bio.data
        db.session.commit()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for('profile.cli_profile_view'))

    return render_template('profile/cli_profile_edit.html', form=form)

@profile_bp.route('/psychologists-list')
def cli_view_psychologists():
    if 'user_id' not in session:
        flash("🔐 Please log in to view psychologists.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if user.role != 'client':
        flash("⛔ Only clients can access this page.", "danger")
        return redirect(url_for('main_routes.home'))

    from datetime import datetime
    psychologists = User.query.filter_by(role='psychologist').all()

    psychologists_data = []
    for psy in psychologists:
        first_available_slot = (
            AvailabilitySlot.query
            .join(AvailabilityDay)
            .filter(
                AvailabilityDay.psychologist_id == psy.id,
                AvailabilitySlot.is_booked == False,
                AvailabilitySlot.is_pending == False,
                AvailabilityDay.date >= datetime.utcnow().date()
            )
            .order_by(AvailabilityDay.date.asc(), AvailabilitySlot.time.asc())
            .first()
        )

        psychologists_data.append({
            "psychologist": psy,
            "slot": first_available_slot
        })

    return render_template('profile/cli_view_psychologists.html', psychologists_data=psychologists_data)


@profile_bp.route('/psychologist/<int:psy_id>')
def cli_view_psychologist(psy_id):
    if 'user_id' not in session:
        flash("🔐 Please log in to continue.", "warning")
        return redirect(url_for('auth.login'))

    client = User.query.get(session['user_id'])
    if client.role != 'client':
        flash("⛔ Only clients can view psychologist availability.", "danger")
        return redirect(url_for('main_routes.home'))

    psychologist = User.query.get_or_404(psy_id)
    profile = psychologist.profile

    # Filter future confirmed availability (not booked)
    from datetime import datetime
    upcoming_slots = (
        Booking.query
        .filter_by(psychologist_id=psychologist.id, status='available')
        .filter(Booking.appointment_time >= datetime.utcnow())
        .order_by(Booking.appointment_time.asc())
        .all()
    )

    return render_template(
        'profile/cli_view_psychologist.html',
        psychologist=psychologist,
        profile=profile,
        upcoming_slots=upcoming_slots
    )


@profile_bp.route('/psychologist-profile', methods=['GET', 'POST'])
def psy_profile_view():
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Only psychologists can view this page.", "danger")
        return redirect(url_for('main_routes.home'))

    profile = user.profile

    if not profile:
        profile = PsychologistProfile(user_id=user.id, license_number='N/A', specialization='', pricing=0.0)
        db.session.add(profile)
        db.session.commit()

    client_ids = {b.client_id for b in user.consultations} if hasattr(user, 'consultations') else set()
    total_clients = len(client_ids)
    total_consults = len(user.consultations) if hasattr(user, 'consultations') else 0

    age = None
    if user.birth_date:
        today = date.today()
        age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))

    if request.method == 'POST':
        profile.show_clients = bool(request.form.get('show_clients'))
        profile.show_consultations = bool(request.form.get('show_consultations'))
        db.session.commit()
        flash("🔧 Profile settings updated!", "success")
        return redirect(url_for('profile.psy_profile_view'))

    return render_template(
        'profile/psy_profile_view.html',
        user=user,
        profile=profile,
        age=age,
        total_clients=total_clients,
        total_consults=total_consults
    )

@profile_bp.route('/psychologist-profile/edit', methods=['GET', 'POST'])
def psy_profile_edit():
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if user.role != 'psychologist':
        flash("⛔ Only psychologists can edit this profile.", "danger")
        return redirect(url_for('main_routes.home'))

    profile = user.profile
    if not profile:
        profile = PsychologistProfile(user_id=user.id, specialization='', pricing=0.0)
        db.session.add(profile)
        db.session.commit()

    form = PsyProfileForm(obj=profile) 

    if form.validate_on_submit():
        profile.specialization = form.specialization.data
        profile.bio = form.bio.data
        profile.pricing = form.pricing.data
        profile.experience_years = form.experience_years.data
        db.session.commit()
        flash("✅ Profile updated successfully.", "success")
        return redirect(url_for('profile.psy_profile_view'))

    return render_template(
        'profile/psy_profile_edit.html',
        form=form,
        user=user,
        profile=profile
    )

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/upload-profile-photo', methods=['POST'])
def upload_profile_photo():
    if 'user_id' not in session:
        flash("🔐 Please log in.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("❌ User not found.", "danger")
        return redirect(url_for('main_routes.home'))

    file = request.files.get('profile_photo')
    print(f"File received: {file.filename if file else 'No file received'}")  # Debug statement

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')

        # Ensure the upload folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        upload_path = os.path.join(upload_folder, filename)
        print(f"Uploading file to: {upload_path}")  # Debug statement

        try:
            # Save the file
            file.save(upload_path)
            print(f"File saved successfully: {upload_path}")  # Debug statement

            # Update user's profile photo path
            user.profile_pic = f'uploads/profile_pics/{filename}'
            db.session.commit()
            print(f"Profile picture path in database: {user.profile_pic}")  # Debug statement

            flash("✅ Profile photo updated successfully!", "success")
        except Exception as e:
            print(f"Error saving file: {e}")  # Debug statement
            flash(f"❌ Error saving file: {str(e)}", "danger")
    else:
        flash("❌ Invalid file type. Please upload an image file.", "danger")

    return redirect(url_for('profile.cli_profile_edit' if user.role == 'client' else 'profile.psy_profile_edit'))