from prix import appliquer_remise


def total(lignes, remise_pct=0):
    """Total du panier, remise comprise, arrondi au centime."""
    brut = sum(prix * quantite for prix, quantite in lignes)
    return round(appliquer_remise(brut, remise_pct), 2)
