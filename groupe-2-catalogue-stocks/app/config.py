"""Configuration du module (valeurs surchargées par les variables d'environnement / .env)."""
import os

try:  # python-dotenv est optionnel : on charge .env s'il est installé
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    DATABASE = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "instance", "catalogue.db"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024          # taille maximale d'une image : 2 Mo
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "changez-moi-en-production")
    SEUIL_ALERTE_DEFAUT = 5
    PAR_PAGE_DEFAUT = 10
    PAR_PAGE_MAX = 100
