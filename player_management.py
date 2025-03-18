import streamlit as st
from database import add_player, update_player_stats, get_players, get_teams

def player_management_section():
    st.header("Player Management")

    teams_df = get_teams()
    players_df = get_players()

    # Add new player
    with st.expander("Add New Player"):
        player_name = st.text_input("Player Name")
        if not teams_df.empty:
            team = st.selectbox("Select Team", teams_df['name'], key='add_player_team')
            team_id = teams_df[teams_df['name'] == team]['id'].iloc[0]

            if st.button("Add Player", key='add_player_button'):
                with st.spinner("Adding new player..."):
                    if player_name:
                        add_player(player_name, team_id)
                        st.success(f"Player {player_name} added successfully!")
                        st.rerun()
                    else:
                        st.warning("Please enter a player name")
        else:
            st.warning("Please add teams first")

    # Update player statistics
    if not players_df.empty:
        with st.expander("Update Player Statistics", expanded=True):
            # Add team filter
            teams = ['All Teams'] + teams_df['name'].tolist()
            selected_team_filter = st.selectbox("Filter by Team", teams, key='player_team_filter')

            # Filter players by team
            if selected_team_filter != 'All Teams':
                team_id = teams_df[teams_df['name'] == selected_team_filter]['id'].iloc[0]
                filtered_players = players_df[players_df['team_id'] == team_id]
            else:
                filtered_players = players_df

            if not filtered_players.empty:
                selected_player = st.selectbox(
                    "Select Player",
                    filtered_players['name'],
                    key='update_player_select'
                )
                player_data = filtered_players[filtered_players['name'] == selected_player].iloc[0]

                col1, col2 = st.columns(2)
                with col1:
                    goals = st.number_input(
                        "Goals",
                        min_value=0,
                        value=int(player_data['goals']),
                        key='goals_input'
                    )
                with col2:
                    assists = st.number_input(
                        "Assists",
                        min_value=0,
                        value=int(player_data['assists']),
                        key='assists_input'
                    )

                if st.button("Update Statistics", key='update_player_stats_button'):
                    with st.spinner("Updating player statistics..."):
                        update_player_stats(player_data['id'], goals, assists)
                        st.success("Statistics updated successfully!")
                        st.rerun()

        # Display player statistics
        st.subheader("Player Statistics")

        # Add team filter for statistics display
        display_team_filter = st.selectbox(
            "Filter Statistics by Team",
            teams,
            key='display_team_filter'
        )

        if display_team_filter != 'All Teams':
            team_id = teams_df[teams_df['name'] == display_team_filter]['id'].iloc[0]
            stats = players_df[players_df['team_id'] == team_id]
        else:
            stats = players_df

        # Calculate total contributions
        stats['Total Contributions'] = stats['goals'] + stats['assists']

        # Sort players by goals, then assists
        stats = stats.sort_values(['goals', 'assists', 'Total Contributions'],
                                ascending=[False, False, False])

        # Display statistics
        st.dataframe(
            stats[['name', 'team_name', 'goals', 'assists', 'Total Contributions']],
            hide_index=True,
            use_container_width=True
        )