"""Tests — catégories."""
from app.errors import Conflit
from app.services import categories
from tests.base import BaseTest


class TestCategories(BaseTest):
    def test_suppression_categorie_non_vide_bloquee(self):
        with self.assertRaises(Conflit):
            categories.supprimer(self.conn, self.id_categorie("Électronique"))
        self.assertEqual(len(categories.lister(self.conn)), 3)

    def test_suppression_categorie_vide(self):
        c = categories.creer(self.conn, "Jouets")
        categories.supprimer(self.conn, c["id"])
        self.assertEqual(len(categories.lister(self.conn)), 3)

    def test_renommer(self):
        cid = self.id_categorie("Informatique")
        c = categories.renommer(self.conn, cid, nom="Informatique & Bureautique")
        self.assertEqual(c["nom"], "Informatique & Bureautique")

    def test_nom_en_double_refuse(self):
        with self.assertRaises(Conflit):
            categories.creer(self.conn, "Papeterie")
