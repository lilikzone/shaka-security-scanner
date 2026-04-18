"""
Unit tests for RequestThrottler.
"""

import pytest
import asyncio
import time
from shaka_security_scanner.http.throttler import RequestThrottler, ThrottlerStats


class TestRequestThrottler:
    """Test cases for RequestThrottler class."""
    
    def test_initialization_default(self):
        """Test throttler initialization with default parameters."""
        throttler = RequestThrottler()
        
        assert throttler.rate_limit == 10.0
        assert throttler.burst_size == 10
        assert throttler.available_tokens == pytest.approx(10.0, rel=0.1)
    
    def test_initialization_custom(self):
        """Test throttler initialization with custom parameters."""
        throttler = RequestThrottler(rate_limit=5.0, burst_size=20)
        
        assert throttler.rate_limit == 5.0
        assert throttler.burst_size == 20
        assert throttler.available_tokens == pytest.approx(20.0, rel=0.1)
    
    def test_initialization_invalid_rate(self):
        """Test throttler initialization with invalid rate limit."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            RequestThrottler(rate_limit=0)
        
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            RequestThrottler(rate_limit=-5)
    
    @pytest.mark.asyncio
    async def test_acquire_single_request(self):
        """Test acquiring permission for a single request."""
        throttler = RequestThrottler(rate_limit=10.0)
        
        start = time.monotonic()
        await throttler.acquire()
        elapsed = time.monotonic() - start
        
        # Should not wait for first request
        assert elapsed < 0.1
        
        stats = throttler.get_stats()
        assert stats.total_requests == 1
        assert stats.throttled_requests == 0
    
    @pytest.mark.asyncio
    async def test_acquire_multiple_requests_within_burst(self):
        """Test acquiring permission for multiple requests within burst size."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=5)
        
        start = time.monotonic()
        for _ in range(5):
            await throttler.acquire()
        elapsed = time.monotonic() - start
        
        # Should not wait significantly for requests within burst
        assert elapsed < 0.2
        
        stats = throttler.get_stats()
        assert stats.total_requests == 5
    
    @pytest.mark.asyncio
    async def test_acquire_exceeds_burst_size(self):
        """Test acquiring permission when exceeding burst size."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=2)
        
        # First 2 requests should be fast
        await throttler.acquire()
        await throttler.acquire()
        
        # Third request should wait
        start = time.monotonic()
        await throttler.acquire()
        elapsed = time.monotonic() - start
        
        # Should wait approximately 0.1 seconds (1/10 rate)
        assert elapsed >= 0.05  # Allow some tolerance
        
        stats = throttler.get_stats()
        assert stats.total_requests == 3
        assert stats.throttled_requests >= 1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting enforces the specified rate."""
        throttler = RequestThrottler(rate_limit=5.0, burst_size=1)
        
        start = time.monotonic()
        for _ in range(3):
            await throttler.acquire()
        elapsed = time.monotonic() - start
        
        # 3 requests at 5 req/s should take ~0.4 seconds
        # (first is immediate, then 2 * 0.2s)
        assert elapsed >= 0.3  # Allow tolerance
        assert elapsed < 0.6
    
    @pytest.mark.asyncio
    async def test_token_replenishment(self):
        """Test that tokens are replenished over time."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=2)
        
        # Consume all tokens
        await throttler.acquire()
        await throttler.acquire()
        
        # Wait for tokens to replenish
        await asyncio.sleep(0.3)
        
        # Should have ~3 tokens now (10 * 0.3 = 3)
        tokens = throttler.available_tokens
        assert tokens >= 2.0
        assert tokens <= 3.5
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test throttler with concurrent requests."""
        throttler = RequestThrottler(rate_limit=5.0, burst_size=2)
        
        async def make_request():
            await throttler.acquire()
        
        start = time.monotonic()
        # Launch 5 concurrent requests
        await asyncio.gather(*[make_request() for _ in range(5)])
        elapsed = time.monotonic() - start
        
        # Should take at least 0.6 seconds for 5 requests at 5 req/s
        assert elapsed >= 0.5
        
        stats = throttler.get_stats()
        assert stats.total_requests == 5
    
    def test_set_rate_limit(self):
        """Test updating rate limit."""
        throttler = RequestThrottler(rate_limit=10.0)
        original_burst = throttler.burst_size
        
        throttler.set_rate_limit(20.0)
        assert throttler.rate_limit == 20.0
        # Burst size should only auto-adjust if it was at default
        # Since we started with default (10), it should adjust
        assert throttler.burst_size == 20
    
    def test_set_rate_limit_invalid(self):
        """Test setting invalid rate limit."""
        throttler = RequestThrottler(rate_limit=10.0)
        
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            throttler.set_rate_limit(0)
        
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            throttler.set_rate_limit(-5)
    
    def test_set_burst_size(self):
        """Test updating burst size."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=5)
        
        throttler.set_burst_size(15)
        assert throttler.burst_size == 15
    
    def test_set_burst_size_invalid(self):
        """Test setting invalid burst size."""
        throttler = RequestThrottler(rate_limit=10.0)
        
        with pytest.raises(ValueError, match="burst_size must be positive"):
            throttler.set_burst_size(0)
        
        with pytest.raises(ValueError, match="burst_size must be positive"):
            throttler.set_burst_size(-5)
    
    def test_set_burst_size_caps_tokens(self):
        """Test that setting burst size caps current tokens."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=10)
        
        # Reduce burst size
        throttler.set_burst_size(5)
        
        # Current tokens should be capped to new burst size
        assert throttler.available_tokens <= 5.0
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting throttling statistics."""
        throttler = RequestThrottler(rate_limit=5.0, burst_size=1)
        
        # Make some requests
        await throttler.acquire()
        await throttler.acquire()
        await throttler.acquire()
        
        stats = throttler.get_stats()
        assert stats.total_requests == 3
        assert stats.throttled_requests >= 1
        assert stats.total_wait_time > 0
        assert stats.average_wait_time > 0
    
    @pytest.mark.asyncio
    async def test_reset_stats(self):
        """Test resetting statistics."""
        throttler = RequestThrottler(rate_limit=5.0, burst_size=1)
        
        # Make some requests
        await throttler.acquire()
        await throttler.acquire()
        
        # Reset stats
        throttler.reset_stats()
        
        stats = throttler.get_stats()
        assert stats.total_requests == 0
        assert stats.throttled_requests == 0
        assert stats.total_wait_time == 0
        assert stats.average_wait_time == 0
    
    def test_available_tokens_property(self):
        """Test available_tokens property."""
        throttler = RequestThrottler(rate_limit=10.0, burst_size=10)
        
        # Initially should have full burst
        tokens = throttler.available_tokens
        assert tokens == pytest.approx(10.0, rel=0.1)
    
    @pytest.mark.asyncio
    async def test_stats_dataclass(self):
        """Test ThrottlerStats dataclass."""
        stats = ThrottlerStats(
            total_requests=10,
            throttled_requests=5,
            total_wait_time=2.5,
            average_wait_time=0.5
        )
        
        assert stats.total_requests == 10
        assert stats.throttled_requests == 5
        assert stats.total_wait_time == 2.5
        assert stats.average_wait_time == 0.5
