"""Validation et nettoyage des entrées (côté serveur)."""
from .errors import ErreurMetier

NOM_MAX = 120
DESC_MAX = 1000


def texte(valeur, champ, obligatoire=True, maxi=NOM_MAX):
    if valeur is None:
        valeur = ""
    if not isinstance(valeur, str):
        raise ErreurMetier(f"{champ} doit être une chaîne de caractères")
    valeur = valeur.strip()
    if obligatoire and not valeur:
        raise ErreurMetier(f"{champ} est obligatoire")
    if len(valeur) > maxi:
        raise ErreurMetier(f"{champ} est trop long ({maxi} caractères maximum)")
    return valeur


def entier(valeur, champ, minimum=0):
    # bool est un sous-type de int en Python : on l'exclut explicitement
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        raise ErreurMetier(f"{champ} doit être un nombre entier")
    if valeur < minimum:
        raise ErreurMetier(f"{champ} doit être supérieur ou égal à {minimum}")
    return valeur


def prix(valeur):
    if valeur is None:
        raise ErreurMetier("Nom et prix valides sont obligatoires")
    return entier(valeur, "Le prix", 0)
