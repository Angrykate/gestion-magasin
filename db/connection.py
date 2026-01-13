import psycopg2
from psycopg2.extras import RealDictCursor
from db.db_config import DB_CONFIG

def get_connection():
    """Renvoie une connexion à la base de données"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Erreur de connexion à la base :", e)
        return None

def get_cursor(conn):
    """Renvoie un curseur avec dictionnaire"""
    return conn.cursor(cursor_factory=RealDictCursor)
