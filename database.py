from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient', 'doctor', 'admin'
    
    # New Profile Fields
    phone_number = db.Column(db.String(20), nullable=True)
    membership_id = db.Column(db.String(20), unique=True, nullable=True)
    
    # Relationships
    appointments_as_patient = db.relationship('Appointment', backref='patient', foreign_keys='Appointment.patient_id', lazy=True)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    specialties = db.Column(db.String(200), nullable=True) # Comma separated list for simple filtering

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    consultation_fee = db.Column(db.Float, nullable=False, default=50.0)
    image_url = db.Column(db.String(200), nullable=True)
    
    # Education
    education = db.Column(db.Text, nullable=True)  # Can store multiple degrees/institutions
    
    # Location for filtering
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    # Link to hospital (Optional)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)
    
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))
    hospital = db.relationship('Hospital', backref=db.backref('doctors', lazy=True))
    appointments = db.relationship('Appointment', backref='doctor', foreign_keys='Appointment.doctor_id', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'completed', 'cancelled'
    type = db.Column(db.String(20), default='online') # 'online', 'physical'
    meeting_link = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
