-- ============================================
-- VUES ADAPTÉES AU SCHÉMA DE GESTION MAGASIN
-- ============================================

-- Vue 1: Produits disponibles pour le caissier
CREATE OR REPLACE VIEW vue_produits_disponibles AS
SELECT 
    p.id_produit,
    p.nom_produit AS nom,
    p.prix_unitaire,
    p.quantite_stock
FROM produit p
WHERE p.quantite_stock > 0 AND p.statut = 'ACTIF'
ORDER BY p.nom_produit;

-- Vue 2: État du stock pour le gestionnaire
CREATE OR REPLACE VIEW vue_etat_stock AS
SELECT 
    p.id_produit,
    p.nom_produit AS nom,
    c.nom_categorie AS categorie,
    p.quantite_stock,
    COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) AS seuil_min,
    CASE 
        WHEN p.quantite_stock <= 0 THEN 'RUPTURE'
        WHEN p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) THEN 'ALERTE'
        ELSE 'NORMAL'
    END AS etat
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
ORDER BY p.quantite_stock ASC;

-- Vue 3: Ventes du jour pour le caissier
CREATE OR REPLACE VIEW vue_ventes_jour AS
SELECT 
    v.id_vente,
    v.date_vente AS date,
    u.nom AS vendeur,
    COUNT(DISTINCT lv.id_produit) AS nb_produits,
    SUM(lv.quantite_vendue) AS total_articles,
    SUM(lv.quantite_vendue * lv.prix_unitaire) AS total
FROM vente v
JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
WHERE DATE(v.date_vente) = CURRENT_DATE
GROUP BY v.id_vente, v.date_vente, u.nom
ORDER BY v.date_vente DESC;

-- Vue 4: Mouvements récents pour le gestionnaire
CREATE OR REPLACE VIEW vue_mouvements_recents AS
SELECT 
    m.date_mouvement AS date,
    p.nom_produit AS produit,
    m.type_mouvement AS type,
    m.quantite,
    CASE 
        WHEN m.id_vente IS NOT NULL THEN 'VENTE'
        WHEN m.id_commande_achat IS NOT NULL THEN 'COMMANDE'
        ELSE 'AJUSTEMENT'
    END AS source,
    '' AS commentaire  -- Vous n'avez pas de colonne commentaire, mais on garde la structure
FROM mouvement_stock m
JOIN produit p ON m.id_produit = p.id_produit
ORDER BY m.date_mouvement DESC
LIMIT 100;

-- Vue 5: Alertes stock et besoins réapprovisionnement
CREATE OR REPLACE VIEW vue_alertes_stock AS
SELECT 
    p.id_produit,
    p.nom_produit AS nom,
    c.nom_categorie AS categorie,
    f.nom_fournisseur AS fournisseur_principal,
    p.quantite_stock,
    COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) AS seuil_min,
    (COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) * 2 - p.quantite_stock) AS quantite_a_commander,
    CASE 
        WHEN p.quantite_stock <= 0 THEN 'RUPTURE'
        WHEN p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) THEN 'CRITIQUE'
        ELSE 'NORMAL'
    END AS niveau_urgence
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
LEFT JOIN produit_fournisseur pf ON p.id_produit = pf.id_produit
LEFT JOIN fournisseur f ON pf.id_fournisseur = f.id_fournisseur
WHERE p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut)
ORDER BY p.quantite_stock ASC;

-- Vue 6: Performance des vendeurs et caissiers
CREATE OR REPLACE VIEW vue_performance_vendeurs AS
SELECT 
    u.id_utilisateur,
    u.nom,
    u.role,
    u.email,
    COUNT(DISTINCT v.id_vente) AS nb_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS articles_vendus,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    CASE 
        WHEN COUNT(DISTINCT v.id_vente) > 0 
        THEN COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) / COUNT(DISTINCT v.id_vente)
        ELSE 0
    END AS panier_moyen,
    MIN(v.date_vente) AS premiere_vente,
    MAX(v.date_vente) AS derniere_vente
FROM utilisateur u
LEFT JOIN vente v ON u.id_utilisateur = v.id_utilisateur
LEFT JOIN ligne_vente lv ON v.id_vente = lv.id_vente
WHERE u.role IN ('CAISSIER', 'ADMIN', 'GESTIONNAIRE_STOCK', 'RESPONSABLE_ACHAT')
GROUP BY u.id_utilisateur, u.nom, u.role, u.email
ORDER BY chiffre_affaires DESC;

-- Vue 7: Top 10 produits par CA
CREATE OR REPLACE VIEW vue_top_produits AS
SELECT 
    p.id_produit,
    p.nom_produit AS nom,
    c.nom_categorie AS categorie,
    SUM(lv.quantite_vendue) AS quantite_vendue,
    SUM(lv.quantite_vendue * lv.prix_unitaire) AS chiffre_affaires,
    SUM(lv.quantite_vendue * lv.prix_unitaire) AS marge_totale,  -- À adapter si vous avez prix d'achat
    AVG(lv.prix_unitaire) AS marge_unitaire,  -- À adapter
    CASE 
        WHEN SUM(lv.quantite_vendue * lv.prix_unitaire) > 0
        THEN 100  -- Taux marge à calculer si vous avez prix d'achat
        ELSE 0
    END AS taux_marge_pourcent
FROM produit p
JOIN ligne_vente lv ON p.id_produit = lv.id_produit
JOIN categorie c ON p.id_categorie = c.id_categorie
GROUP BY p.id_produit, p.nom_produit, c.nom_categorie
ORDER BY chiffre_affaires DESC
LIMIT 10;

-- Vue 8: Performance périodique (mensuelle)
CREATE OR REPLACE VIEW vue_performance_periodique AS
SELECT 
    EXTRACT(YEAR FROM v.date_vente) AS annee,
    EXTRACT(MONTH FROM v.date_vente) AS mois,
    COUNT(DISTINCT v.id_vente) AS nb_ventes,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    COALESCE(SUM(lv.quantite_vendue), 0) AS total_articles_vendus,
    CASE 
        WHEN COUNT(DISTINCT v.id_vente) > 0 
        THEN COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) / COUNT(DISTINCT v.id_vente)
        ELSE 0
    END AS panier_moyen
FROM vente v
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
GROUP BY EXTRACT(YEAR FROM v.date_vente), EXTRACT(MONTH FROM v.date_vente)
ORDER BY annee DESC, mois DESC;

-- Vue 9: Ticket de caisse (détail vente)
CREATE OR REPLACE VIEW vue_ticket_vente AS
SELECT 
    v.id_vente,
    v.date_vente,
    u.nom AS vendeur,
    p.nom_produit AS produit,
    lv.quantite_vendue,
    lv.prix_unitaire,
    lv.quantite_vendue * lv.prix_unitaire AS total_ligne
FROM vente v
JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
JOIN produit p ON lv.id_produit = p.id_produit
ORDER BY v.date_vente DESC, v.id_vente, p.nom_produit;

-- Vue 10: Interface de vente rapide
CREATE OR REPLACE VIEW vue_vente_rapide AS
SELECT 
    p.id_produit,
    p.nom_produit AS nom,
    p.prix_unitaire AS prix,
    p.quantite_stock,
    c.nom_categorie AS categorie
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
WHERE p.quantite_stock > 0 AND p.statut = 'ACTIF'
ORDER BY c.nom_categorie, p.nom_produit;

-- Vue 11: Tableau de bord admin (SIMPLIFIÉ)
CREATE OR REPLACE VIEW vue_tableau_bord_admin AS
WITH 
stats_ventes AS (
    SELECT 
        COUNT(DISTINCT CASE WHEN DATE(v.date_vente) = CURRENT_DATE THEN v.id_vente END) AS ventes_aujourdhui,
        COALESCE(SUM(CASE WHEN DATE(v.date_vente) = CURRENT_DATE THEN v.total_vente END), 0) AS ca_aujourdhui,
        COUNT(DISTINCT CASE WHEN DATE(v.date_vente) = CURRENT_DATE - 1 THEN v.id_vente END) AS ventes_hier,
        COALESCE(SUM(CASE WHEN DATE(v.date_vente) = CURRENT_DATE - 1 THEN v.total_vente END), 0) AS ca_hier,
        COUNT(DISTINCT CASE WHEN EXTRACT(MONTH FROM v.date_vente) = EXTRACT(MONTH FROM CURRENT_DATE) 
                            AND EXTRACT(YEAR FROM v.date_vente) = EXTRACT(YEAR FROM CURRENT_DATE) 
                            THEN v.id_vente END) AS ventes_ce_mois,
        COALESCE(SUM(CASE WHEN EXTRACT(MONTH FROM v.date_vente) = EXTRACT(MONTH FROM CURRENT_DATE) 
                          AND EXTRACT(YEAR FROM v.date_vente) = EXTRACT(YEAR FROM CURRENT_DATE) 
                          THEN v.total_vente END), 0) AS ca_ce_mois,
        COUNT(DISTINCT v.id_vente) AS ventes_total,
        COALESCE(SUM(v.total_vente), 0) AS ca_total
    FROM vente v
),
stats_stock AS (
    SELECT 
        COUNT(*) AS total_produits,
        SUM(CASE WHEN p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) 
                  AND p.quantite_stock > 0 THEN 1 ELSE 0 END) AS produits_alerte,
        SUM(CASE WHEN p.quantite_stock = 0 THEN 1 ELSE 0 END) AS produits_rupture,
        SUM(p.quantite_stock) AS total_articles_stock,
        COALESCE(SUM(p.quantite_stock * p.prix_unitaire), 0) AS valeur_stock_vente
    FROM produit p
    JOIN categorie c ON p.id_categorie = c.id_categorie
),
stats_achats AS (
    SELECT 
        COUNT(DISTINCT ca.id_commande_achat) AS achats_en_attente,
        COALESCE(SUM(lca.quantite_commandee * lca.prix_unitaire), 0) AS valeur_achats_attente
    FROM commande_achat ca
    JOIN ligne_commande_achat lca ON ca.id_commande_achat = lca.id_commande_achat
    WHERE ca.statut = 'EN_COURS'
)
SELECT 
    sv.ca_aujourdhui,
    sv.ca_hier,
    sv.ca_ce_mois,
    sv.ca_total,
    CASE 
        WHEN sv.ca_hier > 0 
        THEN ROUND(((sv.ca_aujourdhui - sv.ca_hier) / sv.ca_hier * 100), 2)
        ELSE 0 
    END AS evolution_ca_pourcent,
    sv.ventes_aujourdhui,
    sv.ventes_hier,
    sv.ventes_ce_mois,
    sv.ventes_total,
    CASE 
        WHEN sv.ventes_aujourdhui > 0 
        THEN ROUND(sv.ca_aujourdhui / sv.ventes_aujourdhui, 2)
        ELSE 0 
    END AS panier_moyen_aujourdhui,
    ss.total_produits,
    ss.produits_alerte,
    ss.produits_rupture,
    ss.total_articles_stock,
    ss.valeur_stock_vente,
    sa.achats_en_attente,
    sa.valeur_achats_attente
FROM stats_ventes sv, stats_stock ss, stats_achats sa;

-- Vue 12: CA par heure (pour graphique)
CREATE OR REPLACE VIEW vue_ca_par_heure AS
SELECT 
    EXTRACT(HOUR FROM v.date_vente) AS heure,
    COUNT(DISTINCT v.id_vente) AS nombre_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS articles_vendus,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    CASE 
        WHEN COUNT(DISTINCT v.id_vente) > 0
        THEN COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) / COUNT(DISTINCT v.id_vente)
        ELSE 0
    END AS panier_moyen
FROM vente v
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
WHERE DATE(v.date_vente) = CURRENT_DATE
GROUP BY EXTRACT(HOUR FROM v.date_vente)
ORDER BY heure;

-- Vue 13: CA par jour des 30 derniers jours
CREATE OR REPLACE VIEW vue_ca_30_derniers_jours AS
SELECT 
    DATE(v.date_vente) AS date,
    COUNT(DISTINCT v.id_vente) AS nombre_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS articles_vendus,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    CASE 
        WHEN COUNT(DISTINCT v.id_vente) > 0 
        THEN COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) / COUNT(DISTINCT v.id_vente)
        ELSE 0
    END AS panier_moyen
FROM vente v
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
WHERE v.date_vente >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(v.date_vente)
ORDER BY date DESC;

-- Vue 14: CA par catégorie
CREATE OR REPLACE VIEW vue_ca_par_categorie AS
SELECT 
    c.id_categorie,
    c.nom_categorie AS categorie,
    COUNT(DISTINCT v.id_vente) AS nombre_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS articles_vendus,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    CASE 
        WHEN (SELECT COALESCE(SUM(lv2.quantite_vendue * lv2.prix_unitaire), 0) FROM ligne_vente lv2) > 0
        THEN ROUND(COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) * 100.0 / 
                   (SELECT COALESCE(SUM(lv2.quantite_vendue * lv2.prix_unitaire), 0) FROM ligne_vente lv2), 2)
        ELSE 0
    END AS pourcentage_ca
FROM categorie c
JOIN produit p ON c.id_categorie = p.id_categorie
JOIN ligne_vente lv ON p.id_produit = lv.id_produit
JOIN vente v ON lv.id_vente = v.id_vente
GROUP BY c.id_categorie, c.nom_categorie
ORDER BY chiffre_affaires DESC;

-- Vue 15: Alertes critiques pour admin
CREATE OR REPLACE VIEW vue_alertes_critiques AS
SELECT 
    'STOCK' AS type_alerte,
    p.id_produit,
    p.nom_produit AS produit,
    c.nom_categorie AS categorie,
    p.quantite_stock,
    COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) AS seuil_min,
    CASE 
        WHEN p.quantite_stock = 0 THEN 'RUPTURE DE STOCK'
        ELSE 'STOCK CRITIQUE'
    END AS message,
    'Reapprovisionnement urgent' AS action_recommandee
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
WHERE p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut)
UNION ALL
SELECT 
    'COMMANDE' AS type_alerte,
    NULL AS id_produit,
    'Commande #' || ca.id_commande_achat AS produit,
    f.nom_fournisseur AS categorie,
    NULL AS quantite_stock,
    NULL AS seuil_min,
    'Commande en attente depuis ' || EXTRACT(DAY FROM CURRENT_TIMESTAMP - ca.date_commande) || ' jours' AS message,
    'Réceptionner la commande' AS action_recommandee
FROM commande_achat ca
JOIN fournisseur f ON ca.id_fournisseur = f.id_fournisseur
WHERE ca.statut = 'EN_COURS' AND ca.date_commande < CURRENT_TIMESTAMP - INTERVAL '3 days'
ORDER BY type_alerte, quantite_stock;

-- Vue 16: Besoins en réapprovisionnement détaillés
CREATE OR REPLACE VIEW vue_besoin_reappro AS
SELECT DISTINCT ON (p.id_produit)
    p.id_produit,
    p.nom_produit AS produit,
    p.quantite_stock,
    COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) AS seuil_min,
    (COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut) * 3) - p.quantite_stock AS quantite_suggeree,
    COALESCE(f.nom_fournisseur, 'AUCUN FOURNISSEUR') AS fournisseur_principal
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
LEFT JOIN produit_fournisseur pf ON p.id_produit = pf.id_produit
LEFT JOIN fournisseur f ON pf.id_fournisseur = f.id_fournisseur
WHERE p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut)
ORDER BY p.id_produit;

-- Vue 17: Journal complet des mouvements de stock
CREATE OR REPLACE VIEW vue_journal_mouvements AS
SELECT 
    m.id_mouvement,
    m.date_mouvement,
    m.type_mouvement AS type,
    p.nom_produit AS produit,
    m.quantite,
    u.nom AS utilisateur,
    u.role AS role_utilisateur,
    CASE 
        WHEN m.id_vente IS NOT NULL THEN 'Vente #' || m.id_vente
        WHEN m.id_commande_achat IS NOT NULL THEN 'Commande #' || m.id_commande_achat
        ELSE 'Manuel'
    END AS operation
FROM mouvement_stock m
JOIN produit p ON m.id_produit = p.id_produit
JOIN utilisateur u ON m.id_utilisateur = u.id_utilisateur
ORDER BY m.date_mouvement DESC;

-- ============================================
-- VUES MATÉRIALISÉES (rafraîchir 1x/jour)
-- ============================================

-- Vue matérialisée 1: Stats annuelles
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stats_annuelles AS
SELECT 
    EXTRACT(YEAR FROM v.date_vente) AS annee,
    COUNT(DISTINCT v.id_vente) AS nb_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS articles_vendus,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires
FROM vente v
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
GROUP BY EXTRACT(YEAR FROM v.date_vente)
ORDER BY annee DESC;

-- Vue matérialisée 2: Stats historiques journalières
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stats_historiques AS
SELECT 
    DATE(v.date_vente) AS date_vente,
    EXTRACT(YEAR FROM v.date_vente) AS annee,
    EXTRACT(MONTH FROM v.date_vente) AS mois,
    EXTRACT(DAY FROM v.date_vente) AS jour,
    COUNT(DISTINCT v.id_vente) AS nb_ventes,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires
FROM vente v
JOIN ligne_vente lv ON v.id_vente = lv.id_vente
GROUP BY DATE(v.date_vente), EXTRACT(YEAR FROM v.date_vente), EXTRACT(MONTH FROM v.date_vente), EXTRACT(DAY FROM v.date_vente)
ORDER BY date_vente DESC;

-- Vue matérialisée 3: Stats produits (pour rapports)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stats_produits AS
SELECT 
    p.id_produit,
    p.nom_produit,
    c.nom_categorie,
    COUNT(DISTINCT lv.id_vente) AS nb_ventes,
    COALESCE(SUM(lv.quantite_vendue), 0) AS total_vendu,
    COALESCE(SUM(lv.quantite_vendue * lv.prix_unitaire), 0) AS chiffre_affaires,
    p.quantite_stock AS stock_actuel
FROM produit p
JOIN categorie c ON p.id_categorie = c.id_categorie
LEFT JOIN ligne_vente lv ON p.id_produit = lv.id_produit
GROUP BY p.id_produit, p.nom_produit, c.nom_categorie, p.quantite_stock
ORDER BY chiffre_affaires DESC;

-- ============================================
-- FONCTIONS POUR RAFRAÎCHIR LES VUES
-- ============================================

CREATE OR REPLACE FUNCTION rafraichir_vues_materialisees()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_stats_annuelles;
    REFRESH MATERIALIZED VIEW mv_stats_historiques;
    REFRESH MATERIALIZED VIEW mv_stats_produits;
    RAISE NOTICE 'Vues matérialisées rafraîchies avec succès';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMMENTAIRES SUR LES VUES (documentation)
-- ============================================

COMMENT ON VIEW vue_produits_disponibles IS 'Produits en stock pour interface de vente';
COMMENT ON VIEW vue_etat_stock IS 'État du stock avec alertes';
COMMENT ON VIEW vue_ventes_jour IS 'Ventes de la journée';
COMMENT ON VIEW vue_tableau_bord_admin IS 'Tableau de bord principal administrateur';
COMMENT ON VIEW vue_ticket_vente IS 'Détail des tickets de caisse';
COMMENT ON VIEW vue_vente_rapide IS 'Interface de vente rapide (produits + prix)';
COMMENT ON VIEW vue_alertes_critiques IS 'Alertes stock et commandes en retard';