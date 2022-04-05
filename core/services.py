from django.conf import settings
from django.core.cache import caches

from core.models import UserProfile, User
from twitter.cache import USER_PROFILE_PATTERN
from utils.memcached_services import MemcachedService

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    @classmethod
    def get_user_profile_from_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        value = cache.get(key)
        if value is not None:
            return value, False
        value, created = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, value)
        return value, created

    @classmethod
    def invalidate_user_profile(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)

    @classmethod
    def get_user_from_cache_with_user_id(cls, user_id):
        user = MemcachedService.get_object_from_cache(User, user_id)
        return user
