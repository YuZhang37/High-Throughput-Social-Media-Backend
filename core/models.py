from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete, post_save

from core import signals


class User(AbstractUser):
    email = models.EmailField(unique=True)

# the following implementation
# is also compatible for codes using the django user model


class UserProfile(models.Model):

    #  Conceptually, this is similar to a ForeignKey with unique=True,
    #  but the “reverse” side of the relation will directly return
    #  a single object.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    nickname = models.CharField(max_length=255)
    avatar = models.FileField(upload_to='userprofile/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def get_or_create_userprofile(user):
    from core.services import UserService
    if hasattr(user, '_cached_userprofile'):
        return getattr(user, '_cached_userprofile'), False
    userprofile, created = UserService.get_user_profile_from_cache(user_id=user.id)
    setattr(user, '_cached_userprofile', userprofile)
    return userprofile, created


def get_userprofile(user):
    profile, _ = user.get_or_create_userprofile()
    return profile


User.get_or_create_userprofile = get_or_create_userprofile
User.profile = property(get_userprofile)

pre_delete.connect(receiver=signals.user_changed, sender=User)
post_save.connect(receiver=signals.user_changed, sender=User)

pre_delete.connect(receiver=signals.user_profile_changed, sender=UserProfile)
post_save.connect(receiver=signals.user_profile_changed, sender=UserProfile)
