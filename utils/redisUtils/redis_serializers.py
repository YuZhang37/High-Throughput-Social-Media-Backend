from django.core import serializers
from utils.redisUtils.json_encoder import JSONEncoder


class RedisModelSerializer:

    @classmethod
    def serialize(cls, obj):
        serialized_data = serializers.serialize('json', [obj], cls=JSONEncoder)
        return serialized_data

    @classmethod
    def deserialize(cls, data):
        objs = serializers.deserialize('json', data)
        model_obj = list(objs)[0].object
        return model_obj
