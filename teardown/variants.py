"""Générateur de variantes du plugin : une copie sans chaque pièce, plus le plugin complet et le plugin vide.

Usage :
    python3 teardown/variants.py                      # génère dans build/variantes et valide tout
    python3 teardown/variants.py --sortie <dossier>
    python3 teardown/variants.py --claude-validate    # en plus : `claude plugin validate --strict` (local, si installé)

Chaque variante est vérifiée par `valider` : manifeste, skills, agents, hooks, chemins référencés.
Ce n'est pas le validateur officiel ; `--claude-validate` le lance quand la CLI Claude Code est là.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PIECES = RACINE / "teardown" / "pieces.json"

EVENEMENTS_HOOKS = {
    "SessionStart", "SessionEnd", "UserPromptSubmit", "PreToolUse", "PostToolUse",
    "PostToolUseFailure", "Notification", "Stop", "SubagentStart", "SubagentStop",
    "PreCompact", "PermissionRequest",
}
NOMS_RESERVES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REF_RACINE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)")


def charger_pieces(chemin: Path = PIECES) -> dict:
    return json.loads(chemin.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- validation

def _frontmatter(texte: str) -> dict | None:
    """Lit un frontmatter YAML très simple (clé: valeur sur une ligne). None s'il manque."""
    if not texte.startswith("---\n"):
        return None
    fin = texte.find("\n---", 4)
    if fin < 0:
        return None
    champs = {}
    for ligne in texte[4:fin].splitlines():
        if ":" in ligne and not ligne.startswith((" ", "\t", "#")):
            cle, _, valeur = ligne.partition(":")
            champs[cle.strip()] = valeur.strip()
    return champs


def valider(plugin: Path) -> list[str]:
    """Renvoie la liste des erreurs de structure d'un plugin (vide = valide)."""
    erreurs: list[str] = []
    manifeste = plugin / ".claude-plugin" / "plugin.json"
    if not manifeste.is_file():
        return [".claude-plugin/plugin.json absent"]
    try:
        meta = json.loads(manifeste.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"plugin.json illisible : {e}"]
    nom = meta.get("name", "")
    if not isinstance(nom, str) or not KEBAB.match(nom):
        erreurs.append(f"name absent ou pas en kebab-case : {nom!r}")
    elif nom.startswith(NOMS_RESERVES) or nom in {"claude", "anthropic", "claude-code"}:
        erreurs.append(f"name réservé : {nom}")
    for cle in ("skills", "agents", "commands", "hooks", "mcpServers", "outputStyles"):
        valeur = meta.get(cle)
        for chemin in ([valeur] if isinstance(valeur, str) else valeur if isinstance(valeur, list) else []):
            if isinstance(chemin, str) and chemin not in (".", "./"):
                if not chemin.startswith("./"):
                    erreurs.append(f"{cle} : le chemin doit commencer par ./ : {chemin}")
                elif not (plugin / chemin).exists():
                    erreurs.append(f"{cle} : chemin introuvable : {chemin}")
    for entree in (plugin / ".claude-plugin").iterdir():
        if entree.name != "plugin.json" and entree.is_dir():
            erreurs.append(f"composant rangé dans .claude-plugin/ : {entree.name}")
    if (plugin / "CLAUDE.md").exists():
        erreurs.append("CLAUDE.md à la racine du plugin n'est pas chargé : utiliser un skill")

    skills = plugin / "skills"
    if skills.is_dir():
        for dossier in sorted(p for p in skills.iterdir() if p.is_dir()):
            fichier = dossier / "SKILL.md"
            if not fichier.is_file():
                erreurs.append(f"skills/{dossier.name}/SKILL.md absent")
                continue
            fm = _frontmatter(fichier.read_text(encoding="utf-8"))
            if fm is None or not fm.get("description"):
                erreurs.append(f"skills/{dossier.name}/SKILL.md : frontmatter sans description")

    agents = plugin / "agents"
    if agents.is_dir():
        for fichier in sorted(agents.rglob("*.md")):
            fm = _frontmatter(fichier.read_text(encoding="utf-8"))
            if fm is None or not fm.get("description"):
                erreurs.append(f"{fichier.relative_to(plugin)} : frontmatter sans description")

    bin_ = plugin / "bin"
    if bin_.is_dir():
        for fichier in bin_.iterdir():
            if fichier.is_file() and not os.access(fichier, os.X_OK):
                erreurs.append(f"bin/{fichier.name} n'est pas exécutable")

    hooks = plugin / "hooks" / "hooks.json"
    if hooks.exists():
        erreurs += _valider_hooks(plugin, hooks)

    evals = plugin / "evals"
    if evals.is_dir():
        for cas in sorted(p for p in evals.iterdir() if p.is_dir() and p.name != "results"):
            if not ((cas / "prompt.md").is_file() or (cas / "case.yaml").is_file()):
                erreurs.append(f"evals/{cas.name} : ni prompt.md ni case.yaml")
            if not any((cas / "graders").glob("*.md")):
                erreurs.append(f"evals/{cas.name} : aucun grader")
    return erreurs


def _valider_hooks(plugin: Path, fichier: Path) -> list[str]:
    erreurs = []
    try:
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"hooks.json illisible : {e}"]
    carte = donnees.get("hooks") if isinstance(donnees, dict) else None
    if not isinstance(carte, dict):
        return ["hooks.json : clé de premier niveau « hooks » absente"]
    for evenement, groupes in carte.items():
        if evenement not in EVENEMENTS_HOOKS:
            erreurs.append(f"hooks.json : événement inconnu {evenement}")
        if not isinstance(groupes, list) or not groupes:
            erreurs.append(f"hooks.json : {evenement} doit être une liste non vide")
            continue
        for groupe in groupes:
            gestionnaires = groupe.get("hooks") if isinstance(groupe, dict) else None
            if not isinstance(gestionnaires, list) or not gestionnaires:
                erreurs.append(f"hooks.json : {evenement} : groupe sans gestionnaire")
                continue
            for g in gestionnaires:
                if g.get("type") != "command" or not isinstance(g.get("command"), str):
                    erreurs.append(f"hooks.json : {evenement} : gestionnaire sans type command")
                    continue
                for ref in REF_RACINE.findall(g["command"]):
                    if not (plugin / ref).is_file():
                        erreurs.append(f"hooks.json : {evenement} : script introuvable {ref}")
    return erreurs


# --------------------------------------------------------------------------- retrait

def _retirer_hooks(plugin: Path, scripts: list[str]) -> None:
    fichier = plugin / "hooks" / "hooks.json"
    if not scripts or not fichier.exists():
        return
    donnees = json.loads(fichier.read_text(encoding="utf-8"))
    carte = {}
    for evenement, groupes in donnees["hooks"].items():
        nouveaux = []
        for groupe in groupes:
            gardes = [g for g in groupe["hooks"]
                      if not any(f"${{CLAUDE_PLUGIN_ROOT}}/{s}" in g.get("command", "") for s in scripts)]
            if gardes:
                nouveaux.append({**groupe, "hooks": gardes})
        if nouveaux:
            carte[evenement] = nouveaux
    if carte:
        fichier.write_text(json.dumps({"hooks": carte}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        shutil.rmtree(plugin / "hooks")


def retirer(plugin: Path, piece: dict) -> None:
    """Retire une pièce d'une copie du plugin, en place."""
    _retirer_hooks(plugin, piece["retrait"].get("scripts_hooks", []))
    for rel in piece["retrait"]["chemins"]:
        cible = plugin / rel
        if cible.is_dir():
            if rel == piece["retrait"]["chemins"][0] or not any(cible.iterdir()):
                shutil.rmtree(cible)
        elif cible.exists():
            cible.unlink()


def _nettoyer_scripts(plugin: Path) -> None:
    """Retire scripts/ s'il ne reste que des fichiers partagés (aucun hook ne s'en sert)."""
    scripts = plugin / "scripts"
    if scripts.is_dir() and not (plugin / "hooks" / "hooks.json").exists():
        shutil.rmtree(scripts)


MARQUEUR = ".teardown-variantes"


def verifier_sortie(sortie: Path, source: Path | None = None) -> None:
    """Refuse un dossier de sortie dangereux à effacer.

    Interdits : le dépôt, un de ses parents, le plugin source ou un de ses dossiers,
    et tout dossier non vide qui ne porte pas le marqueur laissé par cet outil.
    """
    cible = sortie.resolve()
    if cible == RACINE or RACINE.is_relative_to(cible):
        raise ValueError(f"sortie refusée : {sortie} est le dépôt ou l'un de ses parents")
    if source is not None and (cible == source.resolve() or cible.is_relative_to(source.resolve())):
        raise ValueError(f"sortie refusée : {sortie} est dans le plugin source")
    if cible.exists() and (not cible.is_dir() or (any(cible.iterdir()) and not (cible / MARQUEUR).exists())):
        raise ValueError(f"sortie refusée : {sortie} existe, n'est pas vide et n'a pas été créé par cet outil")


def generer(sortie: Path, source: Path | None = None, donnees: dict | None = None) -> dict[str, Path]:
    """Génère complet, vide et sans-<id> pour chaque pièce. Renvoie {nom de variante: dossier}."""
    donnees = donnees or charger_pieces()
    source = source or (RACINE / donnees["plugin"])
    verifier_sortie(sortie, source)
    if sortie.exists():
        shutil.rmtree(sortie)
    sortie.mkdir(parents=True)
    (sortie / MARQUEUR).write_text("Dossier créé par teardown/variants.py : il est effacé à chaque génération.\n",
                                   encoding="utf-8")
    ignorer = shutil.ignore_patterns("__pycache__", "*.pyc", "results")
    variantes: dict[str, Path] = {}

    complet = sortie / "complet"
    shutil.copytree(source, complet, ignore=ignorer)
    variantes["complet"] = complet

    for piece in donnees["pieces"]:
        cible = sortie / f"sans-{piece['id']}"
        shutil.copytree(source, cible, ignore=ignorer)
        retirer(cible, piece)
        _nettoyer_scripts(cible)
        variantes[f"sans-{piece['id']}"] = cible

    vide = sortie / "vide"
    (vide / ".claude-plugin").mkdir(parents=True)
    shutil.copy2(source / ".claude-plugin" / "plugin.json", vide / ".claude-plugin" / "plugin.json")
    variantes["vide"] = vide
    return variantes


def pieces_presentes(plugin: Path, donnees: dict) -> set[str]:
    """Identifiants des pièces encore présentes dans un plugin (fichier étiqueté présent)."""
    return {p["id"] for p in donnees["pieces"] if (plugin / p["fichier_etiquete"]).exists()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sortie", type=Path, default=RACINE / "build" / "variantes")
    parser.add_argument("--claude-validate", action="store_true",
                        help="lance aussi `claude plugin validate --strict` sur chaque variante")
    args = parser.parse_args(argv)

    donnees = charger_pieces()
    try:
        variantes = generer(args.sortie, donnees=donnees)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    echec = False
    for nom, dossier in variantes.items():
        erreurs = valider(dossier)
        n = len(pieces_presentes(dossier, donnees))
        etat = "valide" if not erreurs else "INVALIDE"
        if args.claude_validate and shutil.which("claude"):
            proc = subprocess.run(["claude", "plugin", "validate", "--strict", str(dossier)],
                                  capture_output=True, text=True)
            etat += " · claude validate " + ("ok" if proc.returncode == 0 else "ÉCHEC")
            erreurs += [] if proc.returncode == 0 else [proc.stdout[-500:]]
        print(f"{nom:32} {n:2} pièce(s)  {etat}")
        for e in erreurs:
            print(f"    - {e}")
        echec |= bool(erreurs)
    print(f"\n{len(variantes)} variantes dans {args.sortie}")
    return 1 if echec else 0


if __name__ == "__main__":
    sys.exit(main())
