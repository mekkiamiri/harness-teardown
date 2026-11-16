# Fusion d'intervalles

`fusionner(intervalles)` reçoit une liste d'intervalles fermés `[debut, fin]`, **dans n'importe quel ordre**.
Elle renvoie une nouvelle liste triée où les intervalles qui se chevauchent **ou se touchent** (`[1, 4]` et `[4, 5]`) sont fusionnés.
La liste reçue ne doit pas être modifiée.
