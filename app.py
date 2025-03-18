import streamlit as st
from database import init_db
from team_management import team_management_section
from player_management import player_management_section
from visualization import visualization_section

# Initialize the database
init_db()

# Set up the main page
st.set_page_config(
    page_title="Sports Statistics Tracker",
    page_icon="⚽",
    layout="wide"
)

st.title("Sports Statistics Tracker")

# Navigation
page = st.sidebar.radio("Navigation", 
    ["Overview", "Team Management", "Player Management"])

# Display the selected section
if page == "Overview":
    visualization_section()
elif page == "Team Management":
    team_management_section()
else:
    player_management_section()
