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
        'role': 'role',
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
def add_supplier(nom, adresse):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO fournisseur (nom_fournisseur, adresse_fournisseur)
            VALUES (%s, %s)
            RETURNING id_fournisseur
        """, (nom, adresse))
        supplier_id = cur.fetchone()['id_fournisseur']
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
            SELECT id_fournisseur, nom_fournisseur AS nom, adresse_fournisseur AS adresse
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
            SELECT id_fournisseur, nom_fournisseur AS nom, adresse_fournisseur AS adresse
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
def update_supplier(supplier_id, nom, adresse):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("""
            UPDATE fournisseur
            SET nom_fournisseur=%s, adresse_fournisseur=%s
            WHERE id_fournisseur=%s
        """, (nom, adresse, supplier_id))
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
# ===================== CATEGORIES =====================
def add_category(nom, description, seuil_min_defaut):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO categorie (nom_categorie, seuil_min_defaut, description)
            VALUES (%s, %s, %s)
            RETURNING id_categorie
        """, (nom, seuil_min_defaut, description))

        row = cur.fetchone()
        conn.commit()
        return row['id_categorie']

    except Exception as e:
        print("Erreur add_category :", repr(e))
        conn.rollback()
        return None

    finally:
        cur.close()
        conn.close()


def get_all_categories():
    """
    Récupère toutes les catégories.
    :return: liste de dict
    """
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_categorie, nom_categorie, description, seuil_min_defaut
            FROM categorie
            ORDER BY id_categorie DESC
        """)
        return cur.fetchall()
    except Exception as e:
        print("Erreur get_all_categories :", e)
        return []
    finally:
        cur.close()
        conn.close()


def update_category(cat_id, nom, description, seuil_min_defaut):

    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("""
            UPDATE categorie
            SET nom_categorie=%s, description=%s, seuil_min_defaut=%s
            WHERE id_categorie=%s
        """, (nom, description, seuil_min_defaut, cat_id))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur update_category :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()



def delete_category(cat_id):
    """
    Supprime une catégorie.
    :param cat_id: int
    :return: True si succès, False sinon
    """
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute(
            "DELETE FROM categorie WHERE id_categorie = %s",
            (cat_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Erreur delete_category :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def search_categories(keyword):
    """
    Recherche les catégories par nom.
    :param keyword: str
    :return: liste de dict
    """
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_categorie, nom_categorie, description, seuil_min_defaut
            FROM categorie
            WHERE nom_categorie ILIKE %s
            ORDER BY id_categorie DESC
        """, (f"%{keyword}%",))
        return cur.fetchall()
    except Exception as e:
        print("Erreur search_categories :", e)
        return []
    finally:
        cur.close()
        conn.close()

# ===================== PRODUITS =====================

def add_product(nom_produit, description, prix_unitaire, id_categorie, quantite_stock, seuil_min_personnalise, statut):
    """
    Ajoute un nouveau produit dans la base de données.
    :param nom_produit: str
    :param description: str
    :param prix_unitaire: float
    :param id_categorie: int
    :param quantite_stock: int
    :param seuil_min_personnalise: int ou None
    :param statut: str (ACTIF ou INACTIF)
    :return: id du produit ajouté ou None si erreur
    """
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO produit (nom_produit, description, prix_unitaire, id_categorie, quantite_stock, seuil_min_personnalise, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_produit
        """, (nom_produit, description, prix_unitaire, id_categorie, quantite_stock, seuil_min_personnalise, statut))
        product_id = cur.fetchone()[0]
        conn.commit()
        return product_id
    except Exception as e:
        print("Erreur add_product:", e)
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_all_products():
    """
    Récupère tous les produits de la base de données.
    :return: liste de dicts contenant les informations des produits
    """
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT p.id_produit, p.nom_produit, p.description, p.prix_unitaire, p.id_categorie, p.quantite_stock,
                   p.seuil_min_personnalise, p.statut, p.date_ajout, c.nom_categorie
            FROM produit p
            JOIN categorie c ON p.id_categorie = c.id_categorie
            ORDER BY p.id_produit DESC
        """)
        rows = cur.fetchall()
        products = []
        for row in rows:
            products.append({
                'id_produit': row[0],
                'nom_produit': row[1],
                'description': row[2],
                'prix_unitaire': row[3],
                'id_categorie': row[4],
                'quantite_stock': row[5],
                'seuil_min_personnalise': row[6],
                'statut': row[7],
                'date_ajout': row[8],
                'nom_categorie': row[9]
            })
        return products
    except Exception as e:
        print("Erreur get_all_products:", e)
        return []
    finally:
        cur.close()
        conn.close()


def update_product(id_produit, nom_produit, description, prix_unitaire, id_categorie, quantite_stock, seuil_min_personnalise, statut):
    """
    Met à jour un produit existant.
    :param id_produit: int
    :param nom_produit: str
    :param description: str
    :param prix_unitaire: float
    :param id_categorie: int
    :param quantite_stock: int
    :param seuil_min_personnalise: int ou None
    :param statut: str (ACTIF ou INACTIF)
    :return: True si succès, False sinon
    """
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("""
            UPDATE produit
            SET nom_produit = %s, description = %s, prix_unitaire = %s, id_categorie = %s, quantite_stock = %s, 
                seuil_min_personnalise = %s, statut = %s
            WHERE id_produit = %s
        """, (nom_produit, description, prix_unitaire, id_categorie, quantite_stock, seuil_min_personnalise, statut, id_produit))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur update_product:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def delete_product(id_produit):
    """
    Supprime un produit de la base de données.
    :param id_produit: int
    :return: True si succès, False sinon
    """
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("DELETE FROM produit WHERE id_produit = %s", (id_produit,))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur delete_product:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def get_product_by_id(id_produit):
    """
    Récupère un produit par son ID.
    :param id_produit: int
    :return: dict contenant les informations du produit ou None si non trouvé
    """
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT p.id_produit, p.nom_produit, p.description, p.prix_unitaire, p.id_categorie, p.quantite_stock,
                   p.seuil_min_personnalise, p.statut, p.date_ajout, c.nom_categorie
            FROM produit p
            JOIN categorie c ON p.id_categorie = c.id_categorie
            WHERE p.id_produit = %s
        """, (id_produit,))
        row = cur.fetchone()
        if row:
            return {
                'id_produit': row[0],
                'nom_produit': row[1],
                'description': row[2],
                'prix_unitaire': row[3],
                'id_categorie': row[4],
                'quantite_stock': row[5],
                'seuil_min_personnalise': row[6],
                'statut': row[7],
                'date_ajout': row[8],
                'nom_categorie': row[9]
            }
        return None
    except Exception as e:
        print("Erreur get_product_by_id:", e)
        return None
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
