import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "testuser@example.com").first()
        
        if existing_user:
            print("✅ Test user already exists!")
            print("Email: testuser@example.com")
            print("Password: TestPass123!")
            return
        
        # Create new user
        user = User(
            email="testuser@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("TestPass123!"),
            is_admin=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("Email: testuser@example.com")
        print("Password: TestPass123!")
        print("\nYou can now:")
        print("1. Login with these credentials")
        print("2. Assign permissions to this user via Admin panel")
        print("3. See the Browse/Upload tabs when you select a bucket")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
