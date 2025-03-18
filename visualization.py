import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database import get_teams, get_players

def visualization_section():
    st.header("Statistics Visualization")
    
    teams_df = get_teams()
    players_df = get_players()
    
    if not teams_df.empty:
        col1, col2 = st.columns(2)
        
        # Team Points Chart
        with col1:
            teams_df['Points'] = teams_df['wins'] * 3 + teams_df['draws']
            fig_points = px.bar(teams_df, 
                              x='name', 
                              y='Points',
                              title='Team Points',
                              labels={'name': 'Team', 'Points': 'Points'})
            st.plotly_chart(fig_points, use_container_width=True)
        
        # Win Rate Chart
        with col2:
            teams_df['Matches'] = teams_df['wins'] + teams_df['draws'] + teams_df['losses']
            teams_df['Win Rate'] = (teams_df['wins'] / teams_df['Matches'] * 100).round(2)
            fig_winrate = px.pie(teams_df, 
                               values='Win Rate', 
                               names='name',
                               title='Team Win Rates')
            st.plotly_chart(fig_winrate, use_container_width=True)
        
        # Team Performance Breakdown
        fig_performance = go.Figure(data=[
            go.Bar(name='Wins', x=teams_df['name'], y=teams_df['wins']),
            go.Bar(name='Draws', x=teams_df['name'], y=teams_df['draws']),
            go.Bar(name='Losses', x=teams_df['name'], y=teams_df['losses'])
        ])
        fig_performance.update_layout(barmode='stack', title='Team Performance Breakdown')
        st.plotly_chart(fig_performance, use_container_width=True)
    
    if not players_df.empty:
        col1, col2 = st.columns(2)
        
        # Top Scorers
        with col1:
            top_scorers = players_df.nlargest(5, 'goals')
            fig_scorers = px.bar(top_scorers, 
                                x='name', 
                                y='goals',
                                title='Top 5 Scorers',
                                labels={'name': 'Player', 'goals': 'Goals'})
            st.plotly_chart(fig_scorers, use_container_width=True)
        
        # Top Assisters
        with col2:
            top_assisters = players_df.nlargest(5, 'assists')
            fig_assisters = px.bar(top_assisters, 
                                  x='name', 
                                  y='assists',
                                  title='Top 5 Assisters',
                                  labels={'name': 'Player', 'assists': 'Assists'})
            st.plotly_chart(fig_assisters, use_container_width=True)
