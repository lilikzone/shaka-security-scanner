"""
Unit tests for Headers Scanner.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from web_pen_test_framework.scanners.headers import HeadersScanner
from web_pen_test_framework.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestHeadersScanner:
    """Test cases for HeadersScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = HeadersScanner()
        
        assert scanner.get_name() == "headers"
        assert scanner.get_test_suite() == TestSuite.HEADERS
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that headers scanner supports passive intensity."""
        scanner = HeadersScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.PASSIVE in intensities
        # Headers scanner is passive, so it only supports passive intensity
        assert len(intensities) == 1
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = HeadersScanner()
        
        # Mock HTTP client with good security headers
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        # Create target and config
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        # Execute scan
        result = await scanner.scan(target, config)
        
        # Verify result
        assert result.success is True
        assert result.scanner_name == "headers"
        assert result.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_missing_security_headers(self):
        """Test detection of missing security headers."""
        scanner = HeadersScanner()
        
        # Mock response with no security headers
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/html',
            'Date': 'Mon, 01 Jan 2024 00:00:00 GMT'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect multiple missing headers
        assert len(result.findings) > 0
        
        # Check for specific missing headers
        finding_titles = [f.title for f in result.findings]
        assert any('Strict-Transport-Security' in title for title in finding_titles)
        assert any('Content-Security-Policy' in title for title in finding_titles)
        assert any('X-Frame-Options' in title for title in finding_titles)
    
    @pytest.mark.asyncio
    async def test_information_disclosure_headers(self):
        """Test detection of information disclosure headers."""
        scanner = HeadersScanner()
        
        # Mock response with disclosure headers
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Server': 'Apache/2.4.41 (Ubuntu)',
            'X-Powered-By': 'PHP/7.4.3',
            'X-AspNet-Version': '4.0.30319',
            'Content-Type': 'text/html'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect information disclosure
        disclosure_findings = [
            f for f in result.findings
            if 'Information Disclosure' in f.title
        ]
        assert len(disclosure_findings) >= 3
        assert all(f.severity == Severity.LOW for f in disclosure_findings)
    
    @pytest.mark.asyncio
    async def test_hsts_validation(self):
        """Test HSTS header validation."""
        scanner = HeadersScanner()
        
        # Mock response with weak HSTS
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Strict-Transport-Security': 'max-age=3600'  # Too short, no includeSubDomains
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect HSTS issues
        hsts_findings = [
            f for f in result.findings
            if 'HSTS' in f.title
        ]
        assert len(hsts_findings) >= 2  # Short max-age and missing includeSubDomains
    
    @pytest.mark.asyncio
    async def test_weak_csp(self):
        """Test weak CSP detection."""
        scanner = HeadersScanner()
        
        # Mock response with weak CSP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Security-Policy': "default-src 'self' 'unsafe-inline' 'unsafe-eval' *"
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect weak CSP directives
        csp_findings = [
            f for f in result.findings
            if 'Weak CSP' in f.title
        ]
        assert len(csp_findings) >= 2  # unsafe-inline, unsafe-eval, *
    
    @pytest.mark.asyncio
    async def test_invalid_x_frame_options(self):
        """Test invalid X-Frame-Options detection."""
        scanner = HeadersScanner()
        
        # Mock response with invalid X-Frame-Options
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'X-Frame-Options': 'INVALID'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect invalid X-Frame-Options
        xfo_findings = [
            f for f in result.findings
            if 'X-Frame-Options' in f.title and 'Invalid' in f.title
        ]
        assert len(xfo_findings) > 0
        assert xfo_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_deprecated_headers(self):
        """Test deprecated headers detection."""
        scanner = HeadersScanner()
        
        # Mock response with deprecated headers
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'X-XSS-Protection': '1; mode=block'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect deprecated header
        deprecated_findings = [
            f for f in result.findings
            if 'Deprecated' in f.title
        ]
        assert len(deprecated_findings) > 0
        assert deprecated_findings[0].severity == Severity.INFO
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with HTTP error."""
        scanner = HeadersScanner()
        
        # Mock HTTP client to raise exception
        scanner.http_client.head = AsyncMock(
            side_effect=Exception("Connection timeout")
        )
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        # Execute scan
        result = await scanner.scan(target, config)
        
        # Verify error handling
        assert result.success is False
        assert result.error == "Connection timeout"
    
    @pytest.mark.asyncio
    async def test_hsts_not_checked_for_http(self):
        """Test that HSTS validation is skipped for HTTP sites."""
        scanner = HeadersScanner()
        
        # Mock response with HSTS (which shouldn't be on HTTP)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Strict-Transport-Security': 'max-age=3600'
        }
        
        scanner.http_client.head = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="http://example.com",  # HTTP, not HTTPS
            base_domain="example.com",
            scheme="http"
        )
        config = Configuration(
            test_suites=[TestSuite.HEADERS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should not validate HSTS for HTTP sites
        hsts_validation_findings = [
            f for f in result.findings
            if 'HSTS' in f.title and 'max-age' in f.title.lower()
        ]
        assert len(hsts_validation_findings) == 0
