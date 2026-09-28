# Guide d'intégration — module Catalogue & Stocks (Groupe 2)

Destiné aux autres groupes (Panier/commandes, Authentification, …).

- **URL de base** : `http://<hôte-du-groupe-2>:5002/api` (port configurable via `PORT`)
- **Format** : JSON (UTF-8). Les erreurs ont toujours la forme `{ "erreur": "message" }`.
- **Prix** : entiers en FCFA (pas de centimes).

## Authentification

| Type d'accès | Exigence |
| --- | --- |
| Lecture (`GET`) | Ouverte. L'en-tête `x-client-id` du Groupe 3 est accepté et ignoré. |
| Écriture (`POST`, `PUT`, `PATCH`, `DELETE`) | En-tête `x-admin-key: <clé>` (valeur de `ADMIN_API_KEY` dans le `.env` du Groupe 2). `401` si absent, `403` si incorrect. |
| Traçabilité | En-tête optionnel `x-auteur: <nom>` : enregistré dans le journal et les mouvements de stock. |

> La clé d'administration est un mécanisme provisoire, en attendant le branchement sur l'authentification du Groupe 1. Elle ne doit jamais être écrite dans le dépôt (voir `.env.example`).

## Points d'API exposés

| Méthode | Route | Accès | Description |
| --- | --- | --- | --- |
| GET | `/api/produits` | public | Liste paginée. Paramètres : `q`, `categorie_id`, `disponible` (`true`/`false`), `page`, `par_page` (max 100) |
| GET | `/api/produits/:id` | public | Détail d'un produit — **contient `prix` et `stock`** |
| POST | `/api/produits` | admin | Ajouter `{ nom, description?, prix, categorie_id, quantite_initiale?, seuil_alerte? }` |
| PATCH | `/api/produits/:id` | admin | Modifier (champs partiels : `nom`, `description`, `prix`, `categorie_id`) |
| DELETE | `/api/produits/:id` | admin | Supprimer (stock et mouvements supprimés avec) |
| POST | `/api/produits/:id/image` | admin | Téléverser une image (`multipart/form-data`, champ `image`, JPEG/PNG, 2 Mo max) |
| GET | `/api/images/:fichier` | public | Récupérer une image |
| GET | `/api/categories` | public | Liste des catégories avec `nb_produits` |
| POST | `/api/categories` | admin | Créer `{ nom, description? }` |
| PATCH | `/api/categories/:id` | admin | Renommer `{ nom?, description? }` |
| DELETE | `/api/categories/:id` | admin | Supprimer (refusé `409` si la catégorie contient des produits) |
| GET | `/api/stock/:produitId` | public | Quantité et seuil d'alerte |
| POST | `/api/stock/:produitId/mouvement` | admin | Entrée/sortie `{ variation }` (ex. `-3` = vente de 3) |
| PATCH | `/api/stock/:produitId/seuil` | admin | Changer le seuil `{ seuil_alerte }` |
| GET | `/api/stock/:produitId/mouvements` | public | Historique des mouvements du produit |
| GET | `/api/stock/alertes` | public | Produits au seuil critique ou en rupture |
| GET | `/api/journal` | admin | Journal d'audit (100 dernières actions) |
| GET | `/api/health` | public | Vérification de disponibilité |

## Contrat avec le Groupe 3 (Panier, commandes et livraison)

Le README du Groupe 3 attend que le module Groupe 2 expose `GET /produits/:id` retournant `{ prix, stock }`.

```http
GET /api/produits/1
```
```json
{
  "id": 1, "nom": "Casque audio Bluetooth JBL", "description": "",
  "prix": 22000, "stock": 37, "seuil_alerte": 5,
  "categorie_id": 1, "categorie": "Électronique", "image": null
}
```

Configuration côté Groupe 3 (`.env`) :

```
CATALOG_SERVICE_URL=http://<hôte-du-groupe-2>:5002/api
CATALOG_SERVICE_MOCK=false
```

**Validation d'une commande** : pour décrémenter le stock, le Groupe 3 appelle (avec la clé admin partagée) :

```http
POST /api/stock/1/mouvement
x-admin-key: <clé>
Content-Type: application/json

{ "variation": -3 }
```
Réponse `200` : `{ "produit_id": 1, "quantite": 34, "alerte": false }`.
Si le stock est insuffisant : `409 { "erreur": "Stock insuffisant pour cette opération" }` — la commande doit alors être refusée.

## Codes de retour

| Code | Signification |
| --- | --- |
| 200 / 201 / 204 | Succès / créé / supprimé |
| 400 | Données invalides (prix négatif, nom manquant, catégorie inconnue, JSON invalide…) |
| 401 / 403 | Clé admin absente / incorrecte |
| 404 | Ressource introuvable |
| 409 | Conflit (stock insuffisant, catégorie non vide, nom de catégorie déjà pris) |
| 413 / 415 | Image trop lourde / format ou contenu refusé |

## Exemples `curl`

```bash
curl "http://localhost:5002/api/produits?q=casque"
curl -X POST http://localhost:5002/api/produits \
  -H "x-admin-key: changez-moi-en-production" -H "Content-Type: application/json" \
  -d '{"nom":"Casque audio Bluetooth JBL","prix":25000,"categorie_id":1,"quantite_initiale":40}'
curl -X POST http://localhost:5002/api/stock/1/mouvement \
  -H "x-admin-key: changez-moi-en-production" -H "Content-Type: application/json" -d '{"variation":-3}'
```
