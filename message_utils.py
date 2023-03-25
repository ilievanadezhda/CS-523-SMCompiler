"""
Communication-related helper models and methods.
"""
from __future__ import annotations

import json

from json_utils import json_serialize
from secret_sharing import Share

SECRET_SHARE_LABEL = "Secret_Share_"
RESULT_SHARE_LABEL = "Result_Share_"
PUBLISH_RESULT_LABEL = "Publish_Result"
BEAVER_CONST_SHARE_LABEL = "Beaver_Const_Share_"
BEAVER_CONST_RESULT_LABEL = "Beaver_Const_Result_"


class Message:
    """ Message class for exchanging an int value. """

    def __init__(self, value: int):
        self.value = value

    def serialize(self):
        return json_serialize(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    @staticmethod
    def deserialize(serialized) -> Message:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        return Message(dict_obj['value'])


class ShareMessage:
    """ Message class for exchanging a share of a secret. """

    def __init__(self, id: bytes, value_share: Share):
        self.id = id.decode()
        self.share = value_share

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.id)})"

    def serialize(self):
        return json_serialize(self)

    @staticmethod
    def deserialize(serialized) -> ShareMessage:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        share_obj = Share(dict_obj['share']['value'])
        return ShareMessage(dict_obj['id'].encode(), share_obj)


class ResultShareMessage:
    """ Message class for exchanging a share of a result. """

    def __init__(self, result_share: Share):
        self.share = result_share

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.share.value)})"

    def serialize(self):
        return json_serialize(self)

    @staticmethod
    def deserialize(serialized) -> ResultShareMessage:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        share_obj = Share(dict_obj['share']['value'])
        return ResultShareMessage(share_obj)


class BeaverConstShareMessage:
    """ Message class for exchanging a share of a beaver constant => (x-a), (y-b). """

    def __init__(self, x_part: Share, y_part: Share):
        self.x_part = x_part
        self.y_part = y_part

    def serialize(self):
        return json_serialize(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    @staticmethod
    def deserialize(serialized) -> BeaverConstShareMessage:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        share_x = Share(dict_obj['x_part']['value'])
        share_y = Share(dict_obj['y_part']['value'])
        return BeaverConstShareMessage(share_x, share_y)


class BeaverConstResultMessage:
    """ Message class for exchanging a beaver constant. """

    def __init__(self, x_part: int, y_part: int):
        self.x_part = x_part
        self.y_part = y_part

    def serialize(self):
        return json_serialize(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    @staticmethod
    def deserialize(serialized) -> BeaverConstResultMessage:
        """Restore object from its serialized representation."""
        dict_obj = json.loads(serialized)
        return BeaverConstResultMessage(dict_obj['x_part'], dict_obj['y_part'])
