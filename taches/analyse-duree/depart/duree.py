def en_minutes(texte):
    """'1h30m' -> 90."""
    heures, _, reste = texte.partition("h")
    minutes = reste.rstrip("m")
    return int(heures) * 60 + int(minutes or 0)
