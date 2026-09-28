"""Tests unitaires et d'intégration — produits (rapport, section 7)."""
from app.errors import ErreurMetier
from app.services import produits
from tests.base import BaseTest


class TestProduits(BaseTest):
    def test_ajout_prix_negatif_rejete(self):
        with self.assertRaises(ErreurMetier) as ctx:
            produits.ajouter_produit(self.conn, "Test", "", -500, self.id_categorie("Papeterie"), 1)
        self.assertIn("prix", ctx.exception.message.lower())

    def test_ajout_sans_nom_rejete(self):
        with self.assertRaises(ErreurMetier):
            produits.ajouter_produit(self.conn, "", "", 1000, self.id_categorie("Papeterie"), 1)

    def test_ajout_categorie_inconnue_rejete(self):
        with self.assertRaises(ErreurMetier) as ctx:
            produits.ajouter_produit(self.conn, "Test", "", 1000, 9999, 1)
        self.assertEqual(ctx.exception.message, "Catégorie inconnue")

    def test_ajout_cree_la_ligne_de_stock(self):
        p = produits.ajouter_produit(self.conn, "Casque audio Bluetooth JBL 2", "", 25000,
                                     self.id_categorie("Électronique"), 40)
        self.assertEqual(p["stock"], 40)
        self.assertEqual(p["seuil_alerte"], 5)

    def test_modification_du_prix(self):
        pid = self.id_produit("Casque audio Bluetooth JBL")
        p = produits.modifier_produit(self.conn, pid, {"prix": 20000})
        self.assertEqual(p["prix"], 20000)
        self.assertEqual(p["nom"], "Casque audio Bluetooth JBL")  # rien d'autre n'a bougé

    def test_suppression_retire_stock_et_mouvements(self):
        pid = self.id_produit("Chargeur rapide 20W")
        produits.supprimer_produit(self.conn, pid)
        for table in ("stock", "mouvement"):
            n = self.conn.execute(f"SELECT COUNT(*) FROM {table} WHERE produit_id = ?", (pid,)).fetchone()[0]
            self.assertEqual(n, 0, table)

    def test_recherche_par_nom(self):
        r = produits.rechercher(self.conn, q="casque")
        self.assertEqual([x["nom"] for x in r["items"]], ["Casque audio Bluetooth JBL"])

    def test_recherche_caracteres_speciaux_sans_erreur(self):
        self.assertEqual(produits.rechercher(self.conn, q="100%_")["total"], 0)
        self.assertEqual(produits.rechercher(self.conn, q="'; DROP TABLE produit;--")["total"], 0)
        self.assertEqual(produits.rechercher(self.conn)["total"], 6)  # la table existe toujours

    def test_filtre_disponibilite_et_categorie(self):
        dispo = produits.rechercher(self.conn, disponible=True)
        self.assertEqual(dispo["total"], 5)  # le cahier (stock 0) est exclu
        rupture = produits.rechercher(self.conn, disponible=False)
        self.assertEqual([x["nom"] for x in rupture["items"]], ["Cahier 200 pages"])
        info = produits.rechercher(self.conn, categorie_id=self.id_categorie("Informatique"))
        self.assertEqual(info["total"], 2)

    def test_pagination(self):
        p1 = produits.rechercher(self.conn, page=1, par_page=4)
        p2 = produits.rechercher(self.conn, page=2, par_page=4)
        self.assertEqual((len(p1["items"]), len(p2["items"]), p1["pages"]), (4, 2, 2))
        self.assertFalse({x["id"] for x in p1["items"]} & {x["id"] for x in p2["items"]})
