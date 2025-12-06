#!/usr/bin/env python3
"""
Script to create an admin user
"""
import sys
from getpass import getpass
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_admin():
    """Create an admin user"""
    db = SessionLocal()
    
    try:
        print("=== Create Admin User ===\n")
        
        # Get user input
        email = input("Admin email: ")
        full_name = input("Full name: ")
        password = getpass("Password: ")
        password_confirm = getpass("Confirm password: ")
        
        if password != password_confirm:
            print("❌ Passwords do not match!")
            sys.exit(1)
        
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
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
