# Analyse de durée

`en_minutes(texte)` convertit une durée écrite `<heures>h<minutes>m` en minutes.
Chaque partie est facultative mais il en faut au moins une : `"1h30m"` → 90, `"2h"` → 120, `"45m"` → 45, `"10h05m"` → 605.
Tout autre texte (vide, lettres, espaces) lève `ValueError`.
