# Groupe 3 — Panier, commandes et livraison

Module « Panier, commandes et livraison » — Projet de Systèmes Numériques,
ICT University (section francophone), dirigé par M. Guy Atangana.

Voir [`docs/analyse-conception.md`](docs/analyse-conception.md) pour
l'analyse des besoins et la conception détaillée (synchronisé avec le
support de présentation du groupe).

## Stack technique

- Node.js + Express (API REST)
- Sequelize + PostgreSQL (persistance) — SQLite en mémoire pour les tests
- Jest + Supertest (tests)

## Structure du projet

```
src/
  config/       # connexion base de données
  models/       # Panier, LignePanier, Commande, LigneCommande, Facture, Livraison
  services/     # logique métier (panier, commande, facture, livraison)
  controllers/  # gestion des requêtes HTTP
  routes/       # définition des routes de l'API
  middlewares/  # authentification, gestion des erreurs
  server.js     # point d'entrée
tests/          # tests unitaires, intégration, fonctionnels
docs/           # documentation d'analyse et de conception
```

## Installation

```bash
npm install
cp .env.example .env   # puis renseigner les identifiants PostgreSQL
npm run dev
```

## Tests

```bash
npm test
```

## Statut du projet

- [x] Analyse des besoins
- [x] Conception (modèle de données, architecture)
- [ ] Développement (en cours)
- [ ] Tests
- [ ] Documentation d'intégration finale

## Dépendances avec les autres groupes

- Groupe 1 (authentification) — vérification de l'identité du client
- Groupe 2 (catalogue/stock) — vérification de la disponibilité et du prix
- Groupe 4 (frontend) — interfaces panier / suivi / facture
- Groupe 5 (infra/tests globaux) — intégration continue et tests de bout en bout
