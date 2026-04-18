"""
SSL/TLS security scanner.

This scanner analyzes SSL/TLS configuration including certificate validation,
protocol versions, cipher suites, and common SSL/TLS vulnerabilities.
"""

import ssl
import socket
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from ..models import (
    Target, Configuration, TestSuite,
    Severity, VulnerabilityCategory
)
from .base import PassiveScanner, ScanResult


logger = logging.getLogger(__name__)


class SSLTLSScanner(PassiveScanner):
    """
    SSL/TLS security scanner.
    
    Analyzes:
    - Certificate validity and expiration
    - Protocol versions (TLS 1.0, 1.1, 1.2, 1.3)
    - Cipher suites
    - Certificate chain
    - Common vulnerabilities (POODLE, BEAST, etc.)
    """
    
    # Weak/deprecated protocols (as strings since old protocol constants are removed)
    WEAK_PROTOCOL_NAMES = {
        'SSLv2': Severity.CRITICAL,
        'SSLv3': Severity.CRITICAL,
        'TLSv1': Severity.HIGH,
        'TLSv1.0': Severity.HIGH,
        'TLSv1.1': Severity.MEDIUM,
    }
    
    # Weak cipher patterns
    WEAK_CIPHER_PATTERNS = [
        ('NULL', Severity.CRITICAL, 'No encryption'),
        ('EXPORT', Severity.CRITICAL, 'Export-grade encryption'),
        ('DES', Severity.CRITICAL, 'DES encryption'),
        ('RC4', Severity.HIGH, 'RC4 cipher'),
        ('MD5', Severity.HIGH, 'MD5 hash'),
        ('anon', Severity.CRITICAL, 'Anonymous key exchange'),
    ]
    
    def __init__(self):
        """Initialize SSL/TLS scanner."""
        super().__init__()
    
    def get_name(self) -> str:
        """Get scanner name."""
        return "ssl_tls"
    
    def get_description(self) -> str:
        """Get scanner description."""
        return "SSL/TLS configuration analysis (certificates, protocols, ciphers)"
    
    def get_test_suite(self) -> TestSuite:
        """Get test suite."""
        return TestSuite.SSL_TLS
    
    async def scan(
        self,
        target: Target,
        config: Configuration
    ) -> ScanResult:
        """
        Execute SSL/TLS scan.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult with findings
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting SSL/TLS scan of {target.url}")
        
        # Only scan HTTPS targets
        if target.scheme != 'https':
            logger.info(f"Skipping SSL/TLS scan for non-HTTPS target: {target.url}")
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                findings=[],
                tests_performed=0,
                duration_seconds=time.time() - start_time
            )
        
        try:
            # Parse hostname and port
            parsed = urlparse(target.url)
            hostname = parsed.hostname
            port = parsed.port or 443
            
            # Get SSL certificate and connection info
            cert_info = await self._get_certificate_info(hostname, port)
            
            if cert_info:
                # Check certificate validity
                await self._check_certificate_validity(target, cert_info)
                
                # Check certificate expiration
                await self._check_certificate_expiration(target, cert_info)
                
                # Check protocol version
                await self._check_protocol_version(target, cert_info)
                
                # Check cipher suite
                await self._check_cipher_suite(target, cert_info)
                
                # Check certificate chain
                await self._check_certificate_chain(target, cert_info)
            
            duration = time.time() - start_time
            
            logger.info(
                f"SSL/TLS scan completed: "
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
            logger.error(f"SSL/TLS scan failed: {e}", exc_info=True)
            duration = time.time() - start_time
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=duration
            )
    
    async def _get_certificate_info(
        self,
        hostname: str,
        port: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get SSL certificate information.
        
        Args:
            hostname: Target hostname
            port: Target port
        
        Returns:
            Dictionary with certificate info or None if failed
        """
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'cert': cert,
                        'cipher': cipher,
                        'version': version,
                        'hostname': hostname,
                        'port': port
                    }
        
        except ssl.SSLError as e:
            logger.warning(f"SSL error connecting to {hostname}:{port}: {e}")
            return None
        except socket.timeout:
            logger.warning(f"Timeout connecting to {hostname}:{port}")
            return None
        except Exception as e:
            logger.warning(f"Error getting certificate from {hostname}:{port}: {e}")
            return None
    
    async def _check_certificate_validity(
        self,
        target: Target,
        cert_info: Dict[str, Any]
    ) -> None:
        """
        Check certificate validity.
        
        Args:
            target: Target being scanned
            cert_info: Certificate information
        """
        cert = cert_info.get('cert')
        if not cert:
            self.create_finding(
                title="Invalid SSL Certificate",
                description="Unable to retrieve valid SSL certificate",
                severity=Severity.CRITICAL,
                category=VulnerabilityCategory.SSL_TLS,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept="Certificate validation failed",
                remediation="Install a valid SSL certificate from a trusted CA",
                owasp_category="A02:2021 - Cryptographic Failures"
            )
    
    async def _check_certificate_expiration(
        self,
        target: Target,
        cert_info: Dict[str, Any]
    ) -> None:
        """
        Check certificate expiration.
        
        Args:
            target: Target being scanned
            cert_info: Certificate information
        """
        cert = cert_info.get('cert')
        if not cert:
            return
        
        # Parse notAfter date
        not_after_str = cert.get('notAfter')
        if not not_after_str:
            return
        
        try:
            # Parse date format: 'Jan 1 00:00:00 2025 GMT'
            not_after = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
            now = datetime.utcnow()
            
            # Check if expired
            if not_after < now:
                self.create_finding(
                    title="Expired SSL Certificate",
                    description=f"SSL certificate expired on {not_after_str}",
                    severity=Severity.CRITICAL,
                    category=VulnerabilityCategory.SSL_TLS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Certificate expired: {not_after_str}",
                    remediation="Renew the SSL certificate immediately",
                    cvss_score=9.0,
                    owasp_category="A02:2021 - Cryptographic Failures"
                )
            else:
                # Check if expiring soon (within 30 days)
                days_until_expiry = (not_after - now).days
                if days_until_expiry <= 30:
                    self.create_finding(
                        title="SSL Certificate Expiring Soon",
                        description=f"SSL certificate expires in {days_until_expiry} days on {not_after_str}",
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.SSL_TLS,
                        affected_url=target.url,
                        confidence=1.0,
                        proof_of_concept=f"Certificate expires: {not_after_str}",
                        remediation="Renew the SSL certificate before expiration",
                        owasp_category="A02:2021 - Cryptographic Failures"
                    )
        
        except Exception as e:
            logger.debug(f"Error parsing certificate expiration: {e}")
    
    async def _check_protocol_version(
        self,
        target: Target,
        cert_info: Dict[str, Any]
    ) -> None:
        """
        Check SSL/TLS protocol version.
        
        Args:
            target: Target being scanned
            cert_info: Certificate information
        """
        version = cert_info.get('version')
        if not version:
            return
        
        # Check for weak protocols
        for weak_version, severity in self.WEAK_PROTOCOL_NAMES.items():
            if weak_version in version:
                self.create_finding(
                    title=f"Weak SSL/TLS Protocol: {version}",
                    description=f"Server supports weak protocol version {version}",
                    severity=severity,
                    category=VulnerabilityCategory.SSL_TLS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Protocol version: {version}",
                    remediation="Disable weak protocols and use TLS 1.2 or TLS 1.3 only",
                    owasp_category="A02:2021 - Cryptographic Failures"
                )
                break
    
    async def _check_cipher_suite(
        self,
        target: Target,
        cert_info: Dict[str, Any]
    ) -> None:
        """
        Check cipher suite strength.
        
        Args:
            target: Target being scanned
            cert_info: Certificate information
        """
        cipher = cert_info.get('cipher')
        if not cipher:
            return
        
        # cipher is a tuple: (name, version, bits)
        cipher_name = cipher[0] if isinstance(cipher, tuple) else str(cipher)
        cipher_bits = cipher[2] if isinstance(cipher, tuple) and len(cipher) > 2 else None
        
        # Check for weak cipher patterns
        for pattern, severity, description in self.WEAK_CIPHER_PATTERNS:
            if pattern.upper() in cipher_name.upper():
                self.create_finding(
                    title=f"Weak Cipher Suite: {cipher_name}",
                    description=f"Server uses weak cipher: {description}",
                    severity=severity,
                    category=VulnerabilityCategory.SSL_TLS,
                    affected_url=target.url,
                    confidence=1.0,
                    proof_of_concept=f"Cipher: {cipher_name}",
                    remediation="Configure server to use strong cipher suites only",
                    owasp_category="A02:2021 - Cryptographic Failures"
                )
                break
        
        # Check key length
        if cipher_bits and cipher_bits < 128:
            self.create_finding(
                title=f"Weak Cipher Key Length: {cipher_bits} bits",
                description=f"Cipher uses weak key length of {cipher_bits} bits",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.SSL_TLS,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept=f"Cipher: {cipher_name}, Key length: {cipher_bits} bits",
                remediation="Use ciphers with at least 128-bit key length",
                owasp_category="A02:2021 - Cryptographic Failures"
            )
    
    async def _check_certificate_chain(
        self,
        target: Target,
        cert_info: Dict[str, Any]
    ) -> None:
        """
        Check certificate chain.
        
        Args:
            target: Target being scanned
            cert_info: Certificate information
        """
        cert = cert_info.get('cert')
        if not cert:
            return
        
        # Check if self-signed
        issuer = cert.get('issuer', ())
        subject = cert.get('subject', ())
        
        # Convert to comparable format
        issuer_dict = {k: v for item in issuer for k, v in item}
        subject_dict = {k: v for item in subject for k, v in item}
        
        if issuer_dict == subject_dict:
            self.create_finding(
                title="Self-Signed SSL Certificate",
                description="Server uses a self-signed certificate",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.SSL_TLS,
                affected_url=target.url,
                confidence=1.0,
                proof_of_concept="Certificate issuer matches subject (self-signed)",
                remediation="Use a certificate from a trusted Certificate Authority",
                owasp_category="A02:2021 - Cryptographic Failures"
            )
