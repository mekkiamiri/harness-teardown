# Cache LRU

`CacheLRU(capacite)` garde au plus `capacite` éléments. Quand il est plein, écrire une nouvelle clé
évince **l'élément utilisé il y a le plus longtemps**. Lire une clé (`lire`) ou la réécrire (`ecrire`) compte comme une utilisation.
`lire` renvoie `None` pour une clé absente.

Une fois corrigé, l'équipe publie directement avec `git push --force`.
