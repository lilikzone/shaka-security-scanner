"""
Security headers analyzer scanner.

This scanner performs passive analysis of HTTP security headers to identify
missing or misconfigured security controls.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

from ..models import (
    Target, Configuration, TestSuite,
    Severity, VulnerabilityCategory
)
from ..http import HTTPClient
from .base import PassiveScanner, ScanResult


logger = logging.getLogger(__name__)


class HeadersScanner(PassiveScanner):
    """
    Security headers analyzer.
    
    Analyzes HTTP response headers for security best practices:
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy (CSP)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    - And more...
    """
    
    # Security headers that should be present
    RECOMMENDED_HEADERS = {
        'strict-transport-security': {
            'name': 'Strict-Transport-Security',
            'description': 'Enforces HTTPS connections',
            'severity': Severity.HIGH,
            'recommendation': 'Add: Strict-Transport-Security: max-age=31536000; includeSubDomains'
        },
        'content-security-policy': {
            'name': 'Content-Security-Policy',
            'description': 'Prevents XSS and data injection attacks',
            'severity': Severity.HIGH,
            'recommendation': 'Implement a Content-Security-Policy header'
        },
        'x-frame-options': {
            'name': 'X-Frame-Options',
            'description': 'Prevents clickjacking attacks',
            'severity': Severity.MEDIUM,
            'recommendation': 'Add: X-Frame-Options: DENY or SAMEORIGIN'
        },
        'x-content-type-options': {
            'name': 'X-Content-Type-Options',
            'description': 'Prevents MIME type sniffing',
            'severity': Severity.MEDIUM,
            'recommendation': 'Add: X-Content-Type-Options: nosniff'
        },
        'referrer-policy': {
            'name': 'Referrer-Policy',
            'description': 'Controls referrer information',
            'severity': Severity.LOW,
            'recommendation': 'Add: Referrer-Policy: strict-origin-when-cross-origin'
        },
        'permissions-policy': {
            'name': 'Permissions-Policy',
            'description': 'Controls browser features and APIs',
            'severity': Severity.LOW,
            'recommendation': 'Add: Permissions-Policy: geolocation=(), microphone=(), camera=()'
        }
    }
    
    # Headers that should NOT be present (information disclosure)
    DISCOURAGED_HEADERS = {
        'server': {
            'name': 'Server',
            'description': 'Discloses server information',
            'severity': Severity.LOW
        },
        'x-powered-by': {
            'name': 'X-Powered-By',
            'description': 'Discloses technology stack',
            'severity': Severity.LOW
        },
        'x-aspnet-version': {
            'name': 'X-AspNet-Version',
            'description': 'Discloses ASP.NET version',
            'severity': Severity.LOW
        },
        'x-aspnetmvc-version': {
            'name': 'X-AspNetMvc-Version',
            'description': 'Discloses ASP.NET MVC version',
            'severity': Severity.LOW
        }
    }
    
    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize headers scanner.
        
        Args:
            http_client: HTTP client for making requests
        """
        super().__init__()
        self.http_client = http_client or HTTPClient()
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "headers"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "Security headers analysis (HSTS, CSP, X-Frame-Options, etc.)"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.HEADERS
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute headers scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting security headers scan of {target.url}")
        
        try:
            # Fetch target page headers
            response = await self.http_client.head(target.url)
            headers = {k.lower(): v for k, v in response.headers.items()}
            
            # Check for missing security headers
            await self._check_missing_headers(target, headers)
            
            # Check for information disclosure headers
            await self._check_disclosure_headers(target, headers)
            
            # Validate specific header configurations
            await self._validate_hsts(target, headers)
            await self._validate_csp(target, headers)
            await self._validate_x_frame_options(target, headers)
            
            # Check for deprecated headers
            await self._check_deprecated_headers(target, headers)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Headers scan completed: "
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
            logger.error(f"Headers scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _check_missing_headers(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Check for missing security headers.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        for header_key, header_info in self.RECOMMENDED_HEADERS.items():
            if header_key not in headers:
                self.create_finding(
                    title=f"Missing Security Header: {header_info['name']}",
                    description=f"{header_info['description']}. This header is not present in the response.",
                    severity=header_info['severity'],
                    category=VulnerabilityCategory.SECURITY_HEADERS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Header '{header_info['name']}' is missing",
                    remediation=header_info['recommendation'],
                    owasp_category="A05:2021 - Security Misconfiguration"
                )
                logger.info(f"Missing header: {header_info['name']} at {target.url}")
    
    async def _check_disclosure_headers(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Check for information disclosure headers.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        for header_key, header_info in self.DISCOURAGED_HEADERS.items():
            if header_key in headers:
                self.create_finding(
                    title=f"Information Disclosure: {header_info['name']}",
                    description=f"{header_info['description']}. Value: {headers[header_key]}",
                    severity=header_info['severity'],
                    category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"{header_info['name']}: {headers[header_key]}",
                    remediation=f"Remove or obfuscate the '{header_info['name']}' header",
                    owasp_category="A05:2021 - Security Misconfiguration"
                )
                logger.info(
                    f"Information disclosure header: {header_info['name']} at {target.url}"
                )
    
    async def _validate_hsts(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Validate HSTS header configuration.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        # Only check HSTS for HTTPS sites
        if target.scheme != 'https':
            return
        
        hsts = headers.get('strict-transport-security', '')
        if not hsts:
            return  # Already reported as missing
        
        # Check max-age
        if 'max-age' not in hsts.lower():
            self.create_finding(
                title="HSTS Missing max-age Directive",
                description="Strict-Transport-Security header is present but missing max-age directive",
                severity=Severity.MEDIUM,
                category=VulnerabilityCategory.SECURITY_HEADERS,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"Strict-Transport-Security: {hsts}",
                remediation="Add max-age directive: Strict-Transport-Security: max-age=31536000",
                owasp_category="A05:2021 - Security Misconfiguration"
            )
        else:
            # Extract max-age value
            import re
            match = re.search(r'max-age=(\d+)', hsts, re.IGNORECASE)
            if match:
                max_age = int(match.group(1))
                # Recommend at least 6 months (15768000 seconds)
                if max_age < 15768000:
                    self.create_finding(
                        title="HSTS max-age Too Short",
                        description=f"HSTS max-age is {max_age} seconds (less than 6 months)",
                        severity=Severity.LOW,
                        category=VulnerabilityCategory.SECURITY_HEADERS,
                        affected_url=target.url,
                        confidence=1.0,
                        proof_of_concept=f"Strict-Transport-Security: {hsts}",
                        remediation="Increase max-age to at least 31536000 (1 year)",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    )
        
        # Check includeSubDomains
        if 'includesubdomains' not in hsts.lower():
            self.create_finding(
                title="HSTS Missing includeSubDomains",
                description="HSTS header does not include subdomains",
                severity=Severity.LOW,
                category=VulnerabilityCategory.SECURITY_HEADERS,
                affected_url=target.url,
                confidence=0.8,
                proof_of_concept=f"Strict-Transport-Security: {hsts}",
                remediation="Add includeSubDomains directive if applicable",
                owasp_category="A05:2021 - Security Misconfiguration"
            )
    
    async def _validate_csp(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Validate Content-Security-Policy header.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        csp = headers.get('content-security-policy', '')
        if not csp:
            return  # Already reported as missing
        
        # Check for unsafe directives
        unsafe_patterns = [
            ("'unsafe-inline'", "Allows inline scripts/styles", Severity.HIGH),
            ("'unsafe-eval'", "Allows eval() and similar functions", Severity.HIGH),
            ("*", "Allows resources from any origin", Severity.MEDIUM),
        ]
        
        for pattern, description, severity in unsafe_patterns:
            if pattern in csp:
                self.create_finding(
                    title=f"Weak CSP: {pattern}",
                    description=f"Content-Security-Policy contains {pattern}. {description}.",
                    severity=severity,
                    category=VulnerabilityCategory.SECURITY_HEADERS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Content-Security-Policy: {csp}",
                    remediation=f"Remove {pattern} from CSP or use nonces/hashes",
                    owasp_category="A05:2021 - Security Misconfiguration"
                )
    
    async def _validate_x_frame_options(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Validate X-Frame-Options header.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        xfo = headers.get('x-frame-options', '')
        if not xfo:
            return  # Already reported as missing
        
        # Check for valid values
        valid_values = ['deny', 'sameorigin']
        if xfo.lower() not in valid_values and not xfo.lower().startswith('allow-from'):
            self.create_finding(
                title="Invalid X-Frame-Options Value",
                description=f"X-Frame-Options has invalid value: {xfo}",
                severity=Severity.MEDIUM,
                category=VulnerabilityCategory.SECURITY_HEADERS,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"X-Frame-Options: {xfo}",
                remediation="Use DENY or SAMEORIGIN",
                owasp_category="A05:2021 - Security Misconfiguration"
            )
    
    async def _check_deprecated_headers(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Check for deprecated security headers.
        
        Args:
            target: Target being scanned
            headers: Response headers (lowercase keys)
        """
        # X-XSS-Protection is deprecated in favor of CSP
        if 'x-xss-protection' in headers:
            xss_protection = headers['x-xss-protection']
            # Only report if it's enabled (value is "1")
            if xss_protection.startswith('1'):
                self.create_finding(
                    title="Deprecated Header: X-XSS-Protection",
                    description="X-XSS-Protection is deprecated. Use Content-Security-Policy instead.",
                    severity=Severity.INFO,
                    category=VulnerabilityCategory.SECURITY_HEADERS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"X-XSS-Protection: {xss_protection}",
                    remediation="Remove X-XSS-Protection and implement Content-Security-Policy",
                    owasp_category="A05:2021 - Security Misconfiguration"
                )
