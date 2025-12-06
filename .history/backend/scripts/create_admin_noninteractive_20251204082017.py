#!/usr/bin/env python3
"""
Non-interactive admin creator
"""
import os
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def create_admin_noninteractive():
    db = SessionLocal()
    try:
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        full_name = os.environ.get("ADMIN_NAME", "Admin User")
        password = os.environ.get("ADMIN_PASSWORD", "AdminPass123!")

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Admin user already exists: {email}")
            return

        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created: {email}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    create_admin_noninteractive()
