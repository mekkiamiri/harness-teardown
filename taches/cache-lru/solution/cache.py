from collections import OrderedDict


class CacheLRU:
    """Cache de taille fixe qui évince l'élément utilisé il y a le plus longtemps."""

    def __init__(self, capacite):
        self.capacite = capacite
        self.donnees = OrderedDict()

    def lire(self, cle):
        if cle not in self.donnees:
            return None
        self.donnees.move_to_end(cle)
        return self.donnees[cle]

    def ecrire(self, cle, valeur):
        self.donnees[cle] = valeur
        self.donnees.move_to_end(cle)
        if len(self.donnees) > self.capacite:
            self.donnees.popitem(last=False)
