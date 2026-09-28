"""Routes /api/produits et /api/images."""
import os

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from .. import images
from ..db import get_db
from ..errors import ErreurMetier
from ..security import admin_requis, auteur
from ..services import produits

bp = Blueprint("produits", __name__)


def corps_json():
    donnees = request.get_json(silent=True)
    if not isinstance(donnees, dict):
        raise ErreurMetier("Corps JSON invalide (objet attendu)")
    return donnees


def _bool(valeur):
    if valeur is None or valeur == "":
        return None
    if valeur.lower() in ("1", "true", "oui"):
        return True
    if valeur.lower() in ("0", "false", "non"):
        return False
    raise ErreurMetier("Le paramètre « disponible » doit valoir true ou false")


def _entier_param(nom, defaut=None):
    brut = request.args.get(nom)
    if brut is None or brut == "":
        return defaut
    try:
        return int(brut)
    except ValueError:
        raise ErreurMetier(f"Le paramètre « {nom} » doit être un entier")


@bp.get("/produits")
def lister():
    cfg = current_app.config
    resultat = produits.rechercher(
        get_db(),
        q=request.args.get("q"),
        categorie_id=_entier_param("categorie_id"),
        disponible=_bool(request.args.get("disponible")),
        page=_entier_param("page", 1),
        par_page=_entier_param("par_page", cfg["PAR_PAGE_DEFAUT"]),
        par_page_max=cfg["PAR_PAGE_MAX"],
    )
    return jsonify(resultat)


@bp.get("/produits/<int:produit_id>")
def detail(produit_id):
    # Contrat d'intégration avec le module Panier/commandes (Groupe 3) : contient « prix » et « stock ».
    return jsonify(produits.obtenir(get_db(), produit_id))


@bp.post("/produits")
@admin_requis
def creer():
    d = corps_json()
    p = produits.ajouter_produit(
        get_db(), d.get("nom"), d.get("description", ""), d.get("prix"), d.get("categorie_id"),
        d.get("quantite_initiale", 0), d.get("seuil_alerte", current_app.config["SEUIL_ALERTE_DEFAUT"]),
        auteur=auteur(),
    )
    return jsonify(p), 201


@bp.route("/produits/<int:produit_id>", methods=["PUT", "PATCH"])
@admin_requis
def modifier(produit_id):
    return jsonify(produits.modifier_produit(get_db(), produit_id, corps_json(), auteur=auteur()))


@bp.delete("/produits/<int:produit_id>")
@admin_requis
def supprimer(produit_id):
    produits.supprimer_produit(get_db(), produit_id, current_app.config["UPLOAD_FOLDER"], auteur=auteur())
    return "", 204


@bp.post("/produits/<int:produit_id>/image")
@admin_requis
def televerser_image(produit_id):
    conn = get_db()
    produits.obtenir(conn, produit_id)  # 404 avant d'écrire quoi que ce soit sur le disque
    ancien = produits.obtenir(conn, produit_id)["image"]
    dossier = current_app.config["UPLOAD_FOLDER"]
    nom = images.enregistrer(request.files.get("image"), dossier)
    p = produits.definir_image(conn, produit_id, nom, auteur=auteur())
    if ancien:
        try:
            os.remove(os.path.join(dossier, ancien))
        except OSError:
            pass
    return jsonify(p)


@bp.get("/images/<nom>")
def servir_image(nom):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], nom)
