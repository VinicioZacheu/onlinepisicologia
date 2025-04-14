from app import db
from datetime import datetime

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    notes = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    discount_description = db.Column(db.String(255), nullable=True)
    client = db.relationship('User', foreign_keys=[client_id], backref='bookings_made')
    psychologist = db.relationship('User', foreign_keys=[psychologist_id], backref='bookings_received')
    cancellation_reason = db.Column(db.Text, nullable=True)
    follow_up_required = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, nullable=True)


    def __repr__(self):
        return f'<Booking Client {self.client_id} -> Psychologist {self.psychologist_id} on {self.appointment_time}>'

class SessionFollowUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    client_notes = db.Column(db.Text, nullable=True)
    psychologist_notes = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)
    action_items = db.Column(db.Text, nullable=True)
    next_steps = db.Column(db.Text, nullable=True)

    booking = db.relationship('Booking', backref='followup')

    def __repr__(self):
        return f'<SessionFollowUp for Booking {self.booking_id}>'
