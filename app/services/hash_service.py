import hashlib
import os
import time
import uuid
import base64
from infrastructure.redis_client import get_redis_client
from models.hash_models import HashRequest, HashEntry
from config import HASH_BATCH_SIZE, SERVICE_ID
from redis.exceptions import ResponseError
from redis_om.model import NotFoundError

class HashService:
    def __init__(self):
        self.redis = get_redis_client()
        self.hash_queue_key = "text_hash_queue"
        self.hash_request_stream = "hash_generation_requests"
        self.hash_counter_key = "global_hash_counter"
        self.last_id = "0-0"  # Start from the beginning of the stream
    
    def generate_hash(self):
        """Generate a unique hash using Redis atomic counter"""
        unique_id = self.redis.incr(self.hash_counter_key)
        return self._int_to_base64(unique_id).zfill(8)
    
    def _int_to_base64(self, num):
        """Convert integer to base64 string (URL-safe)"""
        # URL-safe base64 characters: A-Z, a-z, 0-9, -, _
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        if num == 0:
            return chars[0]
        
        result = ""
        while num > 0:
            result = chars[num % 64] + result
            num //= 64
        return result
    
    def generate_hash_batch(self, batch_size):
        """Generate a batch of unique hashes"""
        hashes = set()
        
        # Keep generating until we have the requested batch size
        while len(hashes) < batch_size:
            hashes.add(self.generate_hash())
        
        return list(hashes)
    
    def add_hashes_to_queue(self, hashes):
        """Add generated hashes to the Redis queue and store them as HashEntry models"""
        # Add to queue for backward compatibility
        pipeline = self.redis.pipeline()
        for hash_value in hashes:
            pipeline.rpush(self.hash_queue_key, hash_value)
            
            # Also create a HashEntry model for each hash
            try:
                hash_entry = HashEntry(hash_value=hash_value)
                hash_entry.save()
            except ResponseError:
                # Hash might already exist, just continue
                pass

        pipeline.execute()
        
        return len(hashes)

    def process_hash_requests(self):
        """Process hash generation requests from the stream"""
        streams = {self.hash_request_stream: self.last_id}
        response = self.redis.xread(streams, count=1, block=5000)
        if not response:
            return 0
        
        for stream_name, messages in response:
            for message_id, data in messages:
                self.last_id = message_id
                
                # Extract request parameters
                batch_size = int(data.get("batch_size", HASH_BATCH_SIZE))
                requesting_service = data.get("requesting_service", "unknown")
                request_id = data.get("request_id", str(uuid.uuid4()))
                
                # ✅ ADD THIS: Extract lock key
                lock_key = data.get("lock_key")
                
                print("request_id", request_id)
                print("lock_key", lock_key)  # Debug info
                
                try:
                    # ... existing HashRequest logic ...
                    hash_request = HashRequest.get(request_id)
                except NotFoundError:
                    hash_request = HashRequest(
                        request_id=request_id,
                        batch_size=batch_size,
                        requesting_service=requesting_service,
                        timestamp=data.get("timestamp", str(int(time.time()))),
                        processed=0
                    )
                    hash_request.save()
                
                print(f"Processing hash generation request from {requesting_service} for {batch_size} hashes")
                
                try:
                    # Generate and add hashes
                    hashes = self.generate_hash_batch(batch_size)
                    added = self.add_hashes_to_queue(hashes)
                    print("hashes", hashes)
                    
                    # Mark request as processed
                    hash_request.processed = 1
                    hash_request.save()
                    
                    print(f"Added {added} new hashes to queue")
                    
                    # ✅ ADD THIS: Release the lock upon successful completion
                    if lock_key:
                        deleted = self.redis.delete(lock_key)
                        if deleted:
                            print(f"Released lock: {lock_key}")
                        else:
                            print(f"Lock {lock_key} was already released or expired")
                    
                    # Acknowledge message processing
                    self.redis.xack(self.hash_request_stream, "hash-consumer-group", message_id)
                    
                    return added
                    
                except Exception as e:
                    print(f"Error processing hash request: {e}")
                    
                    # ✅ ADD THIS: Release lock on error too
                    if lock_key:
                        self.redis.delete(lock_key)
                        print(f"Released lock due to error: {lock_key}")
                    
                    # Mark request as failed
                    hash_request.processed = -1  # Use -1 to indicate failure
                    hash_request.save()
                    
                    raise e
        
        return 0 