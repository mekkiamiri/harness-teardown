# kata-fixer

Plugin Claude Code d'exemple, écrit pour être démonté. Il aide un agent à corriger de petits bugs Python dans des katas qui ont des tests.

Chaque composant porte une étiquette dans son en-tête :

- **compense** : il compense une limite supposée du modèle (procédure détaillée, planification imposée, micro-outil, sous-agent, contexte injecté) ;
- **gouverne** : il impose une règle, une sécurité ou une vérification, quel que soit le modèle (hook qui bloque une commande, hook qui lance les tests, éval).

La liste complète, avec l'hypothèse encodée par chaque pièce, est dans [`../teardown/pieces.json`](../teardown/pieces.json).

Charger le plugin pour une session :

```bash
claude --plugin-dir ./plugin
```
