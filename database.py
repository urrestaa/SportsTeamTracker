import sqlitecloud
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite Cloud database connection.
    Handles connection, commit/rollback, and closing.
    """
    # Replace with your actual SQLite Cloud connection string
    conn = sqlitecloud.connect("mysql://stbfutbol_slowlyday:e13ea8ab1137f2ca2653b4abbb079a2ace22f76a@vp6wyl.h.filess.io:3307/stbfutbol_slowlyday")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize database tables if they don't exist."""
    with get_db_connection() as conn:
        # SQLite Cloud uses execute instead of cursor()
        conn.execute('''CREATE TABLE IF NOT EXISTS teams
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      wins INTEGER DEFAULT 0,
                      draws INTEGER DEFAULT 0,
                      losses INTEGER DEFAULT 0,
                      matchesPlayed INTEGER DEFAULT 0)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS players
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      team_id INTEGER,
                      goals INTEGER DEFAULT 0,
                      assists INTEGER DEFAULT 0,
                      FOREIGN KEY (team_id) REFERENCES teams (id))''')

def migrate_database():
    """
    One-time migration function to add matchesPlayed column if it doesn't exist.
    Adapted for SQLite Cloud's execution method.
    """
    with get_db_connection() as conn:
        # Check column existence
        columns_result = conn.execute("PRAGMA table_info(teams)")
        columns = [column[1] for column in columns_result.fetchall()]

        if 'matchesPlayed' not in columns:
            # Add matchesPlayed column
            conn.execute("ALTER TABLE teams ADD COLUMN matchesPlayed INTEGER DEFAULT 0")
            # Update existing records
            conn.execute("UPDATE teams SET matchesPlayed = wins + draws + losses")
            return True
        return False

def get_teams():
    """Retrieve all teams, ensuring migration has been run."""
    migrate_database()

    with get_db_connection() as conn:
        # Use pandas read_sql method with SQLite Cloud connection
        teams = pd.read_sql("SELECT * FROM teams ORDER BY name", conn)
        return teams

def get_players():
    """Retrieve all players with team information."""
    migrate_database()

    with get_db_connection() as conn:
        players = pd.read_sql("""
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
    """Add a new team to the database."""
    with get_db_connection() as conn:
        try:
            conn.execute("INSERT INTO teams (name, wins, draws, losses, matchesPlayed) VALUES (?, 0, 0, 0, 0)", (name,))
            return True
        except sqlitecloud.Error:
            return False

def update_team_stats(team_id, wins, draws, losses):
    """Update team statistics."""
    with get_db_connection() as conn:
        # Verify team exists
        result = conn.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if not result.fetchone():
            raise ValueError(f"No team found with ID {team_id}")
        
        conn.execute("""
            UPDATE teams 
            SET wins=?, draws=?, losses=?, matchesPlayed=?
            WHERE id=?
        """, (wins, draws, losses, wins+draws+losses, team_id))

def add_player(name, team_id):
    """Add a new player to a team."""
    with get_db_connection() as conn:
        # Verify team exists
        result = conn.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if not result.fetchone():
            raise ValueError(f"No team found with ID {team_id}")
        
        conn.execute("""
            INSERT INTO players (name, team_id, goals, assists) 
            VALUES (?, ?, 0, 0)
        """, (name, team_id))
        
        # Fetch the last inserted row ID
        result = conn.execute("SELECT last_insert_rowid()")
        return result.fetchone()[0]

def update_player_stats(player_id, goals, assists):
    """Update player statistics."""
    with get_db_connection() as conn:
        # Verify player exists
        result = conn.execute("SELECT id FROM players WHERE id = ?", (player_id,))
        if not result.fetchone():
            raise ValueError(f"No player found with ID {player_id}")
        
        conn.execute("""
            UPDATE players 
            SET goals=?, assists=? 
            WHERE id=?
        """, (goals, assists, player_id))

def get_player_stats(player_id):
    """Retrieve player statistics."""
    with get_db_connection() as conn:
        result = conn.execute("SELECT goals, assists FROM players WHERE id = ?", (player_id,))
        row = result.fetchone()
        
        if row is None:
            raise ValueError(f"No player found with ID {player_id}")
        
        return {"goals": row[0], "assists": row[1]}

# Optional: Initialization call
if __name__ == "__main__":
    init_db()