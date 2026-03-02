import redis
import time
from typing import Optional, Dict, Tuple
import os

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

class RateLimitService:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        
        # Default limits per level (requests per minute)
        self.limits = {
            "free": 10,
            "trial": 100,
            "personal": 200,
            "family": 500,
            "premium": 1000
        }

    def is_allowed(self, user_id: str, level: str, resource: str = "api") -> Tuple[bool, int, int]:
        """
        Check if a request is allowed based on user's subscription level.
        Returns: (is_allowed, remaining, retry_after)
        """
        key = f"rl:{resource}:{user_id}"
        limit = self.limits.get(level, 10)
        
        # Use Redis sliding window or fixed window
        # For simplicity, using a 1-minute fixed window
        current_minute = int(time.time() / 60)
        key = f"{key}:{current_minute}"
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        results = pipe.execute()
        
        current_usage = results[0]
        
        if current_usage > limit:
            return False, 0, 60 - (int(time.time()) % 60)
        
        return True, limit - current_usage, 0

    def check_resource_limit(self, user_id: str, resource_type: str, daily_limit: int) -> Tuple[bool, int]:
        """
        Check daily limits for specific resources (e.g., AI messages, Scans).
        """
        key = f"limit:{resource_type}:{user_id}:{time.strftime('%Y-%m-%d')}"
        
        current_usage = self.redis.get(key)
        if current_usage and int(current_usage) >= daily_limit:
            return False, int(current_usage)
        
        # We don't increment here, just check. 
        # Incrementing should happen after successful execution in the repository.
        return True, int(current_usage or 0)
