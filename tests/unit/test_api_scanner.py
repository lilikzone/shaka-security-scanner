"""
Unit tests for API Scanner.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from web_pen_test_framework.scanners.api import APIScanner
from web_pen_test_framework.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestAPIScanner:
    """Test cases for APIScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = APIScanner()
        
        assert scanner.get_name() == "api"
        assert scanner.get_test_suite() == TestSuite.API
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that API scanner supports active and aggressive."""
        scanner = APIScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.ACTIVE in intensities
        assert IntensityLevel.AGGRESSIVE in intensities
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = APIScanner()
        
        # Mock API endpoint discovery
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "ok"}'
        mock_response.headers = {'content-type': 'application/json'}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete successfully
        assert result.success is True
        assert result.scanner_name == "api"
        assert result.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_api_endpoint_discovery(self):
        """Test API endpoint discovery."""
        scanner = APIScanner()
        
        # Mock responses for endpoint discovery
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.content = b'{"version": "1.0"}'
        mock_api_response.headers = {'content-type': 'application/json'}
        
        mock_not_found = Mock()
        mock_not_found.status_code = 404
        mock_not_found.content = b'Not Found'
        mock_not_found.headers = {}
        
        scanner.http_client.get = AsyncMock(side_effect=[
            mock_api_response,  # /api found
            mock_not_found,     # /api/v1 not found
            mock_not_found,     # /api/v2 not found
        ])
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        
        endpoints = await scanner._discover_api_endpoints(target)
        
        # Should discover at least one endpoint
        assert len(endpoints) > 0
        assert 'api' in endpoints[0]
    
    @pytest.mark.asyncio
    async def test_missing_authentication_detection(self):
        """Test detection of missing authentication."""
        scanner = APIScanner()
        
        # Mock API endpoint that returns data without auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"users": [{"id": 1, "name": "John"}]}'
        mock_response.headers = {'content-type': 'application/json'}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing authentication
        auth_findings = [
            f for f in result.findings
            if 'Authentication' in f.title
        ]
        assert len(auth_findings) > 0
        assert auth_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_broken_authorization_detection(self):
        """Test detection of broken authorization (BOLA)."""
        scanner = APIScanner()
        
        # Mock API discovery - return 401 so it's discovered but doesn't trigger missing auth
        mock_discovery = Mock()
        mock_discovery.status_code = 401
        mock_discovery.content = b'{"error": "Unauthorized"}'
        mock_discovery.headers = {'content-type': 'application/json'}
        
        # Mock 404 for other discovery endpoints
        mock_not_found = Mock()
        mock_not_found.status_code = 404
        mock_not_found.content = b'Not Found'
        mock_not_found.headers = {}
        
        # Mock BOLA vulnerability - returns user data for any ID
        mock_user_data = Mock()
        mock_user_data.status_code = 200
        mock_user_data.content = b'{"user": {"id": 1, "email": "user@example.com", "name": "John"}}'
        mock_user_data.headers = {'content-type': 'application/json'}
        
        scanner.http_client.get = AsyncMock(side_effect=[
            mock_discovery,  # Discovery /api (401 - discovered)
            mock_not_found,  # Discovery /api/v1 (404 - not found)
            mock_not_found,  # Discovery /api/v2 (404 - not found)
            mock_discovery,  # Missing auth test on /api (401, skipped)
            mock_user_data,  # BOLA test /api/1 - this triggers the finding
        ])
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect BOLA
        bola_findings = [
            f for f in result.findings
            if 'BOLA' in f.title or 'Authorization' in f.title
        ]
        assert len(bola_findings) > 0
        assert bola_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_excessive_data_exposure_detection(self):
        """Test detection of excessive data exposure."""
        scanner = APIScanner()
        
        # Mock API response with sensitive data directly
        mock_sensitive_data = Mock()
        mock_sensitive_data.status_code = 200
        mock_sensitive_data.content = b'{"user": {"id": 1, "name": "John", "password": "hashed123", "api_key": "secret"}}'
        mock_sensitive_data.headers = {'content-type': 'application/json'}
        
        # Mock all calls to return sensitive data
        scanner.http_client.get = AsyncMock(return_value=mock_sensitive_data)
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect excessive data exposure
        exposure_findings = [
            f for f in result.findings
            if 'Excessive Data Exposure' in f.title
        ]
        assert len(exposure_findings) > 0
        assert exposure_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_rate_limiting_detection(self):
        """Test detection of missing rate limiting."""
        scanner = APIScanner()
        
        # Mock API responses - all succeed (no rate limiting)
        mock_discovery = Mock()
        mock_discovery.status_code = 200
        mock_discovery.content = b'{"status": "ok"}'
        mock_discovery.headers = {'content-type': 'application/json'}
        
        mock_success = Mock()
        mock_success.status_code = 200
        mock_success.content = b'{"data": "test"}'
        mock_success.headers = {'content-type': 'application/json'}
        
        # Discovery (3) + auth test (2) + bola test (2) + exposure test (2) + rate limit test (10)
        responses = [mock_discovery] * 3 + [mock_success] * 16
        
        scanner.http_client.get = AsyncMock(side_effect=responses)
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing rate limiting
        rate_findings = [
            f for f in result.findings
            if 'Rate Limiting' in f.title
        ]
        assert len(rate_findings) > 0
        assert rate_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_scan_no_api_endpoints(self):
        """Test scan when no API endpoints are found."""
        scanner = APIScanner()
        
        # Mock 404 responses for all endpoints
        mock_not_found = Mock()
        mock_not_found.status_code = 404
        mock_not_found.content = b'Not Found'
        mock_not_found.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_not_found)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete without findings
        assert result.success is True
        assert len(result.findings) == 0
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with HTTP error."""
        scanner = APIScanner()
        
        # Override the _discover_api_endpoints method to raise exception
        async def mock_discover_error(target):
            raise Exception("Connection timeout")
        
        scanner._discover_api_endpoints = mock_discover_error
        
        target = Target(
            url="https://api.example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should handle error gracefully
        assert result.success is False
        assert result.error == "Connection timeout"
