"""Fonctions partagées par les hooks du plugin (ce fichier n'est pas une pièce démontable)."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

COMMANDE_TESTS = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]


def lire_entree() -> dict:
    """Lit le JSON que Claude Code envoie au hook sur l'entrée standard."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def dossier_projet(entree: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or entree.get("cwd") or os.getcwd()


def noter_incident(piece: str, regle: str, detail: str) -> None:
    """Ajoute une ligne au journal d'incidents si le banc l'a demandé (variable TEARDOWN_INCIDENTS).

    Ne lève jamais d'exception : un hook qui bloque doit sortir en 2 même si le journal est inaccessible.
    """
    chemin = os.environ.get("TEARDOWN_INCIDENTS")
    if not chemin:
        return
    ligne = {
        "quand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "piece": piece,
        "regle": regle,
        "detail": detail[:300],
    }
    try:
        with open(chemin, "a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    except Exception as e:  # le journal ne doit jamais empêcher un blocage
        print(f"(journal d'incidents indisponible : {e})", file=sys.stderr)


def lancer_tests(racine: str, delai: int = 120) -> tuple[bool, str]:
    """Lance les tests visibles du kata. Renvoie (réussite, fin de la sortie)."""
    if not os.path.isdir(os.path.join(racine, "tests")):
        return True, "pas de dossier tests/"
    try:
        proc = subprocess.run(COMMANDE_TESTS, cwd=racine, capture_output=True, text=True, timeout=delai)
    except subprocess.TimeoutExpired:
        return False, f"tests interrompus après {delai} s"
    sortie = (proc.stderr + proc.stdout).strip().splitlines()
    return proc.returncode == 0, "\n".join(sortie[-25:])
