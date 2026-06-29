import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def repair_admin():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        print("Admin user not found. Creating...")
        admin = User(
            username="admin",
            email="admin@voxforge.local",
            role="admin",
            char_quota=500000,
            chars_used=0,
            is_active=True
        )
        db.add(admin)
    else:
        print("Admin user found. Repairing...")
        admin.role = "admin"
        admin.is_active = True
        
    admin.password_hash = hash_password("AdminLogin123")
    
    try:
        db.commit()
        print("Admin user successfully repaired and password set to 'AdminLogin123'.")
    except Exception as e:
        print(f"Error repairing admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    repair_admin()
