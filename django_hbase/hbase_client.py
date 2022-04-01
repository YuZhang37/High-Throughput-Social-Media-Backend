import happybase
from django.conf import settings


class HBaseClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # if not cls.conn:
        #     cls.conn = happybase.Connection(host=settings.HBASE_HOST)
        # return cls.conn
        return happybase.Connection(host=settings.HBASE_HOST)

