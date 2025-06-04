from redis_om import get_redis_connection
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

def get_redis_client():
    print(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)
    return get_redis_connection(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    ) 