from db import get_connection

def create_user(username: str, email: str, password_hash: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"

    cur.execute(sql, (username, email, password_hash))
    conn.commit()

    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return user_id

def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user

def get_user_by_username(username: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user
