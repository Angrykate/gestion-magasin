-- ========================
-- RESET DES TABLES (DEV)
-- ========================
DROP TABLE IF EXISTS
    recu,
    mouvement_stock,
    produit_fournisseur,
    ligne_commande_achat,
    ligne_vente,
    commande_achat,
    vente,
    produit,
    fournisseur,
    utilisateur,
    categorie
CASCADE;

-- ========================
-- TABLE CATEGORIE
-- ========================
CREATE TABLE categorie (
    id_categorie SERIAL PRIMARY KEY,
    nom_categorie VARCHAR(100) NOT NULL,
	seuil_min_defaut INTEGER NOT NULL CHECK (seuil_min_defaut >= 0),
    description TEXT
);

-- ========================
-- TABLE UTILISATEUR
-- ========================
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- ========================
-- TABLE FOURNISSEUR
-- ========================
CREATE TABLE fournisseur (
    id_fournisseur SERIAL PRIMARY KEY,
    nom_fournisseur VARCHAR(150) NOT NULL,
    adresse_fournisseur TEXT
);

-- ========================
-- TABLE PRODUIT
-- ========================
CREATE TABLE produit (
    id_produit SERIAL PRIMARY KEY,
    nom_produit VARCHAR(150) NOT NULL,
    description TEXT,
    prix_unitaire NUMERIC(10,2) NOT NULL CHECK (prix_unitaire > 0),
    date_ajout DATE NOT NULL DEFAULT CURRENT_DATE,
    id_categorie INT NOT NULL,
	quantite_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantite_stock >= 0),
	seuil_min_personnalise INTEGER CHECK (seuil_min_personnalise >= 0),
	statut VARCHAR(20) CHECK (statut IN ('ACTIF', 'INACTIF')) DEFAULT 'ACTIF',
    CONSTRAINT fk_produit_categorie
        FOREIGN KEY (id_categorie)
        REFERENCES categorie(id_categorie)
);

-- ========================
-- TABLE VENTE
-- ========================
CREATE TABLE vente (
    id_vente SERIAL PRIMARY KEY,
    date_vente TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_vente NUMERIC(10,2),
    id_utilisateur INT NOT NULL,
    CONSTRAINT fk_vente_utilisateur
        FOREIGN KEY (id_utilisateur)
        REFERENCES utilisateur(id_utilisateur)
);

-- ========================
-- TABLE COMMANDE_ACHAT
-- ========================
CREATE TABLE commande_achat (
    id_commande_achat SERIAL PRIMARY KEY,
    date_commande DATE NOT NULL DEFAULT CURRENT_DATE,
    statut VARCHAR(50) CHECK (statut IN ('EN_COURS', 'RECUE','ANNULEE')) DEFAULT 'EN_COURS',
    id_fournisseur INT NOT NULL,
    id_utilisateur INT NOT NULL,
    CONSTRAINT fk_commande_fournisseur
        FOREIGN KEY (id_fournisseur)
        REFERENCES fournisseur(id_fournisseur),
    CONSTRAINT fk_commande_utilisateur
        FOREIGN KEY (id_utilisateur)
        REFERENCES utilisateur(id_utilisateur)
);

-- ========================
-- TABLE LIGNE_VENTE
-- ========================
CREATE TABLE ligne_vente (
    id_vente INT NOT NULL,
    id_produit INT NOT NULL,
    quantite_vendue INT NOT NULL CHECK (quantite_vendue > 0),
    prix_unitaire NUMERIC(10,2) NOT NULL CHECK (prix_unitaire > 0),
    PRIMARY KEY (id_vente, id_produit),
    CONSTRAINT fk_lignevente_vente
        FOREIGN KEY (id_vente)
        REFERENCES vente(id_vente),
    CONSTRAINT fk_lignevente_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
);

-- ========================
-- TABLE LIGNE_COMMANDE_ACHAT
-- ========================
CREATE TABLE ligne_commande_achat (
    id_commande_achat INT NOT NULL,
    id_produit INT NOT NULL,
    quantite_commandee INT NOT NULL CHECK (quantite_commandee > 0),
    prix_unitaire NUMERIC(10,2) NOT NULL CHECK (prix_unitaire > 0),
    PRIMARY KEY (id_commande_achat, id_produit),
    CONSTRAINT fk_lignecommande_commande
        FOREIGN KEY (id_commande_achat)
        REFERENCES commande_achat(id_commande_achat),
    CONSTRAINT fk_lignecommande_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit)
);

-- ========================
-- TABLE PRODUIT_FOURNISSEUR
-- ========================
CREATE TABLE produit_fournisseur (
    id_produit INT NOT NULL,
    id_fournisseur INT NOT NULL,
    PRIMARY KEY (id_produit, id_fournisseur),
    CONSTRAINT fk_pf_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit),
    CONSTRAINT fk_pf_fournisseur
        FOREIGN KEY (id_fournisseur)
        REFERENCES fournisseur(id_fournisseur)
);


-- ========================
-- TABLE MOUVEMENT_STOCK
-- ========================
CREATE TABLE mouvement_stock (
    id_mouvement SERIAL PRIMARY KEY,
    date_mouvement TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type_mouvement VARCHAR(20) NOT NULL,
    quantite INT NOT NULL CHECK (quantite > 0),
    id_produit INT NOT NULL,
    id_utilisateur INT NOT NULL,
    id_vente INT,
    id_commande_achat INT,
    CONSTRAINT fk_mouvement_produit
        FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit),
    CONSTRAINT fk_mouvement_utilisateur
        FOREIGN KEY (id_utilisateur)
        REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT fk_mouvement_vente
        FOREIGN KEY (id_vente)
        REFERENCES vente(id_vente),
    CONSTRAINT fk_mouvement_commande
        FOREIGN KEY (id_commande_achat)
        REFERENCES commande_achat(id_commande_achat)
);

-- ========================
-- TABLE RECU
-- ========================
CREATE TABLE recu (
    id_recu SERIAL PRIMARY KEY,
    date_recu TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    montant_total NUMERIC(10,2) NOT NULL CHECK (montant_total >= 0),
    id_vente INT UNIQUE NOT NULL,
    CONSTRAINT fk_recu_vente
        FOREIGN KEY (id_vente)
        REFERENCES vente(id_vente)
);

-- INDEX

CREATE INDEX idx_vente_date ON vente(date_vente);
CREATE INDEX idx_mouvement_date ON mouvement_stock(date_mouvement);
CREATE INDEX idx_produit_categorie ON produit(id_categorie);
CREATE INDEX idx_commande_statut ON commande_achat(statut);
