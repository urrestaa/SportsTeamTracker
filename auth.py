import streamlit as st
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Secret key for JWT encoding/decoding
SECRET_KEY = "your-secret-key-stored-securely"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def init_auth():
    if 'admin_users' not in st.session_state:
        # Initialize with a default admin user
        st.session_state.admin_users = {
            "admin": get_password_hash("admin123")  # Default admin credentials
        }
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def login_page():
    st.title("Sports Statistics Tracker")
    st.subheader("Login")

    # Guest access button
    if st.button("Continue as Guest"):
        st.session_state.user_role = "guest"
        st.session_state.authenticated = True
        st.rerun()

    # Admin login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login as Admin")

        if submitted:
            if (username in st.session_state.admin_users and 
                verify_password(password, st.session_state.admin_users[username])):
                st.session_state.user_role = "admin"
                st.session_state.authenticated = True
                st.success("Successfully logged in as admin!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def check_auth():
    if not st.session_state.authenticated:
        login_page()
        return False
    return True

def require_admin():
    if st.session_state.user_role != "admin":
        st.error("This action requires admin privileges")
        return False
    return True

def logout():
    st.session_state.user_role = None
    st.session_state.authenticated = False
    st.rerun()
