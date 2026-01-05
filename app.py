import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Doctor, Appointment, Hospital
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'doctor_platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'

db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Helper functions for independent admin/user sessions
def get_current_admin():
    """Get current admin user from session without affecting regular user session"""
    # Strict validation: must have both session keys AND they must be valid
    if 'admin_user_id' not in session or 'admin_authenticated' not in session:
        return None
    
    # Verify session flag is actually True (not just present)
    if not session.get('admin_authenticated', False):
        clear_admin_session()
        return None
    
    # Get user and verify it exists and has admin role
    try:
        admin_user = User.query.get(session['admin_user_id'])
        if admin_user and admin_user.role == 'admin':
            return admin_user
        else:
            # User doesn't exist or doesn't have admin role - clear invalid session
            clear_admin_session()
            return None
    except Exception:
        # Any error means invalid session
        clear_admin_session()
        return None

def set_admin_session(user):
    """Set admin session independently from regular user session"""
    # Clear any existing admin session first
    clear_admin_session()
    # Set new admin session with user ID and timestamp
    session['admin_user_id'] = user.id
    session['admin_authenticated'] = True
    session['admin_session_start'] = datetime.utcnow().isoformat()
    session.permanent = True  # Make session persistent

def clear_admin_session():
    """Clear admin session completely"""
    session.pop('admin_user_id', None)
    session.pop('admin_authenticated', None)
    session.pop('admin_session_start', None)

# Context processor to make admin_user available in all templates
# Only returns admin user if they're logged in via admin session AND have admin role
@app.context_processor
def inject_admin_user():
    # CRITICAL SECURITY: Only show admin panel if admin is properly authenticated
    # AND no regular user is logged in (unless the regular user IS the admin)
    
    admin_user = get_current_admin()
    
    # If no valid admin session, definitely no admin panel
    if not admin_user:
        return dict(admin_user=None)
    
    # Additional security check: If a regular user is logged in
    if current_user.is_authenticated:
        # Only show admin panel if the logged-in regular user IS the same admin
        if current_user.id != admin_user.id:
            # Different user is logged in as regular user - don't show admin panel
            # This prevents patients/doctors from seeing admin panel
            return dict(admin_user=None)
    
    # Admin session is valid and either:
    # - No regular user logged in, OR
    # - The regular user IS the admin (same person)
    return dict(admin_user=admin_user)

# Print email configuration status on startup
if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_USERNAME') != 'your-email@gmail.com':
    print(f"✅ Email configured: {app.config.get('MAIL_USERNAME')}")
    print(f"✅ SMTP Server: {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
else:
    print("⚠️  WARNING: Email not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
    print("   Emails will not be sent until configured.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_appointment_confirmation_email(appointment):
    """Send confirmation email to patient when appointment is confirmed"""
    try:
        patient = appointment.patient
        doctor = appointment.doctor
        
        # Check if email is configured
        if not app.config.get('MAIL_USERNAME') or app.config.get('MAIL_USERNAME') == 'your-email@gmail.com':
            print("ERROR: Email not configured. Please set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
            return False
        
        if not app.config.get('MAIL_PASSWORD') or app.config.get('MAIL_PASSWORD') == 'your-app-password':
            print("ERROR: Email password not configured. Please set MAIL_PASSWORD environment variable.")
            return False
        
        print(f"Attempting to send email to: {patient.email}")
        print(f"Using SMTP server: {app.config.get('MAIL_SERVER')}")
        print(f"Using email account: {app.config.get('MAIL_USERNAME')}")
        
        # Create email message
        msg = Message(
            subject='Appointment Confirmed - MediBook',
            recipients=[patient.email],
            html=render_template('emails/appointment_confirmation.html', 
                               appointment=appointment,
                               patient=patient,
                               doctor=doctor)
        )
        
        mail.send(msg)
        print(f"✅ Email sent successfully to {patient.email}")
        return True
    except Exception as e:
        import traceback
        print(f"❌ Error sending email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

@app.route('/')
def index():
    doctors = Doctor.query.limit(4).all()
    return render_template('index.html', doctors=doctors)

from functools import wraps

# Admin Decorator - uses separate admin session
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_user = get_current_admin()
        # Strict check: must be logged in via admin session AND have admin role
        if not admin_user or admin_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            # Clear any invalid admin session
            clear_admin_session()
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- API ROUTES ---
@app.route('/api/slots/<int:doctor_id>')
def get_slots(doctor_id):
    date_str = request.args.get('date') # YYYY-MM-DD
    if not date_str:
        return jsonify([])
        
    # Mock logic: Mon-Fri 9-5
    # In real app: check DB for bookings
    start_date = datetime.strptime(date_str, '%Y-%m-%d')
    slots = []
    
    # Simple hours 9:00 to 17:00
    for hour in range(9, 17):
        time_slot = f"{hour:02d}:00"
        
        # Check collision - only block slots with confirmed appointments
        # Pending appointments don't block slots until they're confirmed
        dt = datetime.strptime(f"{date_str} {time_slot}", '%Y-%m-%d %H:%M')
        booking = Appointment.query.filter_by(doctor_id=doctor_id, date_time=dt).filter(Appointment.status == 'confirmed').first()
        
        slots.append({
            'time': time_slot,
            'available': booking is None
        })
        
    return jsonify(slots)

# --- ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Check admin session (not regular user session)
    admin_user = get_current_admin()
    if admin_user:  # get_current_admin() already verifies role
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if user.role != 'admin':
                flash('Access denied. Admin privileges required.', 'error')
                return redirect(url_for('admin_login'))
                
            # Clear any existing admin session first (security)
            clear_admin_session()
            # Set admin session independently (doesn't affect regular user session)
            set_admin_session(user)
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
            
    return render_template('admin/login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Stats
    total_users = User.query.count()
    total_doctors = Doctor.query.count()
    total_appts = Appointment.query.count()
    pending_appts = Appointment.query.filter_by(status='pending').count()
    
    # Admin can see all recent appointments
    recent_appts = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users, 
                          total_doctors=total_doctors,
                          total_appts=total_appts,
                          pending_appts=pending_appts,
                          recent_appts=recent_appts)

@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.date_time.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/appointment/<int:id>/<action>')
@admin_required
def admin_appt_action(id, action):
    appt = Appointment.query.get_or_404(id)
    if action == 'confirm':
        appt.status = 'confirmed'
        db.session.commit()
        
        # Send confirmation email to patient
        email_sent = send_appointment_confirmation_email(appt)
        if email_sent:
            flash('Appointment confirmed successfully! Confirmation email sent to patient.', 'success')
        else:
            flash('Appointment confirmed, but email could not be sent. Please check email configuration.', 'warning')
    elif action == 'cancel':
        appt.status = 'cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'success')
    else:
        # Reset to pending if needed
        appt.status = 'pending'
        db.session.commit()
        
    return redirect(request.referrer or url_for('admin_appointments'))

@app.route('/admin/doctors', methods=['GET', 'POST'])
@admin_required
def admin_doctors():
    if request.method == 'POST':
        # Add Doctor Logic (User creation + Doctor profile)
        name = request.form.get('name')
        email = request.form.get('email')
        specialization = request.form.get('specialization')
        city = request.form.get('city')
        country = request.form.get('country')
        fee = float(request.form.get('fee', 50.0))
        
        # Check email
        if User.query.filter_by(email=email).first():
            flash('Email exists', 'error')
        else:
            u = User(name=name, email=email, role='doctor', password=generate_password_hash('doctor123', method='pbkdf2:sha256'))
            db.session.add(u)
            db.session.commit()
            
            d = Doctor(user_id=u.id, specialization=specialization, city=city, country=country, consultation_fee=fee)
            db.session.add(d)
            db.session.commit()
            flash('Doctor added', 'success')
        return redirect(url_for('admin_doctors'))
        
    doctors = Doctor.query.all()
    return render_template('admin/doctors.html', doctors=doctors)

@app.route('/admin/hospitals', methods=['GET', 'POST'])
@admin_required
def admin_hospitals():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        country = request.form.get('country')
        specialties = request.form.get('specialties')
        
        h = Hospital(name=name, city=city, country=country, specialties=specialties, image_url="https://via.placeholder.com/400")
        db.session.add(h)
        db.session.commit()
        flash('Hospital added', 'success')
        return redirect(url_for('admin_hospitals'))
        
    hospitals = Hospital.query.all()
    return render_template('admin/hospitals.html', hospitals=hospitals)

@app.route('/doctors')
def list_doctors():
    specialty = request.args.get('specialty')
    city = request.args.get('city')
    country = request.args.get('country')
    
    query = Doctor.query
    if specialty:
        query = query.filter(Doctor.specialization.ilike(f'%{specialty}%'))
    if city:
        query = query.filter(Doctor.city.ilike(f'%{city}%'))
    if country:
        query = query.filter(Doctor.country.ilike(f'%{country}%'))
        
    doctors = query.all()
    
    # Get unique values for filters
    specialties = sorted(set([d.specialization for d in Doctor.query.all()]))
    cities = sorted(set([d.city for d in Doctor.query.filter(Doctor.city != None).all()]))
    countries = sorted(set([d.country for d in Doctor.query.filter(Doctor.country != None).all()]))
    
    return render_template('doctors.html', doctors=doctors, specialties=specialties, cities=cities, countries=countries)

@app.route('/hospitals')
def list_hospitals():
    city = request.args.get('city')
    country = request.args.get('country')
    
    query = Hospital.query
    if city:
        query = query.filter(Hospital.city.ilike(f'%{city}%'))
    if country:
        query = query.filter(Hospital.country.ilike(f'%{country}%'))
        
    hospitals = query.all()
    
    cities = sorted(set([h.city for h in Hospital.query.all()]))
    countries = sorted(set([h.country for h in Hospital.query.all()]))
    
    return render_template('hospitals.html', hospitals=hospitals, cities=cities, countries=countries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Clear any existing admin session when regular user logs in
            # This ensures patients/doctors don't see admin panel
            clear_admin_session()
            
            login_user(user)
            flash('Logged in successfully.', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role', 'patient')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
            
        # Generate unique membership ID
        # Format: MB-YYYY-RANDOM (e.g., MB-2024-A1B2C3)
        import random
        import string
        year = datetime.now().year
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        membership_id = f"MB-{year}-{suffix}"
        
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            phone_number=phone,
            membership_id=membership_id
        )
        db.session.add(new_user)
        db.session.commit()
        
        # If doctor, create doctor profile with professional details
        if role == 'doctor':
            specialization = request.form.get('specialization', 'General')
            education = request.form.get('education', '')
            city = request.form.get('city', '')
            country = request.form.get('country', '')
            consultation_fee = float(request.form.get('consultation_fee', 50.0))
            experience_years = request.form.get('experience_years')
            
            new_doctor = Doctor(
                user_id=new_user.id,
                specialization=specialization,
                education=education,
                city=city,
                country=country,
                consultation_fee=consultation_fee,
                experience_years=int(experience_years) if experience_years else None
            )
            db.session.add(new_doctor)
            db.session.commit()

        # Clear any existing admin session when new user registers and logs in
        clear_admin_session()
        login_user(new_user)
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone_number = request.form.get('phone')
        # Email update is sensitive, normally requires verification, but we allow simple update here
        new_email = request.form.get('email')
        
        if new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email already in use.', 'error')
            else:
                current_user.email = new_email
        
        # Update doctor profile if user is a doctor
        if current_user.role == 'doctor' and current_user.doctor_profile:
            doctor = current_user.doctor_profile
            doctor.specialization = request.form.get('specialization', doctor.specialization)
            doctor.education = request.form.get('education', '')
            doctor.city = request.form.get('city', '')
            doctor.country = request.form.get('country', '')
            doctor.consultation_fee = float(request.form.get('consultation_fee', doctor.consultation_fee))
            doctor.bio = request.form.get('bio', '')
            
            experience_years = request.form.get('experience_years')
            doctor.experience_years = int(experience_years) if experience_years else None
            
            hospital_id = request.form.get('hospital_id')
            doctor.hospital_id = int(hospital_id) if hospital_id else None
                
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Get hospitals for doctor association dropdown
    hospitals = Hospital.query.all() if current_user.role == 'doctor' else []
    return render_template('profile.html', hospitals=hospitals)

@app.route('/dashboard')
@login_required
def dashboard():
    # Prevent admins from accessing regular dashboard
    # Admins should use admin_dashboard, not regular dashboard
    if current_user.role == 'admin':
        # If admin is logged in as regular user, redirect to admin panel
        # But only if they're not also logged in as admin (which would be separate)
        admin_user = get_current_admin()
        if admin_user:
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Please use the admin panel for admin functions.', 'info')
            return redirect(url_for('admin_login'))
    
    # Regular users (patients and doctors) can ONLY access their own appointments
    if current_user.role == 'doctor':
        # Doctors can only see appointments scheduled with them
        if not current_user.doctor_profile:
            flash('Doctor profile not found.', 'error')
            return redirect(url_for('profile'))
        appointments = Appointment.query.filter_by(doctor_id=current_user.doctor_profile.id).all()
        return render_template('dashboard_doctor.html', appointments=appointments)
    elif current_user.role == 'patient':
        # Patients can only see their own appointments
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
        return render_template('dashboard_patient.html', appointments=appointments)
    else:
        # Any other role should not access this
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    # Only logout regular user session, not admin session
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/logout')
def admin_logout():
    # Logout admin session only, doesn't affect regular user session
    clear_admin_session()
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    # Ensure only patients can book appointments (not doctors or admins)
    if current_user.role != 'patient':
        flash('Only patients can book appointments.', 'error')
        return redirect(url_for('dashboard'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        consultation_type = request.form.get('type')
        notes = request.form.get('notes')
        
        # Combine date and time
        dt_string = f"{date_str} {time_str}"
        appointment_time = datetime.strptime(dt_string, '%Y-%m-%d %H:%M')
        
        # Security: Ensure appointment is created with current_user as patient
        # Users can only book appointments for themselves
        new_appointment = Appointment(
            patient_id=current_user.id,  # Always use current_user.id, never from form data
            doctor_id=doctor.id,
            date_time=appointment_time,
            type=consultation_type,
            notes=notes,
            status='pending',  # Appointments start as pending until admin confirms
            meeting_link=f"https://meet.jit.si/consultation-{current_user.id}-{doctor.id}" if consultation_type == 'online' else None
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment requested successfully! It will be confirmed by admin shortly.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('booking.html', doctor=doctor)

# Initialize DB
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
