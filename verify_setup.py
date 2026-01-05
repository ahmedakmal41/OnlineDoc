from app import app, db
from database import User, Doctor, Hospital

def verify():
    print("Verifying setup...")
    with app.app_context():
        # Drop everything to handle schema changes cleanly for dev
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        # Create Hospitals
        h1 = Hospital(name="Mayo Clinic", city="Rochester", country="USA", 
                      image_url="https://images.unsplash.com/photo-1587351021759-3e566b9af9ef?auto=format&fit=crop&w=500",
                      specialties="General, Cardiology, Oncology")
        h2 = Hospital(name="Cleveland Clinic", city="Cleveland", country="USA",
                      image_url="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=500",
                       specialties="Cardiology, Neurology")
        h3 = Hospital(name="Charité", city="Berlin", country="Germany",
                      image_url="https://images.unsplash.com/photo-1516549655169-df83a0929519?auto=format&fit=crop&w=500",
                       specialties="Research, Virology")
        db.session.add_all([h1, h2, h3])
        db.session.commit()
        print("Test hospitals created.")

        # Create Doctors with Locations
        from werkzeug.security import generate_password_hash
        
        # Dr. House (Diagnostic)
        u1 = User(name="Dr. Gregory House", email="house@md.com", role="doctor", 
                 password=generate_password_hash("password", method='pbkdf2:sha256'))
        db.session.add(u1)
        db.session.commit()
        
        d1 = Doctor(user_id=u1.id, specialization="Diagnostics", bio="Specializes in rare diseases.", 
                   experience_years=20, consultation_fee=300.0,
                   city="Princeton", country="USA", hospital_id=h1.id) # Linked to Mayo roughly
        db.session.add(d1)

        # Dr. Strange (Neurology)
        u2 = User(name="Dr. Stephen Strange", email="strange@md.com", role="doctor",
                 password=generate_password_hash("password", method='pbkdf2:sha256'))
        db.session.add(u2)
        db.session.commit()
        
        d2 = Doctor(user_id=u2.id, specialization="Neurology", bio="Master of the mystic... and performing brain surgery.", 
                   experience_years=15, consultation_fee=500.0,
                   city="New York", country="USA", hospital_id=h2.id)
        db.session.add(d2)

        # Dr. Banner
        u3 = User(name="Dr. Bruce Banner", email="hulk@md.com", role="doctor",
                 password=generate_password_hash("password", method='pbkdf2:sha256'))
        db.session.add(u3)
        db.session.commit()
        
        d3 = Doctor(user_id=u3.id, specialization="Radiology", bio="Expert in gamma radiation.", 
                   experience_years=10, consultation_fee=150.0,
                   city="Kolkata", country="India")
        db.session.add(d3)
        
        # Admin User
        admin = User(name="Admin User", email="admin@medibook.com", role="admin",
                    password=generate_password_hash("admin123", method='pbkdf2:sha256'))
        db.session.add(admin)

        db.session.commit()
        print("Test doctors and Admin created.")

if __name__ == "__main__":
    verify()
