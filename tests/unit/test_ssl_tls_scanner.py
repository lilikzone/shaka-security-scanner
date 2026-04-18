"""
Unit tests for SSL/TLS Scanner.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from shaka_security_scanner.scanners.ssl_tls import SSLTLSScanner
from shaka_security_scanner.models import (
    Target, Configuration, TestSuite, IntensityLevel, Severity
)


class TestSSLTLSScanner:
    """Test cases for SSLTLSScanner."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = SSLTLSScanner()
        
        assert scanner.get_name() == "ssl_tls"
        assert scanner.get_test_suite() == TestSuite.SSL_TLS
        assert scanner.is_enabled() is True
    
    def test_supported_intensities(self):
        """Test that SSL/TLS scanner supports passive intensity."""
        scanner = SSLTLSScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.PASSIVE in intensities
        assert len(intensities) == 1
    
    @pytest.mark.asyncio
    async def test_scan_http_target_skipped(self):
        """Test that HTTP targets are skipped."""
        scanner = SSLTLSScanner()
        
        target = Target(
            url="http://example.com",
            base_domain="example.com",
            scheme="http"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should skip HTTP targets
        assert result.success is True
        assert len(result.findings) == 0
        assert result.tests_performed == 0
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        """Test successful scan execution."""
        scanner = SSLTLSScanner()
        
        # Mock certificate info
        future_date = datetime.utcnow() + timedelta(days=365)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': future_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('ECDHE-RSA-AES256-GCM-SHA384', 'TLSv1.2', 256),
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should complete successfully
        assert result.success is True
        assert result.scanner_name == "ssl_tls"
        assert result.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_expired_certificate(self):
        """Test detection of expired certificate."""
        scanner = SSLTLSScanner()
        
        # Mock expired certificate
        past_date = datetime.utcnow() - timedelta(days=30)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': past_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('ECDHE-RSA-AES256-GCM-SHA384', 'TLSv1.2', 256),
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect expired certificate
        expired_findings = [
            f for f in result.findings
            if 'Expired' in f.title
        ]
        assert len(expired_findings) > 0
        assert expired_findings[0].severity == Severity.CRITICAL
    
    @pytest.mark.asyncio
    async def test_expiring_soon_certificate(self):
        """Test detection of certificate expiring soon."""
        scanner = SSLTLSScanner()
        
        # Mock certificate expiring in 15 days
        soon_date = datetime.utcnow() + timedelta(days=15)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': soon_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('ECDHE-RSA-AES256-GCM-SHA384', 'TLSv1.2', 256),
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect certificate expiring soon
        expiring_findings = [
            f for f in result.findings
            if 'Expiring Soon' in f.title
        ]
        assert len(expiring_findings) > 0
        assert expiring_findings[0].severity == Severity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_weak_protocol_detection(self):
        """Test detection of weak SSL/TLS protocols."""
        scanner = SSLTLSScanner()
        
        # Mock weak protocol
        future_date = datetime.utcnow() + timedelta(days=365)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': future_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('RC4-SHA', 'TLSv1.0', 128),
            'version': 'TLSv1.0',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect weak protocol
        protocol_findings = [
            f for f in result.findings
            if 'Weak SSL/TLS Protocol' in f.title
        ]
        assert len(protocol_findings) > 0
        assert protocol_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_weak_cipher_detection(self):
        """Test detection of weak cipher suites."""
        scanner = SSLTLSScanner()
        
        # Mock weak cipher
        future_date = datetime.utcnow() + timedelta(days=365)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': future_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('RC4-SHA', 'TLSv1.2', 128),
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect weak cipher
        cipher_findings = [
            f for f in result.findings
            if 'Weak Cipher' in f.title
        ]
        assert len(cipher_findings) > 0
        assert cipher_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_weak_key_length_detection(self):
        """Test detection of weak cipher key length."""
        scanner = SSLTLSScanner()
        
        # Mock weak key length
        future_date = datetime.utcnow() + timedelta(days=365)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt'),),),
                'notAfter': future_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('DES-CBC3-SHA', 'TLSv1.2', 56),  # 56-bit key
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect weak key length
        key_findings = [
            f for f in result.findings
            if 'Weak Cipher Key Length' in f.title
        ]
        assert len(key_findings) > 0
        assert key_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_self_signed_certificate(self):
        """Test detection of self-signed certificate."""
        scanner = SSLTLSScanner()
        
        # Mock self-signed certificate
        future_date = datetime.utcnow() + timedelta(days=365)
        mock_cert_info = {
            'cert': {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'example.com'),),),  # Same as subject
                'notAfter': future_date.strftime('%b %d %H:%M:%S %Y GMT'),
                'version': 3
            },
            'cipher': ('ECDHE-RSA-AES256-GCM-SHA384', 'TLSv1.2', 256),
            'version': 'TLSv1.2',
            'hostname': 'example.com',
            'port': 443
        }
        
        scanner._get_certificate_info = AsyncMock(return_value=mock_cert_info)
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should detect self-signed certificate
        self_signed_findings = [
            f for f in result.findings
            if 'Self-Signed' in f.title
        ]
        assert len(self_signed_findings) > 0
        assert self_signed_findings[0].severity == Severity.HIGH
    
    @pytest.mark.asyncio
    async def test_scan_with_error(self):
        """Test scan with connection error."""
        scanner = SSLTLSScanner()
        
        # Mock connection error
        scanner._get_certificate_info = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.SSL_TLS],
            intensity=IntensityLevel.PASSIVE
        )
        
        result = await scanner.scan(target, config)
        
        # Should handle error gracefully
        assert result.success is False
        assert result.error == "Connection refused"
