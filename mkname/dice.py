"""
roll
~~~~

Functions that simulate rolling dice using common dice naming syntax.
"""
import yadr                                 # type: ignore


def roll(code: str) -> int:
    """Roll dice."""
    return yadr.roll(code)
