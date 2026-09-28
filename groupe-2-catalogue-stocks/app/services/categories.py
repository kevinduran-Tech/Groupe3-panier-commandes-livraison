"""Logique métier des catégories."""
import sqlite3

from .. import validators as v
from ..db import transaction
from ..errors import Conflit, NonTrouve
from .journal import journaliser


def lister(conn):
    lignes = conn.execute(
        "SELECT c.id, c.nom, c.description, COUNT(p.id) AS nb_produits "
        "FROM categorie c LEFT JOIN produit p ON p.categorie_id = c.id "
        "GROUP BY c.id ORDER BY c.nom"
    ).fetchall()
    return [dict(r) for r in lignes]


def obtenir(conn, categorie_id):
    ligne = conn.execute("SELECT * FROM categorie WHERE id = ?", (categorie_id,)).fetchone()
    if ligne is None:
        raise NonTrouve("Catégorie introuvable")
    return dict(ligne)


def creer(conn, nom, description="", auteur="admin"):
    nom = v.texte(nom, "Le nom de la catégorie")
    description = v.texte(description, "La description", obligatoire=False, maxi=v.DESC_MAX)
    try:
        with transaction(conn):
            cur = conn.execute("INSERT INTO categorie (nom, description) VALUES (?, ?)", (nom, description))
            journaliser(conn, auteur, "creation", "categorie", cur.lastrowid, nom)
    except sqlite3.IntegrityError:
        raise Conflit("Une catégorie porte déjà ce nom")
    return obtenir(conn, cur.lastrowid)


def renommer(conn, categorie_id, nom=None, description=None, auteur="admin"):
    actuelle = obtenir(conn, categorie_id)
    nom = v.texte(nom, "Le nom de la catégorie") if nom is not None else actuelle["nom"]
    description = (
        v.texte(description, "La description", obligatoire=False, maxi=v.DESC_MAX)
        if description is not None else actuelle["description"]
    )
    try:
        with transaction(conn):
            conn.execute("UPDATE categorie SET nom = ?, description = ? WHERE id = ?", (nom, description, categorie_id))
            journaliser(conn, auteur, "modification", "categorie", categorie_id, f"{actuelle['nom']} -> {nom}")
    except sqlite3.IntegrityError:
        raise Conflit("Une catégorie porte déjà ce nom")
    return obtenir(conn, categorie_id)


def supprimer(conn, categorie_id, auteur="admin"):
    actuelle = obtenir(conn, categorie_id)
    with transaction(conn):
        nb = conn.execute("SELECT COUNT(*) FROM produit WHERE categorie_id = ?", (categorie_id,)).fetchone()[0]
        if nb > 0:
            raise Conflit("Suppression impossible : la catégorie contient encore des produits")
        conn.execute("DELETE FROM categorie WHERE id = ?", (categorie_id,))
        journaliser(conn, auteur, "suppression", "categorie", categorie_id, actuelle["nom"])
