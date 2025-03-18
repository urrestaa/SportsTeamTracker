import streamlit as st
import pandas as pd
from database import add_team, update_team_stats, get_teams

def team_management_section():
    st.header("Team Management")
    
    # Add new team
    with st.expander("Add New Team"):
        team_name = st.text_input("Team Name")
        if st.button("Add Team"):
            if team_name:
                if add_team(team_name):
                    st.success(f"Team {team_name} added successfully!")
                    st.rerun()
                else:
                    st.error("Team already exists!")
            else:
                st.warning("Please enter a team name")
    
    # Edit team statistics
    teams_df = get_teams()
    if not teams_df.empty:
        with st.expander("Update Team Statistics"):
            selected_team = st.selectbox("Select Team", teams_df['name'])
            team_data = teams_df[teams_df['name'] == selected_team].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                wins = st.number_input("Wins", min_value=0, value=int(team_data['wins']))
            with col2:
                draws = st.number_input("Draws", min_value=0, value=int(team_data['draws']))
            with col3:
                losses = st.number_input("Losses", min_value=0, value=int(team_data['losses']))
            
            if st.button("Update Statistics"):
                update_team_stats(team_data['id'], wins, draws, losses)
                st.success("Statistics updated successfully!")
                st.rerun()
        
        # Display team standings
        st.subheader("Team Standings")
        teams_df['Points'] = teams_df['wins'] * 3 + teams_df['draws']
        teams_df['Matches'] = teams_df['wins'] + teams_df['draws'] + teams_df['losses']
        teams_df['Win Rate'] = (teams_df['wins'] / teams_df['Matches'] * 100).round(2)
        
        standings = teams_df.sort_values('Points', ascending=False)
        st.dataframe(standings[['name', 'wins', 'draws', 'losses', 'Points', 'Win Rate']])
