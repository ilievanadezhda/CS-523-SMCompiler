"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional, List

ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
    ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return AddOperation(left=self, right=other)

    def __sub__(self, other):
        return AddOperation(left=self, right=MultOperation(left=other, right=Scalar(-1)))

    def __mul__(self, other):
        return MultOperation(left=self, right=other)

    def __hash__(self):
        return hash(self.id)

    # Feel free to add as many methods as you like.


class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            value: Optional[int] = None,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )

    # Feel free to add as many methods as you like.


# Feel free to add as many classes as you like.
class AddOperation(Expression):
    """ Represents an addition operation of two other expressions. """

    def __init__(self, left: Expression, right: Expression, id: Optional[bytes] = None):
        self.left = left
        self.right = right
        super().__init__(id)

    def __repr__(self):
        return f"({repr(self.left)} + {repr(self.right)})"


class MultOperation(Expression):
    """ Represents a multiplication operation of two other expressions. """

    def __init__(self, left: Expression, right: Expression, id: Optional[bytes] = None):
        self.left = left
        self.right = right
        super().__init__(id)

    def __repr__(self):
        return f"{repr(self.left)} * {repr(self.right)}"


def count_num_secrets(expr: Expression) -> int:
    """ Returns the total number of secrets the provided expression. """
    if isinstance(expr, AddOperation) or isinstance(expr, MultOperation):
        return count_num_secrets(expr.left) + count_num_secrets(expr.right)
    if isinstance(expr, Secret):
        return 1
    return 0


def collect_secret_ids(expr: Expression) -> List[bytes]:
    """ Returns list of ids of all secrets in the provided expression. """
    if isinstance(expr, AddOperation) or isinstance(expr, MultOperation):
        return collect_secret_ids(expr.left) + collect_secret_ids(expr.right)
    if isinstance(expr, Secret):
        return [expr.id]
    return []
