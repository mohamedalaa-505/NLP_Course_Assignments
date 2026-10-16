"""Normaliser v0: change nothing except case (provided; level 0)."""
LEVEL = 0


def normalize(text):
    """Lower-case Latin letters; Arabic has no case, so it is untouched."""
    return text.lower()
