import sqlite3
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('sports_stats.db')
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()

        # Drop existing tables to start fresh
        c.execute("DROP TABLE IF EXISTS players")
        c.execute("DROP TABLE IF EXISTS teams")

        # Create teams table
        c.execute('''CREATE TABLE IF NOT EXISTS teams
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      wins INTEGER DEFAULT 0,
                      draws INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0)''')

        # Create players table
        c.execute('''CREATE TABLE IF NOT EXISTS players
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      team_id INTEGER,
                      goals INTEGER DEFAULT 0,
                      assists INTEGER DEFAULT 0,
                      FOREIGN KEY (team_id) REFERENCES teams (id))''')

def get_teams():
    with get_db_connection() as conn:
        teams = pd.read_sql_query("SELECT * FROM teams ORDER BY id", conn)
        return teams

def get_players():
    with get_db_connection() as conn:
        players = pd.read_sql_query("""
            SELECT 
                players.*,
                teams.name as team_name 
            FROM players 
            LEFT JOIN teams ON players.team_id = teams.id
            ORDER BY players.id
        """, conn)
        return players

def add_team(name):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO teams (name, wins, draws, losses) VALUES (?, 0, 0, 0)", (name,))
            return True
        except sqlite3.IntegrityError:
            return False

def update_team_stats(team_id, wins, draws, losses):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE teams 
            SET wins=?, draws=?, losses=? 
            WHERE id=?
        """, (wins, draws, losses, team_id))
        if c.rowcount == 0:
            raise ValueError(f"No team found with ID {team_id}")

def add_player(name, team_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        # First verify the team exists
        c.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if not c.fetchone():
            raise ValueError(f"No team found with ID {team_id}")

        c.execute("""
            INSERT INTO players (name, team_id, goals, assists) 
            VALUES (?, ?, 0, 0)
        """, (name, team_id))
        return c.lastrowid

def update_player_stats(player_id, goals, assists):
    with get_db_connection() as conn:
        c = conn.cursor()
        # First verify the player exists
        c.execute("SELECT id FROM players WHERE id = ?", (player_id,))
        if not c.fetchone():
            raise ValueError(f"No player found with ID {player_id}")

        c.execute("""
            UPDATE players 
            SET goals=?, assists=? 
            WHERE id=?
        """, (goals, assists, player_id))

def get_player_stats(player_id):
    with get_db_connection() as conn:
        result = pd.read_sql_query("""
            SELECT goals, assists 
            FROM players 
            WHERE id=?
        """, conn, params=(player_id,))

        if result.empty:
            raise ValueError(f"No player found with ID {player_id}")

        return result.iloc[0].to_dict()