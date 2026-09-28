-- Schéma du module Catalogue & Stocks (SQLite)
CREATE TABLE IF NOT EXISTS categorie (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS produit (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom          TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    prix         INTEGER NOT NULL CHECK (prix >= 0),          -- en FCFA (pas de centimes)
    image        TEXT,
    categorie_id INTEGER NOT NULL REFERENCES categorie(id)
);

-- Le stock est séparé du produit : il change souvent, la fiche produit non.
CREATE TABLE IF NOT EXISTS stock (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    produit_id   INTEGER NOT NULL UNIQUE REFERENCES produit(id) ON DELETE CASCADE,
    quantite     INTEGER NOT NULL DEFAULT 0 CHECK (quantite >= 0),   -- jamais négatif
    seuil_alerte INTEGER NOT NULL DEFAULT 5 CHECK (seuil_alerte >= 0),
    date_maj     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Historique des mouvements de stock
CREATE TABLE IF NOT EXISTS mouvement (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    produit_id INTEGER NOT NULL REFERENCES produit(id) ON DELETE CASCADE,
    type       TEXT NOT NULL CHECK (type IN ('entree', 'sortie')),
    quantite   INTEGER NOT NULL CHECK (quantite > 0),
    date       TEXT NOT NULL DEFAULT (datetime('now')),
    auteur     TEXT NOT NULL
);

-- Journal d'audit (traçabilité : ajout, modification, suppression, alertes)
CREATE TABLE IF NOT EXISTS journal (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT NOT NULL DEFAULT (datetime('now')),
    auteur    TEXT NOT NULL,
    action    TEXT NOT NULL,
    entite    TEXT NOT NULL,
    entite_id INTEGER,
    detail    TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_produit_nom       ON produit(nom);
CREATE INDEX IF NOT EXISTS idx_produit_categorie ON produit(categorie_id);
CREATE INDEX IF NOT EXISTS idx_mouvement_produit ON mouvement(produit_id);
