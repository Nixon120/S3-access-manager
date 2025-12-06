#!/usr/bin/env python3
"""
Quick script to create an admin user
"""
import sys
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


# User credentials
email = "nixonlauture@gmail.com"
full_name = "Nixon Lauture"
password = "Maya100$"

db = SessionLocal()

try:
    print(f"=== Creating Admin User ===\n")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"✅ User with email {email} already exists!")
        print(f"   Email: {email}")
        print(f"   Name: {existing_user.full_name}")
        print(f"   Admin: {existing_user.is_admin}")
    else:
        # Create admin user
        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Admin: True")
    
except Exception as e:
    print(f"❌ Error creating admin user: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()
