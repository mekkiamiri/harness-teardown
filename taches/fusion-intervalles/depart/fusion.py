def fusionner(intervalles):
    """Fusionne des intervalles fermés [debut, fin]."""
    resultat = []
    for debut, fin in intervalles:
        if resultat and debut < resultat[-1][1]:
            resultat[-1][1] = max(resultat[-1][1], fin)
        else:
            resultat.append([debut, fin])
    return resultat
