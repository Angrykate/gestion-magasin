from db.connection import get_connection, get_cursor

# Exemple minimal pour l'insertion
def add_employee(nom, email, mot_de_passe, role):
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
        print("Erreur add_employee :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_all_employees():
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_utilisateur, nom, email, mot_de_passe, role
            FROM utilisateur
            WHERE role != 'ADMIN'
            ORDER BY id_utilisateur DESC
        """)
        return cur.fetchall()
    except Exception as e:
        print("Erreur get_all_employees :", e)
        return []
    finally:
        cur.close()
        conn.close()


def authenticate_user(email, password):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_utilisateur, nom, role
            FROM utilisateur
            WHERE email = %s AND mot_de_passe = %s
        """, (email, password))

        return cur.fetchone()
    except Exception as e:
        print("Erreur login :", e)
        return None
    finally:
        cur.close()
        conn.close()
