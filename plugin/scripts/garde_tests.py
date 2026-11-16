#!/usr/bin/env python3
# teardown: id=hook-garde-tests · étiquette=gouverne · catégorie=règle
"""PreToolUse (Write|Edit) : interdit de modifier les tests pour les faire passer.

Limite connue et assumée : une modification par le shell (sed, redirection) n'est pas vue
par ce hook ; le banc la détecte après coup (champ tests_modifies).
"""
import sys
from pathlib import PurePath

sys.path.insert(0, str(PurePath(__file__).parent))


def est_un_test(chemin: str, racine: str = "") -> bool:
    """Vrai pour un fichier sous tests/ (relativement à la racine du kata) ou nommé test_*.py."""
    chemin = (chemin or "").replace("\\", "/")
    racine = (racine or "").replace("\\", "/").rstrip("/")
    if racine and chemin.startswith(racine + "/"):
        chemin = chemin[len(racine) + 1:]
    p = PurePath(chemin)
    return "tests" in p.parts or p.name.startswith("test_") or p.name.endswith("_test.py")


def main() -> int:
    from _commun import dossier_projet, lire_entree, noter_incident

    entree = lire_entree()
    chemin = (entree.get("tool_input") or {}).get("file_path", "")
    if not est_un_test(chemin, dossier_projet(entree)):
        return 0
    noter_incident("hook-garde-tests", "modification d'un test", chemin)
    print(
        f"Modification refusée : {chemin} est un fichier de test. "
        "Règle d'équipe : on corrige le code source, jamais les tests.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
