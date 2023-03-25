"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""
import random

from secret_sharing import share_secret, reconstruct_secret, Share, FIELD_MODULUS


def test_share_secret():
    assert len(share_secret(5, 2)) == 2


# Share secret
def test_share_secret_1():
    secret = 42
    num_shares = 1
    shares = share_secret(secret, num_shares)
    assert len(shares) == num_shares
    assert shares[0].value == secret % FIELD_MODULUS


def test_share_secret_2():
    secret = 1234
    num_shares = 5
    shares = share_secret(secret, num_shares)
    assert len(shares) == num_shares
    assert sum([share.value for share in shares]) % FIELD_MODULUS == secret % FIELD_MODULUS


def test_share_secret_3():
    secret = 9876
    num_shares = 1000
    shares = share_secret(secret, num_shares)
    assert len(shares) == num_shares
    assert sum([share.value for share in shares]) % FIELD_MODULUS == secret % FIELD_MODULUS


# Reconstruct secret
def test_reconstruct_secret_1():
    shares = []
    assert reconstruct_secret(shares) == 0


def test_reconstruct_secret_2():
    shares = [Share(1), Share(2), Share(3), Share(4)]
    assert reconstruct_secret(shares) == sum([share.value for share in shares]) % FIELD_MODULUS


def test_reconstruct_secret_3():
    shares = [Share(random.randint(0, FIELD_MODULUS)) for _ in range(10000)]
    assert reconstruct_secret(shares) == sum([share.value for share in shares]) % FIELD_MODULUS
