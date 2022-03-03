from django.conf import settings
from django.core.cache import caches

from twitter.cache import OBJECT_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class MemcachedService:

    @classmethod
    def get_object_from_cache(cls, model_class, object_id):
        key = OBJECT_PATTERN.format(
            class_name=model_class.__name__, object_id=object_id
        )
        value = cache.get(key)
        if value is not None:
            return value
        # don't need try and except User.DoesNotExist, if user doesn't exist
        # throw out an exception
        value = model_class.objects.get(id=object_id)
        cache.set(key, value)
        return value

    @classmethod
    def invalidate_object(cls, model_class, object_id):
        key = OBJECT_PATTERN.format(
            class_name=model_class.__name__, object_id=object_id
        )
        cache.delete(key)
