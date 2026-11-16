#!/usr/bin/env python3
# teardown: id=hook-rappel-session · étiquette=compense · catégorie=contexte injecté
"""SessionStart : rappelle à l'agent comment le kata est organisé et comment lancer les tests.

Ce que le hook écrit sur la sortie standard (code 0) est ajouté au contexte de l'agent.
"""
print(
    "Conventions des katas de l'équipe :\n"
    "- l'énoncé est dans ENONCE.md, il fait foi ;\n"
    "- les tests sont dans tests/ ; on les lance à la racine avec : "
    "python3 -m unittest discover -s tests -t .\n"
    "- on corrige le code source, jamais les tests ;\n"
    "- l'outil `kata-echecs` résume les tests en échec, s'il est disponible."
)
