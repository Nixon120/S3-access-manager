#!/usr/bin/env python3
"""
Reset password for a user using a plaintext password (will generate bcrypt hash using bcrypt library)
ENV VARS: TARGET_EMAIL, TARGET_PASSWORD
"""
import os
import sys
import bcrypt
from app.core.database import SessionLocal
from app.models.user import User


def reset_password(email, plain_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            sys.exit(1)
        hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
        user.hashed_password = hashed
        db.commit()
        print(f"Password updated for {email}")
    except Exception as e:
        print(f"Error updating password: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    email = os.environ.get('TARGET_EMAIL')
    password = os.environ.get('TARGET_PASSWORD')
    if not (email and password):
        print('TARGET_EMAIL and TARGET_PASSWORD must be set')
        sys.exit(1)
    reset_password(email, password)
