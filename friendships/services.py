from friendships.models import Friendship


class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship\
            .objects.filter(to_user=user)\
            .prefetch_related('from_user')
        followers = [
            friendship.from_user
            for friendship in friendships
        ]
        return followers

    @classmethod
    def has_followed(cls, from_user, to_user):
        # is_anonymous is property in User and AnonymousUser
        if from_user.is_anonymous or to_user.is_anonymous:
            return False
        return Friendship.objects\
            .filter(from_user=from_user, to_user=to_user)\
            .exists()
