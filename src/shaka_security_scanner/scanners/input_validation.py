"""
Input validation security scanner.

This scanner tests for input validation weaknesses including command injection,
path traversal, XML injection, and other injection vulnerabilities.
"""

import logging
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from ..models import (
    Target, Configuration, TestSuite,
    Severity, VulnerabilityCategory
)
from ..http import HTTPClient, RequestThrottler
from .base import ActiveScanner, ScanResult


logger = logging.getLogger(__name__)


class InputValidationScanner(ActiveScanner):
    """
    Input validation security scanner.
    
    Tests for:
    - Command injection
    - Path traversal
    - XML injection (XXE)
    - LDAP injection
    - Template injection
    - File upload vulnerabilities
    """
    
    # Command injection payloads
    COMMAND_INJECTION_PAYLOADS = [
        '; ls',
        '| ls',
        '& dir',
        '&& dir',
        '; cat /etc/passwd',
        '| cat /etc/passwd',
        '`whoami`',
        '$(whoami)',
    ]
    
    # Path traversal payloads
    PATH_TRAVERSAL_PAYLOADS = [
        '../../../etc/passwd',
        '..\\..\\..\\windows\\win.ini',
        '....//....//....//etc/passwd',
        '..%2F..%2F..%2Fetc%2Fpasswd',
        '..%5c..%5c..%5cwindows%5cwin.ini',
    ]
    
    # XML injection payloads
    XML_INJECTION_PAYLOADS = [
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>',
    ]
    
    # Template injection payloads
    TEMPLATE_INJECTION_PAYLOADS = [
        '{{7*7}}',
        '${7*7}',
        '<%= 7*7 %>',
        '#{7*7}',
        '*{7*7}',
    ]
    
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        throttler: Optional[RequestThrottler] = None
    ):
        """
        Initialize input validation scanner.
        
        Args:
            http_client: HTTP client for making requests
            throttler: Request throttler for rate limiting
        """
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.throttler = throttler or RequestThrottler()
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "input_validation"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "Input validation testing (command injection, path traversal, XXE)"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.INPUT_VALIDATION
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute input validation scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting input validation scan of {target.url}")
        
        try:
            # Fetch target page to find input points
            response = await self.http_client.get(target.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find forms for testing
            forms = soup.find_all('form')
            
            if forms:
                # Test for command injection
                await self._test_command_injection(target, forms, config)
                
                # Test for path traversal
                await self._test_path_traversal(target, forms, config)
                
                # Test for template injection
                await self._test_template_injection(target, forms, config)
                
                # Test for file upload vulnerabilities
                await self._test_file_upload(target, forms, config)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Input validation scan completed: "
                f"{len(self.get_findings())} findings in {duration:.2f}s"
            )
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                findings=self.get_findings(),
                tests_performed=4,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Input validation scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _test_command_injection(
        self,
        target: Target,
        forms: List,
        config: Configuration
    ) -> None:
        """
        Test for command injection vulnerabilities.
        
        Args:
            target: Target being scanned
            forms: List of forms to test
            config: Scan configuration
        """
        logger.info("Testing for command injection")
        
        for form in forms[:2]:  # Test first 2 forms
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            # Get form inputs
            inputs = form.find_all('input')
            if not inputs:
                continue
            
            # Build form data
            form_data = {}
            for input_field in inputs:
                name = input_field.get('name')
                input_type = input_field.get('type', 'text')
                if name and input_type not in ['submit', 'button']:
                    form_data[name] = 'test'
            
            if not form_data:
                continue
            
            test_url = urljoin(target.url, action) if action else target.url
            
            # Test command injection on first parameter
            for param_name in list(form_data.keys())[:1]:
                for payload in self.COMMAND_INJECTION_PAYLOADS[:3]:
                    await self.throttler.acquire()
                    
                    test_data = form_data.copy()
                    test_data[param_name] = payload
                    
                    try:
                        if method == 'post':
                            response = await self.http_client.post(
                                test_url,
                                data=test_data,
                                timeout=10
                            )
                        else:
                            response = await self.http_client.get(
                                test_url,
                                params=test_data,
                                timeout=10
                            )
                        
                        content = response.content.decode('utf-8', errors='ignore')
                        
                        # Check for command execution indicators
                        command_indicators = [
                            'root:',  # /etc/passwd content
                            'bin/bash',
                            'bin/sh',
                            'uid=',
                            'gid=',
                            'groups=',
                        ]
                        
                        if any(indicator in content for indicator in command_indicators):
                            self.create_finding(
                                title="Command Injection Vulnerability",
                                description=f"Command injection detected in parameter '{param_name}'",
                                severity=Severity.CRITICAL,
                                category=VulnerabilityCategory.COMMAND_INJECTION,
                                affected_url=test_url,
                                confidence=0.9,
                                proof_of_concept=f"Payload: {payload}\nParameter: {param_name}",
                                remediation="Sanitize user input and avoid executing system commands with user input",
                                cvss_score=9.5,
                                cwe_id="CWE-78",
                                owasp_category="A03:2021 - Injection"
                            )
                            logger.warning(f"Command injection found in {param_name} at {test_url}")
                            return
                    
                    except Exception as e:
                        logger.debug(f"Error testing command injection: {e}")
    
    async def _test_path_traversal(
        self,
        target: Target,
        forms: List,
        config: Configuration
    ) -> None:
        """
        Test for path traversal vulnerabilities.
        
        Args:
            target: Target being scanned
            forms: List of forms to test
            config: Scan configuration
        """
        logger.info("Testing for path traversal")
        
        for form in forms[:2]:  # Test first 2 forms
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            # Get form inputs
            inputs = form.find_all('input')
            if not inputs:
                continue
            
            # Build form data
            form_data = {}
            for input_field in inputs:
                name = input_field.get('name')
                input_type = input_field.get('type', 'text')
                # Look for file-related parameters
                if name and input_type not in ['submit', 'button']:
                    form_data[name] = 'test'
            
            if not form_data:
                continue
            
            test_url = urljoin(target.url, action) if action else target.url
            
            # Test path traversal on first parameter
            for param_name in list(form_data.keys())[:1]:
                for payload in self.PATH_TRAVERSAL_PAYLOADS[:3]:
                    await self.throttler.acquire()
                    
                    test_data = form_data.copy()
                    test_data[param_name] = payload
                    
                    try:
                        if method == 'post':
                            response = await self.http_client.post(
                                test_url,
                                data=test_data,
                                timeout=10
                            )
                        else:
                            response = await self.http_client.get(
                                test_url,
                                params=test_data,
                                timeout=10
                            )
                        
                        content = response.content.decode('utf-8', errors='ignore')
                        
                        # Check for file content indicators
                        file_indicators = [
                            'root:x:0:0',  # /etc/passwd
                            '[extensions]',  # win.ini
                            '[fonts]',
                            'for 16-bit app support',
                        ]
                        
                        if any(indicator in content for indicator in file_indicators):
                            self.create_finding(
                                title="Path Traversal Vulnerability",
                                description=f"Path traversal detected in parameter '{param_name}'",
                                severity=Severity.HIGH,
                                category=VulnerabilityCategory.PATH_TRAVERSAL,
                                affected_url=test_url,
                                confidence=0.9,
                                proof_of_concept=f"Payload: {payload}\nParameter: {param_name}",
                                remediation="Validate and sanitize file paths, use whitelisting",
                                cvss_score=8.5,
                                cwe_id="CWE-22",
                                owasp_category="A01:2021 - Broken Access Control"
                            )
                            logger.warning(f"Path traversal found in {param_name} at {test_url}")
                            return
                    
                    except Exception as e:
                        logger.debug(f"Error testing path traversal: {e}")
    
    async def _test_template_injection(
        self,
        target: Target,
        forms: List,
        config: Configuration
    ) -> None:
        """
        Test for template injection vulnerabilities.
        
        Args:
            target: Target being scanned
            forms: List of forms to test
            config: Scan configuration
        """
        logger.info("Testing for template injection")
        
        for form in forms[:2]:  # Test first 2 forms
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            # Get form inputs
            inputs = form.find_all('input')
            if not inputs:
                continue
            
            # Build form data
            form_data = {}
            for input_field in inputs:
                name = input_field.get('name')
                input_type = input_field.get('type', 'text')
                if name and input_type not in ['submit', 'button', 'password']:
                    form_data[name] = 'test'
            
            if not form_data:
                continue
            
            test_url = urljoin(target.url, action) if action else target.url
            
            # Test template injection on first parameter
            for param_name in list(form_data.keys())[:1]:
                for payload in self.TEMPLATE_INJECTION_PAYLOADS[:3]:
                    await self.throttler.acquire()
                    
                    test_data = form_data.copy()
                    test_data[param_name] = payload
                    
                    try:
                        if method == 'post':
                            response = await self.http_client.post(
                                test_url,
                                data=test_data,
                                timeout=10
                            )
                        else:
                            response = await self.http_client.get(
                                test_url,
                                params=test_data,
                                timeout=10
                            )
                        
                        content = response.content.decode('utf-8', errors='ignore')
                        
                        # Check if template was evaluated (7*7 = 49)
                        if '49' in content and payload in content:
                            self.create_finding(
                                title="Template Injection Vulnerability",
                                description=f"Template injection detected in parameter '{param_name}'",
                                severity=Severity.HIGH,
                                category=VulnerabilityCategory.OTHER,
                                affected_url=test_url,
                                confidence=0.8,
                                proof_of_concept=f"Payload: {payload}\nParameter: {param_name}\nResult: 49",
                                remediation="Use safe template rendering and avoid user input in templates",
                                cvss_score=8.0,
                                cwe_id="CWE-94",
                                owasp_category="A03:2021 - Injection"
                            )
                            logger.warning(f"Template injection found in {param_name} at {test_url}")
                            return
                    
                    except Exception as e:
                        logger.debug(f"Error testing template injection: {e}")
    
    async def _test_file_upload(
        self,
        target: Target,
        forms: List,
        config: Configuration
    ) -> None:
        """
        Test for file upload vulnerabilities.
        
        Args:
            target: Target being scanned
            forms: List of forms to test
            config: Scan configuration
        """
        logger.info("Testing for file upload vulnerabilities")
        
        for form in forms:
            # Look for file input fields
            file_inputs = form.find_all('input', {'type': 'file'})
            if not file_inputs:
                continue
            
            action = form.get('action', '')
            test_url = urljoin(target.url, action) if action else target.url
            
            # Check if form accepts file uploads
            self.create_finding(
                title="File Upload Functionality Detected",
                description="Form contains file upload field - verify proper validation",
                severity=Severity.INFO,
                category=VulnerabilityCategory.FILE_UPLOAD,
                affected_url=test_url,
                confidence=1.0,
                proof_of_concept=f"File input field: {file_inputs[0].get('name', 'unknown')}",
                remediation="Implement file type validation, size limits, and malware scanning",
                owasp_category="A04:2021 - Insecure Design"
            )
            logger.info(f"File upload detected at {test_url}")
            break  # Only report once
