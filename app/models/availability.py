from app import db

class AvailabilityDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_holiday = db.Column(db.Boolean, default=False)
    slot_duration = db.Column(db.Integer, nullable=True)

    psychologist = db.relationship('User', backref='available_days')

class AvailabilitySlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('availability_day.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    is_pending = db.Column(db.Boolean, default=False)

    day = db.relationship('AvailabilityDay', backref='slots')

