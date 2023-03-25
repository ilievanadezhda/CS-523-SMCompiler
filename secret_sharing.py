"""
Secret sharing scheme.
"""

from __future__ import annotations

import json
from random import randint
from typing import List

from json_utils import json_serialize

FIELD_MODULUS = 2003


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value % FIELD_MODULUS

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"
    
    def __add__(self, other):
        if isinstance(other, Share) or isinstance(other, Constant):
            return Share((self.value + other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Unsupported opperation")
    
    def __sub__(self, other):
        if isinstance(other, Share) or isinstance(other, Constant):
            return Share((self.value - other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Unsupported opperation")
    
    def __mul__(self, other):
        if isinstance(other, Constant):
            return Share((self.value * other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Beaver triplets! / Unsupported opperation")
    
    def __hash__(self):
        return hash(self.value)
    
    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json_serialize(self)

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        return Share(dict_obj['value'])


class Constant:
    """
    A constant in a finite field.
    """

    def __init__(self, value, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value % FIELD_MODULUS

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"
    
    def __add__(self, other):
        if isinstance(other, Share):
            return Share((self.value + other.value) % FIELD_MODULUS)
        elif isinstance(other, Constant):
            return Constant((self.value + other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Unsupported opperation")
    
    def __sub__(self, other):
        if isinstance(other, Share):
            return Share((self.value - other.value) % FIELD_MODULUS)
        elif isinstance(other, Constant):
            return Constant((self.value - other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Unsupported opperation")

    def __mul__(self, other):
        if isinstance(other, Share):
            return Share((self.value * other.value) % FIELD_MODULUS)
        elif isinstance(other, Constant):
            return Constant((self.value * other.value) % FIELD_MODULUS)
        else:
            raise TypeError("Unsupported opperation")

    def __hash__(self):
        return hash(self.value)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json_serialize(self)

    @staticmethod
    def deserialize(serialized) -> Constant:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        return Constant(dict_obj['value'])


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = [Share(randint(0, FIELD_MODULUS - 1)) for _ in range(num_shares - 1)]
    shares.append(Share((secret - sum([share.value for share in shares])) % FIELD_MODULUS))
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum([share.value for share in shares]) % FIELD_MODULUS
