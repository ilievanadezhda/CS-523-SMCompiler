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

    # After each operation we can do mod FIELD_MODULUS, but I don't think it's necessary.
    # For example Share((self.value + other.value) % self.FIELD_MOD))
    # It would not change much other than the fact that the numbers would be smaller.

    def __init__(self, value, leader_flag = False, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value % FIELD_MODULUS
        self.leader_flag = leader_flag

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __add__(self, other):
        if isinstance(other, Share):
            return Share((self.value + other.value) % FIELD_MODULUS, self.leader_flag)
        elif isinstance(other, Constant):
            if self.leader_flag:
                return Share((self.value + other.value) % FIELD_MODULUS, self.leader_flag)
            else:
                return Share(self.value % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

    def __sub__(self, other):
        if isinstance(other, Share):
            return Share((self.value - other.value) % FIELD_MODULUS, self.leader_flag)
        elif isinstance(other, Constant):
            if self.leader_flag:
                return Share((self.value - other.value) % FIELD_MODULUS, self.leader_flag)
            else:
                return Share(self.value % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

    def __mul__(self, other):
        if isinstance(other, Share) or isinstance(other, Constant):
            return Share((self.value * other.value) % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

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

    def __init__(self, value, leader_flag=False, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value % FIELD_MODULUS
        self.leader_flag = leader_flag

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __add__(self, other):
        if isinstance(other, Share):
            if self.leader_flag:
                return Share((self.value + other.value) % FIELD_MODULUS, self.leader_flag)
            else:
                return Share(other.value % FIELD_MODULUS, self.leader_flag)
        elif isinstance(other, Constant):
            return Constant((self.value + other.value) % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

    def __sub__(self, other):
        if isinstance(other, Share):
            if self.leader_flag:
                return Share((self.value - other.value) % FIELD_MODULUS, self.leader_flag)
            else:
                return Share((-other.value) % FIELD_MODULUS, self.leader_flag)
        elif isinstance(other, Constant):
            return Constant((self.value - other.value) % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

    def __mul__(self, other):
        if isinstance(other, Share):
            return Share((self.value * other.value) % FIELD_MODULUS, self.leader_flag)
        elif isinstance(other, Constant):
            return Constant((self.value * other.value) % FIELD_MODULUS, self.leader_flag)
        else:
            raise TypeError("This operation is not supported!")

    def __hash__(self):
        return hash(self.value)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json_serialize(self)

    @staticmethod
    def deserialize(serialized) -> Constant:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        return Constant(dict_obj['value'], dict_obj['leader_flag'])


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = [Share(randint(0, FIELD_MODULUS - 1)) for _ in range(num_shares - 1)]
    shares.append(Share((secret - sum([share.value for share in shares])) % FIELD_MODULUS))
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum([share.value for share in shares]) % FIELD_MODULUS
