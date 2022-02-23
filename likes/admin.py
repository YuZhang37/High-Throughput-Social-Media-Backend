from django.contrib import admin

from likes.models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'content_type',
        'object_id',
        'content_object',
        'created_at'
    ]
    date_hierarchy = 'created_at'
    list_filter = ['content_type', ]
