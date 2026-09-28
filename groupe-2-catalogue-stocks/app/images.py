"""Gestion des images produit : contrôle du format (JPEG/PNG), de la taille et du contenu réel."""
import os
import uuid

from .errors import ErreurMetier

EXTENSIONS = {"jpg": "jpg", "jpeg": "jpg", "png": "png"}
TAILLE_MAX = 2 * 1024 * 1024
SIGNATURES = {"jpg": b"\xff\xd8\xff", "png": b"\x89PNG\r\n\x1a\n"}


def enregistrer(fichier, dossier):
    """Valide puis enregistre l'image sous un nom aléatoire. Retourne le nom du fichier."""
    if fichier is None or not fichier.filename:
        raise ErreurMetier("Aucun fichier image reçu (champ « image »)")
    extension = fichier.filename.rsplit(".", 1)[-1].lower() if "." in fichier.filename else ""
    if extension not in EXTENSIONS:
        raise ErreurMetier("Format d'image refusé : seuls JPEG et PNG sont acceptés", 415)
    contenu = fichier.read(TAILLE_MAX + 1)
    if len(contenu) > TAILLE_MAX:
        raise ErreurMetier("Fichier trop volumineux (2 Mo maximum)", 413)
    type_reel = EXTENSIONS[extension]
    # On vérifie la signature réelle du fichier : renommer un .exe en .png ne suffit pas.
    if not contenu.startswith(SIGNATURES[type_reel]):
        raise ErreurMetier("Le contenu du fichier ne correspond pas à son extension", 415)
    nom = f"{uuid.uuid4().hex}.{type_reel}"
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, nom), "wb") as f:
        f.write(contenu)
    return nom
