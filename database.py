import sqlitecloud
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlitecloud.connect("sqlitecloud://cdjgp22tnk.g3.sqlite.cloud:8860/sports_stats.db?apikey=dyN479x8iljSx7MnfgOKz3DheG0jLXXwHBOisOQb6L8")

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
        cursor = conn.execute('SELECT * FROM <tablename>;')
        # Create teams table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS teams
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      wins INTEGER DEFAULT 0,
                      draws INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0,
                      matchesPlayed INTEGER DEFAULT 0)''')
        # Create players table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS players
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      team_id INTEGER,
                      goals INTEGER DEFAULT 0,
                      assists INTEGER DEFAULT 0,
                      FOREIGN KEY (team_id) REFERENCES teams (id))''')

# One-time migration function to add matchesPlayed column if it doesn't exist
def migrate_database():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM <tablename>;')
        # Check if matchesPlayed column exists
        c.execute("PRAGMA table_info(teams)")
        columns = [column[1] for column in c.fetchall()]

        if 'matchesPlayed' not in columns:
            # Add matchesPlayed column
            c.execute("ALTER TABLE teams ADD COLUMN matchesPlayed INTEGER DEFAULT 0")
            # Update existing records
            c.execute("UPDATE teams SET matchesPlayed = wins + draws + losses")
            return True
        return False

def get_teams():
    # Ensure migration has been run
    migrate_database()

    with get_db_connection() as conn:
        teams = pd.read_sql_query("SELECT * FROM teams ORDER BY name", conn)
        return teams

def get_players():
    # Ensure migration has been run
    migrate_database()

    with get_db_connection() as conn:
        players = pd.read_sql_query("""
            SELECT 
                players.*,
                teams.name as team_name,
                teams.wins,
                teams.draws,
                teams.losses,
                teams.matchesPlayed
            FROM players 
            LEFT JOIN teams ON players.team_id = teams.id
            ORDER BY players.name
        """, conn)
        return players

def add_team(name):
    with get_db_connection() as conn:
        c = conn.execute('SELECT * FROM <tablename>;')
        try:
            c.execute("INSERT INTO teams (name, wins, draws, losses, matchesPlayed) VALUES (?, 0, 0, 0, 0)", (name,))
            return True
        except sqlite3.IntegrityError:
            return False

def update_team_stats(team_id, wins, draws, losses):
    with get_db_connection() as conn:
        c = conn.execute('SELECT * FROM <tablename>;')
        # First verify the team exists
        c.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if not c.fetchone():
            raise ValueError(f"No team found with ID {team_id}")
        c.execute("""
            UPDATE teams 
            SET wins=?, draws=?, losses=?, matchesPlayed=?
            WHERE id=?
        """, (wins, draws, losses, wins+draws+losses, team_id))

def add_player(name, team_id):
    with get_db_connection() as conn:
        c = conn.execute('SELECT * FROM <tablename>;')
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
        c = conn.execute('SELECT * FROM <tablename>;')
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
        c = conn.execute('SELECT * FROM <tablename>;')
        c.execute("SELECT goals, assists FROM players WHERE id = ?", (player_id,))
        result = c.fetchone()
        if result is None:
            raise ValueError(f"No player found with ID {player_id}")
        return {"goals": result[0], "assists": result[1]}