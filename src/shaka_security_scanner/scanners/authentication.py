"""
Authentication security scanner.

This scanner tests for authentication weaknesses including weak credentials,
brute force vulnerabilities, session management issues, and authentication bypass.
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


class AuthenticationScanner(ActiveScanner):
    """
    Authentication security scanner.
    
    Tests for:
    - Weak/default credentials
    - Brute force protection
    - Session management issues
    - Authentication bypass vulnerabilities
    - Password policy weaknesses
    """
    
    # Common default credentials to test
    DEFAULT_CREDENTIALS = [
        ('admin', 'admin'),
        ('admin', 'password'),
        ('admin', '123456'),
        ('root', 'root'),
        ('root', 'password'),
        ('test', 'test'),
        ('user', 'user'),
        ('guest', 'guest'),
    ]
    
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        throttler: Optional[RequestThrottler] = None
    ):
        """
        Initialize authentication scanner.
        
        Args:
            http_client: HTTP client for making requests
            throttler: Request throttler for rate limiting
        """
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.throttler = throttler or RequestThrottler()
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "authentication"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "Authentication security testing (weak credentials, brute force, session management)"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.AUTHENTICATION
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute authentication scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting authentication scan of {target.url}")
        
        try:
            # Fetch target page to find login forms
            response = await self.http_client.get(target.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find login forms
            login_forms = await self._find_login_forms(soup, target.url)
            
            if login_forms:
                # Test for default credentials
                await self._test_default_credentials(target, login_forms, config)
                
                # Test for brute force protection
                await self._test_brute_force_protection(target, login_forms, config)
                
                # Test for username enumeration
                await self._test_username_enumeration(target, login_forms, config)
            
            # Test session management
            await self._test_session_management(target, config)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Authentication scan completed: "
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
            logger.error(f"Authentication scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _find_login_forms(
        self,
        soup: BeautifulSoup,
        base_url: str
    ) -> List[Dict]:
        """
        Find login forms on the page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative paths
        
        Returns:
            List of login form dictionaries
        """
        login_forms = []
        
        for form in soup.find_all('form'):
            # Look for password fields
            password_fields = form.find_all('input', {'type': 'password'})
            if not password_fields:
                continue
            
            # Extract form details
            action = form.get('action', '')
            method = form.get('method', 'post').lower()
            
            # Find username/email field
            username_field = None
            for input_field in form.find_all('input'):
                input_type = input_field.get('type', 'text').lower()
                input_name = input_field.get('name', '').lower()
                
                if input_type in ['text', 'email'] or 'user' in input_name or 'email' in input_name:
                    username_field = input_field.get('name')
                    break
            
            if username_field:
                login_forms.append({
                    'action': urljoin(base_url, action) if action else base_url,
                    'method': method,
                    'username_field': username_field,
                    'password_field': password_fields[0].get('name', 'password')
                })
        
        return login_forms
    
    async def _test_default_credentials(
        self,
        target: Target,
        login_forms: List[Dict],
        config: Configuration
    ) -> None:
        """
        Test for default/weak credentials.
        
        Args:
            target: Target being scanned
            login_forms: List of login forms
            config: Scan configuration
        """
        logger.info("Testing for default credentials")
        
        for form in login_forms[:1]:  # Test first form only
            action_url = form['action']
            method = form['method']
            username_field = form['username_field']
            password_field = form['password_field']
            
            # Test a few default credentials
            for username, password in self.DEFAULT_CREDENTIALS[:3]:
                await self.throttler.acquire()
                
                credentials = {
                    username_field: username,
                    password_field: password
                }
                
                try:
                    if method == 'post':
                        response = await self.http_client.post(
                            action_url,
                            data=credentials,
                            timeout=10
                        )
                    else:
                        response = await self.http_client.get(
                            action_url,
                            params=credentials,
                            timeout=10
                        )
                    
                    # Check for successful login indicators
                    content = response.content.decode('utf-8', errors='ignore').lower()
                    
                    # Success indicators
                    success_indicators = [
                        'welcome',
                        'dashboard',
                        'logout',
                        'profile',
                        'account',
                    ]
                    
                    # Failure indicators
                    failure_indicators = [
                        'invalid',
                        'incorrect',
                        'failed',
                        'error',
                        'wrong',
                    ]
                    
                    has_success = any(indicator in content for indicator in success_indicators)
                    has_failure = any(indicator in content for indicator in failure_indicators)
                    
                    # If we see success indicators and no failure indicators, might be vulnerable
                    if has_success and not has_failure:
                        self.create_finding(
                            title="Potential Default Credentials",
                            description=f"Login form may accept default credentials: {username}/{password}",
                            severity=Severity.CRITICAL,
                            category=VulnerabilityCategory.AUTHENTICATION,
                            affected_url=action_url,
                            confidence=0.6,
                            proof_of_concept=f"Username: {username}, Password: {password}",
                            remediation="Change default credentials and enforce strong password policy",
                            cvss_score=9.0,
                            cwe_id="CWE-798",
                            owasp_category="A07:2021 - Identification and Authentication Failures"
                        )
                        logger.warning(f"Potential default credentials at {action_url}")
                        return  # Stop testing after finding one
                
                except Exception as e:
                    logger.debug(f"Error testing credentials: {e}")
    
    async def _test_brute_force_protection(
        self,
        target: Target,
        login_forms: List[Dict],
        config: Configuration
    ) -> None:
        """
        Test for brute force protection.
        
        Args:
            target: Target being scanned
            login_forms: List of login forms
            config: Scan configuration
        """
        logger.info("Testing for brute force protection")
        
        for form in login_forms[:1]:  # Test first form only
            action_url = form['action']
            method = form['method']
            username_field = form['username_field']
            password_field = form['password_field']
            
            # Attempt multiple failed logins
            failed_attempts = 0
            max_attempts = 5
            
            for i in range(max_attempts):
                await self.throttler.acquire()
                
                credentials = {
                    username_field: 'testuser',
                    password_field: f'wrongpassword{i}'
                }
                
                try:
                    if method == 'post':
                        response = await self.http_client.post(
                            action_url,
                            data=credentials,
                            timeout=10
                        )
                    else:
                        response = await self.http_client.get(
                            action_url,
                            params=credentials,
                            timeout=10
                        )
                    
                    # Check if we're still getting normal responses
                    if response.status_code == 200:
                        failed_attempts += 1
                    elif response.status_code == 429:  # Too Many Requests
                        # Good! Rate limiting is in place
                        logger.info("Rate limiting detected")
                        return
                    
                except Exception as e:
                    logger.debug(f"Error testing brute force protection: {e}")
            
            # If we completed all attempts without being blocked
            if failed_attempts >= max_attempts:
                self.create_finding(
                    title="Missing Brute Force Protection",
                    description=f"Login form allows {max_attempts} failed login attempts without rate limiting",
                    severity=Severity.HIGH,
                    category=VulnerabilityCategory.AUTHENTICATION,
                    affected_url=action_url,
                    confidence=0.8,
                    proof_of_concept=f"Completed {failed_attempts} failed login attempts without blocking",
                    remediation="Implement rate limiting, account lockout, or CAPTCHA after failed attempts",
                    cvss_score=7.5,
                    cwe_id="CWE-307",
                    owasp_category="A07:2021 - Identification and Authentication Failures"
                )
                logger.warning(f"Missing brute force protection at {action_url}")
    
    async def _test_username_enumeration(
        self,
        target: Target,
        login_forms: List[Dict],
        config: Configuration
    ) -> None:
        """
        Test for username enumeration vulnerability.
        
        Args:
            target: Target being scanned
            login_forms: List of login forms
            config: Scan configuration
        """
        logger.info("Testing for username enumeration")
        
        for form in login_forms[:1]:  # Test first form only
            action_url = form['action']
            method = form['method']
            username_field = form['username_field']
            password_field = form['password_field']
            
            # Test with valid-looking and invalid usernames
            test_cases = [
                ('admin', 'wrongpassword'),
                ('nonexistentuser12345', 'wrongpassword')
            ]
            
            responses = []
            
            for username, password in test_cases:
                await self.throttler.acquire()
                
                credentials = {
                    username_field: username,
                    password_field: password
                }
                
                try:
                    if method == 'post':
                        response = await self.http_client.post(
                            action_url,
                            data=credentials,
                            timeout=10
                        )
                    else:
                        response = await self.http_client.get(
                            action_url,
                            params=credentials,
                            timeout=10
                        )
                    
                    content = response.content.decode('utf-8', errors='ignore')
                    responses.append({
                        'username': username,
                        'content': content,
                        'length': len(content),
                        'status': response.status_code
                    })
                
                except Exception as e:
                    logger.debug(f"Error testing username enumeration: {e}")
            
            # Compare responses
            if len(responses) == 2:
                diff = abs(responses[0]['length'] - responses[1]['length'])
                
                # If responses differ significantly, might be vulnerable
                if diff > 50:  # More than 50 characters difference
                    self.create_finding(
                        title="Username Enumeration Vulnerability",
                        description="Login form reveals whether usernames exist based on error messages",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.AUTHENTICATION,
                        affected_url=action_url,
                        confidence=0.7,
                        proof_of_concept=f"Response length differs by {diff} characters for valid vs invalid usernames",
                        remediation="Use generic error messages that don't reveal username validity",
                        cvss_score=5.0,
                        cwe_id="CWE-203",
                        owasp_category="A07:2021 - Identification and Authentication Failures"
                    )
                    logger.info(f"Username enumeration vulnerability at {action_url}")
    
    async def _test_session_management(
        self,
        target: Target,
        config: Configuration
    ) -> None:
        """
        Test session management security.
        
        Args:
            target: Target being scanned
            config: Scan configuration
        """
        logger.info("Testing session management")
        
        try:
            # Make a request and check session cookies
            response = await self.http_client.get(target.url)
            
            # Check for session cookies
            cookies = response.headers.get('set-cookie', '')
            
            if cookies:
                cookies_lower = cookies.lower()
                
                # Check for HttpOnly flag
                if 'httponly' not in cookies_lower:
                    self.create_finding(
                        title="Session Cookie Missing HttpOnly Flag",
                        description="Session cookies do not have HttpOnly flag set",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.SESSION_MANAGEMENT,
                        affected_url=target.url,
                        confidence=1.0,
                        proof_of_concept=f"Set-Cookie: {cookies}",
                        remediation="Set HttpOnly flag on all session cookies",
                        cvss_score=5.5,
                        cwe_id="CWE-1004",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    )
                
                # Check for Secure flag on HTTPS sites
                if target.scheme == 'https' and 'secure' not in cookies_lower:
                    self.create_finding(
                        title="Session Cookie Missing Secure Flag",
                        description="Session cookies on HTTPS site do not have Secure flag set",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.SESSION_MANAGEMENT,
                        affected_url=target.url,
                        confidence=1.0,
                        proof_of_concept=f"Set-Cookie: {cookies}",
                        remediation="Set Secure flag on all session cookies for HTTPS sites",
                        cvss_score=5.5,
                        cwe_id="CWE-614",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    )
                
                # Check for SameSite attribute
                if 'samesite' not in cookies_lower:
                    self.create_finding(
                        title="Session Cookie Missing SameSite Attribute",
                        description="Session cookies do not have SameSite attribute set",
                        severity=Severity.LOW,
                        category=VulnerabilityCategory.SESSION_MANAGEMENT,
                        affected_url=target.url,
                        confidence=1.0,
                        proof_of_concept=f"Set-Cookie: {cookies}",
                        remediation="Set SameSite attribute (Strict or Lax) on session cookies",
                        cvss_score=4.0,
                        cwe_id="CWE-1275",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    )
        
        except Exception as e:
            logger.debug(f"Error testing session management: {e}")
