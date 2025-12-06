#!/usr/bin/env python3
"""
Script to create an admin user via command line arguments
"""
import sys
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_admin(email: str, full_name: str, password: str):
    """Create an admin user"""
    db = SessionLocal()
    
    try:
        print(f"=== Creating Admin User ===\n")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            sys.exit(1)
        
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
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_user_cmd.py <email> <full_name> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    full_name = sys.argv[2]
    password = sys.argv[3]
    
    create_admin(email, full_name, password)
