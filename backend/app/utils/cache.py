import json
import redis
from app.utils.config import REDIS_URL

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def cache_get(key):
    try:
        data = get_redis().get(key)
        if data:
            return json.loads(data)
        return None
    except redis.ConnectionError:
        return None


def cache_set(key, value, ttl=300):
    try:
        get_redis().setex(key, ttl, json.dumps(value, default=str))
    except redis.ConnectionError:
        pass


def cache_delete(key):
    try:
        get_redis().delete(key)
    except redis.ConnectionError:
        pass
