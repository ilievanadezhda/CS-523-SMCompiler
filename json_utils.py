import json


def simple_json_encoder(obj):
    """ Returns dict representation of the provided object. """
    return obj.__dict__


def json_serialize(obj):
    """ Returns json representation of the provided object. """
    return json.dumps(obj, default=simple_json_encoder)
