#!/usr/bin/env python3
# teardown: id=hook-tests-apres-edition · étiquette=gouverne · catégorie=vérification
"""PostToolUse (Write|Edit) : relance les tests visibles après chaque modification de fichier Python.

Si les tests échouent, code 2 : la fin de la sortie des tests est montrée à l'agent
(l'outil a déjà tourné, rien n'est annulé).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    from _commun import dossier_projet, lancer_tests, lire_entree

    entree = lire_entree()
    chemin = (entree.get("tool_input") or {}).get("file_path", "")
    if not chemin.endswith(".py"):
        return 0
    ok, sortie = lancer_tests(dossier_projet(entree))
    if ok:
        return 0
    print("Les tests visibles échouent après cette modification :\n" + sortie, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
