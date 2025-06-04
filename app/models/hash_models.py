from redis_om import HashModel, Field
from typing import Optional
from datetime import datetime
import uuid

class HashRequest(HashModel):
    batch_size: int = Field(index=True)
    requesting_service: str = Field(index=True)
    timestamp: str = Field(index=True)
    request_id: str = Field(primary_key=True)
    processed: int = Field(default=0, index=True)
    
    class Meta:
        global_key_prefix = "hash_gen"

class HashEntry(HashModel):
    hash_value: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    used: int = Field(default=0, index=True)
    
    class Meta:
        global_key_prefix = "hash_gen" 