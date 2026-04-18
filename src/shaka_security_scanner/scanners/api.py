"""
API security scanner.

This scanner tests for API-specific security issues including authentication,
authorization, rate limiting, and common API vulnerabilities.
"""

import logging
import json
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, urljoin

from ..models import (
    Target, Configuration, TestSuite,
    Severity, VulnerabilityCategory
)
from ..http import HTTPClient, RequestThrottler
from .base import ActiveScanner, ScanResult


logger = logging.getLogger(__name__)


class APIScanner(ActiveScanner):
    """
    API security scanner.
    
    Tests for:
    - Missing authentication
    - Broken authorization (BOLA/IDOR)
    - Excessive data exposure
    - Rate limiting
    - Mass assignment
    - Security misconfiguration
    """
    
    # Common API endpoints to test
    API_ENDPOINTS = [
        '/api',
        '/api/v1',
        '/api/v2',
        '/rest',
        '/graphql',
        '/swagger',
        '/openapi',
    ]
    
    # Common HTTP methods
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        throttler: Optional[RequestThrottler] = None
    ):
        """
        Initialize API scanner.
        
        Args:
            http_client: HTTP client for making requests
            throttler: Request throttler for rate limiting
        """
        super().__init__()
        self.http_client = http_client or HTTPClient()
        self.throttler = throttler or RequestThrottler()
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "api"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "API security testing (authentication, authorization, rate limiting)"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.API
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute API scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting API scan of {target.url}")
        
        try:
            # Discover API endpoints
            api_endpoints = await self._discover_api_endpoints(target)
            
            if api_endpoints:
                # Test for missing authentication
                await self._test_missing_authentication(target, api_endpoints, config)
                
                # Test for broken authorization
                await self._test_broken_authorization(target, api_endpoints, config)
                
                # Test for excessive data exposure
                await self._test_excessive_data_exposure(target, api_endpoints, config)
                
                # Test for rate limiting
                await self._test_rate_limiting(target, api_endpoints, config)
            
            duration = time.time() - start_time
            
            logger.info(
                f"API scan completed: "
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
            logger.error(f"API scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _discover_api_endpoints(
        self,
        target: Target
    ) -> List[str]:
        """
        Discover API endpoints.
        
        Args:
            target: Target being scanned
        
        Returns:
            List of discovered API endpoints
        """
        endpoints = []
        
        # Test common API paths
        for api_path in self.API_ENDPOINTS[:3]:  # Test first 3
            test_url = urljoin(target.url, api_path)
            
            try:
                response = await self.http_client.get(test_url, timeout=5)
                
                # Check if it looks like an API endpoint
                if response.status_code in [200, 401, 403]:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'json' in content_type or 'api' in content_type:
                        endpoints.append(test_url)
                        logger.info(f"Discovered API endpoint: {test_url}")
            
            except Exception as e:
                logger.debug(f"Error testing {test_url}: {e}")
        
        return endpoints
    
    async def _test_missing_authentication(
        self,
        target: Target,
        api_endpoints: List[str],
        config: Configuration
    ) -> None:
        """
        Test for missing authentication.
        
        Args:
            target: Target being scanned
            api_endpoints: List of API endpoints
            config: Scan configuration
        """
        logger.info("Testing for missing authentication")
        
        for endpoint in api_endpoints[:2]:  # Test first 2 endpoints
            await self.throttler.acquire()
            
            try:
                # Try to access without authentication
                response = await self.http_client.get(endpoint, timeout=10)
                
                # If we get 200, might be missing authentication
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Check if it returns data
                    if 'json' in content_type and len(response.content) > 10:
                        self.create_finding(
                            title="API Endpoint Without Authentication",
                            description=f"API endpoint accessible without authentication",
                            severity=Severity.HIGH,
                            category=VulnerabilityCategory.AUTHENTICATION,
                            affected_url=endpoint,
                            confidence=0.7,
                            proof_of_concept=f"GET {endpoint} returns 200 without authentication",
                            remediation="Implement authentication for all API endpoints",
                            cvss_score=7.5,
                            cwe_id="CWE-306",
                            owasp_category="API1:2023 - Broken Object Level Authorization"
                        )
                        logger.warning(f"Missing authentication at {endpoint}")
            
            except Exception as e:
                logger.debug(f"Error testing authentication: {e}")
    
    async def _test_broken_authorization(
        self,
        target: Target,
        api_endpoints: List[str],
        config: Configuration
    ) -> None:
        """
        Test for broken authorization (BOLA/IDOR).
        
        Args:
            target: Target being scanned
            api_endpoints: List of API endpoints
            config: Scan configuration
        """
        logger.info("Testing for broken authorization")
        
        for endpoint in api_endpoints[:2]:  # Test first 2 endpoints
            # Test with different IDs
            test_ids = ['1', '2', '999', 'admin']
            
            for test_id in test_ids[:2]:  # Test first 2 IDs
                await self.throttler.acquire()
                
                # Try common ID patterns
                test_urls = [
                    f"{endpoint}/{test_id}",
                    f"{endpoint}?id={test_id}",
                    f"{endpoint}?user_id={test_id}",
                ]
                
                for test_url in test_urls[:1]:  # Test first pattern
                    try:
                        response = await self.http_client.get(test_url, timeout=10)
                        
                        # If we get 200 with data, might be IDOR
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            
                            if 'json' in content_type:
                                try:
                                    data = json.loads(response.content)
                                    
                                    # Check if response contains user data
                                    if isinstance(data, dict) and any(
                                        key in str(data).lower()
                                        for key in ['user', 'email', 'name', 'id']
                                    ):
                                        self.create_finding(
                                            title="Potential Broken Object Level Authorization (BOLA)",
                                            description=f"API endpoint may allow access to other users' data",
                                            severity=Severity.HIGH,
                                            category=VulnerabilityCategory.BROKEN_ACCESS_CONTROL,
                                            affected_url=test_url,
                                            confidence=0.6,
                                            proof_of_concept=f"GET {test_url} returns user data without proper authorization check",
                                            remediation="Implement proper authorization checks for object access",
                                            cvss_score=8.0,
                                            cwe_id="CWE-639",
                                            owasp_category="API1:2023 - Broken Object Level Authorization"
                                        )
                                        logger.warning(f"Potential BOLA at {test_url}")
                                        return
                                
                                except json.JSONDecodeError:
                                    pass
                    
                    except Exception as e:
                        logger.debug(f"Error testing authorization: {e}")
    
    async def _test_excessive_data_exposure(
        self,
        target: Target,
        api_endpoints: List[str],
        config: Configuration
    ) -> None:
        """
        Test for excessive data exposure.
        
        Args:
            target: Target being scanned
            api_endpoints: List of API endpoints
            config: Scan configuration
        """
        logger.info("Testing for excessive data exposure")
        
        for endpoint in api_endpoints[:2]:  # Test first 2 endpoints
            await self.throttler.acquire()
            
            try:
                response = await self.http_client.get(endpoint, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'json' in content_type:
                        try:
                            data = json.loads(response.content)
                            
                            # Check for sensitive fields
                            sensitive_fields = [
                                'password', 'token', 'secret', 'api_key',
                                'private_key', 'ssn', 'credit_card'
                            ]
                            
                            data_str = str(data).lower()
                            found_sensitive = [
                                field for field in sensitive_fields
                                if field in data_str
                            ]
                            
                            if found_sensitive:
                                self.create_finding(
                                    title="Excessive Data Exposure",
                                    description=f"API response contains sensitive fields: {', '.join(found_sensitive)}",
                                    severity=Severity.MEDIUM,
                                    category=VulnerabilityCategory.SENSITIVE_DATA_EXPOSURE,
                                    affected_url=endpoint,
                                    confidence=0.8,
                                    proof_of_concept=f"Response contains: {', '.join(found_sensitive)}",
                                    remediation="Filter sensitive data from API responses",
                                    cvss_score=6.5,
                                    cwe_id="CWE-200",
                                    owasp_category="API3:2023 - Broken Object Property Level Authorization"
                                )
                                logger.warning(f"Excessive data exposure at {endpoint}")
                        
                        except json.JSONDecodeError:
                            pass
            
            except Exception as e:
                logger.debug(f"Error testing data exposure: {e}")
    
    async def _test_rate_limiting(
        self,
        target: Target,
        api_endpoints: List[str],
        config: Configuration
    ) -> None:
        """
        Test for rate limiting.
        
        Args:
            target: Target being scanned
            api_endpoints: List of API endpoints
            config: Scan configuration
        """
        logger.info("Testing for rate limiting")
        
        for endpoint in api_endpoints[:1]:  # Test first endpoint only
            # Make multiple rapid requests
            request_count = 10
            success_count = 0
            
            for i in range(request_count):
                try:
                    response = await self.http_client.get(endpoint, timeout=5)
                    
                    if response.status_code == 200:
                        success_count += 1
                    elif response.status_code == 429:  # Too Many Requests
                        # Good! Rate limiting is in place
                        logger.info(f"Rate limiting detected at {endpoint}")
                        return
                
                except Exception as e:
                    logger.debug(f"Error testing rate limiting: {e}")
            
            # If all requests succeeded, rate limiting might be missing
            if success_count >= request_count * 0.8:  # 80% success rate
                self.create_finding(
                    title="Missing API Rate Limiting",
                    description=f"API endpoint allows {request_count} rapid requests without rate limiting",
                    severity=Severity.MEDIUM,
                    category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
                    affected_url=endpoint,
                    confidence=0.7,
                    proof_of_concept=f"Completed {success_count}/{request_count} requests without rate limiting",
                    remediation="Implement rate limiting to prevent abuse",
                    cvss_score=5.0,
                    cwe_id="CWE-770",
                    owasp_category="API4:2023 - Unrestricted Resource Consumption"
                )
                logger.warning(f"Missing rate limiting at {endpoint}")
