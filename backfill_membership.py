from app import app, db, User
import random
import string
from datetime import datetime

def generate_id():
    year = datetime.now().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"MB-{year}-{suffix}"

with app.app_context():
    users = User.query.filter(User.membership_id == None).all()
    print(f"Found {len(users)} users without Membership ID.")
    
    for user in users:
        new_id = generate_id()
        # Ensure uniqueness (simple check)
        while User.query.filter_by(membership_id=new_id).first():
            new_id = generate_id()
            
        user.membership_id = new_id
        print(f"Assigned {new_id} to {user.name}")
        
    db.session.commit()
    print("Backfill complete!")
