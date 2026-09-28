"""Tests — stock : mise à jour, alertes, journalisation, concurrence."""
import threading

from app import db
from app.errors import ErreurMetier
from app.services import produits, stock
from tests.base import BaseTest


class TestStock(BaseTest):
    def test_vente_de_3_casques(self):
        pid = self.id_produit("Casque audio Bluetooth JBL")
        r = stock.mettre_a_jour_stock(self.conn, pid, -3, "testeur")
        self.assertEqual(r["quantite"], 34)  # 37 -> 34
        self.assertFalse(r["alerte"])
        mvts = stock.mouvements(self.conn, pid)
        self.assertEqual((mvts[0]["type"], mvts[0]["quantite"], mvts[0]["auteur"]), ("sortie", 3, "testeur"))

    def test_stock_jamais_negatif(self):
        pid = self.id_produit("Souris optique sans fil")  # stock 4
        with self.assertRaises(ErreurMetier) as ctx:
            stock.mettre_a_jour_stock(self.conn, pid, -5)
        self.assertEqual(ctx.exception.code, 409)
        self.assertEqual(stock.lire(self.conn, pid)["quantite"], 4)  # inchangé (rollback)

    def test_alerte_declenchee_au_seuil(self):
        pid = self.id_produit("Ramette de papier A4")  # stock 60, seuil 10
        self.assertFalse(stock.mettre_a_jour_stock(self.conn, pid, -49)["alerte"])  # 11
        self.assertTrue(stock.mettre_a_jour_stock(self.conn, pid, -1)["alerte"])    # 10 = seuil
        actions = [j["action"] for j in self.conn.execute("SELECT action FROM journal").fetchall()]
        self.assertIn("alerte_stock", actions)

    def test_liste_des_alertes_du_jeu_de_donnees(self):
        noms = {a["nom"]: a["niveau"] for a in stock.alertes(self.conn)}
        self.assertEqual(noms, {"Souris optique sans fil": "critique", "Cahier 200 pages": "rupture"})

    def test_variation_nulle_ou_non_entiere_refusee(self):
        pid = self.id_produit("Clé USB 32 Go")
        for mauvaise in (0, 2.5, "3", None, True):
            with self.assertRaises(ErreurMetier):
                stock.mettre_a_jour_stock(self.conn, pid, mauvaise)

    def test_deux_ventes_simultanees_aucune_perte(self):
        """20 ventes simultanées d'une unité sur un stock de 10 : exactement 10 réussissent."""
        p = produits.ajouter_produit(self.conn, "Produit concurrent", "", 1000,
                                     self.id_categorie("Papeterie"), 10, 0)
        resultats = []

        def vendre():
            conn = db.connecter(self.app.config["DATABASE"])
            try:
                stock.mettre_a_jour_stock(conn, p["id"], -1, "thread")
                resultats.append("ok")
            except ErreurMetier:
                resultats.append("refuse")
            finally:
                conn.close()

        threads = [threading.Thread(target=vendre) for _ in range(20)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(resultats.count("ok"), 10)
        self.assertEqual(resultats.count("refuse"), 10)
        self.assertEqual(stock.lire(self.conn, p["id"])["quantite"], 0)
