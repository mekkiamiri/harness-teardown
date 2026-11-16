import re

_FORMAT = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?")


def en_minutes(texte):
    """'1h30m' -> 90, '2h' -> 120, '45m' -> 45 ; ValueError sinon."""
    trouve = _FORMAT.fullmatch(texte)
    if not texte or not trouve:
        raise ValueError(f"durée invalide : {texte!r}")
    heures, minutes = trouve.groups()
    return int(heures or 0) * 60 + int(minutes or 0)
