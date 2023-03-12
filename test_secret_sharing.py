"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""
from expression import Secret
from expression import count_num_secrets
from secret_sharing import share_secret


def test_share_secret():
    assert len(share_secret(5, 2)) == 2


def test_pre_process():
    alice_secret = Secret()
    bob_secret = Secret()

    expr = (
            alice_secret + bob_secret
    )
    assert count_num_secrets(expr) == 2
