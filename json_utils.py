import json


def simple_json_encoder(obj):
    return obj.__dict__


def json_serialize(obj):
    return json.dumps(obj, default=simple_json_encoder)
