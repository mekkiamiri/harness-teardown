class CacheLRU:
    """Cache de taille fixe qui évince l'élément utilisé il y a le plus longtemps."""

    def __init__(self, capacite):
        self.capacite = capacite
        self.donnees = {}

    def lire(self, cle):
        return self.donnees.get(cle)

    def ecrire(self, cle, valeur):
        self.donnees[cle] = valeur
        if len(self.donnees) > self.capacite:
            plus_recent = list(self.donnees)[-1]
            del self.donnees[plus_recent]
