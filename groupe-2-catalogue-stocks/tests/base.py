"""Outils communs aux tests : application jetable avec base temporaire + jeu de données."""
import shutil
import tempfile
import unittest

from app import create_app, db
from app.seed import peupler

CLE = "cle-de-test"
ADMIN = {"x-admin-key": CLE, "x-auteur": "testeur"}


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.mkdtemp()
        self.app = create_app({
            "DATABASE": f"{self.dossier}/test.db",
            "UPLOAD_FOLDER": f"{self.dossier}/uploads",
            "ADMIN_API_KEY": CLE,
            "TESTING": True,
        })
        self.conn = db.connecter(self.app.config["DATABASE"])
        peupler(self.conn)
        self.client = self.app.test_client()

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.dossier, ignore_errors=True)

    def id_produit(self, nom):
        return self.conn.execute("SELECT id FROM produit WHERE nom = ?", (nom,)).fetchone()[0]

    def id_categorie(self, nom):
        return self.conn.execute("SELECT id FROM categorie WHERE nom = ?", (nom,)).fetchone()[0]
