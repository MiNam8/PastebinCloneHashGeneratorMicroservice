import unittest
import re
from app.services.hash_service import HashService

class TestHashService(unittest.TestCase):
    def setUp(self):
        # Mock Redis connection for testing
        self.hash_service = HashService()
        # Replace the Redis client with a mock
        self.hash_service.redis = None

    def test_hash_generation(self):
        # Generate a hash
        hash_value = self.hash_service.generate_hash()
        
        # Verify the hash is 8 characters long
        self.assertEqual(len(hash_value), 8)
        
        # Verify the hash only contains valid base64url characters
        valid_chars = re.compile(r'^[A-Za-z0-9_-]+$')
        self.assertTrue(valid_chars.match(hash_value))
        
    def test_batch_generation(self):
        # Generate a batch of 10 hashes
        batch_size = 10
        hashes = self.hash_service.generate_hash_batch(batch_size)
        
        # Verify we got the right number of hashes
        self.assertEqual(len(hashes), batch_size)
        
        # Verify all hashes are unique
        self.assertEqual(len(hashes), len(set(hashes)))
        
        # Verify all hashes are 8 characters long
        for hash_value in hashes:
            self.assertEqual(len(hash_value), 8)

if __name__ == '__main__':
    unittest.main() 