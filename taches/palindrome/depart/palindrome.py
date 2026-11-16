def est_palindrome(texte):
    """Vrai si texte se lit pareil dans les deux sens."""
    propre = texte.replace(" ", "")
    return propre == propre[::-1]
