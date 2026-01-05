import sqlite3
import os

db_path = 'doctor_platform.db'

print(f"Checking database at {db_path}...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check columns in user table
    cursor.execute("PRAGMA table_info(user)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'phone_number' not in columns:
        print("Adding phone_number column...")
        cursor.execute("ALTER TABLE user ADD COLUMN phone_number TEXT")
    else:
        print("phone_number column already exists.")

    if 'membership_id' not in columns:
        print("Adding membership_id column...")
        # SQLite limitation: Cannot ADD UNIQUE column directly easily.
        # We add it as standard TEXT. App logic will ensure uniqueness.
        cursor.execute("ALTER TABLE user ADD COLUMN membership_id TEXT")
    else:
        print("membership_id column already exists.")

    # Check columns in doctor table
    cursor.execute("PRAGMA table_info(doctor)")
    doctor_columns = [info[1] for info in cursor.fetchall()]
    
    if 'education' not in doctor_columns:
        print("Adding education column to doctor table...")
        cursor.execute("ALTER TABLE doctor ADD COLUMN education TEXT")
    else:
        print("education column already exists in doctor table.")

    # Update appointment status: change 'scheduled' to 'pending'
    cursor.execute("SELECT COUNT(*) FROM appointment WHERE status = 'scheduled'")
    scheduled_count = cursor.fetchone()[0]
    if scheduled_count > 0:
        print(f"Updating {scheduled_count} appointment(s) from 'scheduled' to 'pending'...")
        cursor.execute("UPDATE appointment SET status = 'pending' WHERE status = 'scheduled'")
    else:
        print("No appointments with 'scheduled' status to update.")

    conn.commit()
    conn.close()
    print("Migration complete.")
except Exception as e:
    print(f"Error during migration: {e}")
