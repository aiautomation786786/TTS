import secrets
import string
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def generate_secure_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 2
                and any(c in "!@#$%^&*" for c in password)):
            return password

def setup_admin_login():
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username='admin').first()
        if not user:
            print("Admin user not found. Creating...")
            user = User(username='admin', email='admin@voxforge.local', role='admin')
            db.add(user)
        
        plain_password = generate_secure_password()
        user.password_hash = hash_password(plain_password)
        db.commit()
        
        print("\n" + "="*50)
        print("SUCCESS: Admin Login Password Generated")
        print("="*50)
        print("Admin Login:")
        print(f"Username: admin")
        print(f"Password: {plain_password}")
        print("="*50)
        print("IMPORTANT: Save this password. It is only shown once.")
        print("It has been securely hashed and stored in the database.")
        print("To rotate the admin login password, run this script again.")
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin_login()
