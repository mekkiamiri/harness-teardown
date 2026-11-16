def est_palindrome(texte):
    """Vrai si texte se lit pareil dans les deux sens (casse, espaces et ponctuation ignorés)."""
    propre = [c.lower() for c in texte if c.isalnum()]
    return propre == propre[::-1]
