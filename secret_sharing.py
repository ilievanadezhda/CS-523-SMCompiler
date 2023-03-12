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

    def __init__(self, value, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __add__(self, other):
        return Share(self.value + other.value)

    def __sub__(self, other):
        return Share(self.value - other.value)

    def __mul__(self, other):
        return Share(self.value * other.value)

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
    shares = []
    total_value = 0
    for i in range(num_shares - 1):
        share_value = randint(0, FIELD_MODULUS - 1)
        shares.append(Share(share_value))
        total_value += share_value
    shares.append(Share(((secret - total_value) % FIELD_MODULUS)))
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    sum = 0
    for share in shares:
        sum += share.value
    return sum % FIELD_MODULUS

# Feel free to add as many methods as you want.
