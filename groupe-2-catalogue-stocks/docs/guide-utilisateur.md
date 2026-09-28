# Guide d'utilisation — administration du catalogue

Ouvrir `http://localhost:5002/` après avoir lancé le module.

## Consulter et rechercher
Saisir un mot dans la barre de recherche (ex. « casque »), choisir éventuellement une catégorie ou la disponibilité, puis cliquer sur **Rechercher**. Les résultats sont paginés par 10. Les lignes en **jaune** sont au seuil critique, en **rouge** en rupture.

## Administrer (clé requise)
Saisir la clé administrateur dans le champ « Clé administrateur » (celle définie dans `.env`).
- **Ajouter un produit** : nom, prix (FCFA, entier ≥ 0), quantité initiale, catégorie → *Ajouter un produit*.
- **Vendre 1 / +10** : enregistre une sortie ou une entrée de stock. Si le stock atteint le seuil, une alerte s'affiche.

Les autres opérations (modifier, supprimer, catégories, images, seuils) se font via l'API : voir `integration-api.md`.

## FAQ
- **Pourquoi « Stock insuffisant » ?** Le stock ne peut jamais devenir négatif.
- **Pourquoi ma catégorie ne peut pas être supprimée ?** Elle contient encore des produits.
- **Quels formats d'image ?** JPEG et PNG, 2 Mo maximum.
- **Quand une alerte se déclenche-t-elle ?** Quand la quantité devient inférieure ou égale au seuil d'alerte du produit (5 par défaut).
