from message_utils import Message, ShareMessage, ResultShareMessage, BeaverConstShareMessage, BeaverConstResultMessage
from secret_sharing import Share, Constant


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


def test_serialize_constant():
    constant = Constant(6)
    serialized = constant.serialize()
    deserialized = Constant.deserialize(serialized)

    assert deserialized.value == constant.value


def test_serialize_beaver_const_share_message():
    beaver_const_share = BeaverConstShareMessage(Share(2), Share(5))
    serialized = beaver_const_share.serialize()
    deserialized = BeaverConstShareMessage.deserialize(serialized)

    assert deserialized.x_part.value == 2
    assert deserialized.y_part.value == 5


def test_serialize_beaver_const_result_message():
    beaver_const_result = BeaverConstResultMessage(2, 5)
    serialized = beaver_const_result.serialize()
    deserialized = BeaverConstResultMessage.deserialize(serialized)

    assert deserialized.x_part == 2
    assert deserialized.y_part == 5
