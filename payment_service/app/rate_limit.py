"""Simple in-memory rate limiter for /api/activation/retrieve."""
import time
from collections import defaultdict
from typing import Dict, Tuple


class RateLimiter:
    """In-memory rate limiter using sliding window."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed.
        Returns (is_allowed, remaining_requests).
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            return False, 0
        
        # Add current request
        self.requests[key].append(now)
        remaining = self.max_requests - len(self.requests[key])
        return True, remaining
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if key in self.requests:
            del self.requests[key]


# Global rate limiter instance
_rate_limiter: RateLimiter = None


def get_rate_limiter(max_requests: int, window_seconds: int) -> RateLimiter:
    """Get or create rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(max_requests, window_seconds)
    return _rate_limiter



