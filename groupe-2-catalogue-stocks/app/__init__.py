"""Module Groupe 2 — Catalogue de produits et gestion des stocks (Flask + SQLite)."""
import os

from flask import Flask, jsonify, send_from_directory

from . import db
from .config import Config
from .errors import ErreurMetier


def create_app(config=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    conn = db.connecter(app.config["DATABASE"])
    db.init_schema(conn)
    conn.close()
    app.teardown_appcontext(db.fermer_db)

    from .routes import categories, journal, produits, stock
    for module in (produits, categories, stock, journal):
        app.register_blueprint(module.bp, url_prefix="/api")

    @app.get("/")
    def accueil():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"statut": "ok", "module": "catalogue-stocks"})

    @app.errorhandler(ErreurMetier)
    def erreur_metier(e):
        return jsonify({"erreur": e.message}), e.code

    @app.errorhandler(404)
    def non_trouve(_e):
        return jsonify({"erreur": "Ressource introuvable"}), 404

    @app.errorhandler(405)
    def methode(_e):
        return jsonify({"erreur": "Méthode non autorisée"}), 405

    @app.errorhandler(413)
    def trop_gros(_e):
        return jsonify({"erreur": "Fichier trop volumineux (2 Mo maximum)"}), 413

    @app.errorhandler(500)
    def erreur_serveur(_e):
        return jsonify({"erreur": "Erreur interne du serveur"}), 500

    return app
