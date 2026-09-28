"""Routes /api/stock."""
from flask import Blueprint, jsonify

from ..db import get_db
from ..security import admin_requis, auteur
from ..services import stock
from .produits import corps_json

bp = Blueprint("stock", __name__)


@bp.get("/stock/alertes")
def alertes():
    return jsonify(stock.alertes(get_db()))


@bp.get("/stock/<int:produit_id>")
def lire(produit_id):
    return jsonify(stock.lire(get_db(), produit_id))


@bp.post("/stock/<int:produit_id>/mouvement")
@admin_requis
def mouvement(produit_id):
    """Corps : { "variation": -3 } (sortie de 3) ou { "variation": 20 } (entrée de 20).
    Utilisé par le module Commandes (Groupe 3) pour décrémenter le stock à la validation d'une commande."""
    d = corps_json()
    return jsonify(stock.mettre_a_jour_stock(get_db(), produit_id, d.get("variation"), auteur()))


@bp.patch("/stock/<int:produit_id>/seuil")
@admin_requis
def seuil(produit_id):
    d = corps_json()
    return jsonify(stock.definir_seuil(get_db(), produit_id, d.get("seuil_alerte"), auteur()))


@bp.get("/stock/<int:produit_id>/mouvements")
def historique(produit_id):
    return jsonify(stock.mouvements(get_db(), produit_id))
