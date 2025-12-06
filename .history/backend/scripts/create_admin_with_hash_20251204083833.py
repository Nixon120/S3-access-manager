#!/usr/bin/env python3
"""
Create admin using pre-hashed password (salted bcrypt) passed through env var
ENV VARS: ADMIN_EMAIL, ADMIN_NAME, ADMIN_PWHASH
"""
import os
import sys
from app.core.database import SessionLocal
from app.models.user import User


def create_admin_with_hash(email, full_name, hashed_password):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User already exists: {email}")
            return

        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin created: {email}")
    except Exception as e:
        print(f"Error creating admin: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    email = os.environ.get('ADMIN_EMAIL')
    name = os.environ.get('ADMIN_NAME')
    pwhash = os.environ.get('ADMIN_PWHASH')

    if not (email and name and pwhash):
        print("ADMIN_EMAIL, ADMIN_NAME, and ADMIN_PWHASH must be set")
        sys.exit(1)

    create_admin_with_hash(email, name, pwhash)
