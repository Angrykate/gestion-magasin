-- ============================================
-- TRIGGERS ADAPTÉS AU SCHÉMA
-- ============================================

-- TRIGGER 1: Pré-remplir prix unitaire dans ligne_vente
CREATE OR REPLACE FUNCTION fn_pre_remplir_prix_vente()
RETURNS TRIGGER AS $$
BEGIN
    -- Récupérer le prix actuel du produit
    SELECT prix_unitaire INTO NEW.prix_unitaire 
    FROM produit WHERE id_produit = NEW.id_produit;
    
    -- Si le produit n'existe pas, bloquer
    IF NEW.prix_unitaire IS NULL THEN
        RAISE EXCEPTION 'Produit introuvable : %', NEW.id_produit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_pre_remplir_prix ON ligne_vente;
CREATE TRIGGER trg_pre_remplir_prix
BEFORE INSERT ON ligne_vente
FOR EACH ROW
EXECUTE FUNCTION fn_pre_remplir_prix_vente();

-- TRIGGER 2: Mise à jour stock après vente
CREATE OR REPLACE FUNCTION fn_maj_stock_vente()
RETURNS TRIGGER AS $$
DECLARE
    v_stock_actuel INT;
    v_nouveau_stock INT;
    v_seuil_min INT;
    v_id_utilisateur INT;
BEGIN
    -- Récupérer le stock actuel et le seuil
    SELECT p.quantite_stock, 
           COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut)
    INTO v_stock_actuel, v_seuil_min
    FROM produit p
    JOIN categorie c ON p.id_categorie = c.id_categorie
    WHERE p.id_produit = NEW.id_produit
    FOR UPDATE;
    
    -- Récupérer l'utilisateur de la vente
    SELECT id_utilisateur INTO v_id_utilisateur
    FROM vente 
    WHERE id_vente = NEW.id_vente;
    
    -- Vérifier le stock
    IF v_stock_actuel < NEW.quantite_vendue THEN
        RAISE EXCEPTION 'Stock insuffisant pour le produit ID: % (Stock: %, Demandé: %)', 
                        NEW.id_produit, v_stock_actuel, NEW.quantite_vendue;
    END IF;

    -- Calculer nouveau stock
    v_nouveau_stock := v_stock_actuel - NEW.quantite_vendue;

    -- Mettre à jour le stock
    UPDATE produit 
    SET quantite_stock = v_nouveau_stock
    WHERE id_produit = NEW.id_produit;

    -- Alerte si stock bas
    IF v_nouveau_stock <= v_seuil_min THEN
        RAISE NOTICE 'ALERTE : Stock bas pour le produit % (Stock: %, Seuil: %)', 
                     NEW.id_produit, v_nouveau_stock, v_seuil_min;
    END IF;

    -- Créer mouvement de stock
    INSERT INTO mouvement_stock (
        date_mouvement, type_mouvement, quantite, id_utilisateur, 
        id_produit, id_vente
    ) VALUES (
        CURRENT_TIMESTAMP, 
        'SORTIE', 
        NEW.quantite_vendue,
        v_id_utilisateur,
        NEW.id_produit,
        NEW.id_vente
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_vente ON ligne_vente;
CREATE TRIGGER trg_stock_vente
AFTER INSERT ON ligne_vente
FOR EACH ROW
EXECUTE FUNCTION fn_maj_stock_vente();

-- TRIGGER 3: Mettre à jour total_vente automatiquement
CREATE OR REPLACE FUNCTION fn_update_total_vente()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculer le total de la vente
    UPDATE vente v
    SET total_vente = (
        SELECT COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0)
        FROM ligne_vente lv
        WHERE lv.id_vente = NEW.id_vente
    )
    WHERE v.id_vente = NEW.id_vente;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_total_vente ON ligne_vente;
CREATE TRIGGER trg_update_total_vente
AFTER INSERT OR DELETE OR UPDATE ON ligne_vente
FOR EACH ROW
EXECUTE FUNCTION fn_update_total_vente();

-- TRIGGER 4: Générer reçu automatiquement après vente
CREATE OR REPLACE FUNCTION fn_generer_recu_auto()
RETURNS TRIGGER AS $$
BEGIN
    -- Insérer automatiquement dans la table recu
    INSERT INTO recu (montant_total, id_vente)
    VALUES (NEW.total_vente, NEW.id_vente);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_generer_recu ON vente;
CREATE TRIGGER trg_generer_recu
AFTER INSERT ON vente
FOR EACH ROW
EXECUTE FUNCTION fn_generer_recu_auto();

-- TRIGGER 5: Vérifier rôle pour les commandes d'achat
CREATE OR REPLACE FUNCTION fn_verif_role_commande()
RETURNS TRIGGER AS $$
DECLARE
    v_role VARCHAR(50);
BEGIN
    SELECT role INTO v_role 
    FROM utilisateur 
    WHERE id_utilisateur = NEW.id_utilisateur;
    
    IF v_role NOT IN ('ADMIN', 'RESPONSABLE_ACHAT') THEN
        RAISE EXCEPTION 'Accès refusé : Seul un Responsable Achats ou un Administrateur peut créer une commande. (Rôle actuel: %)', v_role;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_role_commande ON commande_achat;
CREATE TRIGGER trg_check_role_commande
BEFORE INSERT ON commande_achat
FOR EACH ROW 
EXECUTE FUNCTION fn_verif_role_commande();

-- TRIGGER 6: Mise à jour stock après réception commande
CREATE OR REPLACE FUNCTION fn_maj_stock_reception()
RETURNS TRIGGER AS $$
DECLARE
    rec RECORD;
BEGIN
    -- Seulement si le statut passe à 'RECUE'
    IF NEW.statut = 'RECUE' AND OLD.statut != 'RECUE' THEN
        -- Parcourir toutes les lignes de la commande
        FOR rec IN (
            SELECT lca.id_produit, lca.quantite_commandee, lca.prix_unitaire
            FROM ligne_commande_achat lca
            WHERE lca.id_commande_achat = NEW.id_commande_achat
        )
        LOOP
            -- Mettre à jour le stock
            UPDATE produit
            SET quantite_stock = quantite_stock + rec.quantite_commandee
            WHERE id_produit = rec.id_produit;

            -- Créer un mouvement de stock
            INSERT INTO mouvement_stock (
                date_mouvement, type_mouvement, quantite, id_utilisateur,
                id_produit, id_commande_achat
            ) VALUES (
                CURRENT_TIMESTAMP,
                'ENTREE',
                rec.quantite_commandee,
                NEW.id_utilisateur,
                rec.id_produit,
                NEW.id_commande_achat
            );
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_reception ON commande_achat;
CREATE TRIGGER trg_stock_reception
AFTER UPDATE OF statut ON commande_achat
FOR EACH ROW
EXECUTE FUNCTION fn_maj_stock_reception();