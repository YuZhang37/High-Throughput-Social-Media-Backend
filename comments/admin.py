from django.contrib import admin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tweet', 'created_at', 'updated_at', 'content')
    date_hierarchy = 'created_at'
