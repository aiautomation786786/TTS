import secrets
import string
import os
import bcrypt

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def generate_secure_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 2
                and any(c in "!@#$%^&*" for c in password)):
            return password

def update_env_file(key, value):
    lines = []
    found = False
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
            
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
            
    if not found:
        lines.append(f"{key}={value}\n")
        
    with open(ENV_PATH, "w") as f:
        f.writelines(lines)

def setup_admin_gate():
    print("Generating secure Admin Gate Password...")
    plain_password = generate_secure_password()
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    
    update_env_file("ADMIN_GATE_PASSWORD_HASH", hashed)
    
    print("\n" + "="*50)
    print("SUCCESS: Admin Gate Password Generated")
    print("="*50)
    print(f"Admin Panel Gate Password: {plain_password}")
    print("="*50)
    print("IMPORTANT: Save this password. It is only shown once.")
    print("It has been securely hashed and stored in backend/.env")
    print("To rotate it, simply run this script again.")

if __name__ == "__main__":
    setup_admin_gate()
