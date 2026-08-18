import sqlite3
import os
from config import Config

def get_db_connection():
    try:
        db_dir = os.path.dirname(Config.DATABASE_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
    except Exception:
        # Fallback path for Linux cloud hosting permissions (e.g. Render /tmp)
        fallback_path = os.path.join('/tmp', 'app.db')
        conn = sqlite3.connect(fallback_path, check_same_thread=False)
        
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(full_name, email, password_hash):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)',
                  (full_name, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user
