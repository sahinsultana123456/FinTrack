from models import get_db_connection
import bcrypt

# ──────────────── User Registration ────────────────
def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        return True, "Registration successful."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# ──────────────── User Login ────────────────
def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, password FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[1].encode()):
            return True, row[0]
        else:
            return False, "Invalid username or password."
    finally:
        cursor.close()
        conn.close()
