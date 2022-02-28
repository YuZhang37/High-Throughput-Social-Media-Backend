from django.contrib import admin

from tweets.models import Tweet, TweetPhoto


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = [
        "id",
        "user",
        "created_at",
        "content",
    ]


@admin.register(TweetPhoto)
class TweetPhoto(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = [
        'id',
        'user',
        'tweet',
        'file',
        'status',
        'order',
        'created_at',
        'has_deleted',
        'deleted_at',
    ]

    # the default fields are editable fields from list_display
    # fields = (
    #     'user',
    #     'tweet',
    #     'file',
    #     'status',
    #     'order',
    #     'has_deleted',
    # )
    # blank=True can also solve the problem of not wanting to specify deleted_at

    list_filter = ('status', 'has_deleted')
