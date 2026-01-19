import sys
import os

# Ajouter le dossier parent au path pour importer db.connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_connection, get_cursor

def update_schema():
    conn = get_connection()
    if not conn:
        print("Erreur de connexion")
        return

    cur = get_cursor(conn)
    try:
        print("Mise à jour de la table vente...")
        
        # Ajouter montant_recu
        cur.execute("""
            ALTER TABLE vente 
            ADD COLUMN IF NOT EXISTS montant_recu DECIMAL(10, 2) DEFAULT NULL
        """)
        
        # Ajouter monnaie_rendue
        cur.execute("""
            ALTER TABLE vente 
            ADD COLUMN IF NOT EXISTS monnaie_rendue DECIMAL(10, 2) DEFAULT NULL
        """)
        
        # Ajouter mode_paiement
        cur.execute("""
            ALTER TABLE vente 
            ADD COLUMN IF NOT EXISTS mode_paiement VARCHAR(20) DEFAULT 'ESPECES'
        """)
        
        conn.commit()
        print("Succès : Colonnes ajoutées à la table vente.")
        
    except Exception as e:
        print(f"Erreur : {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
