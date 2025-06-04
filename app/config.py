import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
SERVICE_ID = os.getenv("SERVICE_ID", "hash-generator-1")
HASH_BATCH_SIZE = int(os.getenv("HASH_BATCH_SIZE", "100")) 