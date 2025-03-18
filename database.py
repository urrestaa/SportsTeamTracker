import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('sports_stats.db')
    c = conn.cursor()
    
    # Create teams table
    c.execute('''CREATE TABLE IF NOT EXISTS teams
                 (id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE,
                  wins INTEGER DEFAULT 0,
                  draws INTEGER DEFAULT 0,
                  losses INTEGER DEFAULT 0)''')
    
    # Create players table
    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  team_id INTEGER,
                  goals INTEGER DEFAULT 0,
                  assists INTEGER DEFAULT 0,
                  FOREIGN KEY (team_id) REFERENCES teams (id))''')
    
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect('sports_stats.db')

def get_teams():
    conn = get_db()
    teams = pd.read_sql_query("SELECT * FROM teams", conn)
    conn.close()
    return teams

def get_players():
    conn = get_db()
    players = pd.read_sql_query("""
        SELECT players.*, teams.name as team_name 
        FROM players 
        LEFT JOIN teams ON players.team_id = teams.id
    """, conn)
    conn.close()
    return players

def add_team(name):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO teams (name, wins, draws, losses) VALUES (?, 0, 0, 0)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_team_stats(team_id, wins, draws, losses):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE teams SET wins=?, draws=?, losses=? WHERE id=?", 
             (wins, draws, losses, team_id))
    conn.commit()
    conn.close()

def add_player(name, team_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO players (name, team_id, goals, assists) VALUES (?, ?, 0, 0)", 
             (name, team_id))
    conn.commit()
    conn.close()

def update_player_stats(player_id, goals, assists):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE players SET goals=?, assists=? WHERE id=?", 
             (goals, assists, player_id))
    conn.commit()
    conn.close()
