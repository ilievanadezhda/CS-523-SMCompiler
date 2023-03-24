"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar, count_num_secrets, collect_secret_ids


# Example test, you can adapt it to your needs.

def test_pre_process():
    alice_secret = Secret()
    bob_secret = Secret()

    expr = (
            alice_secret + bob_secret
    )
    assert count_num_secrets(expr) == 2
    ids_list = collect_secret_ids(expr)
    assert alice_secret.id in ids_list
    assert bob_secret.id in ids_list


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


def test_num_secrets_1():
    """
    f(a1, a2, a3, b) = a1 + a2 + a3 + b
    """
    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secret = Secret()

    expr = alice_secrets[0] + alice_secrets[1] + alice_secrets[2] + bob_secret
    assert count_num_secrets(expr) == 4


def test_num_secrets_2():
    """
    f(a, b) = a * b * (15 + 15 * 3)
    """
    alice_secret = Secret()
    bob_secret = Secret()

    expr = alice_secret + bob_secret * (Scalar(15) + Scalar(15) * Scalar(3))
    assert count_num_secrets(expr) == 2
