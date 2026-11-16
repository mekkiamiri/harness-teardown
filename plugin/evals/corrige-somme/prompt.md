---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Le test `somme_intervalle(1, 3) == 6` échoue avec ce code. Quel est le bug et quel est le correctif ?

```python
def somme_intervalle(a, b):
    """Somme des entiers de a à b inclus. Si a > b, renvoie 0."""
    return sum(range(a, b))
```
