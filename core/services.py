from django.conf import settings
from django.core.cache import caches

from core.models import User, UserProfile
from twitter.cache import USER_PATTERN, USER_PROFILE_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    @classmethod
    def get_user_from_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        value = cache.get(key)
        if value is not None:
            return value
        # don't need try and except User.DoesNotExist, if user doesn't exist
        # throw out an exception
        value = User.objects.get(id=user_id)
        cache.set(key, value)
        return value

    @classmethod
    def invalidate_user(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        cache.delete(key)

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
