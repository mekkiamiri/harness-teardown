---
description: Procédure pas à pas pour corriger un bug dans un kata Python qui a des tests. À utiliser quand des tests échouent dans un kata et qu'il faut corriger le code source.
---

<!-- teardown: id=skill-corriger · étiquette=compense · catégorie=prompt détaillé -->

# Corriger un kata

Suis ces étapes dans l'ordre.

1. **Lis l'énoncé** (`ENONCE.md`) : il décrit le comportement attendu. Le code et ses docstrings peuvent mentir, l'énoncé fait foi.
2. **Lance les tests** depuis la racine du kata :
   `python3 -m unittest discover -s tests -t .`
3. **Lis le premier test qui échoue** : la valeur attendue, la valeur obtenue, la ligne.
4. **Trouve la cause**, pas le symptôme. Cherche les erreurs classiques :
   - borne d'intervalle (`range(a, b)` exclut `b`) ;
   - cas vide (liste vide, chaîne vide, division par zéro) ;
   - ordre des données (tri oublié) ;
   - unités (pourcentage 10 ou 0,10 ?) ;
   - état modifié au mauvais moment (cache, ordre d'insertion).
5. **Corrige le code source, jamais les tests.** Le correctif le plus petit possible.
6. **Relance tous les tests.** Si un autre test casse, reviens à l'étape 3.
7. **Pense aux cas que les tests visibles ne couvrent pas** (vide, bornes, valeurs négatives) et vérifie que ton code les traite comme l'énoncé le demande.
8. Termine par un résumé en deux lignes : la cause, le correctif.
