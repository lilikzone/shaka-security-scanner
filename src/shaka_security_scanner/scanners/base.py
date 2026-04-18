"""
Base classes for scanner modules.

This module provides abstract base classes and interfaces for implementing
security scanner modules in the penetration testing framework.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, UTC

from ..models import (
    Target, Configuration, Finding, TestSuite, 
    IntensityLevel, Severity, VulnerabilityCategory
)


@dataclass
class ScanResult:
    """Result from a scanner module execution."""
    
    scanner_name: str
    test_suite: TestSuite
    findings: List[Finding] = field(default_factory=list)
    tests_performed: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if scan completed successfully."""
        return self.error is None
    
    @property
    def finding_count(self) -> int:
        """Get total number of findings."""
        return len(self.findings)
    
    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """
        Get findings filtered by severity.
        
        Args:
            severity: Severity level to filter by
        
        Returns:
            List of findings with specified severity
        """
        return [f for f in self.findings if f.severity == severity]
    
    def get_critical_findings(self) -> List[Finding]:
        """Get all critical severity findings."""
        return self.get_findings_by_severity(Severity.CRITICAL)
    
    def get_high_findings(self) -> List[Finding]:
        """Get all high severity findings."""
        return self.get_findings_by_severity(Severity.HIGH)


class ScannerModule(ABC):
    """
    Abstract base class for all scanner modules.
    
    All scanner implementations must inherit from this class and implement
    the required abstract methods.
    
    Attributes:
        name: Scanner module name
        description: Scanner module description
        enabled: Whether scanner is enabled
    """
    
    def __init__(self):
        """Initialize scanner module."""
        self.enabled = True
        self._findings: List[Finding] = []
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get scanner module name.
        
        Returns:
            Scanner name (e.g., "reconnaissance", "vulnerability")
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get scanner module description.
        
        Returns:
            Human-readable description of what the scanner does
        """
        pass
    
    @abstractmethod
    def get_test_suite(self) -> TestSuite:
        """
        Get the test suite this scanner belongs to.
        
        Returns:
            TestSuite enum value
        """
        pass
    
    @abstractmethod
    async def scan(
        self, 
        target: Target, 
        config: Configuration
    ) -> ScanResult:
        """
        Execute the scan against the target.
        
        Args:
            target: Target to scan
            config: Scan configuration
        
        Returns:
            ScanResult containing findings and metadata
        """
        pass
    
    def is_enabled(self) -> bool:
        """
        Check if scanner is enabled.
        
        Returns:
            True if scanner is enabled
        """
        return self.enabled
    
    def enable(self) -> None:
        """Enable the scanner."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the scanner."""
        self.enabled = False
    
    def should_run(self, config: Configuration) -> bool:
        """
        Check if scanner should run based on configuration.
        
        Args:
            config: Scan configuration
        
        Returns:
            True if scanner should run
        """
        if not self.enabled:
            return False
        
        # Check if scanner's test suite is in enabled suites
        return self.get_test_suite() in config.test_suites
    
    def create_finding(
        self,
        title: str,
        description: str,
        severity: Severity,
        category: VulnerabilityCategory,
        affected_url: str,
        confidence: float = 1.0,
        proof_of_concept: str = "",
        remediation: str = "",
        cvss_score: Optional[float] = None,
        cwe_id: Optional[str] = None,
        owasp_category: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> Finding:
        """
        Create a finding with common fields pre-filled.
        
        Args:
            title: Finding title
            description: Detailed description
            severity: Severity level
            category: Vulnerability category
            affected_url: Affected URL
            confidence: Confidence level (0.0-1.0)
            proof_of_concept: Proof of concept/evidence
            remediation: Remediation advice
            cvss_score: CVSS score (0.0-10.0)
            cwe_id: CWE identifier
            owasp_category: OWASP category
            references: List of reference URLs
        
        Returns:
            Finding object
        """
        finding = Finding(
            id=f"{self.get_name()}-{datetime.now(UTC).timestamp()}",
            title=title,
            description=description,
            severity=severity,
            category=category,
            affected_url=affected_url,
            confidence=confidence,
            proof_of_concept=proof_of_concept,
            remediation=remediation,
            cvss_score=cvss_score,
            cwe_id=cwe_id,
            owasp_category=owasp_category,
            references=references or []
        )
        
        self._findings.append(finding)
        return finding
    
    def get_findings(self) -> List[Finding]:
        """
        Get all findings discovered by this scanner.
        
        Returns:
            List of findings
        """
        return self._findings.copy()
    
    def clear_findings(self) -> None:
        """Clear all findings."""
        self._findings.clear()
    
    def get_supported_intensities(self) -> List[IntensityLevel]:
        """
        Get list of supported scan intensities.
        
        Default implementation supports all intensities.
        Override to restrict supported intensities.
        
        Returns:
            List of supported IntensityLevel values
        """
        return [
            IntensityLevel.PASSIVE,
            IntensityLevel.ACTIVE,
            IntensityLevel.AGGRESSIVE
        ]
    
    def supports_intensity(self, intensity: IntensityLevel) -> bool:
        """
        Check if scanner supports given intensity level.
        
        Args:
            intensity: Scan intensity to check
        
        Returns:
            True if intensity is supported
        """
        return intensity in self.get_supported_intensities()


class PassiveScanner(ScannerModule):
    """
    Base class for passive scanners.
    
    Passive scanners only observe and analyze without actively probing.
    Examples: Header analysis, technology detection, SSL/TLS inspection.
    """
    
    def get_supported_intensities(self) -> List[IntensityLevel]:
        """Passive scanners only support passive intensity."""
        return [IntensityLevel.PASSIVE]


class ActiveScanner(ScannerModule):
    """
    Base class for active scanners.
    
    Active scanners send probes and test inputs to discover vulnerabilities.
    Examples: SQL injection testing, XSS testing, authentication testing.
    """
    
    def get_supported_intensities(self) -> List[IntensityLevel]:
        """Active scanners support active and aggressive intensities."""
        return [IntensityLevel.ACTIVE, IntensityLevel.AGGRESSIVE]


@dataclass
class ScannerRegistry:
    """
    Registry for managing scanner modules.
    
    Provides centralized registration and lookup of scanner modules.
    """
    
    _scanners: Dict[str, ScannerModule] = field(default_factory=dict)
    
    def register(self, scanner: ScannerModule) -> None:
        """
        Register a scanner module.
        
        Args:
            scanner: Scanner module to register
        
        Raises:
            ValueError: If scanner with same name already registered
        """
        name = scanner.get_name()
        if name in self._scanners:
            raise ValueError(f"Scanner '{name}' already registered")
        
        self._scanners[name] = scanner
    
    def unregister(self, name: str) -> None:
        """
        Unregister a scanner module.
        
        Args:
            name: Name of scanner to unregister
        """
        self._scanners.pop(name, None)
    
    def get(self, name: str) -> Optional[ScannerModule]:
        """
        Get scanner by name.
        
        Args:
            name: Scanner name
        
        Returns:
            Scanner module or None if not found
        """
        return self._scanners.get(name)
    
    def get_all(self) -> List[ScannerModule]:
        """
        Get all registered scanners.
        
        Returns:
            List of all scanner modules
        """
        return list(self._scanners.values())
    
    def get_by_test_suite(self, test_suite: TestSuite) -> List[ScannerModule]:
        """
        Get all scanners for a specific test suite.
        
        Args:
            test_suite: Test suite to filter by
        
        Returns:
            List of scanners for the test suite
        """
        return [
            scanner for scanner in self._scanners.values()
            if scanner.get_test_suite() == test_suite
        ]
    
    def get_enabled(self) -> List[ScannerModule]:
        """
        Get all enabled scanners.
        
        Returns:
            List of enabled scanner modules
        """
        return [
            scanner for scanner in self._scanners.values()
            if scanner.is_enabled()
        ]
    
    def count(self) -> int:
        """
        Get total number of registered scanners.
        
        Returns:
            Number of registered scanners
        """
        return len(self._scanners)
    
    def clear(self) -> None:
        """Clear all registered scanners."""
        self._scanners.clear()
