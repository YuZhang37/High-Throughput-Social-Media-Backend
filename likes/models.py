from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.services import UserService


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id',)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together will also create an index
        # https://stackoverflow.com/questions/27784701/
        # why-does-django-create-an-index-on-a-unique-field-explicitly
        unique_together = (('user', 'content_type', 'object_id'), )
        index_together = (('content_type', 'object_id', 'created_at'), )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )

    @property
    def cached_user(self):
        user = UserService.get_user_from_cache(self.user_id)
        return user
