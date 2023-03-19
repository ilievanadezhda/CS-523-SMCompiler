"""
Communication-related helper models and methods.
"""
from __future__ import annotations

import json
from typing import Optional

from json_utils import json_serialize
from secret_sharing import Share

SECRET_SHARE_LABEL = "Secret_Share_"
RESULT_SHARE_LABEL = "Result_Share_"
PUBLISH_RESULT_LABEL = "Publish_Result"


class Message:

    def __init__(self, value: Optional[int]):
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
