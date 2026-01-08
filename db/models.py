from db.connection import get_connection, get_cursor

# Exemple minimal pour l'insertion
def add_utilisateur(nom, email, mot_de_passe, role):
    conn = get_connection()
    if not conn:
        return False
    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO utilisateur (nom, email, mot_de_passe, role)
            VALUES (%s, %s, %s, %s)
        """, (nom, email, mot_de_passe, role))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur add_utilisateur :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
