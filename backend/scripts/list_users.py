#!/usr/bin/env python3
from app.core.database import SessionLocal
from app.models.user import User
s=SessionLocal()
users=[(u.email,u.id,u.is_admin) for u in s.query(User).all()]
print(users)
s.close()
