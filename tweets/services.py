from tweets.models import TweetPhoto


class TweetPhotoService:

    @classmethod
    def create_tweet_photos(cls, tweet, files):
        tweet_photos = []
        for index, file in enumerate(files):
            instance = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                order=index,
                file=file,
            )
            tweet_photos.append(instance)
        TweetPhoto.objects.bulk_create(tweet_photos)
