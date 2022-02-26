from django.db import models

from django.contrib.auth.models import AbstractUser


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
    if hasattr(user, '_cached_userprofile'):
        return getattr(user, '_cached_userprofile'), False
    userprofile, created = UserProfile.objects.get_or_create(user=user)
    setattr(user, '_cached_userprofile', userprofile)
    return userprofile, created


User.get_or_create_userprofile = property(get_or_create_userprofile)

