# harness-teardown

**Le harnais d'un agent est-il mort ? On démonte un plugin d'équipe pièce par pièce, sur trois tailles de modèle, et on mesure ce que chaque pièce apporte encore.**

> Support du talk « Le harnais est-il mort ? Je l'ai démonté pièce par pièce » (Tools-in-Action, proposé à Devoxx France 2027).

- **Page de démo** (classez vous-même les pièces) : <https://mekkiamiri.github.io/harness-teardown/>
- **Slides** : <https://mekkiamiri.github.io/harness-teardown/slides/>

## L'idée

Chaque pièce d'un harnais encode une hypothèse sur ce que le modèle ne sait pas faire seul ([Anthropic, 24/03/2026](https://www.anthropic.com/engineering/harness-design-long-running-apps)). Ce dépôt classe chaque pièce dans l'une de deux familles :

| Étiquette | La pièce… | Exemples dans le plugin |
|---|---|---|
| **compense** | compense une limite supposée du modèle | procédure détaillée, planification imposée, micro-outil, sous-agent, contexte injecté, retour automatique des tests |
| **gouverne** | impose une règle, une sécurité, une vérification | hook qui bloque `rm -r` ou `git push`, hook qui interdit de toucher aux tests, hook qui refuse la fin tant que les tests échouent, évals |

Une onzième pièce, **témoin**, n'a aucun effet : son Δ mesure le bruit du banc.

**Hypothèse du talk** (pas un résultat) : sur les gros modèles, les pièces qui compensent n'apportent plus rien ; celles qui gouvernent gardent leur valeur. Si la mesure dit le contraire, le talk le dira.

## Ce qui tourne

| Élément | Où | État |
|---|---|---|
| Plugin d'équipe d'exemple `kata-fixer` (2 skills, 1 sous-agent, 1 micro-outil, 5 hooks, évals) | [`plugin/`](plugin/) | fait, `claude plugin validate --strict` passe en local |
| Manifeste des pièces (10 réelles + 1 témoin) : étiquette, hypothèse encodée, comment la retirer, prédiction | [`teardown/pieces.json`](teardown/pieces.json) | fait |
| Générateur de variantes (complet, vide, sans chaque pièce) + validation | [`teardown/variants.py`](teardown/variants.py) | fait : 13 variantes, toutes valides ; refuse d'écrire dans le dépôt ou un dossier étranger |
| 6 katas Python avec tests visibles, tests cachés et solution de référence | [`taches/`](taches/), [`teardown/taches.py`](teardown/taches.py) | fait : chaque kata échoue au départ et passe avec la solution |
| Lanceur des exécutions (plan, dossier jetable + permissions strictes par défaut, conteneur en option, lecture du flux `stream-json`, refus et blocages comptés, modèle servi vérifié, essais écartés) | [`teardown/run.py`](teardown/run.py) | testé avec une fausse CLI, puis lancé contre de vrais modèles (premiers passages dans [`resultats/banc-local-premier-passage/`](resultats/banc-local-premier-passage/)) |
| Noteur : tableau « pièce retirée → delta », dispersion entre essais, seuil de bruit validé par le témoin | [`teardown/score.py`](teardown/score.py) | fait, testé sur des données synthétiques |
| Protocole (3 tailles de modèle) | [`PROTOCOLE.md`](PROTOCOLE.md) | fait |
| **Mesures sur 3 tailles de modèle** | `resultats/` | **à mesurer** |

Aucun chiffre n'est publié avant d'avoir été mesuré. Les tests du noteur utilisent des données synthétiques, marquées comme telles.

## Lancer

Python 3.10+ suffit, sans dépendance. Aucune commande ci-dessous n'appelle un modèle.

```bash
python3 -m unittest discover -s tests     # tout le banc (81 tests)
```

Et pour voir chaque morceau :

```bash
python3 teardown/variants.py              # génère et valide les 13 variantes dans build/variantes
python3 teardown/taches.py --check        # les 6 katas sont faisables et vérifiables
python3 teardown/run.py                   # le plan des exécutions, sans rien lancer
python3 teardown/score.py                 # le tableau vide : « à mesurer » partout
```

Les exécutions réelles (appels de modèle) se lancent avec `--executer` : chaque essai tourne dans un dossier jetable sous `$TMPDIR` (copie du kata et de la variante), et la CLI d'agent n'y exécute que les outils d'une liste blanche (`--permission-mode dontAsk` : lecture, écriture, recherche, et `Bash` limité aux commandes de test). Tout le reste est refusé, et chaque refus est compté comme incident. Voir [PROTOCOLE.md](PROTOCOLE.md). La garde des commandes du plugin est contournable (comme toute garde par motifs) : la liste blanche est la vraie barrière.

```bash
python3 teardown/run.py --taches panier-remise --variantes complet,sans-hook-garde-tests --essais 1 --executer
```

## Ce qui reste à faire

- Lancer le protocole sur trois tailles de modèle et publier `resultats/` (prévu avant la conférence).
- Trouver un accès à un troisième modèle, plus petit : sur le poste de mesure, seuls `claude-sonnet-5-5` et `claude-opus-5-5` sont servis.
- Montrer les erreurs réelles des agents telles quelles, pas seulement les taux.

## Sources du débat

Katz, [« Is the Agent Harness Dead? »](https://www.youtube.com/watch?v=7Y4sbZgBdnc) · Schmid, [« How Foundational Models Became Superhuman in Bash »](https://www.philschmid.de/superhuman-bash) et [« Why Agents Are Soon Only Going to Have 1 Tool »](https://www.philschmid.de/code-mode) · Anthropic, [« Harness design for long-running application development »](https://www.anthropic.com/engineering/harness-design-long-running-apps) · Railway (Angelo Saraceno), [« Skill Issue, Writing /skills to solve agent failures »](https://blog.railway.com/p/skills-issue-writing-skills), 24/06/2026 · Böckeler, [« Harness engineering for coding agent users »](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html).

## Licence

Apache 2.0.
