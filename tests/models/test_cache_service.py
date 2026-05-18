"""
Unit tests for CacheService.
"""
import unittest
import json
import importlib
from unittest.mock import patch
import redis
from app.models.cache_service import get_cached_data, set_cached_data


class TestCacheService(unittest.TestCase):
    """Test cases for CacheService."""

    @patch('app.models.cache_service._redis_client')
    def test_set_and_get_cache(self, mock_redis):
        """Test basic set and get functionality."""
        mock_redis.get.return_value = json.dumps("value")
        set_cached_data("key", "value")
        mock_redis.set.assert_called_with("key", json.dumps("value"))

        self.assertEqual(get_cached_data("key"), "value")

    @patch('app.models.cache_service._redis_client')
    def test_set_cache_ttl(self, mock_redis):
        """Test set with TTL."""
        set_cached_data("key", "value", ttl=10)
        mock_redis.setex.assert_called_with("key", 10, json.dumps("value"))

    @patch('app.models.cache_service._redis_client')
    def test_get_nonexistent_key(self, mock_redis):
        """Test getting a key that doesn't exist."""
        mock_redis.get.return_value = None
        self.assertIsNone(get_cached_data("none"))

    @patch('app.models.cache_service._redis_client')
    def test_redis_error_handling(self, mock_redis):
        """Test handling of Redis errors."""
        mock_redis.get.side_effect = redis.RedisError("Error")
        self.assertIsNone(get_cached_data("key"))

    @patch('app.models.cache_service._redis_client')
    def test_set_cache_error_handling(self, mock_redis):
        """Test set_cached_data broad exception handling."""
        mock_redis.set.side_effect = Exception("Broad Error")
        set_cached_data("key", "value") # Should not crash

    @patch('app.models.cache_service._redis_client')
    def test_json_decode_error(self, mock_redis):
        """Test handling of JSON decode errors."""
        mock_redis.get.return_value = "invalid-json"
        self.assertIsNone(get_cached_data("key"))

    @patch('app.models.cache_service.json.dumps')
    @patch('app.models.cache_service._redis_client')
    def test_set_cache_json_error(self, mock_redis, mock_dumps):
        """Test handling of JSON serialization errors."""
        mock_dumps.side_effect = TypeError("Not serializable")
        set_cached_data("key", object()) # Should not crash
        mock_redis.set.assert_not_called()

    @patch('app.models.cache_service._redis_client', None)
    def test_no_redis_client(self):
        """Test behavior when Redis client is not available."""
        self.assertIsNone(get_cached_data("key"))
        set_cached_data("key", "value") # Should not crash

    def test_redis_init_failure(self):
        """Test module initialization when Redis connection fails."""
        # pylint: disable=protected-access,import-outside-toplevel
        import app.models.cache_service as cs
        with patch('redis.Redis', side_effect=Exception("Connection failed")):
            importlib.reload(cs)
            self.assertIsNone(cs._redis_client)

        # Reload again to restore state for other tests if necessary
        importlib.reload(cs)
