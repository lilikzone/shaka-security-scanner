"""
Unit tests for scanner base classes.
"""

import pytest
from datetime import datetime, UTC

from web_pen_test_framework.scanners.base import (
    ScannerModule, PassiveScanner, ActiveScanner,
    ScanResult, ScannerRegistry
)
from web_pen_test_framework.models import (
    Target, Configuration, Finding, TestSuite,
    IntensityLevel, Severity, VulnerabilityCategory
)


# Test scanner implementations
class MockScanner(ScannerModule):
    """Mock scanner for unit tests."""
    
    def get_name(self) -> str:
        return "mock_scanner"
    
    def get_description(self) -> str:
        return "Mock scanner for unit tests"
    
    def get_test_suite(self) -> TestSuite:
        return TestSuite.RECONNAISSANCE
    
    async def scan(self, target: Target, config: Configuration) -> ScanResult:
        return ScanResult(
            scanner_name=self.get_name(),
            test_suite=self.get_test_suite(),
            tests_performed=5,
            duration_seconds=1.5
        )


class MockPassiveScanner(PassiveScanner):
    """Mock passive scanner."""
    
    def get_name(self) -> str:
        return "passive_mock"
    
    def get_description(self) -> str:
        return "Passive mock scanner"
    
    def get_test_suite(self) -> TestSuite:
        return TestSuite.HEADERS
    
    async def scan(self, target: Target, config: Configuration) -> ScanResult:
        return ScanResult(
            scanner_name=self.get_name(),
            test_suite=self.get_test_suite()
        )


class MockActiveScanner(ActiveScanner):
    """Mock active scanner."""
    
    def get_name(self) -> str:
        return "active_mock"
    
    def get_description(self) -> str:
        return "Active mock scanner"
    
    def get_test_suite(self) -> TestSuite:
        return TestSuite.VULNERABILITY
    
    async def scan(self, target: Target, config: Configuration) -> ScanResult:
        return ScanResult(
            scanner_name=self.get_name(),
            test_suite=self.get_test_suite()
        )


class TestScanResult:
    """Test cases for ScanResult class."""
    
    def test_creation(self):
        """Test creating a scan result."""
        result = ScanResult(
            scanner_name="test",
            test_suite=TestSuite.RECONNAISSANCE,
            tests_performed=10,
            duration_seconds=5.5
        )
        
        assert result.scanner_name == "test"
        assert result.test_suite == TestSuite.RECONNAISSANCE
        assert result.tests_performed == 10
        assert result.duration_seconds == 5.5
        assert result.finding_count == 0
        assert result.success is True
    
    def test_with_findings(self):
        """Test scan result with findings."""
        finding = Finding(
            id="test-1",
            title="Test Finding",
            description="Test description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.SQL_INJECTION,
            affected_url="https://example.com",
            confidence=0.9
        )
        
        result = ScanResult(
            scanner_name="test",
            test_suite=TestSuite.VULNERABILITY,
            findings=[finding]
        )
        
        assert result.finding_count == 1
        assert len(result.findings) == 1
    
    def test_with_error(self):
        """Test scan result with error."""
        result = ScanResult(
            scanner_name="test",
            test_suite=TestSuite.RECONNAISSANCE,
            error="Connection timeout"
        )
        
        assert result.success is False
        assert result.error == "Connection timeout"
    
    def test_get_findings_by_severity(self):
        """Test filtering findings by severity."""
        findings = [
            Finding(
                id="f1", title="Critical", description="desc",
                severity=Severity.CRITICAL,
                category=VulnerabilityCategory.SQL_INJECTION,
                affected_url="https://example.com"
            ),
            Finding(
                id="f2", title="High", description="desc",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.XSS,
                affected_url="https://example.com"
            ),
            Finding(
                id="f3", title="High2", description="desc",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.CSRF,
                affected_url="https://example.com"
            )
        ]
        
        result = ScanResult(
            scanner_name="test",
            test_suite=TestSuite.VULNERABILITY,
            findings=findings
        )
        
        critical = result.get_findings_by_severity(Severity.CRITICAL)
        assert len(critical) == 1
        
        high = result.get_findings_by_severity(Severity.HIGH)
        assert len(high) == 2


class TestScannerModule:
    """Test cases for ScannerModule base class."""
    
    @pytest.mark.asyncio
    async def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = MockScanner()
        
        assert scanner.enabled is True
        assert scanner.get_name() == "mock_scanner"
        assert scanner.get_test_suite() == TestSuite.RECONNAISSANCE
    
    def test_enable_disable(self):
        """Test enabling and disabling scanner."""
        scanner = MockScanner()
        
        assert scanner.is_enabled() is True
        
        scanner.disable()
        assert scanner.is_enabled() is False
        
        scanner.enable()
        assert scanner.is_enabled() is True
    
    def test_should_run(self):
        """Test should_run logic."""
        scanner = MockScanner()
        
        # Scanner should run if enabled and test suite is in config
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        assert scanner.should_run(config) is True
        
        # Scanner should not run if test suite not in config
        config2 = Configuration(
            test_suites=[TestSuite.VULNERABILITY]
        )
        assert scanner.should_run(config2) is False
        
        # Scanner should not run if disabled
        scanner.disable()
        assert scanner.should_run(config) is False
    
    def test_create_finding(self):
        """Test creating a finding."""
        scanner = MockScanner()
        
        finding = scanner.create_finding(
            title="SQL Injection",
            description="SQL injection vulnerability found",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.SQL_INJECTION,
            affected_url="https://example.com/api",
            confidence=0.95,
            proof_of_concept="' OR '1'='1",
            remediation="Use parameterized queries"
        )
        
        assert finding.title == "SQL Injection"
        assert finding.severity == Severity.HIGH
        assert finding.confidence == 0.95
        
        # Finding should be added to scanner's findings
        findings = scanner.get_findings()
        assert len(findings) == 1
        assert findings[0] == finding
    
    def test_get_supported_intensities(self):
        """Test getting supported intensities."""
        scanner = MockScanner()
        
        intensities = scanner.get_supported_intensities()
        assert IntensityLevel.PASSIVE in intensities
        assert IntensityLevel.ACTIVE in intensities
        assert IntensityLevel.AGGRESSIVE in intensities


class TestPassiveScanner:
    """Test cases for PassiveScanner class."""
    
    def test_supported_intensities(self):
        """Test that passive scanner only supports passive intensity."""
        scanner = MockPassiveScanner()
        
        intensities = scanner.get_supported_intensities()
        assert len(intensities) == 1
        assert IntensityLevel.PASSIVE in intensities


class TestActiveScanner:
    """Test cases for ActiveScanner class."""
    
    def test_supported_intensities(self):
        """Test that active scanner supports active and aggressive."""
        scanner = MockActiveScanner()
        
        intensities = scanner.get_supported_intensities()
        assert len(intensities) == 2
        assert IntensityLevel.ACTIVE in intensities
        assert IntensityLevel.AGGRESSIVE in intensities


class TestScannerRegistry:
    """Test cases for ScannerRegistry class."""
    
    def test_register_scanner(self):
        """Test registering a scanner."""
        registry = ScannerRegistry()
        scanner = MockScanner()
        
        registry.register(scanner)
        
        assert registry.count() == 1
        assert registry.get("mock_scanner") == scanner
    
    def test_register_duplicate(self):
        """Test registering duplicate scanner raises error."""
        registry = ScannerRegistry()
        scanner1 = MockScanner()
        scanner2 = MockScanner()
        
        registry.register(scanner1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(scanner2)
    
    def test_get_all(self):
        """Test getting all scanners."""
        registry = ScannerRegistry()
        scanner1 = MockScanner()
        scanner2 = MockPassiveScanner()
        
        registry.register(scanner1)
        registry.register(scanner2)
        
        all_scanners = registry.get_all()
        assert len(all_scanners) == 2
        assert scanner1 in all_scanners
        assert scanner2 in all_scanners
    
    def test_get_by_test_suite(self):
        """Test getting scanners by test suite."""
        registry = ScannerRegistry()
        scanner1 = MockScanner()  # RECONNAISSANCE
        scanner2 = MockPassiveScanner()  # HEADERS
        scanner3 = MockActiveScanner()  # VULNERABILITY
        
        registry.register(scanner1)
        registry.register(scanner2)
        registry.register(scanner3)
        
        recon_scanners = registry.get_by_test_suite(TestSuite.RECONNAISSANCE)
        assert len(recon_scanners) == 1
        assert scanner1 in recon_scanners
