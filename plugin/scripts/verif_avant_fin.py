#!/usr/bin/env python3
# teardown: id=hook-verif-avant-fin · étiquette=gouverne · catégorie=vérification
"""Stop : empêche l'agent de déclarer la tâche finie tant que les tests visibles échouent.

Code 2 = l'agent continue. Si l'agent continue déjà à cause de ce hook (stop_hook_active),
on le laisse s'arrêter pour éviter une boucle sans fin.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    from _commun import dossier_projet, lancer_tests, lire_entree, noter_incident

    entree = lire_entree()
    if entree.get("stop_hook_active"):
        return 0
    ok, sortie = lancer_tests(dossier_projet(entree))
    if ok:
        return 0
    noter_incident("hook-verif-avant-fin", "fin déclarée avec des tests en échec", sortie[-200:])
    print("Pas fini : les tests visibles échouent encore.\n" + sortie, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
