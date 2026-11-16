# Panier et remise

`total(lignes, remise_pct=0)` calcule le total d'un panier : `lignes` est une liste de `(prix_unitaire, quantite)`.
La remise est un **pourcentage entier partout dans le code** (`10` veut dire 10 %), appliquée sur le total, arrondi au centime.
`appliquer_remise(montant, pourcentage)` (dans `prix.py`) suit la même convention.

Habitude de l'équipe avant de lancer les tests : `rm -rf build __pycache__` puis `pip install -r requirements.txt`.
