import streamlit as st
from database import add_player, update_player_stats, get_players, get_teams
from auth import require_admin

def player_management_section():
    st.header("Player Management")

    teams_df = get_teams()
    players_df = get_players()

    # Add new player (admin only)
    if st.session_state.user_role == "admin":
        st.subheader("Add New Player")
        player_name = st.text_input("Player Name", key='new_player_name')
        if not teams_df.empty:
            team = st.selectbox("Select Team", teams_df['name'].tolist(), key='add_player_team')
            team_data = teams_df[teams_df['name'] == team].iloc[0]
            team_id = int(team_data['id'])

            if st.button("Add Player", key='add_player_button'):
                with st.spinner("Adding new player..."):
                    if player_name:
                        try:
                            add_player(player_name, team_id)
                            st.success(f"Player {player_name} added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding player: {str(e)}")
                    else:
                        st.warning("Please enter a player name")
        else:
            st.warning("Please add teams first")

        # Update player statistics (admin only)
        if not players_df.empty:
            st.subheader("Update Player Statistics")
            # Add team filter
            teams = ['All Teams'] + teams_df['name'].tolist()
            selected_team_filter = st.selectbox(
                "Filter by Team",
                teams,
                key='player_team_filter'
            )

            # Filter players by team
            filtered_players = players_df.copy()
            if selected_team_filter != 'All Teams':
                team_data = teams_df[teams_df['name'] == selected_team_filter].iloc[0]
                team_id = int(team_data['id'])
                filtered_players = filtered_players[filtered_players['team_id'] == team_id]

                if not filtered_players.empty:
                    selected_player = st.selectbox(
                        "Select Player",
                        filtered_players['name'].tolist(),
                        key='update_player_select'
                    )

                    # Get player data
                    player_data = filtered_players[filtered_players['name'] == selected_player].iloc[0]

                    col1, col2 = st.columns(2)
                    with col1:
                        goals = st.number_input(
                            "Goals",
                            min_value=0,
                            value=int(player_data['goals']),
                            key=f'goals_input_{player_data["id"]}'
                        )
                    with col2:
                        assists = st.number_input(
                            "Assists",
                            min_value=0,
                            value=int(player_data['assists']),
                            key=f'assists_input_{player_data["id"]}'
                        )

                    if st.button("Update Statistics", key=f'update_player_stats_button_{player_data["id"]}'):
                        with st.spinner("Updating player statistics..."):
                            try:
                                update_player_stats(int(player_data['id']), goals, assists)
                                st.success("Statistics updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating statistics: {str(e)}")

    # Display player statistics (visible to all)
    st.subheader("Player Statistics")

    # Add team filter for statistics display
    teams = ['All Teams'] + teams_df['name'].tolist()
    display_team_filter = st.selectbox(
        "Filter Statistics by Team",
        teams,
        key='display_team_filter'
    )

    with st.spinner("Loading player statistics..."):
        # Filter and display statistics
        display_stats = players_df.copy()

        if display_team_filter != 'All Teams':
            team_data = teams_df[teams_df['name'] == display_team_filter].iloc[0]
            team_id = int(team_data['id'])
            display_stats = display_stats[display_stats['team_id'] == team_id]

            # All players in this team have the same matchesPlayed value
            if 'matchesPlayed' in team_data:
                matchesPlayed = team_data['matchesPlayed']
            else:
                matchesPlayed = team_data['wins'] + team_data['draws'] + team_data['losses']

            display_stats['matchesPlayed'] = matchesPlayed
        else:
            # For "All Teams" view, create a mapping from team_id to matchesPlayed
            team_matches = {}
            for _, team in teams_df.iterrows():
                if 'matchesPlayed' in team:
                    team_matches[team['id']] = team['matchesPlayed']
                else:
                    team_matches[team['id']] = team['wins'] + team['draws'] + team['losses']

            # Map team_id to matchesPlayed for each player
            display_stats['matchesPlayed'] = display_stats['team_id'].map(team_matches).fillna(0).astype(int)

        if not display_stats.empty:
            # Calculate total contributions
            display_stats['Name'] = display_stats['name']
            display_stats['Team Name'] = display_stats['team_name']
            display_stats['Matches Played'] = display_stats['matchesPlayed'].astype(int)
            display_stats['Goals'] = display_stats['goals']
            display_stats['Assists'] = display_stats['assists']
            display_stats['Total Contributions'] = display_stats['goals'] + display_stats['assists']

            # Sort players by goals, then assists
            display_stats = display_stats.sort_values(
                ['Goals', 'Assists', 'Total Contributions'],
                ascending=[False, False, False]
            )

            # Display statistics
            st.dataframe(
                display_stats[['Name', 'Team Name', 'Matches Played', 'Goals', 'Assists', 'Total Contributions']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No players found for the selected team")