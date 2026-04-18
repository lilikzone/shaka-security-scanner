"""
Unit tests for Reconnaissance Scanner.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from bs4 import BeautifulSoup

from web_pen_test_framework.scanners.reconnaissance import ReconnaissanceScanner
from web_pen_test_framework.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestReconnaissanceScanner:
    """Test cases for ReconnaissanceScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = ReconnaissanceScanner()
        
        assert scanner.get_name() == "reconnaissance"
        assert scanner.get_test_suite() == TestSuite.RECONNAISSANCE
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that reconnaissance scanner only supports passive intensity."""
        scanner = ReconnaissanceScanner()
        
        intensities = scanner.get_supported_intensities()
        assert len(intensities) == 1
        assert IntensityLevel.PASSIVE in intensities
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = ReconnaissanceScanner()
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <head><title>Test</title></head>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <form action="/submit" method="post"></form>
                <!-- TODO: Fix this -->
                <script src="/js/app.js"></script>
            </body>
        </html>
        """
        mock_response.headers = {
            'server': 'Apache/2.4.41',
            'x-powered-by': 'PHP/7.4.3'
        }
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        # Create target and config
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        # Execute scan
        result = await scanner.scan(target, config)
        
        # Verify result
        assert result.success is True
        assert result.scanner_name == "reconnaissance"
        assert result.tests_performed == 5
        assert result.duration_seconds > 0
        assert len(result.findings) > 0
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with HTTP error."""
        scanner = ReconnaissanceScanner()
        
        # Mock HTTP client to raise exception
        scanner.http_client.get = AsyncMock(
            side_effect=Exception("Connection timeout")
        )
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        # Execute scan
        result = await scanner.scan(target, config)
        
        # Verify error handling
        assert result.success is False
        assert result.error == "Connection timeout"
    
    @pytest.mark.asyncio
    async def test_detect_technologies(self):
        """Test technology detection."""
        scanner = ReconnaissanceScanner()
        
        # Mock response with Django indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <input type="hidden" name="csrfmiddlewaretoken" value="abc123">
                <script src="/static/jquery.min.js"></script>
            </body>
        </html>
        """
        mock_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect Django and jQuery
        tech_findings = [
            f for f in result.findings
            if "Technologies Detected" in f.title
        ]
        assert len(tech_findings) > 0
    
    @pytest.mark.asyncio
    async def test_discover_endpoints(self):
        """Test endpoint discovery."""
        scanner = ReconnaissanceScanner()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="https://external.com">External</a>
                <form action="/submit" method="post"></form>
                <script src="/js/app.js"></script>
            </body>
        </html>
        """
        mock_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        result = await scanner.scan(target, config)
        
        # Should discover endpoints and forms
        endpoint_findings = [
            f for f in result.findings
            if "Endpoints Discovered" in f.title or "Forms Discovered" in f.title
        ]
        assert len(endpoint_findings) > 0
    
    @pytest.mark.asyncio
    async def test_extract_sensitive_comments(self):
        """Test extraction of sensitive comments."""
        scanner = ReconnaissanceScanner()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <!-- TODO: Remove hardcoded password -->
                <!-- API key: abc123 -->
                <!-- Internal IP: 192.168.1.100 -->
                <p>Content</p>
            </body>
        </html>
        """
        mock_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        result = await scanner.scan(target, config)
        
        # Should find sensitive comments
        comment_findings = [
            f for f in result.findings
            if "Sensitive Information in Comments" in f.title
        ]
        assert len(comment_findings) > 0
        assert comment_findings[0].severity == Severity.LOW
    
    @pytest.mark.asyncio
    async def test_extract_emails(self):
        """Test email extraction."""
        scanner = ReconnaissanceScanner()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <p>Contact: admin@example.com</p>
                <p>Support: support@example.com</p>
            </body>
        </html>
        """
        mock_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        result = await scanner.scan(target, config)
        
        # Should find emails
        email_findings = [
            f for f in result.findings
            if "Email Addresses Exposed" in f.title
        ]
        assert len(email_findings) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_headers(self):
        """Test header analysis."""
        scanner = ReconnaissanceScanner()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {
            'server': 'Apache/2.4.41 (Ubuntu)',
            'x-powered-by': 'PHP/7.4.3'
        }
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        
        result = await scanner.scan(target, config)
        
        # Should find server header disclosure
        header_findings = [
            f for f in result.findings
            if "Header Disclosure" in f.title
        ]
        assert len(header_findings) >= 1
