"""Contrôle d'accès : écriture réservée aux administrateurs (clé d'API), lecture ouverte."""
import hmac
from functools import wraps

from flask import current_app, request

from .errors import ErreurMetier


def admin_requis(fonction):
    """Exige l'en-tête `x-admin-key`. L'en-tête optionnel `x-auteur` identifie qui agit
    (utilisé pour la traçabilité) ; par défaut « admin »."""
    @wraps(fonction)
    def enveloppe(*args, **kwargs):
        fournie = request.headers.get("x-admin-key", "")
        attendue = current_app.config["ADMIN_API_KEY"]
        if not fournie:
            raise ErreurMetier("Authentification requise (en-tête x-admin-key)", 401)
        if not hmac.compare_digest(fournie.encode(), attendue.encode()):
            raise ErreurMetier("Accès réservé aux administrateurs", 403)
        return fonction(*args, **kwargs)
    return enveloppe


def auteur():
    return (request.headers.get("x-auteur") or "admin").strip()[:60] or "admin"
