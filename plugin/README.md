# kata-fixer

Plugin Claude Code d'exemple, écrit pour être démonté. Il aide un agent à corriger de petits bugs Python dans des katas qui ont des tests.

Chaque composant porte une étiquette dans son en-tête :

- **compense** : il compense une limite supposée du modèle (procédure détaillée, planification imposée, micro-outil, sous-agent, contexte injecté, retour automatique des tests) ;
- **gouverne** : il impose une règle, une sécurité ou une vérification, quel que soit le modèle (hook qui bloque une commande, hook qui refuse la fin tant que les tests échouent, éval).

La liste complète, avec l'hypothèse encodée par chaque pièce, est dans [`../teardown/pieces.json`](../teardown/pieces.json).

Charger le plugin pour une session :

```bash
claude --plugin-dir ./plugin
```

Une pièce **témoin** (`temoin/`) n'est chargée par rien : elle sert à mesurer le bruit du banc.

La garde des commandes (`scripts/garde_commandes.py`) analyse chaque commande avec `shlex`, mais une garde par motifs reste contournable : ce n'est pas une barrière de sécurité, le conteneur du banc en est une.
