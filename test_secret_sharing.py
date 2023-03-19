"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""
import random

from expression import Secret, count_num_secrets, collect_secret_ids
from message_utils import Message, ShareMessage, ResultShareMessage
from secret_sharing import share_secret, reconstruct_secret, Share, FIELD_MODULUS


def test_share_secret():
    assert len(share_secret(5, 2)) == 2


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


def test_serialize_message():
    message = Message(6)
    serialized = message.serialize()
    deserialized = Message.deserialize(serialized)

    assert deserialized.value == message.value


def test_serialize_share_message():
    message = ShareMessage("test".encode(), Share(11))
    serialized = message.serialize()
    deserialized = ShareMessage.deserialize(serialized)

    assert deserialized.id == message.id
    assert deserialized.share.value == message.share.value


def test_serialize_result_share_message():
    message = ResultShareMessage(Share(6))
    serialized = message.serialize()
    deserialized = ResultShareMessage.deserialize(serialized)

    assert deserialized.share.value == message.share.value


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
