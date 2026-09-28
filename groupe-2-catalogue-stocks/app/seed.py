"""Jeu de données de démonstration (identique à celui du rapport et de la présentation).

Usage :  python -m app.seed
"""
from . import db
from .config import Config
from .services import categories, produits

DONNEES = [
    # (catégorie, produit, prix FCFA, stock, seuil d'alerte)
    ("Électronique", "Casque audio Bluetooth JBL", 22000, 37, 5),
    ("Électronique", "Chargeur rapide 20W", 6500, 80, 10),
    ("Informatique", "Clé USB 32 Go", 3000, 120, 15),
    ("Informatique", "Souris optique sans fil", 8500, 4, 5),
    ("Papeterie", "Ramette de papier A4", 4000, 60, 10),
    ("Papeterie", "Cahier 200 pages", 1200, 0, 10),
]


def peupler(conn):
    """Insère le jeu de données si le catalogue est vide. Retourne le nombre de produits ajoutés."""
    if conn.execute("SELECT COUNT(*) FROM produit").fetchone()[0] > 0:
        return 0
    ids = {}
    for nom_cat, nom, prix, stock, seuil in DONNEES:
        if nom_cat not in ids:
            ids[nom_cat] = categories.creer(conn, nom_cat, auteur="seed")["id"]
        produits.ajouter_produit(conn, nom, "", prix, ids[nom_cat], stock, seuil, auteur="seed")
    return len(DONNEES)


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    conn = db.connecter(Config.DATABASE)
    db.init_schema(conn)
    n = peupler(conn)
    print(f"{n} produit(s) de démonstration ajouté(s)." if n else "Le catalogue contient déjà des produits.")
