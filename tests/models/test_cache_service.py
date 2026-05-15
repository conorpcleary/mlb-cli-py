"""
Unit tests for the cache_service module.
"""
import sys
import importlib
import unittest
from unittest.mock import patch
import fakeredis
from app.models.cache_service import get_cached_data, set_cached_data

class TestCacheService(unittest.TestCase):
    """Test cases for cache_service.py functions."""

    def setUp(self):
        """Initialize fakeredis client for testing."""
        self.fake_redis = fakeredis.FakeRedis(decode_responses=True)
        # Patch the internal client in the module
        self.patcher = patch('app.models.cache_service._redis_client', self.fake_redis)
        self.patcher.start()

    def tearDown(self):
        """Stop patching."""
        self.patcher.stop()

    def test_set_get_cached_data(self):
        """Test basic set and get functionality."""
        data = {'key': 'value'}
        set_cached_data('test_key', data)

        retrieved = get_cached_data('test_key')
        self.assertEqual(retrieved, data)

    def test_get_cached_data_not_found(self):
        """Test get_cached_data returns None when key is missing."""
        self.assertIsNone(get_cached_data('missing_key'))

    def test_set_cached_data_with_ttl(self):
        """Test set_cached_data respects TTL."""
        data = [1, 2, 3]
        set_cached_data('ttl_key', data, ttl=300)

        self.assertEqual(get_cached_data('ttl_key'), data)
        self.assertTrue(self.fake_redis.ttl('ttl_key') > 0)

    def test_get_cached_data_invalid_json(self):
        """Test get_cached_data handles invalid JSON gracefully."""
        self.fake_redis.set('bad_json', 'not-json')
        self.assertIsNone(get_cached_data('bad_json'))

    @patch('app.models.cache_service._redis_client', None)
    def test_cache_disabled_no_client(self):
        """Test that cache functions do nothing if client is None."""
        # This tests the 'if _redis_client is None' branches
        self.assertIsNone(get_cached_data('any_key'))
        # Should not raise any errors
        set_cached_data('any_key', {'a': 1})

    @patch('app.models.cache_service.redis.Redis')
    def test_set_cached_data_error(self, _mock_redis):
        """Test set_cached_data handles Redis errors."""
        # Use a real MagicMock for the internal client
        with patch('app.models.cache_service._redis_client') as mock_client:
            mock_client.set.side_effect = Exception("Redis Error")
            # Should catch exception and not raise
            set_cached_data('key', 'data')
            mock_client.set.assert_called_once()

    def test_init_redis_failure(self):
        """Test module level Redis client initialization failure."""
        # Mock redis.Redis to raise on instantiation
        with patch('redis.Redis', side_effect=Exception("Connection Error")):
            # Force reload the module to trigger the try/except block at the top
            if 'app.models.cache_service' in sys.modules:
                importlib.reload(sys.modules['app.models.cache_service'])

            # pylint: disable=import-outside-toplevel
            from app.models.cache_service import _redis_client as failing_client
            self.assertIsNone(failing_client)

        # Reload again to restore the fake client for other tests
        importlib.reload(sys.modules['app.models.cache_service'])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
