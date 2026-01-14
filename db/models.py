from db.connection import get_connection, get_cursor
from psycopg2.extras import RealDictCursor
from datetime import datetime


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
def add_product(
        nom_produit,
        description,
        prix_unitaire,
        id_categorie,
        quantite_stock,
        seuil_min_personnalise,
        statut
):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO produit (
                nom_produit,
                description,
                prix_unitaire,
                id_categorie,
                quantite_stock,
                seuil_min_personnalise,
                statut
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_produit
        """, (
            nom_produit,
            description,
            prix_unitaire,
            id_categorie,
            quantite_stock,
            seuil_min_personnalise,
            statut
        ))

        result = cur.fetchone()
        prod_id = result['id_produit'] if result else None

        conn.commit()
        return prod_id

    except Exception as e:
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_all_products():
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT 
                p.id_produit,
                p.nom_produit,
                p.description,
                p.prix_unitaire,
                p.quantite_stock,
                p.seuil_min_personnalise,
                p.statut,
                p.date_ajout,
                c.nom_categorie
            FROM produit p
            JOIN categorie c ON p.id_categorie = c.id_categorie
            ORDER BY p.id_produit DESC
        """)
        return cur.fetchall()
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()


def update_product(
        id_produit,
        nom_produit,
        description,
        prix_unitaire,
        id_categorie,
        seuil_min_personnalise,
        statut
):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute("""
            UPDATE produit
            SET 
                nom_produit=%s,
                description=%s,
                prix_unitaire=%s,
                id_categorie=%s,
                seuil_min_personnalise=%s,
                statut=%s
            WHERE id_produit=%s
        """, (
            nom_produit,
            description,
            prix_unitaire,
            id_categorie,
            seuil_min_personnalise,
            statut,
            id_produit
        ))

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def delete_product(product_id):
    conn = get_connection()
    if not conn:
        return False

    cur = get_cursor(conn)
    try:
        cur.execute(
            "DELETE FROM produit WHERE id_produit = %s",
            (product_id,)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def get_product_by_id(id_produit):
    conn = get_connection()
    if not conn:
        return None

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT p.id_produit, p.nom_produit, p.description, p.prix_unitaire, 
                   p.id_categorie, p.quantite_stock, p.seuil_min_personnalise, 
                   p.statut, p.date_ajout, c.nom_categorie
            FROM produit p
            JOIN categorie c ON p.id_categorie = c.id_categorie
            WHERE p.id_produit = %s
        """, (id_produit,))

        row = cur.fetchone()
        if row:
            return {
                'id_produit': row['id_produit'],
                'nom_produit': row['nom_produit'],
                'description': row['description'],
                'prix_unitaire': row['prix_unitaire'],
                'id_categorie': row['id_categorie'],
                'quantite_stock': row['quantite_stock'],
                'seuil_min_personnalise': row['seuil_min_personnalise'],
                'statut': row['statut'],
                'date_ajout': row['date_ajout'],
                'nom_categorie': row['nom_categorie']
            }
        return None

    except Exception:
        return None
    finally:
        cur.close()
        conn.close()


def get_categories_for_dropdown():
    """Retourne les catégories formatées pour un menu déroulant"""
    conn = get_connection()
    if not conn:
        return []

    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_categorie, nom_categorie 
            FROM categorie 
            ORDER BY nom_categorie
        """)
        return cur.fetchall()
    except Exception:
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

# ===================== VENTES =====================

def get_products_for_sale():
    conn = get_connection()
    cur = get_cursor(conn)

    cur.execute("""
        SELECT
            id_produit,
            nom_produit,
            prix_unitaire,
            quantite_stock
        FROM produit
        WHERE quantite_stock > 0
        ORDER BY nom_produit
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows

def process_sale(panier, id_utilisateur):
    """
    panier = [
        {
            'id': int,
            'quantité': int,
            'prix_unitaire': float
        }
    ]
    """

    conn = get_connection()
    if not conn:
        return False, "Connexion BD impossible"

    cur = conn.cursor()

    try:
        # =========================
        # 1. Vérifier le stock
        # =========================
        for item in panier:
            cur.execute(
                "SELECT quantite_stock FROM produit WHERE id_produit = %s",
                (item['id'],)
            )
            row = cur.fetchone()

            if not row:
                raise Exception("Produit introuvable")

            stock_dispo = row[0]
            if item['quantité'] > stock_dispo:
                raise Exception(
                    f"Stock insuffisant pour le produit ID {item['id']}"
                )

        # =========================
        # 2. Calcul du total
        # =========================
        total_vente = sum(
            item['quantité'] * item['prix_unitaire']
            for item in panier
        )

        # =========================
        # 3. Créer la vente
        # =========================
        cur.execute("""
            INSERT INTO vente (total_vente, id_utilisateur)
            VALUES (%s, %s)
            RETURNING id_vente
        """, (total_vente, id_utilisateur))

        id_vente = cur.fetchone()[0]

        # =========================
        # 4. Lignes + stock
        # =========================
        for item in panier:
            # ligne_vente
            cur.execute("""
                INSERT INTO ligne_vente
                (id_vente, id_produit, quantite_vendue, prix_unitaire)
                VALUES (%s, %s, %s, %s)
            """, (
                id_vente,
                item['id'],
                item['quantité'],
                item['prix_unitaire']
            ))

            # mise à jour stock
            cur.execute("""
                UPDATE produit
                SET quantite_stock = quantite_stock - %s
                WHERE id_produit = %s
            """, (item['quantité'], item['id']))

        conn.commit()
        return True, id_vente

    except Exception as e:
        conn.rollback()
        print("Erreur process_sale :", e)
        return False, str(e)

    finally:
        cur.close()
        conn.close()


