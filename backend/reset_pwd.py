from app.core.security import hash_password
import sqlite3
conn = sqlite3.connect('d:/TTS/backend/data/db/voxforge.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET password_hash=? WHERE username="admin"', (hash_password('admin123'),))
conn.commit()
conn.close()
print('Password updated successfully!')
