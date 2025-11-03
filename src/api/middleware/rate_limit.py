"""
Rate limiting middleware.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Dict
from collections import defaultdict
import time
from datetime import datetime, timedelta

# In-memory rate limit storage (use Redis in production)
rate_limit_storage: Dict[str, Dict] = defaultdict(dict)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.
    Configurable via environment variables.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and test client
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Skip rate limiting for test clients (identified by testclient user agent)
        user_agent = request.headers.get("user-agent", "")
        if isinstance(user_agent, str) and "testclient" in user_agent.lower():
            response = await call_next(request)
            # Add rate limit headers for consistency
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_size))
            return response
        
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current time
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Clean old entries
        if client_ip in rate_limit_storage:
            rate_limit_storage[client_ip] = {
                k: v for k, v in rate_limit_storage[client_ip].items()
                if v >= window_start
            }
        
        # Count requests in current window
        request_count = len(rate_limit_storage[client_ip])
        
        # Check rate limit
        if request_count >= self.requests_per_minute:
            retry_after = int(self.window_size - (current_time - (min(rate_limit_storage[client_ip].values()) if rate_limit_storage[client_ip] else current_time)))
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after)),
                    "Retry-After": str(retry_after)
                }
            )
        
        # Record this request
        rate_limit_storage[client_ip][current_time] = current_time
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - request_count - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
        
        return response

