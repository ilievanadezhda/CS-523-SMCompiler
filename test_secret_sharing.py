"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret
from expression import count_num_secrets, collect_secret_ids
from message_utils import Message, ShareMessage, ResultShareMessage
from secret_sharing import share_secret, Share


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
