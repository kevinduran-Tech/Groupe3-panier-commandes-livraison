"""Logique métier des produits : ajout, modification, suppression, recherche paginée."""
import math
import os

from .. import validators as v
from ..db import transaction
from ..errors import ErreurMetier, NonTrouve
from .journal import journaliser

SELECT_PRODUIT = (
    "SELECT p.id, p.nom, p.description, p.prix, p.image, p.categorie_id, "
    "       c.nom AS categorie, s.quantite AS stock, s.seuil_alerte "
    "FROM produit p "
    "JOIN categorie c ON c.id = p.categorie_id "
    "JOIN stock s ON s.produit_id = p.id "
)


def _categorie_existe(conn, categorie_id):
    return conn.execute("SELECT 1 FROM categorie WHERE id = ?", (categorie_id,)).fetchone() is not None


def obtenir(conn, produit_id):
    ligne = conn.execute(SELECT_PRODUIT + "WHERE p.id = ?", (produit_id,)).fetchone()
    if ligne is None:
        raise NonTrouve("Produit introuvable")
    return dict(ligne)


def ajouter_produit(conn, nom, description, prix, categorie_id, quantite_initiale=0,
                    seuil_alerte=5, auteur="admin"):
    # 1. Validation métier avant tout accès en écriture
    nom = v.texte(nom, "Le nom")
    description = v.texte(description, "La description", obligatoire=False, maxi=v.DESC_MAX)
    prix = v.prix(prix)
    categorie_id = v.entier(categorie_id, "La catégorie", 1)
    quantite_initiale = v.entier(quantite_initiale, "La quantité initiale", 0)
    seuil_alerte = v.entier(seuil_alerte, "Le seuil d'alerte", 0)
    if not _categorie_existe(conn, categorie_id):
        raise ErreurMetier("Catégorie inconnue")

    with transaction(conn):
        # 2. Insertion du produit (requêtes préparées : pas d'injection SQL possible)
        cur = conn.execute(
            "INSERT INTO produit (nom, description, prix, categorie_id) VALUES (?, ?, ?, ?)",
            (nom, description, prix, categorie_id),
        )
        produit_id = cur.lastrowid
        # 3. Création automatique de la ligne de stock associée
        conn.execute(
            "INSERT INTO stock (produit_id, quantite, seuil_alerte) VALUES (?, ?, ?)",
            (produit_id, quantite_initiale, seuil_alerte),
        )
        if quantite_initiale > 0:
            conn.execute(
                "INSERT INTO mouvement (produit_id, type, quantite, auteur) VALUES (?, 'entree', ?, ?)",
                (produit_id, quantite_initiale, auteur),
            )
        journaliser(conn, auteur, "creation", "produit", produit_id, f"{nom} (stock initial {quantite_initiale})")
    return obtenir(conn, produit_id)


def modifier_produit(conn, produit_id, champs, auteur="admin"):
    """Mise à jour partielle : seuls les champs fournis sont modifiés."""
    actuel = obtenir(conn, produit_id)
    nom = v.texte(champs["nom"], "Le nom") if "nom" in champs else actuel["nom"]
    description = (
        v.texte(champs["description"], "La description", obligatoire=False, maxi=v.DESC_MAX)
        if "description" in champs else actuel["description"]
    )
    prix = v.prix(champs["prix"]) if "prix" in champs else actuel["prix"]
    categorie_id = actuel["categorie_id"]
    if "categorie_id" in champs:
        categorie_id = v.entier(champs["categorie_id"], "La catégorie", 1)
        if not _categorie_existe(conn, categorie_id):
            raise ErreurMetier("Catégorie inconnue")
    with transaction(conn):
        conn.execute(
            "UPDATE produit SET nom = ?, description = ?, prix = ?, categorie_id = ? WHERE id = ?",
            (nom, description, prix, categorie_id, produit_id),
        )
        detail = f"prix {actuel['prix']} -> {prix}" if prix != actuel["prix"] else f"{actuel['nom']} modifié"
        journaliser(conn, auteur, "modification", "produit", produit_id, detail)
    return obtenir(conn, produit_id)


def supprimer_produit(conn, produit_id, dossier_images=None, auteur="admin"):
    """Supprime le produit ; le stock et les mouvements associés partent en cascade."""
    actuel = obtenir(conn, produit_id)
    with transaction(conn):
        conn.execute("DELETE FROM produit WHERE id = ?", (produit_id,))
        journaliser(conn, auteur, "suppression", "produit", produit_id, actuel["nom"])
    if dossier_images and actuel["image"]:
        try:
            os.remove(os.path.join(dossier_images, actuel["image"]))
        except OSError:
            pass


def definir_image(conn, produit_id, nom_fichier, auteur="admin"):
    obtenir(conn, produit_id)
    with transaction(conn):
        conn.execute("UPDATE produit SET image = ? WHERE id = ?", (nom_fichier, produit_id))
        journaliser(conn, auteur, "modification", "produit", produit_id, f"image = {nom_fichier}")
    return obtenir(conn, produit_id)


def _echapper_like(texte):
    return texte.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def rechercher(conn, q=None, categorie_id=None, disponible=None, page=1, par_page=10, par_page_max=100):
    """Recherche par nom, catégorie et/ou disponibilité, avec pagination."""
    page = max(1, int(page))
    par_page = min(max(1, int(par_page)), par_page_max)
    where, params = [], []
    if q:
        where.append("p.nom LIKE ? ESCAPE '\\'")
        params.append(f"%{_echapper_like(q.strip())}%")
    if categorie_id is not None:
        where.append("p.categorie_id = ?")
        params.append(int(categorie_id))
    if disponible is True:
        where.append("s.quantite > 0")
    elif disponible is False:
        where.append("s.quantite = 0")
    clause = ("WHERE " + " AND ".join(where) + " ") if where else ""

    total = conn.execute(
        "SELECT COUNT(*) FROM produit p JOIN stock s ON s.produit_id = p.id " + clause, params
    ).fetchone()[0]
    lignes = conn.execute(
        SELECT_PRODUIT + clause + "ORDER BY p.nom LIMIT ? OFFSET ?",
        params + [par_page, (page - 1) * par_page],
    ).fetchall()
    return {
        "items": [dict(r) for r in lignes],
        "page": page,
        "par_page": par_page,
        "total": total,
        "pages": max(1, math.ceil(total / par_page)),
    }
