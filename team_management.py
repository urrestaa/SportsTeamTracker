import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    add_team, update_team_stats, get_teams, get_players, 
    update_player_stats, get_player_stats
)
from auth import require_admin

def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

def quick_match_update():
    # Initialize score tracking variables
    if 'home_goals' not in st.session_state:
        st.session_state.home_goals = 0
        st.session_state.home_assists = 0
        st.session_state.away_goals = 0
        st.session_state.away_assists = 0
    teams_df = get_teams()
    players_df = get_players()

    st.subheader("Quick Match Update")

    if teams_df.empty:
        st.warning("Please add some teams first")
        return

    # Team selection and score input - Mobile friendly layout
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Home Team", teams_df['name'].tolist(), key='home_team')
        team1_score = st.number_input("Home Team Score", min_value=0, key='home_score')
    with col2:
        team2 = st.selectbox("Away Team", teams_df['name'].tolist(), key='away_team')
        team2_score = st.number_input("Away Team Score", min_value=0, key='away_score')

    if team1 == team2:
        st.error("Please select different teams")
        return

    # Get team data
    team1_data = teams_df[teams_df['name'] == team1].iloc[0]
    team2_data = teams_df[teams_df['name'] == team2].iloc[0]

    try:
        # Player Statistics Interface
        st.subheader("Player Statistics Update")

        # Home Team Players
        with st.expander(f"{team1} - Player Stats", expanded=True):
            team1_players = players_df[players_df['team_id'] == int(team1_data['id'])]

            if not team1_players.empty:
                # Create a table-like interface for quick updates
                st.write("Click + to add goals/assists")
                for _, player in team1_players.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 2])

                    with col1:
                        st.write(player['name'])

                    with col2:
                        if st.button("+G", key=f"addgoal_{player['id']}_home"):
                            st.session_state.home_goals = clamp(st.session_state.home_goals + 1, 0, team1_score)
                            st.rerun()

                    with col3:
                        if st.button("-G", key=f"substractgoal_{player['id']}_home"):
                            st.session_state.home_goals = clamp(st.session_state.home_goals - 1, 0, team1_score)
                            st.rerun()
                    with col4:
                        if st.button("+A", key=f"addassist_{player['id']}_home"):
                            st.session_state.home_assists = clamp(st.session_state.home_assists + 1, 0, team1_score)
                            st.rerun()

                    with col5:
                        if st.button("-A", key=f"substractassist_{player['id']}_home"):
                            st.session_state.home_assists = clamp(st.session_state.home_assists - 1, 0, team1_score)
                            st.rerun()

                    with col6:
                        st.write(f"G: {st.session_state.home_goals} | A: {st.session_state.home_assists}")

            team2_players = players_df[players_df['team_id'] == int(team2_data['id'])]
                
        
        """
        with st.expander(f"{team1} - Player Stats", expanded=True):
            team1_players = players_df[players_df['team_id'] == int(team1_data['id'])]

            if not team1_players.empty:
                # Create a table-like interface for quick updates
                st.write("Click + to add goals/assists")
                for _, player in team1_players.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

                    with col1:
                        st.write(player['name'])

                    with col2:
                        if st.button("+G", key=f"goal_{player['id']}_home"):
                            current_stats = get_player_stats(int(player['id']))
                            update_player_stats(
                                int(player['id']),
                                current_stats['goals'] + 1,
                                current_stats['assists']
                            )
                            st.rerun()

                    with col3:
                        if st.button("+A", key=f"assist_{player['id']}_home"):
                            current_stats = get_player_stats(int(player['id']))
                            update_player_stats(
                                int(player['id']),
                                current_stats['goals'],
                                current_stats['assists'] + 1
                            )
                            st.rerun()

                    with col4:
                        st.write(f"G: {player['goals']} A: {player['assists']}")
        """

        # Away Team Players
        
        
        """st.subheader(f"{team2} - Player Stats")
        team2_players = players_df[players_df['team_id'] == int(team2_data['id'])]

        if not team2_players.empty:
            st.write("Click + to add goals/assists")
            for _, player in team2_players.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

                with col1:
                    st.write(player['name'])

                with col2:
                    if st.button("+G", key=f"goal_{player['id']}_away"):
                        current_stats = get_player_stats(int(player['id']))
                        update_player_stats(
                            int(player['id']),
                            current_stats['goals'] + 1,
                            current_stats['assists']
                        )
                        st.rerun()

                with col3:
                    if st.button("+A", key=f"assist_{player['id']}_away"):
                        current_stats = get_player_stats(int(player['id']))
                        update_player_stats(
                            int(player['id']),
                            current_stats['goals'],
                            current_stats['assists'] + 1
                        )
                        st.rerun()

                with col4:
                    st.write(f"G: {player['goals']} A: {player['assists']}")
        """

        if st.button("Update Match Result", type="primary"):
            with st.spinner("Updating match statistics..."):
                try:
                    # Update team statistics based on match result
                    if team1_score > team2_score:
                        update_team_stats(
                            int(team1_data['id']),
                            int(team1_data['wins']) + 1,
                            int(team1_data['draws']),
                            int(team1_data['losses'])
                        )
                        update_team_stats(
                            int(team2_data['id']),
                            int(team2_data['wins']),
                            int(team2_data['draws']),
                            int(team2_data['losses']) + 1
                        )
                    elif team2_score > team1_score:
                        update_team_stats(
                            int(team2_data['id']),
                            int(team2_data['wins']) + 1,
                            int(team2_data['draws']),
                            int(team2_data['losses'])
                        )
                        update_team_stats(
                            int(team1_data['id']),
                            int(team1_data['wins']),
                            int(team1_data['draws']),
                            int(team1_data['losses']) + 1
                        )
                    else:
                        update_team_stats(
                            int(team1_data['id']),
                            int(team1_data['wins']),
                            int(team1_data['draws']) + 1,
                            int(team1_data['losses'])
                        )
                        update_team_stats(
                            int(team2_data['id']),
                            int(team2_data['wins']),
                            int(team2_data['draws']) + 1,
                            int(team2_data['losses'])
                        )

                    # Show success message and reset form
                    st.success("Match result updated successfully!")

                    # Reset stats
                    st.session_state.home_goals = 0
                    st.session_state.home_assists = 0
                    st.session_state.away_goals = 0
                    st.session_state.away_assists = 0
                    
                    # Clear session state and use query params to force reset
                    for key in list(st.session_state.keys()):
                        if key.startswith(('home_', 'away_')):
                            del st.session_state[key]
                    st.experimental_set_query_params(reset=str(datetime.now().timestamp()))
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating match result: {str(e)}")

    except Exception as e:
        st.error(f"Error loading players: {str(e)}")

def team_management_section():
    st.header("Team Management")

    # Add new team (admin only)
    if st.session_state.user_role == "admin":
        with st.expander("Add New Team"):
            team_name = st.text_input("Team Name", key='add_team_name')
            if st.button("Add Team", key='add_team_button'):
                if team_name:
                    try:
                        if add_team(team_name):
                            st.success(f"Team {team_name} added successfully!")
                            st.rerun()
                        else:
                            st.error("Team already exists!")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please enter a team name")

        # Quick match update section (admin only)
        quick_match_update()

        # Edit team statistics (admin only)
        teams_df = get_teams()
        if not teams_df.empty:
            with st.expander("Update Team Statistics"):
                selected_team = st.selectbox("Select Team", teams_df['name'].tolist(), key='update_team_select')
                team_data = teams_df[teams_df['name'] == selected_team].iloc[0]

                col1, col2, col3 = st.columns(3)
                with col1:
                    wins = st.number_input("Wins", min_value=0, value=int(team_data['wins']), key='wins_input')
                with col2:
                    draws = st.number_input("Draws", min_value=0, value=int(team_data['draws']), key='draws_input')
                with col3:
                    losses = st.number_input("Losses", min_value=0, value=int(team_data['losses']), key='losses_input')

                if st.button("Update Statistics", key='update_stats_button'):
                    with st.spinner("Updating team statistics..."):
                        try:
                            update_team_stats(int(team_data['id']), wins, draws, losses)
                            st.success("Statistics updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"An error occurred while updating statistics: {e}")

    # Display team standings (visible to all)
    st.subheader("Team Standings")
    teams_df = get_teams()  # Refresh data
    if not teams_df.empty:
        with st.spinner("Loading team statistics..."):
            teams_df['Points'] = teams_df['wins'] * 3 + teams_df['draws']
            teams_df['Matches'] = teams_df['wins'] + teams_df['draws'] + teams_df['losses']
            teams_df['Win Rate'] = (teams_df['wins'] / teams_df['Matches'].where(teams_df['Matches'] > 0, 1) * 100).round(2)

            standings = teams_df.sort_values('Points', ascending=False)
            st.dataframe(
                standings[['name', 'wins', 'draws', 'losses', 'Points', 'Win Rate']],
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("No teams found. Please contact an administrator to add teams.")