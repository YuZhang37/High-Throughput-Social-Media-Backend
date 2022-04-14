from django.conf import settings

NEWSFEED_FANOUT_BATCH_SIZE = 1000 if not settings.TESTING else 3
NEWSFEED_FANOUT_BATCH_NUM_LIMIT = 1000 if not settings.TESTING else 3
