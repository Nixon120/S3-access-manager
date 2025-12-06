#!/usr/bin/env python3
"""
Update admin user password to Maya100$
"""
import sys
from app.core.database import SessionLocal
from app.models.user import User
import bcrypt


# User credentials
email = "nixonlauture@gmail.com"
password = "Maya100$"  # The requested password

# Generate hash using bcrypt directly
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
hashed_password = hashed.decode('utf-8')

db = SessionLocal()

try:
    print(f"=== Updating Admin User Password ===\n")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User {email} not found!")
        sys.exit(1)
    
    # Update password
    user.hashed_password = hashed_password
    db.commit()
    
    print(f"✅ Password updated successfully!")
    print(f"   Email: {email}")
    print(f"   New Password: {password}")
    print(f"   Hash: {hashed_password}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()
