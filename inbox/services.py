from notifications.signals import notify

from comments.models import Comment
from likes.models import Like


class NotificationService:

    @classmethod
    def send_like_notification(cls, like: Like):
        actor = like.user
        target = like.content_object
        if actor == target.user:
            return
        model_name = like.content_type.model
        notify.send(
            sender=actor,
            recipient=target.user,
            verb=f"liked your {model_name}: ",
            target=target,
        )

    @classmethod
    def send_comment_notification(cls, comment: Comment):
        actor = comment.user
        target = comment.tweet
        if actor == target.user:
            return
        notify.send(
            sender=actor,
            recipient=target.user,
            verb="liked your tweet: ",
            target=target
        )
