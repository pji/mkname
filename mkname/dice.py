"""
roll
~~~~

Functions that simulate rolling dice using common dice naming syntax.
"""
import random

import yadr                                 # type: ignore


def seed(seed: int) -> None:
    """Seed the random number generator for testing purposes."""
    if isinstance(seed, str):
        seed = bytes(seed, encoding='utf_8')
    if isinstance(seed, bytes):
        seed = int.from_bytes(seed, 'little')
    random.seed(seed)


def roll(code: str) -> int:
    """Roll dice."""
    return yadr.roll(code)
