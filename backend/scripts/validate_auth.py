import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password
from app.config import get_settings

def print_result(name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name} {detail}")

def validate_auth():
    print("=======================================")
    print("      Authentication Diagnostics       ")
    print("=======================================")
    
    settings = get_settings()
    print(f"Database Path: {settings.DATABASE_URL}")
    
    db = SessionLocal()
    
    # Check users table
    try:
        users_count = db.query(User).count()
        print_result("Users table exists", True, f"({users_count} users found)")
    except Exception as e:
        print_result("Users table exists", False, str(e))
        db.close()
        return

    # Check admin user
    admin = db.query(User).filter(User.username == 'admin').first()
    if admin:
        print_result("Admin user exists", True)
        print_result("Admin password hash exists", bool(admin.password_hash))
        
        # Test verification
        verifies = verify_password('AdminLogin123', admin.password_hash)
        print_result("Admin login password verifies (AdminLogin123)", verifies)
    else:
        print_result("Admin user exists", False)

    db.close()
    
    print("\n--- API Tests ---")
    base_url = "http://localhost:8000"
    
    # Test Normal User Creation
    test_user_data = {
        "username": "auth_test_user",
        "email": "auth_test_user@example.com",
        "password": "AuthTest123!"
    }
    
    try:
        reg_res = requests.post(f"{base_url}/api/auth/register", json=test_user_data)
        # 200 or 400 (if already exists) are both fine for this script's idempotency
        if reg_res.status_code in [200, 400]:
            print_result("Test user can be created", True)
        else:
            print_result("Test user can be created", False, f"Status: {reg_res.status_code}")
            
        # Test Login (username)
        login_res_user = requests.post(f"{base_url}/api/auth/login", data={
            "username": "auth_test_user",
            "password": "AuthTest123!"
        })
        print_result("Test user login with username works", login_res_user.status_code == 200)
        
        # Test Login (email)
        login_res_email = requests.post(f"{base_url}/api/auth/login", data={
            "username": "auth_test_user@example.com",
            "password": "AuthTest123!"
        })
        print_result("Test user login with email works", login_res_email.status_code == 200)
        
        # Test wrong password
        login_fail = requests.post(f"{base_url}/api/auth/login", data={
            "username": "auth_test_user",
            "password": "WrongPassword!"
        })
        print_result("Wrong password fails", login_fail.status_code == 401)
        
        if login_res_user.status_code == 200:
            token = login_res_user.json().get("access_token")
            print_result("JWT token can be generated", bool(token))
            
            # Test /me
            me_res = requests.get(f"{base_url}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            print_result("/me works with token", me_res.status_code == 200)
            
            # Test Admin endpoint rejection
            admin_res = requests.get(f"{base_url}/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
            print_result("Admin protected endpoint rejects normal users", admin_res.status_code in [401, 403])
            
    except Exception as e:
        print_result("API Tests", False, f"Could not connect to {base_url}. Is the server running? {e}")

    # Admin Login and Gate Test
    try:
        admin_login = requests.post(f"{base_url}/api/auth/login", data={
            "username": "admin",
            "password": "AdminLogin123"
        })
        
        if admin_login.status_code == 200:
            admin_token = admin_login.json().get("access_token")
            gate_res = requests.post(f"{base_url}/api/admin/verify-gate", json={"password": "TTSAdminPanel123"}, headers={"Authorization": f"Bearer {admin_token}"})
            print_result("Admin gate password verifies", gate_res.status_code == 200)
            if gate_res.status_code == 200:
                print_result("Admin gate token can be generated", bool(gate_res.json().get("admin_gate_token")))
        else:
            print_result("Admin login API test", False, "Run repair_auth.py first.")
    except Exception as e:
        print_result("Admin Gate API Tests", False, f"Could not connect. {e}")

    print("=======================================")

if __name__ == "__main__":
    validate_auth()
