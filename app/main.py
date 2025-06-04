import time
import logging
from services.hash_service import HashService
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    hash_service = HashService()
    logger.info("Hash Generator Service started")
    
    try:
        while True:
            processed = hash_service.process_hash_requests()
            if processed == 0:
                # If no messages were processed, sleep briefly to avoid CPU spinning
                time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Service shutting down...")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        raise

if __name__ == "__main__":
    main() 