import streamlit as st
import pandas as pd
from database import add_team, update_team_stats, get_teams, get_players, update_player_stats

def quick_match_update():
    teams_df = get_teams()
    players_df = get_players()

    st.subheader("Quick Match Update")

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Home Team", teams_df['name'], key='home_team')
        team1_score = st.number_input("Home Team Score", min_value=0, key='home_score')
    with col2:
        team2 = st.selectbox("Away Team", teams_df['name'], key='away_team')
        team2_score = st.number_input("Away Team Score", min_value=0, key='away_score')

    # Get team data
    team1_data = teams_df[teams_df['name'] == team1].iloc[0]
    team2_data = teams_df[teams_df['name'] == team2].iloc[0]

    # Player selections for goals and assists
    st.subheader("Match Statistics")

    # Home team scorers
    team1_players = players_df[players_df['team_id'] == team1_data['id']]
    if not team1_players.empty and team1_score > 0:
        st.write(f"{team1} Scorers")
        for i in range(int(team1_score)):
            col1, col2 = st.columns(2)
            with col1:
                scorer = st.selectbox(
                    f"Goal {i+1} Scorer",
                    team1_players['name'],
                    key=f'home_scorer_{i}'
                )
            with col2:
                assister = st.selectbox(
                    f"Goal {i+1} Assist",
                    ['No Assist'] + team1_players['name'].tolist(),
                    key=f'home_assist_{i}'
                )

    # Away team scorers
    team2_players = players_df[players_df['team_id'] == team2_data['id']]
    if not team2_players.empty and team2_score > 0:
        st.write(f"{team2} Scorers")
        for i in range(int(team2_score)):
            col1, col2 = st.columns(2)
            with col1:
                scorer = st.selectbox(
                    f"Goal {i+1} Scorer",
                    team2_players['name'],
                    key=f'away_scorer_{i}'
                )
            with col2:
                assister = st.selectbox(
                    f"Goal {i+1} Assist",
                    ['No Assist'] + team2_players['name'].tolist(),
                    key=f'away_assist_{i}'
                )

    if st.button("Update Match Result", type="primary"):
        with st.spinner("Updating match statistics..."):
            # Update team statistics
            if team1_score > team2_score:
                update_team_stats(team1_data['id'], 
                                team1_data['wins'] + 1, 
                                team1_data['draws'], 
                                team1_data['losses'])
                update_team_stats(team2_data['id'], 
                                team2_data['wins'], 
                                team2_data['draws'], 
                                team2_data['losses'] + 1)
            elif team2_score > team1_score:
                update_team_stats(team2_data['id'], 
                                team2_data['wins'] + 1, 
                                team2_data['draws'], 
                                team2_data['losses'])
                update_team_stats(team1_data['id'], 
                                team1_data['wins'], 
                                team1_data['draws'], 
                                team1_data['losses'] + 1)
            else:
                update_team_stats(team1_data['id'], 
                                team1_data['wins'], 
                                team1_data['draws'] + 1, 
                                team1_data['losses'])
                update_team_stats(team2_data['id'], 
                                team2_data['wins'], 
                                team2_data['draws'] + 1, 
                                team2_data['losses'])

            # Update player statistics
            if team1_score > 0:
                for i in range(int(team1_score)):
                    scorer = st.session_state[f'home_scorer_{i}']
                    assister = st.session_state[f'home_assist_{i}']

                    # Update scorer
                    scorer_data = team1_players[team1_players['name'] == scorer].iloc[0]
                    update_player_stats(scorer_data['id'], 
                                    scorer_data['goals'] + 1, 
                                    scorer_data['assists'])

                    # Update assister if there was one
                    if assister != 'No Assist':
                        assister_data = team1_players[team1_players['name'] == assister].iloc[0]
                        update_player_stats(assister_data['id'], 
                                        assister_data['goals'], 
                                        assister_data['assists'] + 1)

            if team2_score > 0:
                for i in range(int(team2_score)):
                    scorer = st.session_state[f'away_scorer_{i}']
                    assister = st.session_state[f'away_assist_{i}']

                    # Update scorer
                    scorer_data = team2_players[team2_players['name'] == scorer].iloc[0]
                    update_player_stats(scorer_data['id'], 
                                    scorer_data['goals'] + 1, 
                                    scorer_data['assists'])

                    # Update assister if there was one
                    if assister != 'No Assist':
                        assister_data = team2_players[team2_players['name'] == assister].iloc[0]
                        update_player_stats(assister_data['id'], 
                                        assister_data['goals'], 
                                        assister_data['assists'] + 1)

            st.success("Match result updated successfully!")
            st.experimental_rerun()

def team_management_section():
    st.header("Team Management")

    # Add new team
    with st.expander("Add New Team"):
        team_name = st.text_input("Team Name")
        if st.button("Add Team", key='add_team_button'):
            if team_name:
                try:
                    if add_team(team_name):
                        st.success(f"Team {team_name} added successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Team already exists!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a team name")

    # Quick match update section
    with st.expander("Quick Match Update", expanded=True):
        quick_match_update()

    # Edit team statistics
    teams_df = get_teams()
    if not teams_df.empty:
        with st.expander("Update Team Statistics"):
            selected_team = st.selectbox("Select Team", teams_df['name'], key='update_team_select')
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
                        update_team_stats(team_data['id'], wins, draws, losses)
                        st.success("Statistics updated successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"An error occurred while updating statistics: {e}")

        # Display team standings
        st.subheader("Team Standings")
        teams_df['Points'] = teams_df['wins'] * 3 + teams_df['draws']
        teams_df['Matches'] = teams_df['wins'] + teams_df['draws'] + teams_df['losses']
        teams_df['Win Rate'] = (teams_df['wins'] / teams_df['Matches'] * 100).round(2)

        standings = teams_df.sort_values('Points', ascending=False)
        st.dataframe(standings[['name', 'wins', 'draws', 'losses', 'Points', 'Win Rate']])