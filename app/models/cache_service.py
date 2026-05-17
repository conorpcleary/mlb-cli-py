"""
Caching service module for the MLB CLI application.
Uses Redis to store API responses with specific TTL policies.
"""
import json
import redis

from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

try:
    # pylint: disable=invalid-name
    _redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )
except Exception:  # pylint: disable=broad-exception-caught
    _redis_client = None


def get_cached_data(key):
    """
    Retrieves data from the cache.

    Args:
        key (str): The cache key.

    Returns:
        dict/list/None: The cached data if found and valid, else None.
    """
    if _redis_client is None:
        return None

    try:
        data = _redis_client.get(key)
        return json.loads(data) if data else None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_cached_data(key, data, ttl=None):
    """
    Stores data in the cache.

    Args:
        key (str): The cache key.
        data (dict/list): The data to cache.
        ttl (int, optional): Time-to-live in seconds.
    """
    if _redis_client is None:
        return

    try:
        json_data = json.dumps(data)
        if ttl:
            _redis_client.setex(key, ttl, json_data)
        else:
            _redis_client.set(key, json_data)
    except Exception:  # pylint: disable=broad-exception-caught
        pass
