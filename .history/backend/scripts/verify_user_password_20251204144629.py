#!/usr/bin/env python3
import os
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

email = os.environ.get('TARGET_EMAIL')
password = os.environ.get('TARGET_PASSWORD')
if not email or not password:
    print('TARGET_EMAIL and TARGET_PASSWORD are required')
    raise SystemExit(1)

s = SessionLocal()
user = s.query(User).filter(User.email == email).first()
if not user:
    print('NOT_FOUND')
else:
    ok = verify_password(password, user.hashed_password)
    print(f'FOUND, matches={ok}')
    # print last_login for inspection (not a secret)
    print('last_login=', user.last_login)
s.close()