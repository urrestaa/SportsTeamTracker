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
            team = st.selectbox("Select Team", teams_df['name'])
            team_id = teams_df[teams_df['name'] == team]['id'].iloc[0]
            
            if st.button("Add Player"):
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
        with st.expander("Update Player Statistics"):
            selected_player = st.selectbox("Select Player", players_df['name'])
            player_data = players_df[players_df['name'] == selected_player].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                goals = st.number_input("Goals", min_value=0, value=int(player_data['goals']))
            with col2:
                assists = st.number_input("Assists", min_value=0, value=int(player_data['assists']))
            
            if st.button("Update Statistics"):
                update_player_stats(player_data['id'], goals, assists)
                st.success("Statistics updated successfully!")
                st.rerun()
        
        # Display player statistics
        st.subheader("Player Statistics")
        stats = players_df.sort_values('goals', ascending=False)
        st.dataframe(stats[['name', 'team_name', 'goals', 'assists']])
