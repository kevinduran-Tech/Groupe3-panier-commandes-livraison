# Groupe 2 — Catalogue de produits et gestion des stocks

Module « Catalogue de produits et gestion des stocks » — Projet de Systèmes Numériques, ICT University (section francophone), dirigé par M. Guy Atangana.

**Groupe 2 :** Soumelong Jordan Landry (ICTU20251294) · Bekonje Bekonje Alexandre (ICTU20251313)

Voir `docs/analyse-conception.md` pour l'analyse des besoins et la conception détaillée (synchronisée avec le support de présentation du groupe), et `docs/integration-api.md` pour le guide d'intégration destiné aux autres groupes (endpoints, formats, dépendances).

## Stack technique

- Python 3.10+ et Flask (API REST)
- SQLite (persistance, un seul fichier, sans serveur à installer)
- unittest / pytest (tests)
- HTML/CSS/JavaScript simple pour la démonstration (`app/static/index.html`)

## Structure du projet

```
app/
  __init__.py     # création de l'application, gestion des erreurs
  config.py       # configuration (variables d'environnement / .env)
  db.py           # connexion SQLite, transactions atomiques
  schema.sql      # tables : categorie, produit, stock, mouvement, journal
  validators.py   # validation des entrées
  security.py     # contrôle d'accès (écriture réservée aux administrateurs)
  images.py       # contrôle des images (JPEG/PNG, taille, signature)
  errors.py       # exceptions métier
  seed.py         # jeu de données de démonstration
  services/       # logique métier (produits, categories, stock, journal)
  routes/         # définition des routes de l'API
  static/         # page HTML de démonstration
tests/            # tests unitaires, intégration, concurrence, performance
docs/             # analyse/conception, guide d'intégration, guide utilisateur, rapport et présentation
run.py            # point d'entrée
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # puis choisir une valeur pour ADMIN_API_KEY
python -m app.seed               # (facultatif) charge le jeu de données de démonstration
python run.py
```

Le module écoute sur `http://localhost:5002` (interface de démonstration à la racine, API sous `/api`).

## Tests

```bash
python -m pytest        # ou : python -m unittest discover -s tests -t .
```

31 tests : validation (prix négatif, nom manquant), catégories (suppression bloquée si non vide), stock (vente de 3 casques 37 → 34, jamais négatif, alerte au seuil), **20 ventes simultanées sans perte d'écriture**, contrôle d'accès, contrat avec le Groupe 3, images refusées (mauvais format, faux contenu, trop lourdes) et recherche sur 1000 produits en moins de 300 ms.

## Statut du projet

- [x] Analyse des besoins
- [x] Conception (modèle de données, architecture en couches)
- [x] Développement (produits, catégories, images, stock, recherche/filtrage, pagination, alertes, journal)
- [x] Tests (31 tests passants)
- [x] Documentation d'intégration pour les autres groupes (`docs/integration-api.md`)
- [ ] Documentation OpenAPI/Swagger (nice-to-have, non bloquant)
- [ ] Branchement réel sur l'authentification du Groupe 1 (clé d'administration provisoire en attendant)

## Intégration avec les autres groupes

**Groupe 3 (Panier, commandes et livraison)** consomme ce module :

- `GET /api/produits/:id` retourne notamment `{ prix, stock }`
- `POST /api/stock/:id/mouvement` avec `{ "variation": -3 }` décrémente le stock à la validation d'une commande (`409` si stock insuffisant)

Côté Groupe 3, renseigner dans `.env` :

```
CATALOG_SERVICE_URL=http://<hôte-du-groupe-2>:5002/api
CATALOG_SERVICE_MOCK=false
```

**Groupe 1 (authentification)** : en attendant l'intégration, l'écriture est protégée par l'en-tête `x-admin-key` ; la lecture est ouverte.

## Points d'API principaux

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/api/produits` | Liste paginée, recherche `q`, filtres `categorie_id`, `disponible` |
| GET | `/api/produits/:id` | Détail d'un produit (avec `prix` et `stock`) |
| POST / PATCH / DELETE | `/api/produits[/:id]` | Ajouter / modifier / supprimer (admin) |
| POST | `/api/produits/:id/image` | Téléverser une image (admin) |
| GET / POST / PATCH / DELETE | `/api/categories[/:id]` | Gérer les catégories |
| GET | `/api/stock/:produitId` | Stock et seuil d'alerte |
| POST | `/api/stock/:produitId/mouvement` | Entrée/sortie de stock (admin) |
| GET | `/api/stock/alertes` | Produits au seuil critique ou en rupture |
| GET | `/api/journal` | Journal d'audit (admin) |

Détail complet : `docs/integration-api.md`.
