import streamlit as st
import sqlite3
import hashlib
import os
DATA_FOLDER = "restaurants"
USER_DB = os.path.join(DATA_FOLDER, "users.db")
os.makedirs(DATA_FOLDER, exist_ok=True)


def init_user_db():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def delete_user(username_to_delete, current_user):
    db_path = os.path.join(DATA_FOLDER, f"{username_to_delete}.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
    conn.commit()
    conn.close()

    st.success(f"User '{username_to_delete}' deleted successfully.")

    if username_to_delete == current_user:
        st.session_state.pop("logged_in", None)
        st.session_state.pop("username", None)
        st.rerun()