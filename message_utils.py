"""
Communication-related helper models and methods.
"""
from typing import Optional

import jsonpickle

from secret_sharing import Share

SECRET_SHARE_LABEL = "Secret_Share"
RESULT_SHARE_LABEL = "Result_Share"
PUBLISH_RESULT_LABEL = "Publish_Result"


class Message:

    def __init__(self, value: Optional[int]):
        self.value = value

    def json_rep(self):
        return jsonpickle.encode(self)


class ShareMessage(Message):

    def __init__(self, id: bytes, value_share: Share):
        self.id = id
        self.share = value_share
        super().__init__(None)


class ResultShareMessage(Message):

    def __init__(self, result_share: Share):
        self.share = result_share
        super().__init__(None)
