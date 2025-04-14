from app import db

class PsychologistProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    license_number = db.Column(db.String(50), nullable=True)
    specialization = db.Column(db.String(200), nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    languages = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    pricing = db.Column(db.Float, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    show_clients = db.Column(db.Boolean, default=False)
    show_consultations = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    def __repr__(self):
        return f'<Profile for User ID {self.user_id}>'

class ClientProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('client_profile', uselist=False))

    def __repr__(self):
        return f'<ClientProfile for User ID {self.user_id}>'