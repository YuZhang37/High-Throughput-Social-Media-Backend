import json

from django.conf import settings
from django.core import serializers

from django_hbase.models import HBaseModel
from utils.redisUtils.constants import REDIS_ENCODING
from utils.redisUtils.json_encoder import JSONEncoder


class RedisSerializerService:

    @classmethod
    def get_serializer(cls, gk_class, gk_name):
        if gk_class.is_switch_on(gk_name):
            serializer = RedisHBaseSerializer
        else:
            serializer = RedisModelSerializer
        return serializer


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


class RedisHBaseSerializer:

    @classmethod
    def get_hbase_model(cls, model_name):
        for subclass in HBaseModel.__subclasses__():
            if subclass.__name__ == model_name:
                return subclass
        raise Exception(f'hbase model of {model_name} does not exist')

    @classmethod
    def serialize(cls, obj):
        data = {'model_name': obj.__class__.__name__}
        for key in obj.get_class_fields():
            value = obj.__dict__.get(key)
            data[key] = value
        return json.dumps(data)

    @classmethod
    def deserialize(cls, serialized_data):
        data = json.loads(serialized_data)
        hbase_model = cls.get_hbase_model(data['model_name'])
        del data['model_name']
        obj = hbase_model(**data)
        return obj


class IntegerSerializer:

    @classmethod
    def serialize(cls, num):
        return str(num).encode(encoding=REDIS_ENCODING)

    @classmethod
    def deserialize(cls, num_bytes):
        num = int(num_bytes.decode(encoding=REDIS_ENCODING))
        return num
