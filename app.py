import streamlit as st
from database import init_db
from team_management import team_management_section
from player_management import player_management_section
from player_awards import load_player_awards
from visualization import visualization_section
from auth import init_auth, check_auth, logout
from keep_alive import keep_alive

# Initialize the database and auth
keep_alive()
init_db()
init_auth()

# Set up the main page
st.set_page_config(
    page_title="Sports Statistics Tracker",
    page_icon="⚽",
    layout="wide"
)

# Check authentication
if not check_auth():
    st.stop()

# Show logout button if authenticated
if st.session_state.authenticated:
    st.sidebar.button("Logout", on_click=logout)

    # Show user role
    role_label = "Admin" if st.session_state.user_role == "admin" else "Guest"
    st.sidebar.info(f"Logged in as: {role_label}")

    # Navigation
    page = st.sidebar.radio("Navigation", 
        ["Overview", "Team Management", "Player Management", "Player Awards"])

    # Display the selected section
    if page == "Overview":
        visualization_section()
    elif page == "Team Management":
        team_management_section()
    elif page == "Player Management":
        player_management_section()
    else:
        load_player_awards()