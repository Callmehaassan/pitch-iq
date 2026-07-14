import time
import asyncio
from typing import Optional

class TokenBucketRateLimiter:
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_tokens = requests_per_minute
        self.token_tokens = tokens_per_minute
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        if elapsed >= 60:
            self.request_tokens = self.requests_per_minute
            self.token_tokens = self.tokens_per_minute
            self.last_refill = now

    def can_request(self, estimated_tokens: int = 500) -> bool:
        self._refill()
        return self.request_tokens > 0 and self.token_tokens >= estimated_tokens

    def consume(self, estimated_tokens: int = 500):
        self.request_tokens -= 1
        self.token_tokens -= estimated_tokens

agent_limiter = TokenBucketRateLimiter(requests_per_minute=30, tokens_per_minute=6000)
sentiment_limiter = TokenBucketRateLimiter(requests_per_minute=30, tokens_per_minute=131072)
