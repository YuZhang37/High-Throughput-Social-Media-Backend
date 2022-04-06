from gatekeeper.constants import GATEKEEPER_PREFIX
from utils.redisUtils.redis_client import RedisClient


class GateKeeper:

    @classmethod
    def get(cls, gk_name):
        name = GATEKEEPER_PREFIX.format(gk_name=gk_name)
        conn = RedisClient.get_connection()
        if not conn.exists(name):
            return {
                'percentage': 0,
                'description': '',
                'bias': 0,
            }
        hash_value = conn.hgetall(name)
        return {
            'percentage': int(hash_value.get(b'percentage', 0)),
            'description': hash_value.get(b'description', ''),
            'bias': int(hash_value.get(b'bias', 0)),
        }

    @classmethod
    def set_kv(cls, gk_name, key, value):
        name = GATEKEEPER_PREFIX.format(gk_name=gk_name)
        conn = RedisClient.get_connection()
        conn.hset(name, key, value)

    @classmethod
    def is_switch_on(cls, gk_name):
        percentage = cls.get(gk_name).get('percentage')
        return percentage == 100

    @classmethod
    def in_gk(cls, gk_name, user_id):
        hash_value = cls.get(gk_name)
        result = ((user_id + hash_value.get('bias')) % 100) \
            < hash_value.get('percentage')
        return result
