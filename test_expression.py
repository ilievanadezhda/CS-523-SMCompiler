"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import (Secret, Scalar, AddOperation, MultOperation, count_num_secrets, count_num_mults)


# Example test, you can adapt it to your needs.
def test_expr_construction_1():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = a + b + c
    assert repr(expr) == "((Secret(1) + Secret(2)) + Secret(3))"

def test_expr_construction_2():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c * Scalar(4) + Scalar(3)
    assert repr(expr) == "((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3))"

# Count number of secrets tests

def test_num_secrets_1():
    """
    f(a1, a2, a3, b) = a1 + a2 + a3 + b
    """
    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secrets[0]: 3, alice_secrets[1]: 14, alice_secrets[2]: 2},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secrets[0] + alice_secrets[1] + alice_secrets[2] + bob_secret
    assert count_num_secrets(expr) == 4


def test_num_secrets_2():
    """
    f(a, b) = a * b * (15 + 15 * 3)
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secret + bob_secret * (Scalar(15) + Scalar(15) * Scalar(3))
    assert count_num_secrets(expr) == 2


# Count number of multiplications tests

def test_num_mults_1():
    """
    f(a, b) = a * b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secret * bob_secret 
    assert count_num_mults(expr) == 1

def test_num_mults_2():
    """
    f(a, b) = a * 4
    """
    alice_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
    }

    expr = alice_secret * Scalar(3)
    assert count_num_mults(expr) == 0

def test_num_mults_3():
    """
    f(a, b) = a * (4 + 3)
    """
    alice_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
    }

    expr = alice_secret * (Scalar(4) + Scalar(3))
    assert count_num_mults(expr) == 0

def test_num_mults_4():
    expr = Scalar(2) * Scalar(3) * (Scalar(2) + Scalar(3)*Scalar(4))
    assert count_num_mults(expr) == 0

def test_num_mults_5():
    """
    f(a, b) = a + b * (15 + 15 * 3)
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secret + bob_secret * (Scalar(15) + Scalar(15) * Scalar(3))
    assert count_num_mults(expr) == 0
