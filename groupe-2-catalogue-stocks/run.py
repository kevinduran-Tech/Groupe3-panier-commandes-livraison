"""Point d'entrée du module Groupe 2 — Catalogue de produits et gestion des stocks."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")), debug=True)
