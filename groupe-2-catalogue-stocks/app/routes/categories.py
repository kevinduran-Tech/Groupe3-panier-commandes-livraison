"""Routes /api/categories."""
from flask import Blueprint, jsonify

from ..db import get_db
from ..security import admin_requis, auteur
from ..services import categories
from .produits import corps_json

bp = Blueprint("categories", __name__)


@bp.get("/categories")
def lister():
    return jsonify(categories.lister(get_db()))


@bp.post("/categories")
@admin_requis
def creer():
    d = corps_json()
    return jsonify(categories.creer(get_db(), d.get("nom"), d.get("description", ""), auteur())), 201


@bp.route("/categories/<int:categorie_id>", methods=["PUT", "PATCH"])
@admin_requis
def renommer(categorie_id):
    d = corps_json()
    return jsonify(categories.renommer(get_db(), categorie_id, d.get("nom"), d.get("description"), auteur()))


@bp.delete("/categories/<int:categorie_id>")
@admin_requis
def supprimer(categorie_id):
    categories.supprimer(get_db(), categorie_id, auteur())
    return "", 204
