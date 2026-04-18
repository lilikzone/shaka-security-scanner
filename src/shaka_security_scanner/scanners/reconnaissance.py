"""
Reconnaissance scanner for passive information gathering.

This scanner performs passive reconnaissance to gather information about
the target without actively probing for vulnerabilities.
"""

import re
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from ..models import (
    Target, Configuration, Finding, TestSuite,
    Severity, VulnerabilityCategory, Technology
)
from ..http import HTTPClient
from .base import PassiveScanner, ScanResult


logger = logging.getLogger(__name__)


class ReconnaissanceScanner(PassiveScanner):
    """
    Passive reconnaissance scanner.
    
    Performs information gathering including:
    - Technology detection (frameworks, servers, libraries)
    - Endpoint discovery (links, forms, API endpoints)
    - Comment extraction (developer comments, TODOs)
    - Metadata extraction (emails, phone numbers, internal IPs)
    """
    
    def __init__(self, http_client: Optional[HTTPClient] = None):
        """
        Initialize reconnaissance scanner.
        
        Args:
            http_client: HTTP client for making requests (creates new if None)
        """
        super().__init__()
        self.http_client = http_client or HTTPClient()
        
        # Technology detection patterns
        self.tech_patterns = {
            # Frameworks
            'Django': [
                r'csrfmiddlewaretoken',
                r'__admin',
                r'django',
            ],
            'Flask': [
                r'flask',
                r'werkzeug',
            ],
            'Express': [
                r'express',
                r'X-Powered-By.*Express',
            ],
            'Laravel': [
                r'laravel',
                r'laravel_session',
            ],
            'Ruby on Rails': [
                r'rails',
                r'_session_id',
            ],
            'ASP.NET': [
                r'__VIEWSTATE',
                r'ASP\.NET',
                r'\.aspx',
            ],
            'WordPress': [
                r'wp-content',
                r'wp-includes',
                r'wordpress',
            ],
            'Joomla': [
                r'joomla',
                r'/components/',
            ],
            'Drupal': [
                r'drupal',
                r'sites/default',
            ],
            
            # JavaScript Libraries
            'jQuery': [r'jquery'],
            'React': [r'react', r'_react'],
            'Angular': [r'angular', r'ng-'],
            'Vue.js': [r'vue', r'v-'],
            
            # Servers
            'Apache': [r'Apache'],
            'Nginx': [r'nginx'],
            'IIS': [r'IIS', r'Microsoft-IIS'],
            'Tomcat': [r'Tomcat'],
        }
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "reconnaissance"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "Passive reconnaissance and information gathering"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.RECONNAISSANCE
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute reconnaissance scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting reconnaissance scan of {target.url}")
        
        try:
            # Fetch target page
            response = await self.http_client.get(target.url)
            
            if response.status_code != 200:
                logger.warning(
                    f"Non-200 response: {response.status_code}"
                )
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Perform reconnaissance tasks
            await self._detect_technologies(target, response, soup)
            await self._discover_endpoints(target, soup, target.url)
            await self._extract_comments(target, soup)
            await self._extract_metadata(target, soup, response.content)
            await self._analyze_headers(target, response.headers)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Reconnaissance scan completed: "
                f"{len(self.get_findings())} findings in {duration:.2f}s"
            )
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                findings=self.get_findings(),
                tests_performed=5,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Reconnaissance scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _detect_technologies(
        self,
        target: Target,
        response,
        soup: BeautifulSoup
    ) -> None:
        """
        Detect technologies used by the target.
        
        Args:
            target: Target being scanned
            response: HTTP response
            soup: Parsed HTML
        """
        detected_techs: Set[str] = set()
        
        # Check response headers
        headers_str = str(response.headers).lower()
        
        # Check response body
        body_str = str(soup).lower()
        
        # Check against patterns
        for tech_name, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, headers_str, re.IGNORECASE):
                    detected_techs.add(tech_name)
                    break
                elif re.search(pattern, body_str, re.IGNORECASE):
                    detected_techs.add(tech_name)
                    break
        
        # Create findings for detected technologies
        if detected_techs:
            tech_list = ', '.join(sorted(detected_techs))
            self.create_finding(
                title="Technologies Detected",
                description=f"Detected technologies: {tech_list}",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=0.8,
                proof_of_concept=f"Technologies: {tech_list}",
                remediation="Review exposed technology information"
            )
            
            logger.info(f"Detected technologies: {tech_list}")
    
    async def _discover_endpoints(
        self,
        target: Target,
        soup: BeautifulSoup,
        base_url: str
    ) -> None:
        """
        Discover endpoints from HTML.
        
        Args:
            target: Target being scanned
            soup: Parsed HTML
            base_url: Base URL for resolving relative URLs
        """
        endpoints: Set[str] = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Only include same-domain URLs
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                endpoints.add(full_url)
        
        # Find forms
        forms = soup.find_all('form')
        if forms:
            form_actions = []
            for form in forms:
                action = form.get('action', '')
                if action:
                    full_url = urljoin(base_url, action)
                    endpoints.add(full_url)
                    form_actions.append(full_url)
            
            if form_actions:
                self.create_finding(
                    title="Forms Discovered",
                    description=f"Found {len(forms)} forms on the page",
                    severity=Severity.INFO,
                    category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Form actions: {', '.join(form_actions[:5])}",
                    remediation="Review form security (CSRF tokens, validation)"
                )
        
        # Find scripts
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script['src']
            full_url = urljoin(base_url, src)
            endpoints.add(full_url)
        
        if endpoints:
            logger.info(f"Discovered {len(endpoints)} endpoints")
            
            # Create finding for endpoint discovery
            endpoint_sample = list(endpoints)[:10]
            self.create_finding(
                title="Endpoints Discovered",
                description=f"Discovered {len(endpoints)} endpoints",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"Sample endpoints: {', '.join(endpoint_sample)}",
                remediation="Review endpoint security and access controls"
            )
    
    async def _extract_comments(
        self,
        target: Target,
        soup: BeautifulSoup
    ) -> None:
        """
        Extract HTML comments.
        
        Args:
            target: Target being scanned
            soup: Parsed HTML
        """
        from bs4 import Comment
        
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        
        if comments:
            # Look for sensitive information in comments
            sensitive_patterns = [
                (r'password', 'Password reference'),
                (r'api[_-]?key', 'API key reference'),
                (r'secret', 'Secret reference'),
                (r'token', 'Token reference'),
                (r'TODO|FIXME|HACK|XXX', 'Developer note'),
                (r'admin', 'Admin reference'),
                (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP address'),
            ]
            
            sensitive_comments = []
            for comment in comments:
                comment_text = str(comment).strip()
                for pattern, description in sensitive_patterns:
                    if re.search(pattern, comment_text, re.IGNORECASE):
                        sensitive_comments.append({
                            'text': comment_text[:100],
                            'type': description
                        })
                        break
            
            if sensitive_comments:
                comment_summary = '\n'.join([
                    f"- {c['type']}: {c['text']}"
                    for c in sensitive_comments[:5]
                ])
                
                self.create_finding(
                    title="Sensitive Information in Comments",
                    description=f"Found {len(sensitive_comments)} comments with potentially sensitive information",
                    severity=Severity.LOW,
                    category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                    affected_url=target.url,
                    confidence=0.7,
                    proof_of_concept=comment_summary,
                    remediation="Remove sensitive information from HTML comments"
                )
                
                logger.info(f"Found {len(sensitive_comments)} sensitive comments")
    
    async def _extract_metadata(
        self,
        target: Target,
        soup: BeautifulSoup,
        content: bytes
    ) -> None:
        """
        Extract metadata like emails, phone numbers.
        
        Args:
            target: Target being scanned
            soup: Parsed HTML
            content: Raw response content
        """
        content_str = content.decode('utf-8', errors='ignore')
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, content_str))
        
        if emails:
            self.create_finding(
                title="Email Addresses Exposed",
                description=f"Found {len(emails)} email addresses",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=0.9,
                proof_of_concept=f"Emails: {', '.join(list(emails)[:5])}",
                remediation="Consider obfuscating email addresses to prevent scraping"
            )
            
            logger.info(f"Found {len(emails)} email addresses")
        
        # Extract internal IP addresses
        internal_ip_pattern = r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b'
        internal_ips = set(re.findall(internal_ip_pattern, content_str))
        
        if internal_ips:
            self.create_finding(
                title="Internal IP Addresses Exposed",
                description=f"Found {len(internal_ips)} internal IP addresses",
                severity=Severity.LOW,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=0.8,
                proof_of_concept=f"IPs: {', '.join(internal_ips)}",
                remediation="Remove internal IP addresses from public content"
            )
            
            logger.info(f"Found {len(internal_ips)} internal IPs")
    
    async def _analyze_headers(
        self,
        target: Target,
        headers: Dict[str, str]
    ) -> None:
        """
        Analyze HTTP response headers.
        
        Args:
            target: Target being scanned
            headers: Response headers
        """
        # Check for server header disclosure
        if 'server' in headers:
            server = headers['server']
            self.create_finding(
                title="Server Header Disclosure",
                description=f"Server header reveals: {server}",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"Server: {server}",
                remediation="Consider removing or obfuscating server header"
            )
        
        # Check for X-Powered-By header
        if 'x-powered-by' in headers:
            powered_by = headers['x-powered-by']
            self.create_finding(
                title="X-Powered-By Header Disclosure",
                description=f"X-Powered-By header reveals: {powered_by}",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"X-Powered-By: {powered_by}",
                remediation="Remove X-Powered-By header"
            )
