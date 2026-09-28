"""Test de performance : recherche sur 1000 produits en moins de 300 ms (rapport, section 2.3)."""
import time

from app.services import produits
from tests.base import BaseTest


class TestPerformance(BaseTest):
    def test_recherche_sur_1000_produits_sous_300_ms(self):
        cid = self.id_categorie("Électronique")
        for i in range(994):  # 6 produits du jeu de données + 994 = 1000
            produits.ajouter_produit(self.conn, f"Produit générique {i}", "", 1000 + i, cid, 10)
        self.assertEqual(produits.rechercher(self.conn)["total"], 1000)
        debut = time.perf_counter()
        r = produits.rechercher(self.conn, q="casque")
        duree = time.perf_counter() - debut
        self.assertEqual(r["total"], 1)
        self.assertLess(duree, 0.3, f"recherche trop lente : {duree * 1000:.0f} ms")
