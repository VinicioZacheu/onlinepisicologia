from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import User, AvailabilityDay, AvailabilitySlot, Booking
from app import db
from datetime import datetime

book_bp = Blueprint('booking', __name__)

@book_bp.route('/book-session')
def cli_book_session():
    if 'user_id' not in session:
        flash("🔐 Please log in to book a session.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if user.role != 'client':
        flash("⛔ Access denied. Only clients can book sessions.", "danger")
        return redirect(url_for('main_routes.home'))

    available_days = AvailabilityDay.query.all()

    return render_template('booking/cli_book_session.html', user=user, available_days=available_days)


@book_bp.route('/book-session/<int:slot_id>')
def cli_request_booking(slot_id):  # 👈 Renamed
    if 'user_id' not in session:
        flash("Please log in.", "warning")
        return redirect(url_for('auth.login'))

    client = User.query.get(session['user_id'])
    slot = AvailabilitySlot.query.get(slot_id)

    if not slot or slot.is_booked or slot.is_pending:
        flash("⚠️ Slot not available.", "danger")
        return redirect(url_for('booking.cli_book_session'))

    booking = Booking(
        client_id=client.id,
        psychologist_id=slot.day.psychologist_id,
        appointment_time=datetime.combine(slot.day.date, slot.time),
        status='pending'
    )
    db.session.add(booking)

    slot.is_pending = True
    db.session.commit()

    flash("✅ Booking request submitted. Waiting for psychologist approval.", "success")
    return redirect(url_for('dashboard.cli_dashboard'))

@book_bp.route('/add-availability', methods=['GET', 'POST'])
def psy_add_availability():
    if 'user_id' not in session:
        flash("You must be logged in as a psychologist.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if user.role != 'psychologist':
        flash("Access denied: only psychologists can set availability.", "danger")
        return redirect(url_for('main_routes.home'))

    from app.forms import AvailabilityForm
    form = AvailabilityForm()

    if form.validate_on_submit():
        day = AvailabilityDay(
            psychologist_id=user.id,
            date=form.date.data
        )
        db.session.add(day)
        db.session.commit()

        for slot_form in form.slots:
            if slot_form.time.data:
                slot = AvailabilitySlot(day_id=day.id, time=slot_form.time.data)
                db.session.add(slot)

        db.session.commit()
        flash("✅ Availability added successfully.", "success")

        if form.add_another.data:
            flash("🔁 You chose to add another one.", "info")
            return redirect(url_for('booking.psy_add_availability'))
        else:
            flash("🔙 Redirecting to your dashboard.", "info")
            return redirect(url_for('dashboard.psy_dashboard'))

    return render_template('booking/psy_add_availability.html', form=form)

@book_bp.route('/pending-bookings')
def psy_pending_bookings():
    if 'user_id' not in session:
        flash("🔐 Debug: No user_id in session. Redirecting to login.", "warning")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("❌ Debug: User not found.", "danger")
        return redirect(url_for('auth.login'))

    if user.role != 'psychologist':
        flash(f"⛔ Debug: Access denied for role '{user.role}'. Redirecting to home.", "danger")
        return redirect(url_for('main_routes.home'))

    bookings = Booking.query.filter_by(psychologist_id=user.id, status='pending').order_by(Booking.appointment_time).all()
    flash(f"🧠 Debug: Loaded {len(bookings)} pending bookings for {user.name}.", "info")

    return render_template('booking/psy_pending_bookings.html', bookings=bookings, user=user)

@book_bp.route('/handle-booking/<int:booking_id>/<string:action>')
def psy_handle_booking(booking_id, action):
    user_id = session.get('user_id')
    booking = Booking.query.get(booking_id)

    if not booking:
        flash(f"❌ Debug: Booking ID {booking_id} not found.", "danger")
        return redirect(url_for('booking.psy_pending_bookings'))

    if booking.psychologist_id != user_id:
        flash(f"🚫 Debug: Booking {booking_id} does not belong to logged-in psychologist (ID {user_id}).", "danger")
        return redirect(url_for('booking.psy_pending_bookings'))

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

    return redirect(url_for('booking.psy_pending_bookings'))

