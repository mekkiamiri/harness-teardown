def fusionner(intervalles):
    """Fusionne des intervalles fermés [debut, fin] qui se chevauchent ou se touchent."""
    resultat = []
    for debut, fin in sorted([list(i) for i in intervalles]):
        if resultat and debut <= resultat[-1][1]:
            resultat[-1][1] = max(resultat[-1][1], fin)
        else:
            resultat.append([debut, fin])
    return resultat
