from db.connection import get_connection, get_cursor
from psycopg2.extras import RealDictCursor

# Exemple minimal pour l'insertion
def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(query, params or ())
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results
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

def search_employees(field, keyword):
    allowed_fields = {
        'id_utilisateur': 'id_utilisateur',
        'nom': 'nom',
        'email': 'email'
    }

    if field not in allowed_fields:
        return []

    query = f"""
        SELECT *
        FROM utilisateur
        WHERE {allowed_fields[field]} ILIKE %s
        AND role != 'ADMIN'
    """

    return fetch_all(query, (f"%{keyword}%",))



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


def delete_employee(emp_id):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute(
            "DELETE FROM utilisateur WHERE id_utilisateur = %s",
            (emp_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Erreur delete_employee :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def update_employee(emp_id, nom, email, password, role):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        if password:
            cur.execute("""
                UPDATE utilisateur
                SET nom=%s, email=%s, mot_de_passe=%s, role=%s
                WHERE id_utilisateur=%s
            """, (nom, email, password, role, emp_id))
        else:
            cur.execute("""
                UPDATE utilisateur
                SET nom=%s, email=%s, role=%s
                WHERE id_utilisateur=%s
            """, (nom, email, role, emp_id))

        conn.commit()
        return True
    except Exception as e:
        print("Erreur update_employee :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# ===================== AJOUTER UN FOURNISSEUR =====================
def add_supplier(nom, contact):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO fournisseur (nom_fournisseur, adresse_fournisseur)
            VALUES (%s, %s)
            RETURNING id_fournisseur
        """, (nom, contact))
        supplier_id = cur.fetchone()[0]
        conn.commit()
        return supplier_id
    except Exception as e:
        print("Erreur add_supplier :", e)
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


# ===================== OBTENIR TOUS LES FOURNISSEURS =====================
def get_all_suppliers():
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_fournisseur, nom_fournisseur AS nom, adresse_fournisseur AS contact
            FROM fournisseur
            ORDER BY id_fournisseur DESC
        """)
        return cur.fetchall()
    except Exception as e:
        print("Erreur get_all_suppliers :", e)
        return []
    finally:
        cur.close()
        conn.close()


# ===================== RECHERCHER UN FOURNISSEUR PAR NOM =====================
def search_suppliers(keyword):
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_fournisseur, nom_fournisseur AS nom, adresse_fournisseur AS contact
            FROM fournisseur
            WHERE nom_fournisseur ILIKE %s
            ORDER BY id_fournisseur DESC
        """, (f"%{keyword}%",))
        return cur.fetchall()
    except Exception as e:
        print("Erreur search_suppliers :", e)
        return []
    finally:
        cur.close()
        conn.close()


# ===================== METTRE À JOUR UN FOURNISSEUR =====================
def update_supplier(supplier_id, nom, contact):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("""
            UPDATE fournisseur
            SET nom_fournisseur=%s, adresse_fournisseur=%s
            WHERE id_fournisseur=%s
        """, (nom, contact, supplier_id))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur update_supplier :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


# ===================== SUPPRIMER UN FOURNISSEUR =====================
def delete_supplier(supplier_id):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute(
            "DELETE FROM fournisseur WHERE id_fournisseur = %s",
            (supplier_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Erreur delete_supplier :", e)
        conn.rollback()
        return False
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
