"""
Unit tests for HTTPClient.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from shaka_security_scanner.http.client import HTTPClient, HTTPClientError
from shaka_security_scanner.models import HTTPRequest


class TestHTTPClient:
    """Tests for HTTPClient class."""
    
    @pytest.fixture
    def http_client(self):
        """Create HTTPClient instance."""
        return HTTPClient(
            timeout=10,
            user_agent="TestAgent/1.0",
            retry_attempts=2,
            retry_delay=0.1  # Short delay for tests
        )
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, http_client):
        """Test HTTP client initialization."""
        assert http_client.timeout == 10
        assert http_client.user_agent == "TestAgent/1.0"
        assert http_client.retry_attempts == 2
        assert http_client._client is None  # Not initialized yet
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with HTTPClient() as client:
            assert client._client is not None
        
        # Client should be closed after context
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_set_timeout(self, http_client):
        """Test setting timeout."""
        http_client.set_timeout(20)
        assert http_client.timeout == 20
    
    @pytest.mark.asyncio
    async def test_set_timeout_invalid(self, http_client):
        """Test setting invalid timeout."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            http_client.set_timeout(0)
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            http_client.set_timeout(-5)
    
    @pytest.mark.asyncio
    async def test_set_user_agent(self, http_client):
        """Test setting user agent."""
        http_client.set_user_agent("CustomAgent/2.0")
        assert http_client.user_agent == "CustomAgent/2.0"
        assert http_client._default_headers["User-Agent"] == "CustomAgent/2.0"
    
    @pytest.mark.asyncio
    async def test_set_proxy(self, http_client):
        """Test setting proxy."""
        http_client.set_proxy("http://proxy.example.com:8080")
        assert http_client.proxy == "http://proxy.example.com:8080"
    
    @pytest.mark.asyncio
    async def test_get_stats(self, http_client):
        """Test getting client statistics."""
        stats = http_client.get_stats()
        
        assert isinstance(stats, dict)
        assert stats["timeout"] == 10
        assert stats["user_agent"] == "TestAgent/1.0"
        assert stats["retry_attempts"] == 2
        assert stats["client_initialized"] is False
    
    @pytest.mark.asyncio
    async def test_send_request_success(self, http_client):
        """Test successful request."""
        # Mock httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html>Success</html>"
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        # Mock httpx client
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            request = HTTPRequest(
                method="GET",
                url="https://example.com"
            )
            
            response = await http_client.send_request(request)
            
            assert response.status_code == 200
            assert response.body == "<html>Success</html>"
            assert response.elapsed_time == 0.5
            assert "Content-Type" in response.headers
    
    @pytest.mark.asyncio
    async def test_send_request_timeout(self, http_client):
        """Test request timeout with retry."""
        # Mock httpx client to raise timeout
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timeout")
            
            request = HTTPRequest(
                method="GET",
                url="https://example.com"
            )
            
            with pytest.raises(HTTPClientError, match="failed after"):
                await http_client.send_request(request)
            
            # Should have retried
            assert mock_request.call_count == http_client.retry_attempts
    
    @pytest.mark.asyncio
    async def test_send_request_network_error(self, http_client):
        """Test network error with retry."""
        # Mock httpx client to raise network error
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")
            
            request = HTTPRequest(
                method="GET",
                url="https://example.com"
            )
            
            with pytest.raises(HTTPClientError, match="failed after"):
                await http_client.send_request(request)
            
            # Should have retried
            assert mock_request.call_count == http_client.retry_attempts
    
    @pytest.mark.asyncio
    async def test_get_request(self, http_client):
        """Test GET request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "GET response"
        mock_response.elapsed.total_seconds.return_value = 0.3
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.get("https://example.com/api")
            
            assert response.status_code == 200
            assert response.body == "GET response"
            
            # Verify GET method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "GET"
    
    @pytest.mark.asyncio
    async def test_post_request(self, http_client):
        """Test POST request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.text = "POST response"
        mock_response.elapsed.total_seconds.return_value = 0.4
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.post(
                "https://example.com/api",
                data='{"key": "value"}'
            )
            
            assert response.status_code == 201
            assert response.body == "POST response"
            
            # Verify POST method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "POST"
            assert call_args[1]["data"] == '{"key": "value"}'
    
    @pytest.mark.asyncio
    async def test_put_request(self, http_client):
        """Test PUT request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "PUT response"
        mock_response.elapsed.total_seconds.return_value = 0.3
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.put("https://example.com/api/1")
            
            assert response.status_code == 200
            
            # Verify PUT method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "PUT"
    
    @pytest.mark.asyncio
    async def test_delete_request(self, http_client):
        """Test DELETE request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.text = ""
        mock_response.elapsed.total_seconds.return_value = 0.2
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.delete("https://example.com/api/1")
            
            assert response.status_code == 204
            
            # Verify DELETE method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "DELETE"
    
    @pytest.mark.asyncio
    async def test_head_request(self, http_client):
        """Test HEAD request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Length": "1234"}
        mock_response.text = ""
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.head("https://example.com")
            
            assert response.status_code == 200
            assert "Content-Length" in response.headers
            
            # Verify HEAD method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "HEAD"
    
    @pytest.mark.asyncio
    async def test_options_request(self, http_client):
        """Test OPTIONS request convenience method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Allow": "GET, POST, PUT, DELETE"}
        mock_response.text = ""
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client.options("https://example.com/api")
            
            assert response.status_code == 200
            assert "Allow" in response.headers
            
            # Verify OPTIONS method was used
            call_args = mock_request.call_args
            assert call_args[1]["method"] == "OPTIONS"
    
    @pytest.mark.asyncio
    async def test_custom_headers(self, http_client):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "Response"
        mock_response.elapsed.total_seconds.return_value = 0.2
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            custom_headers = {"X-Custom-Header": "CustomValue"}
            response = await http_client.get(
                "https://example.com",
                headers=custom_headers
            )
            
            assert response.status_code == 200
            
            # Verify custom header was included
            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            assert "X-Custom-Header" in headers
            assert headers["X-Custom-Header"] == "CustomValue"
            # Default headers should also be present
            assert "User-Agent" in headers
    
    @pytest.mark.asyncio
    async def test_query_parameters(self, http_client):
        """Test request with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "Response"
        mock_response.elapsed.total_seconds.return_value = 0.2
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            params = {"key1": "value1", "key2": "value2"}
            response = await http_client.get(
                "https://example.com/api",
                params=params
            )
            
            assert response.status_code == 200
            
            # Verify params were included
            call_args = mock_request.call_args
            assert call_args[1]["params"] == params
    
    @pytest.mark.asyncio
    async def test_close_client(self, http_client):
        """Test closing the client."""
        # Initialize client
        await http_client._ensure_client()
        assert http_client._client is not None
        
        # Close client
        await http_client.close()
        assert http_client._client is None


class TestHTTPClientRetry:
    """Tests for HTTP client retry logic."""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_second_attempt(self):
        """Test successful request on second retry."""
        client = HTTPClient(retry_attempts=3, retry_delay=0.1)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "Success"
        mock_response.elapsed.total_seconds.return_value = 0.3
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            # First attempt fails, second succeeds
            mock_request.side_effect = [
                httpx.TimeoutException("Timeout"),
                mock_response
            ]
            
            request = HTTPRequest(method="GET", url="https://example.com")
            response = await client.send_request(request)
            
            assert response.status_code == 200
            assert mock_request.call_count == 2
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff between retries."""
        client = HTTPClient(retry_attempts=3, retry_delay=0.1)
        
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Timeout")
            
            request = HTTPRequest(method="GET", url="https://example.com")
            
            import time
            start_time = time.time()
            
            with pytest.raises(HTTPClientError):
                await client.send_request(request)
            
            elapsed = time.time() - start_time
            
            # Should have delays: 0.1s + 0.2s = 0.3s minimum
            # (first retry delay + second retry delay)
            assert elapsed >= 0.3
            assert mock_request.call_count == 3
        
        await client.close()
