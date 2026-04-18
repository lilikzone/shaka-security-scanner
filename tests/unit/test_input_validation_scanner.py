"""
Unit tests for Input Validation Scanner.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from web_pen_test_framework.scanners.input_validation import InputValidationScanner
from web_pen_test_framework.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestInputValidationScanner:
    """Test cases for InputValidationScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = InputValidationScanner()
        
        assert scanner.get_name() == "input_validation"
        assert scanner.get_test_suite() == TestSuite.INPUT_VALIDATION
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that input validation scanner supports active and aggressive."""
        scanner = InputValidationScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.ACTIVE in intensities
        assert IntensityLevel.AGGRESSIVE in intensities
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = InputValidationScanner()
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <form action="/search" method="post">
                    <input type="text" name="query">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete successfully
        assert result.success is True
        assert result.scanner_name == "input_validation"
        assert result.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_command_injection_detection(self):
        """Test detection of command injection."""
        scanner = InputValidationScanner()
        
        # Mock response with form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/execute" method="post">
                    <input type="text" name="cmd">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        
        # Mock response with command execution output
        mock_exec_response = Mock()
        mock_exec_response.status_code = 200
        mock_exec_response.content = b"""
        <html>
            <body>
                <pre>
                root:x:0:0:root:/root:/bin/bash
                daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
                </pre>
            </body>
        </html>
        """
        
        scanner.http_client.get = AsyncMock(return_value=mock_form_response)
        scanner.http_client.post = AsyncMock(return_value=mock_exec_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect command injection
        cmd_findings = [
            f for f in result.findings
            if 'Command Injection' in f.title
        ]
        assert len(cmd_findings) > 0
        assert cmd_findings[0].severity == Severity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_path_traversal_detection(self):
        """Test detection of path traversal."""
        scanner = InputValidationScanner()
        
        # Mock response with form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/view" method="get">
                    <input type="text" name="file">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        
        # Mock responses - command injection tests first (3 calls), then path traversal
        responses = [
            # Command injection tests (3 payloads)
            Mock(status_code=200, content=b"<html><body>Invalid</body></html>"),
            Mock(status_code=200, content=b"<html><body>Invalid</body></html>"),
            Mock(status_code=200, content=b"<html><body>Invalid</body></html>"),
            # Path traversal test - this one succeeds
            Mock(status_code=200, content=b"<html><body><pre>root:x:0:0:root:/root:/bin/bash</pre></body></html>"),
        ]
        
        scanner.http_client.get = AsyncMock(side_effect=[mock_form_response] + responses)
        scanner.http_client.post = AsyncMock(return_value=Mock(status_code=200, content=b"Invalid"))
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect path traversal
        path_findings = [
            f for f in result.findings
            if 'Path Traversal' in f.title
        ]
        assert len(path_findings) > 0
        assert path_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_template_injection_detection(self):
        """Test detection of template injection."""
        scanner = InputValidationScanner()
        
        # Mock response with form
        mock_form_response = Mock()
        mock_form_response.status_code = 200
        mock_form_response.content = b"""
        <html>
            <body>
                <form action="/render" method="post">
                    <input type="text" name="template">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        
        # Mock response with template evaluation
        mock_eval_response = Mock()
        mock_eval_response.status_code = 200
        mock_eval_response.content = b"""
        <html>
            <body>
                <p>Result: {{7*7}} = 49</p>
            </body>
        </html>
        """
        
        scanner.http_client.get = AsyncMock(return_value=mock_form_response)
        scanner.http_client.post = AsyncMock(return_value=mock_eval_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect template injection
        template_findings = [
            f for f in result.findings
            if 'Template Injection' in f.title
        ]
        assert len(template_findings) > 0
        assert template_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_file_upload_detection(self):
        """Test detection of file upload functionality."""
        scanner = InputValidationScanner()
        
        # Mock response with file upload form
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="document">
                    <input type="submit">
                </form>
            </body>
        </html>
        """
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        scanner.http_client.post = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect file upload
        upload_findings = [
            f for f in result.findings
            if 'File Upload' in f.title
        ]
        assert len(upload_findings) > 0
        assert upload_findings[0].severity == Severity.INFO
    
    @pytest.mark.asyncio
    async def test_scan_no_forms(self):
        """Test scan with no forms."""
        scanner = InputValidationScanner()
        
        # Mock response without forms
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <h1>Welcome</h1>
                <p>No forms here</p>
            </body>
        </html>
        """
        
        scanner.http_client.get = AsyncMock(return_value=mock_response)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete without findings
        assert result.success is True
        assert len(result.findings) == 0
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with HTTP error."""
        scanner = InputValidationScanner()
        
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
            test_suites=[TestSuite.INPUT_VALIDATION],
            intensity=IntensityLevel.ACTIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should handle error gracefully
        assert result.success is False
        assert result.error == "Connection timeout"
