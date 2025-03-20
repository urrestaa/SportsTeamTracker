from pyarrow import null
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database import get_teams, get_players

def visualization_section():
    st.header("Statistics Visualization")

    teams_df = get_teams()
    players_df = get_players()

    if not teams_df.empty:
        with st.spinner("Loading team statistics..."):
            # Make layout more mobile-friendly with full-width columns
            st.subheader("Team Performance")

            # Team Points Chart
            teams_df['Points'] = teams_df['wins'] * 3 + teams_df['draws']
            fig_points = px.bar(teams_df, 
                             x='name', 
                             y='Points',
                             title='Team Points',
                             labels={'name': 'Team', 'Points': 'Points'})
            fig_points.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_points, use_container_width=True)

            # Win Rate Chart with improved mobile layout
            teams_df['Win Rate'] = ((teams_df['wins'] / teams_df['matchesPlayed']) * 100).round(0)
            fig_winrate = px.pie(teams_df, 
                              values='Win Rate', 
                              names='name',
                              title='Team Win Rates')
            fig_winrate.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_winrate, use_container_width=True)

    if not players_df.empty:
        st.subheader("Player Statistics")
        with st.spinner("Loading player statistics..."):
            # Calculate total contributions
            players_df['Total Contributions'] = players_df['goals'] + players_df['assists']

            # Goals vs Assists Comparison
            fig_comparison = go.Figure()

            # Sort players by total contributions
            top_players = players_df.nlargest(10, 'Total Contributions')

            fig_comparison.add_trace(go.Bar(
                name='Goals',
                x=top_players['name'],
                y=top_players['goals'],
                marker_color='#1f77b4'
            ))

            fig_comparison.add_trace(go.Bar(
                name='Assists',
                x=top_players['name'],
                y=top_players['assists'],
                marker_color='#ff7f0e'
            ))

            fig_comparison.update_layout(
                title='Top 10 Players - Goals vs Assists',
                barmode='group',
                xaxis_tickangle=-45,
                height=400,
                margin=dict(l=10, r=10, t=40, b=80),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Most Contributions Chart
            fig_contributions = px.bar(
                top_players,
                x='name',
                y='Total Contributions',
                title='Top 10 Players - Total Contributions',
                color='Total Contributions',
                labels={'name': 'Player', 'Total Contributions': 'Goals + Assists'}
            )
            fig_contributions.update_layout(
                xaxis_tickangle=-45,
                height=400,
                margin=dict(l=10, r=10, t=40, b=80),
                showlegend=False
            )
            st.plotly_chart(fig_contributions, use_container_width=True)

            # Team-wise Player Stats
            st.subheader("Team-wise Player Statistics")

            # Add team filter
            teams = ['All Teams'] + teams_df['name'].tolist()
            selected_team = st.selectbox(
                "Select Team",
                teams,
                key='viz_team_filter'
            )

            filtered_stats = players_df.copy()
            if selected_team != 'All Teams':
                team_data = teams_df[teams_df['name'] == selected_team].iloc[0]
                filtered_stats = filtered_stats[filtered_stats['team_id'] == int(team_data['id'])]

            if not filtered_stats.empty:
                filtered_stats = filtered_stats.sort_values('Total Contributions', ascending=False)

                filtered_stats["Name"] = filtered_stats["name"]
                filtered_stats["Team Name"] = filtered_stats["team_name"]
                filtered_stats["Matches Played"] = filtered_stats["matchesPlayed"]
                filtered_stats["Goals"] = filtered_stats["goals"]
                filtered_stats["Assists"] = filtered_stats["assists"]
                filtered_stats["Total Contributions"] = filtered_stats["Total Contributions"]

                st.dataframe(
                    filtered_stats[['Name', 'Team Name', 'Matches Played', 'Goals', 'Assists', 'Total Contributions']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No players found for the selected team")