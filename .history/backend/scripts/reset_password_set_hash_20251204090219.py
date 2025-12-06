#!/usr/bin/env python3
"""
Reset password for a user based on a precomputed bcrypt hash.
ENV VARS: TARGET_EMAIL, TARGET_PWHASH
"""
import os
import sys
from app.core.database import SessionLocal
from app.models.user import User


def reset_password(email, pwhash):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            sys.exit(1)
        user.hashed_password = pwhash
        db.commit()
        print(f"Password updated for {email}")
    except Exception as e:
        print(f"Error updating password: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    email = os.environ.get('TARGET_EMAIL')
    pwhash = os.environ.get('TARGET_PWHASH')
    if not (email and pwhash):
        print('TARGET_EMAIL and TARGET_PWHASH must be set')
        sys.exit(1)
    reset_password(email, pwhash)
