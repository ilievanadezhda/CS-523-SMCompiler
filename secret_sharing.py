"""
Secret sharing scheme.
"""

from __future__ import annotations

from random import randint
from typing import List

import jsonpickle

FIELD_MODULUS = 2003


class Share:
    """
    A secret share in a finite field.
    """

    # After each operation we can do mod FIELD_MODULUS, but I don't think it's necessary.
    # For example Share((self.value + other.value) % self.FIELD_MOD))
    # It would not change much other than the fact that the numbers would be smaller.

    def __init__(self, value, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value % FIELD_MODULUS

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __add__(self, other):
        return Share((self.value + other.value) % FIELD_MODULUS)

    def __sub__(self, other):
        return Share((self.value - other.value) % FIELD_MODULUS)

    def __mul__(self, other):
        return Share((self.value * other.value) % FIELD_MODULUS)

    def __hash__(self):
        return hash(self.value)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        raise jsonpickle.encode(self)

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        raise jsonpickle.decode(serialized, classes=Share)


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = [Share(randint(0, FIELD_MODULUS - 1)) for _ in range(num_shares - 1)]
    shares.append(Share((secret - sum([share.value for share in shares])) % FIELD_MODULUS))
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum([share.value for share in shares]) % FIELD_MODULUS

# Feel free to add as many methods as you want.
