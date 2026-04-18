"""
Request throttler implementation using token bucket algorithm.

This module provides rate limiting functionality to prevent overwhelming target
servers and ensure responsible penetration testing practices.
"""

import asyncio
import time
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ThrottlerStats:
    """Statistics for request throttling."""
    
    total_requests: int = 0
    throttled_requests: int = 0
    total_wait_time: float = 0.0
    average_wait_time: float = 0.0


class RequestThrottler:
    """
    Token bucket rate limiter for HTTP requests.
    
    Implements the token bucket algorithm to enforce rate limits:
    - Tokens are added to the bucket at a constant rate
    - Each request consumes one token
    - If no tokens available, request waits until token is available
    
    Attributes:
        rate_limit: Maximum requests per second
        burst_size: Maximum burst capacity (tokens in bucket)
    """
    
    def __init__(
        self,
        rate_limit: float = 10.0,
        burst_size: Optional[int] = None
    ):
        """
        Initialize request throttler.
        
        Args:
            rate_limit: Maximum requests per second (default: 10)
            burst_size: Maximum burst capacity. If None, defaults to rate_limit
        
        Raises:
            ValueError: If rate_limit <= 0
        """
        if rate_limit <= 0:
            raise ValueError("rate_limit must be positive")
        
        self.rate_limit = rate_limit
        self.burst_size = burst_size if burst_size is not None else int(rate_limit)
        self._burst_is_default = burst_size is None  # Track if burst was auto-set
        
        # Token bucket state
        self._tokens = float(self.burst_size)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()
        
        # Statistics
        self._stats = ThrottlerStats()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request.
        
        Blocks until a token is available. Updates statistics.
        """
        async with self._lock:
            now = time.monotonic()
            
            # Add tokens based on elapsed time
            elapsed = now - self._last_update
            self._tokens = min(
                self.burst_size,
                self._tokens + elapsed * self.rate_limit
            )
            self._last_update = now
            
            # Wait if no tokens available
            if self._tokens < 1.0:
                wait_time = (1.0 - self._tokens) / self.rate_limit
                await asyncio.sleep(wait_time)
                
                # Update stats
                self._stats.throttled_requests += 1
                self._stats.total_wait_time += wait_time
                
                # Recalculate tokens after wait
                now = time.monotonic()
                elapsed = now - self._last_update
                self._tokens = min(
                    self.burst_size,
                    self._tokens + elapsed * self.rate_limit
                )
                self._last_update = now
            
            # Consume one token
            self._tokens -= 1.0
            self._stats.total_requests += 1
            
            # Update average wait time
            if self._stats.throttled_requests > 0:
                self._stats.average_wait_time = (
                    self._stats.total_wait_time / self._stats.throttled_requests
                )
    
    def set_rate_limit(self, rate_limit: float) -> None:
        """
        Update the rate limit.
        
        Args:
            rate_limit: New maximum requests per second
        
        Raises:
            ValueError: If rate_limit <= 0
        """
        if rate_limit <= 0:
            raise ValueError("rate_limit must be positive")
        
        self.rate_limit = rate_limit
        # Adjust burst size proportionally if it was auto-set
        if self._burst_is_default:
            self.burst_size = int(rate_limit)
    
    def set_burst_size(self, burst_size: int) -> None:
        """
        Update the burst size.
        
        Args:
            burst_size: New maximum burst capacity
        
        Raises:
            ValueError: If burst_size <= 0
        """
        if burst_size <= 0:
            raise ValueError("burst_size must be positive")
        
        self.burst_size = burst_size
        # Cap current tokens to new burst size
        self._tokens = min(self._tokens, float(burst_size))
    
    def get_stats(self) -> ThrottlerStats:
        """
        Get throttling statistics.
        
        Returns:
            ThrottlerStats object with current statistics
        """
        return ThrottlerStats(
            total_requests=self._stats.total_requests,
            throttled_requests=self._stats.throttled_requests,
            total_wait_time=self._stats.total_wait_time,
            average_wait_time=self._stats.average_wait_time
        )
    
    def reset_stats(self) -> None:
        """Reset throttling statistics."""
        self._stats = ThrottlerStats()
    
    @property
    def available_tokens(self) -> float:
        """
        Get current number of available tokens.
        
        Returns:
            Number of tokens currently in the bucket
        """
        now = time.monotonic()
        elapsed = now - self._last_update
        tokens = min(
            self.burst_size,
            self._tokens + elapsed * self.rate_limit
        )
        return tokens
