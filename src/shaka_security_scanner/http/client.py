"""
HTTP Client for the Web Penetration Testing Framework.

This module provides an async HTTP client with connection pooling,
retry logic, and comprehensive error handling.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from urllib.parse import urljoin

import httpx

from ..models import HTTPRequest, HTTPResponse


logger = logging.getLogger(__name__)


class HTTPClientError(Exception):
    """Exception raised for HTTP client errors."""
    pass


class HTTPClient:
    """
    Async HTTP client with connection pooling and retry logic.
    
    This class provides:
    - Async HTTP requests using httpx
    - Connection pooling for performance
    - Automatic retry with exponential backoff
    - Timeout handling
    - Proxy support
    - Custom headers and user agent
    """
    
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "WebPenTestFramework/0.1.0",
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        max_redirects: int = 10,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the HTTP Client.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string
            proxy: Proxy URL (e.g., "http://proxy.example.com:8080")
            verify_ssl: Whether to verify SSL certificates
            follow_redirects: Whether to follow HTTP redirects
            max_redirects: Maximum number of redirects to follow
            max_connections: Maximum number of connections in pool
            max_keepalive_connections: Maximum number of keepalive connections
            retry_attempts: Number of retry attempts on failure
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.timeout = timeout
        self.user_agent = user_agent
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Create httpx client with connection pooling
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._client_config = {
            "timeout": httpx.Timeout(timeout),
            "limits": limits,
            "verify": verify_ssl,
            "follow_redirects": follow_redirects,
            "max_redirects": max_redirects,
            "proxy": proxy
        }
        
        self._default_headers = {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(**self._client_config)
            logger.debug("HTTP client initialized")
    
    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTP client closed")
    
    def set_timeout(self, seconds: int) -> None:
        """
        Set request timeout.
        
        Args:
            seconds: Timeout in seconds
        """
        if seconds <= 0:
            raise ValueError("Timeout must be positive")
        
        self.timeout = seconds
        self._client_config["timeout"] = httpx.Timeout(seconds)
        
        # If client already exists, need to recreate it
        if self._client is not None:
            logger.warning("Timeout changed. Client will be recreated on next request.")
    
    def set_user_agent(self, user_agent: str) -> None:
        """
        Set user agent string.
        
        Args:
            user_agent: User agent string
        """
        self.user_agent = user_agent
        self._default_headers["User-Agent"] = user_agent
        logger.debug(f"User agent set to: {user_agent}")
    
    def set_proxy(self, proxy_url: Optional[str]) -> None:
        """
        Set proxy URL.
        
        Args:
            proxy_url: Proxy URL (e.g., "http://proxy.example.com:8080") or None to disable
        """
        self.proxy = proxy_url
        self._client_config["proxy"] = proxy_url
        
        # If client already exists, need to recreate it
        if self._client is not None:
            logger.warning("Proxy changed. Client will be recreated on next request.")
    
    async def send_request(
        self,
        request: HTTPRequest,
        allow_redirects: Optional[bool] = None
    ) -> HTTPResponse:
        """
        Send an HTTP request with retry logic.
        
        Args:
            request: HTTPRequest object
            allow_redirects: Override follow_redirects setting for this request
        
        Returns:
            HTTPResponse object
        
        Raises:
            HTTPClientError: If request fails after all retries
        """
        await self._ensure_client()
        
        # Merge headers
        headers = {**self._default_headers, **request.headers}
        
        # Determine redirect behavior
        follow = allow_redirects if allow_redirects is not None else self.follow_redirects
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(
                    f"Sending {request.method} request to {request.url} "
                    f"(attempt {attempt + 1}/{self.retry_attempts})"
                )
                
                # Send request
                response = await self._client.request(
                    method=request.method,
                    url=request.url,
                    headers=headers,
                    params=request.params,
                    data=request.body,
                    cookies=request.cookies,
                    follow_redirects=follow
                )
                
                # Convert to HTTPResponse
                http_response = HTTPResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.text,
                    elapsed_time=response.elapsed.total_seconds()
                )
                
                logger.debug(
                    f"Response received: {response.status_code} "
                    f"({response.elapsed.total_seconds():.2f}s)"
                )
                
                return http_response
                
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Request timeout (attempt {attempt + 1}): {e}")
                
            except httpx.NetworkError as e:
                last_error = e
                logger.warning(f"Network error (attempt {attempt + 1}): {e}")
                
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"HTTP status error (attempt {attempt + 1}): {e}")
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.retry_attempts - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.debug(f"Waiting {delay:.2f}s before retry...")
                await asyncio.sleep(delay)
        
        # All retries failed
        error_msg = f"Request failed after {self.retry_attempts} attempts: {last_error}"
        logger.error(error_msg)
        raise HTTPClientError(error_msg)
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send a GET request.
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="GET",
            url=url,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    async def post(
        self,
        url: str,
        data: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send a POST request.
        
        Args:
            url: URL to request
            data: Request body
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="POST",
            url=url,
            body=data,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    async def put(
        self,
        url: str,
        data: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send a PUT request.
        
        Args:
            url: URL to request
            data: Request body
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="PUT",
            url=url,
            body=data,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    async def delete(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send a DELETE request.
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="DELETE",
            url=url,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    async def head(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send a HEAD request.
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="HEAD",
            url=url,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    async def options(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """
        Send an OPTIONS request.
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers
        
        Returns:
            HTTPResponse object
        """
        request = HTTPRequest(
            method="OPTIONS",
            url=url,
            params=params or {},
            headers=headers or {}
        )
        return await self.send_request(request)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Dictionary with client statistics
        """
        return {
            "timeout": self.timeout,
            "user_agent": self.user_agent,
            "proxy": self.proxy,
            "verify_ssl": self.verify_ssl,
            "follow_redirects": self.follow_redirects,
            "max_redirects": self.max_redirects,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "client_initialized": self._client is not None
        }
