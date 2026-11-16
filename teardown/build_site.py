"""Recopie les pièces de teardown/pieces.json dans la page de démo (docs/index.html).

Usage :
    python3 teardown/build_site.py           # met la page à jour
    python3 teardown/build_site.py --check   # échoue si la page n'est pas à jour (CI)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGE = RACINE / "docs" / "index.html"
PIECES = RACINE / "teardown" / "pieces.json"
BLOC = re.compile(r"(/\*PIECES\*/).*?(/\*FIN-PIECES\*/)", re.S)
CHAMPS = ("id", "nom", "fait", "type", "etiquette", "categorie", "hypothese", "prediction", "discussion", "mesure")


def donnees_page() -> str:
    pieces = json.loads(PIECES.read_text(encoding="utf-8"))["pieces"]
    return json.dumps([{k: p[k] for k in CHAMPS} for p in pieces], ensure_ascii=False, indent=1)


def page_a_jour(html: str) -> str:
    if not BLOC.search(html):
        raise ValueError("marqueurs /*PIECES*/ … /*FIN-PIECES*/ absents de la page")
    return BLOC.sub(lambda m: m.group(1) + donnees_page() + m.group(2), html)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    html = PAGE.read_text(encoding="utf-8")
    neuf = page_a_jour(html)
    if args.check:
        if neuf != html:
            print("docs/index.html n'est pas à jour : lancer python3 teardown/build_site.py", file=sys.stderr)
            return 1
        print("page à jour")
        return 0
    PAGE.write_text(neuf, encoding="utf-8")
    print(f"écrit {PAGE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
