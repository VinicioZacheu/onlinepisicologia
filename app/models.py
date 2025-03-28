from . import db
from datetime import datetime, date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' or 'psychologist'
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.name} - {self.role}>'
    
class PsychologistProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    pricing = db.Column(db.Float, nullable=False)
    experience_years = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    def __repr__(self):
        return f'<Profile for User ID {self.user_id}>'
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # e.g., scheduled, completed, canceled
    notes = db.Column(db.Text, nullable=True)

    price = db.Column(db.Float, nullable=True)  # Final price for that session
    discount_description = db.Column(db.String(255), nullable=True)

    client = db.relationship('User', foreign_keys=[client_id], backref='bookings_made')
    psychologist = db.relationship('User', foreign_keys=[psychologist_id], backref='bookings_received')

    def __repr__(self):
        return f'<Booking Client {self.client_id} -> Psychologist {self.psychologist_id} on {self.appointment_time}>'
    
class SessionFollowUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    client_notes = db.Column(db.Text, nullable=True)
    psychologist_notes = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)

    booking = db.relationship('Booking', backref='followup')

    def __repr__(self):
        return f'<SessionFollowUp for Booking {self.booking_id}>'
    
class ClientLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    mood_score = db.Column(db.Float, nullable=True)  # For sentiment analysis

    client = db.relationship('User', backref='daily_logs')

    def __repr__(self):
        return f'<ClientLog {self.client_id} on {self.date_logged}>'

class AvailabilityDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=False)

    psychologist = db.relationship('User', backref='available_days')


class AvailabilitySlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('availability_day.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    is_pending = db.Column(db.Boolean, default=False)

    day = db.relationship('AvailabilityDay', backref='slots')

class PsychologistNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking = db.relationship('Booking', backref='psychologist_notes')


class ClientEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('User', backref='evaluations')

class ClientTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1–10

    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    client_note = db.Column(db.Text, nullable=True)
    client_photo = db.Column(db.String(256), nullable=True)  # Path to uploaded photo

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('User', foreign_keys=[client_id], backref='tasks')
    psychologist = db.relationship('User', foreign_keys=[psychologist_id])

class ClientNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('User', foreign_keys=[client_id], backref='notes')
    psychologist = db.relationship('User', foreign_keys=[psychologist_id])
