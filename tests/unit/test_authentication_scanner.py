"""
Unit tests for Authentication Scanner.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from shaka_security_scanner.scanners.authentication import AuthenticationScanner
from shaka_security_scanner.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestAuthenticationScanner:
    """Test cases for AuthenticationScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = AuthenticationScanner()
        
        assert scanner.get_name() == "authentication"
        assert scanner.get_test_suite() == TestSuite.AUTHENTICATION
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that authentication scanner supports active and aggressive."""
        scanner = AuthenticationScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.ACTIVE in intensities
        assert IntensityLevel.AGGRESSIVE in intensities
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = AuthenticationScanner()
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        """
        mock_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete successfully
        assert result.success is True
        assert result.scanner_name == "authentication"
        assert result.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_default_credentials_detection(self):
        """Test detection of default credentials."""
        scanner = AuthenticationScanner()
        
        # Mock response with login form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        mock_form_response.headers = {}
        
        # Mock successful login response
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.content = b"""
        <html>
            <body>
                <h1>Welcome to Dashboard</h1>
                <a href="/logout">Logout</a>
            </body>
        </html>
        """
        mock_success_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_form_response)
        scanner.http_client.post = AsyncMock(return_value=mock_success_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect potential default credentials
        default_cred_findings = [
            f for f in result.findings
            if 'Default Credentials' in f.title
        ]
        assert len(default_cred_findings) > 0
        assert default_cred_findings[0].severity == Severity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_brute_force_protection_missing(self):
        """Test detection of missing brute force protection."""
        scanner = AuthenticationScanner()
        
        # Mock response with login form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        mock_form_response.headers = {}
        
        # Mock failed login response (always returns 200)
        mock_failed_response = Mock()
        mock_failed_response.status_code = 200
        mock_failed_response.content = b"""
        <html>
            <body>
                <p>Invalid credentials</p>
            </body>
        </html>
        """
        mock_failed_response.headers = {}
        
        scanner.http_client.get = AsyncMock(return_value=mock_form_response)
        scanner.http_client.post = AsyncMock(return_value=mock_failed_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing brute force protection
        brute_force_findings = [
            f for f in result.findings
            if 'Brute Force Protection' in f.title
        ]
        assert len(brute_force_findings) > 0
        assert brute_force_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_username_enumeration(self):
        """Test detection of username enumeration."""
        scanner = AuthenticationScanner()
        
        # Mock response with login form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        mock_form_response.headers = {}
        
        # Mock different responses for valid vs invalid usernames
        responses = [
            # First POST call (default credentials test - admin/admin)
            Mock(status_code=200, content=b"<html><body><p>Invalid credentials</p></body></html>", headers={}),
            # Second POST call (default credentials test - admin/password)
            Mock(status_code=200, content=b"<html><body><p>Invalid credentials</p></body></html>", headers={}),
            # Third POST call (default credentials test - admin/123456)
            Mock(status_code=200, content=b"<html><body><p>Invalid credentials</p></body></html>", headers={}),
            # Fourth POST call (brute force test 1)
            Mock(status_code=200, content=b"<html><body><p>Invalid</p></body></html>", headers={}),
            # Fifth POST call (brute force test 2)
            Mock(status_code=200, content=b"<html><body><p>Invalid</p></body></html>", headers={}),
            # Sixth POST call (brute force test 3)
            Mock(status_code=200, content=b"<html><body><p>Invalid</p></body></html>", headers={}),
            # Seventh POST call (brute force test 4)
            Mock(status_code=200, content=b"<html><body><p>Invalid</p></body></html>", headers={}),
            # Eighth POST call (brute force test 5)
            Mock(status_code=200, content=b"<html><body><p>Invalid</p></body></html>", headers={}),
            # Ninth POST call (username enumeration - admin) - LONGER response
            Mock(status_code=200, content=b"<html><body><p>Invalid password for user admin. Please check your password and try again. If you forgot your password, click the reset link below.</p></body></html>", headers={}),
            # Tenth POST call (username enumeration - nonexistent) - SHORTER response
            Mock(status_code=200, content=b"<html><body><p>User not found</p></body></html>", headers={}),
        ]
        
        scanner.http_client.get = AsyncMock(return_value=mock_form_response)
        scanner.http_client.post = AsyncMock(side_effect=responses)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect username enumeration
        enum_findings = [
            f for f in result.findings
            if 'Username Enumeration' in f.title
        ]
        assert len(enum_findings) > 0
        assert enum_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_session_cookie_missing_httponly(self):
        """Test detection of missing HttpOnly flag."""
        scanner = AuthenticationScanner()
        
        # Mock response with cookie without HttpOnly
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {
            'set-cookie': 'sessionid=abc123; Path=/'
        }
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing HttpOnly flag
        httponly_findings = [
            f for f in result.findings
            if 'HttpOnly' in f.title
        ]
        assert len(httponly_findings) > 0
        assert httponly_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_session_cookie_missing_secure(self):
        """Test detection of missing Secure flag on HTTPS."""
        scanner = AuthenticationScanner()
        
        # Mock response with cookie without Secure flag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {
            'set-cookie': 'sessionid=abc123; Path=/; HttpOnly'
        }
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing Secure flag
        secure_findings = [
            f for f in result.findings
            if 'Secure Flag' in f.title
        ]
        assert len(secure_findings) > 0
        assert secure_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_session_cookie_missing_samesite(self):
        """Test detection of missing SameSite attribute."""
        scanner = AuthenticationScanner()
        
        # Mock response with cookie without SameSite
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {
            'set-cookie': 'sessionid=abc123; Path=/; HttpOnly; Secure'
        }
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect missing SameSite attribute
        samesite_findings = [
            f for f in result.findings
            if 'SameSite' in f.title
        ]
        assert len(samesite_findings) > 0
        assert samesite_findings[0].severity == Severity.LOW
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with HTTP error."""
        scanner = AuthenticationScanner()
        
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
            test_suites=[TestSuite.AUTHENTICATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should handle error gracefully
        assert result.success is False
        assert result.error == "Connection timeout"
