def appliquer_remise(montant, pourcentage):
    """Applique une remise exprimée en pourcentage entier (10 = 10 %)."""
    return montant * (1 - pourcentage / 100)
