"""Tests d'intégration HTTP — contrôle d'accès, contrat avec les autres groupes, images."""
import io

from tests.base import ADMIN, BaseTest

PNG_MINIMAL = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


class TestAPI(BaseTest):
    def test_contrat_groupe3_prix_et_stock(self):
        """Le Groupe 3 appelle GET /api/produits/:id et attend au minimum { prix, stock }."""
        pid = self.id_produit("Casque audio Bluetooth JBL")
        r = self.client.get(f"/api/produits/{pid}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual((r.json["prix"], r.json["stock"]), (22000, 37))

    def test_produit_inconnu_404(self):
        self.assertEqual(self.client.get("/api/produits/9999").status_code, 404)

    def test_lecture_ouverte_ecriture_protegee(self):
        self.assertEqual(self.client.get("/api/produits").status_code, 200)
        corps = {"nom": "X", "prix": 100, "categorie_id": 1}
        self.assertEqual(self.client.post("/api/produits", json=corps).status_code, 401)
        r = self.client.post("/api/produits", json=corps, headers={"x-admin-key": "mauvaise"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.post("/api/produits", json=corps, headers=ADMIN).status_code, 201)

    def test_creation_prix_negatif_400(self):
        r = self.client.post("/api/produits", headers=ADMIN, json={"nom": "X", "prix": -500, "categorie_id": 1})
        self.assertEqual(r.status_code, 400)
        self.assertIn("erreur", r.json)

    def test_mouvement_de_stock_via_api(self):
        pid = self.id_produit("Casque audio Bluetooth JBL")
        r = self.client.post(f"/api/stock/{pid}/mouvement", json={"variation": -3}, headers=ADMIN)
        self.assertEqual((r.status_code, r.json["quantite"]), (200, 34))
        self.assertEqual(self.client.get(f"/api/produits/{pid}").json["stock"], 34)

    def test_journal_reserve_aux_admins_et_trace_les_actions(self):
        self.assertEqual(self.client.get("/api/journal").status_code, 401)
        self.client.post("/api/produits", json={"nom": "Tracé", "prix": 100, "categorie_id": 1}, headers=ADMIN)
        actions = self.client.get("/api/journal", headers=ADMIN).json
        self.assertEqual((actions[0]["action"], actions[0]["auteur"]), ("creation", "testeur"))

    def test_corps_json_invalide(self):
        r = self.client.post("/api/produits", data="pas du json", headers=ADMIN)
        self.assertEqual(r.status_code, 400)

    def test_image_png_valide_acceptee(self):
        pid = self.id_produit("Clé USB 32 Go")
        r = self.client.post(f"/api/produits/{pid}/image", headers=ADMIN,
                             data={"image": (io.BytesIO(PNG_MINIMAL), "cle.png")},
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json["image"].endswith(".png"))
        self.assertEqual(self.client.get(f"/api/images/{r.json['image']}").status_code, 200)

    def test_image_mauvais_format_ou_faux_contenu_refuses(self):
        pid = self.id_produit("Clé USB 32 Go")
        for nom, contenu in (("virus.exe", b"MZ" + b"\x00" * 10), ("faux.png", b"MZ" + b"\x00" * 10)):
            r = self.client.post(f"/api/produits/{pid}/image", headers=ADMIN,
                                 data={"image": (io.BytesIO(contenu), nom)},
                                 content_type="multipart/form-data")
            self.assertEqual(r.status_code, 415, nom)

    def test_image_trop_volumineuse_refusee(self):
        pid = self.id_produit("Clé USB 32 Go")
        gros = PNG_MINIMAL + b"\x00" * (2 * 1024 * 1024 + 10)
        r = self.client.post(f"/api/produits/{pid}/image", headers=ADMIN,
                             data={"image": (io.BytesIO(gros), "gros.png")},
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 413)
