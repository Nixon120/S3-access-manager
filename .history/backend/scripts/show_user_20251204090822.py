#!/usr/bin/env python3
import os
from app.core.database import SessionLocal
from app.models.user import User

email = os.environ.get('TARGET_EMAIL')
if not email:
    print('TARGET_EMAIL must be set')
    raise SystemExit(1)

s = SessionLocal()
u = s.query(User).filter(User.email == email).first()
if not u:
    print('Not found')
else:
    print(u.email)
    print('is_admin=', u.is_admin)
    print('is_active=', u.is_active)
    print('last_login=', u.last_login)

s.close()
