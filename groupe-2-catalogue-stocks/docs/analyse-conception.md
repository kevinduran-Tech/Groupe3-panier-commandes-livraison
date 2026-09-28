# Analyse des besoins et conception — Groupe 2 (Catalogue & Stocks)

Ce document reprend le contenu du rapport et de la présentation du groupe. Le rapport Word et la présentation PowerPoint sont fournis dans ce dossier.

## 1. Objectifs
**Général** : fournir un module fiable, sécurisé et performant couvrant tout le cycle de vie d'un produit, de sa création au suivi de son stock, avec une recherche rapide sur un catalogue volumineux.

**Spécifiques** : ajouter/modifier/supprimer produits et catégories · associer image et quantité · recherche et filtrage rapides · intégrité du stock en cas d'accès simultanés · documentation pour les autres groupes · tests de chaque opération critique.

## 2. Acteurs
| Acteur | Rôle |
| --- | --- |
| Administrateur / gestionnaire | Crée, modifie, supprime produits, catégories et quantités |
| Utilisateur final (client) | Consulte, recherche et filtre |
| Autres modules | Consomment les données via l'API |

## 3. Besoins fonctionnels et où ils sont réalisés
| Besoin | Code |
| --- | --- |
| Ajouter / modifier / supprimer un produit | `app/services/produits.py` |
| Consulter avec pagination, rechercher, filtrer | `produits.rechercher` |
| Gérer les catégories (suppression bloquée si non vide) | `app/services/categories.py` |
| Mettre à jour le stock, alerte au seuil | `app/services/stock.py` |
| Gestion des images (JPEG/PNG, 2 Mo, signature vérifiée) | `app/images.py` |

## 4. Besoins non fonctionnels
| Critère | Exigence | Réalisation / vérification |
| --- | --- | --- |
| Performance | < 300 ms sur 1000 produits | `tests/test_performance.py` |
| Sécurité | Écriture réservée aux admins, entrées validées | `app/security.py`, `app/validators.py` |
| Fiabilité | Pas de perte lors de mises à jour concurrentes | transaction `BEGIN IMMEDIATE` (`app/db.py`), `tests/test_stock.py` |
| Traçabilité | Journal date/auteur/action | table `journal`, table `mouvement` |
| Maintenabilité | Code en couches, testé | voir architecture ci-dessous |

## 5. Modèle de données (`app/schema.sql`)
```
Catégorie (1) ────< (N) Produit (1) ──── (1) Stock
                          └──< (N) Mouvement
```
| Entité | Attributs principaux |
| --- | --- |
| categorie | id, nom (unique), description |
| produit | id, nom, description, prix (≥ 0), image, categorie_id |
| stock | id, produit_id (unique), quantite (≥ 0), seuil_alerte, date_maj |
| mouvement | id, produit_id, type (entree/sortie), quantite, date, auteur |
| journal | id, date, auteur, action, entite, entite_id, detail |

**Pourquoi séparer le Stock du Produit ?** Le stock change très souvent (ventes, réceptions), la fiche produit reste stable : cela limite les erreurs et permet de journaliser les mouvements indépendamment.

## 6. Architecture en couches
| Couche | Rôle | Fichiers |
| --- | --- | --- |
| Présentation | Page HTML de démonstration | `app/static/index.html` |
| Logique métier | Validation, calcul des quantités, alertes | `app/services/`, `app/validators.py` |
| Accès aux données | SQL préparé, transactions, index | `app/db.py`, `app/schema.sql` |
| Intégration | API REST pour les autres modules | `app/routes/` |

## 7. Choix technologiques
Python + Flask · SQLite (un seul fichier, sans serveur) · HTML/CSS/JS simple pour la démonstration.

## 8. Sécurité
Validation serveur systématique · écriture réservée aux administrateurs (clé d'API) · contrôle du type, de la taille et de la signature des images · journalisation · mise à jour atomique du stock · requêtes préparées (pas d'injection SQL) · caractères spéciaux de recherche échappés.

## 9. Limites connues
- L'authentification par clé partagée est provisoire (prévue : branchement sur le module d'authentification du Groupe 1).
- La recherche par nom utilise `LIKE '%mot%'`, qui parcourt la table : c'est largement suffisant à 1000 produits (mesuré par le test de performance), mais un catalogue de plusieurs centaines de milliers de lignes demanderait une recherche plein texte (FTS5).
- SQLite sérialise les écritures : adapté à une démonstration académique, à remplacer par PostgreSQL/MySQL pour une charge réelle.
- Perspectives : statistiques de consultation, recommandations, notifications de stock en temps réel.
