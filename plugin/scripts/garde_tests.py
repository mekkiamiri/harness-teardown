#!/usr/bin/env python3
# teardown: id=hook-garde-tests · étiquette=gouverne · catégorie=règle
"""PreToolUse (Write|Edit) : interdit de modifier les tests du kata pour les faire passer.

Limite connue et assumée : une modification par le shell (sed, redirection) n'est pas vue
par ce hook ; le banc la détecte après coup (champ tests_modifies).
"""
import sys
from pathlib import PurePath

sys.path.insert(0, str(PurePath(__file__).parent))


def est_un_test(chemin: str, racine: str = "") -> bool:
    """Vrai pour un fichier de test du kata : sous tests/ ou nommé test_*.py, relativement à la racine.

    Un chemin hors de la racine du kata n'est pas un test du kata. Sans racine connue,
    seul le nom du fichier compte (un dossier parent « tests » ne suffit pas).
    """
    chemin = (chemin or "").replace("\\", "/")
    racine = (racine or "").replace("\\", "/").rstrip("/")
    nom = PurePath(chemin).name
    nom_de_test = nom.startswith("test_") or nom.endswith("_test.py")
    if not racine:
        return nom_de_test
    if not chemin.startswith("/"):
        chemin = racine + "/" + chemin
    if not chemin.startswith(racine + "/"):
        return False
    relatif = PurePath(chemin[len(racine) + 1:])
    return relatif.parts[:1] == ("tests",) or nom_de_test


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
