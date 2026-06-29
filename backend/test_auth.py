from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models.user import User

def test_auth():
    init_db() # Ensures admin is seeded and DB is ready
    client = TestClient(app)
    
    print("Testing Registration...")
    reg_response = client.post("/api/auth/register", json={
        "username": "tester",
        "email": "tester@example.com",
        "password": "password123"
    })
    
    if reg_response.status_code == 400 and "already registered" in reg_response.text:
        print("Test user already exists, proceeding...")
    else:
        assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
        print("Registration successful!")

    print("Testing Login with Username...")
    log_un = client.post("/api/auth/login", data={"username": "tester", "password": "password123"})
    assert log_un.status_code == 200, f"Login with username failed: {log_un.text}"
    print("Login with username successful!")

    print("Testing Login with Email...")
    log_em = client.post("/api/auth/login", data={"username": "tester@example.com", "password": "password123"})
    assert log_em.status_code == 200, f"Login with email failed: {log_em.text}"
    print("Login with email successful!")

    print("Testing Wrong Password...")
    log_wrong = client.post("/api/auth/login", data={"username": "tester", "password": "wrongpassword"})
    assert log_wrong.status_code == 401, "Wrong password did not fail!"
    assert "Invalid username/email or password" in log_wrong.text
    print("Wrong password failed properly!")

    print("Testing Admin Login...")
    log_admin = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    assert log_admin.status_code == 200, f"Admin login failed: {log_admin.text}"
    print("Admin login successful!")

    print("Testing Protected Routes (Admin)...")
    # Verify the admin token
    admin_token = log_admin.json()["access_token"]
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert me_resp.json()["role"] == "admin"
    print("Admin token verified role!")

    print("All tests passed.")
    
    # Cleanup tester
    db = SessionLocal()
    tester = db.query(User).filter(User.username == "tester").first()
    if tester:
        db.delete(tester)
        db.commit()

if __name__ == "__main__":
    test_auth()
