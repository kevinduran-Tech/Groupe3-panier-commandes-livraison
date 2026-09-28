"""Logique métier du stock : mises à jour atomiques, alertes, mouvements."""
import logging

from .. import validators as v
from ..db import transaction
from ..errors import ErreurMetier, NonTrouve
from .journal import journaliser

log = logging.getLogger("catalogue.stock")


def lire(conn, produit_id):
    ligne = conn.execute(
        "SELECT produit_id, quantite, seuil_alerte, date_maj FROM stock WHERE produit_id = ?", (produit_id,)
    ).fetchone()
    if ligne is None:
        raise NonTrouve("Produit introuvable")
    return dict(ligne)


def mettre_a_jour_stock(conn, produit_id, variation, auteur="admin"):
    """Ajoute `variation` (positive = entrée, négative = sortie) au stock d'un produit.

    Toute l'opération se déroule dans une transaction qui verrouille la base :
    une vente et une réception simultanées ne peuvent pas se marcher dessus.
    La quantité ne peut jamais devenir négative."""
    variation = v.entier(variation, "La variation", minimum=-10**9)
    if variation == 0:
        raise ErreurMetier("La variation ne peut pas être nulle")
    with transaction(conn):
        ligne = conn.execute(
            "SELECT quantite, seuil_alerte FROM stock WHERE produit_id = ?", (produit_id,)
        ).fetchone()
        if ligne is None:
            raise NonTrouve("Produit introuvable")
        nouvelle = ligne["quantite"] + variation
        if nouvelle < 0:
            raise ErreurMetier("Stock insuffisant pour cette opération", 409)
        conn.execute(
            "UPDATE stock SET quantite = ?, date_maj = datetime('now') WHERE produit_id = ?",
            (nouvelle, produit_id),
        )
        conn.execute(
            "INSERT INTO mouvement (produit_id, type, quantite, auteur) VALUES (?, ?, ?, ?)",
            (produit_id, "sortie" if variation < 0 else "entree", abs(variation), auteur),
        )
        alerte = nouvelle <= ligne["seuil_alerte"]
        if alerte:
            declencher_alerte(conn, produit_id, nouvelle, auteur)
    return {"produit_id": produit_id, "quantite": nouvelle, "alerte": alerte}


def declencher_alerte(conn, produit_id, quantite, auteur="systeme"):
    """Alerte de stock critique : tracée dans le journal et dans les logs du serveur."""
    detail = f"stock critique : {quantite} unité(s)"
    journaliser(conn, auteur, "alerte_stock", "stock", produit_id, detail)
    log.warning("ALERTE produit %s : %s", produit_id, detail)


def definir_seuil(conn, produit_id, seuil, auteur="admin"):
    seuil = v.entier(seuil, "Le seuil d'alerte", 0)
    with transaction(conn):
        cur = conn.execute("UPDATE stock SET seuil_alerte = ? WHERE produit_id = ?", (seuil, produit_id))
        if cur.rowcount == 0:
            raise NonTrouve("Produit introuvable")
        journaliser(conn, auteur, "modification", "stock", produit_id, f"seuil_alerte = {seuil}")
    return lire(conn, produit_id)


def alertes(conn):
    """Produits dont le stock est au niveau du seuil ou en dessous (rupture incluse)."""
    lignes = conn.execute(
        "SELECT p.id AS produit_id, p.nom, s.quantite, s.seuil_alerte, "
        "       CASE WHEN s.quantite = 0 THEN 'rupture' ELSE 'critique' END AS niveau "
        "FROM stock s JOIN produit p ON p.id = s.produit_id "
        "WHERE s.quantite <= s.seuil_alerte ORDER BY s.quantite, p.nom"
    ).fetchall()
    return [dict(r) for r in lignes]


def mouvements(conn, produit_id, limite=100):
    lire(conn, produit_id)  # 404 si le produit n'existe pas
    lignes = conn.execute(
        "SELECT * FROM mouvement WHERE produit_id = ? ORDER BY id DESC LIMIT ?", (produit_id, limite)
    ).fetchall()
    return [dict(r) for r in lignes]
