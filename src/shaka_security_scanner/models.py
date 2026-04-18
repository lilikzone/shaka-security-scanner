"""
Core data models for the Web Penetration Testing Framework.

This module defines all the data structures used throughout the framework,
including Target, Configuration, Finding, AuthorizationToken, and more.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


# Enums

class ScanStatus(str, Enum):
    """Status of a scan session."""
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(str, Enum):
    """Categories of vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    XML_INJECTION = "xml_injection"
    FILE_UPLOAD = "file_upload"
    SSL_TLS = "ssl_tls"
    SECURITY_HEADERS = "security_headers"
    SESSION_MANAGEMENT = "session_management"
    API_SECURITY = "api_security"
    INFORMATION_DISCLOSURE = "information_disclosure"
    OTHER = "other"


class IntensityLevel(str, Enum):
    """Scan intensity levels."""
    PASSIVE = "passive"
    ACTIVE = "active"
    AGGRESSIVE = "aggressive"


class TestSuite(str, Enum):
    """Available test suites."""
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY = "vulnerability"
    HEADERS = "headers"
    AUTHENTICATION = "authentication"
    INPUT_VALIDATION = "input_validation"
    SSL_TLS = "ssl_tls"
    API = "api"


class PayloadCategory(str, Enum):
    """Categories of payloads."""
    SQL_INJECTION = "sqli"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    XML_INJECTION = "xml_injection"
    XXE = "xxe"
    LDAP_INJECTION = "ldap_injection"
    XPATH_INJECTION = "xpath_injection"
    TEMPLATE_INJECTION = "template_injection"
    OTHER = "other"


class ReportFormat(str, Enum):
    """Report output formats."""
    HTML = "html"
    JSON = "json"
    PDF = "pdf"
    MARKDOWN = "markdown"


# Data Models

@dataclass
class Technology:
    """Detected technology information."""
    name: str
    version: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class InputField:
    """HTML input field information."""
    name: str
    field_type: str  # text, password, email, etc.
    form_action: Optional[str] = None
    method: str = "GET"
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class Target:
    """Target web application information."""
    url: str
    base_domain: str
    scheme: str  # http or https
    discovered_endpoints: List[str] = field(default_factory=list)
    technologies: List[Technology] = field(default_factory=list)
    input_fields: List[InputField] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate target data."""
        if not self.url:
            raise ValueError("Target URL cannot be empty")
        if self.scheme not in ["http", "https"]:
            raise ValueError(f"Invalid scheme: {self.scheme}. Must be 'http' or 'https'")


@dataclass
class Payload:
    """Test payload information."""
    value: str
    category: PayloadCategory
    encoding: Optional[str] = None  # url, html, unicode, etc.
    description: str = ""
    
    def __post_init__(self) -> None:
        """Validate payload data."""
        if not self.value:
            raise ValueError("Payload value cannot be empty")


@dataclass
class Configuration:
    """Scan configuration."""
    test_suites: List[TestSuite]
    intensity: IntensityLevel = IntensityLevel.ACTIVE
    rate_limit: int = 10  # requests per second
    timeout: int = 30  # seconds
    exclusions: List[str] = field(default_factory=list)  # URL patterns to exclude
    custom_payloads: List[Payload] = field(default_factory=list)
    enable_destructive_tests: bool = False
    enable_ai_analysis: bool = True
    max_concurrent_requests: int = 10
    user_agent: str = "WebPenTestFramework/0.1.0"
    follow_redirects: bool = True
    max_redirects: int = 10
    verify_ssl: bool = True
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate configuration data."""
        if self.rate_limit <= 0:
            raise ValueError("Rate limit must be positive")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_concurrent_requests <= 0:
            raise ValueError("Max concurrent requests must be positive")
        if not self.test_suites:
            raise ValueError("At least one test suite must be specified")


@dataclass
class AuthorizationToken:
    """Authorization token for scan permission."""
    token: str
    target_domain: str
    issued_at: datetime
    expires_at: datetime
    scope: List[str] = field(default_factory=list)  # allowed test types
    
    def __post_init__(self) -> None:
        """Validate authorization token."""
        if not self.token:
            raise ValueError("Token cannot be empty")
        if not self.target_domain:
            raise ValueError("Target domain cannot be empty")
        if self.expires_at <= self.issued_at:
            raise ValueError("Expiration date must be after issue date")
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.now() < self.expires_at
    
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now() >= self.expires_at


@dataclass
class Finding:
    """Security finding/vulnerability."""
    id: str
    title: str
    description: str
    severity: Severity
    category: VulnerabilityCategory
    affected_url: str
    affected_parameter: Optional[str] = None
    proof_of_concept: str = ""
    remediation: str = ""
    references: List[str] = field(default_factory=list)  # OWASP, CWE references
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0  # 0.0 to 1.0
    cvss_score: Optional[float] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate finding data."""
        if not self.id:
            raise ValueError("Finding ID cannot be empty")
        if not self.title:
            raise ValueError("Finding title cannot be empty")
        if not self.affected_url:
            raise ValueError("Affected URL cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.cvss_score is not None and not 0.0 <= self.cvss_score <= 10.0:
            raise ValueError("CVSS score must be between 0.0 and 10.0")


@dataclass
class HTTPRequest:
    """HTTP request information."""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    params: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate HTTP request data."""
        if not self.method:
            raise ValueError("HTTP method cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        if self.method.upper() not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {self.method}")


@dataclass
class HTTPResponse:
    """HTTP response information."""
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    elapsed_time: float = 0.0  # seconds
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate HTTP response data."""
        if not 100 <= self.status_code < 600:
            raise ValueError(f"Invalid HTTP status code: {self.status_code}")
        if self.elapsed_time < 0:
            raise ValueError("Elapsed time cannot be negative")


@dataclass
class ScanSession:
    """Scan session information."""
    session_id: str
    target: Target
    config: Configuration
    status: ScanStatus = ScanStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    findings: List[Finding] = field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0
    current_test: str = ""
    total_requests: int = 0
    failed_requests: int = 0
    
    def __post_init__(self) -> None:
        """Validate scan session data."""
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        if self.total_requests < 0:
            raise ValueError("Total requests cannot be negative")
        if self.failed_requests < 0:
            raise ValueError("Failed requests cannot be negative")
        if self.failed_requests > self.total_requests:
            raise ValueError("Failed requests cannot exceed total requests")
    
    def get_duration(self) -> Optional[float]:
        """Get scan duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None
    
    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Get findings filtered by severity."""
        return [f for f in self.findings if f.severity == severity]
    
    def get_critical_count(self) -> int:
        """Get count of critical findings."""
        return len(self.get_findings_by_severity(Severity.CRITICAL))
    
    def get_high_count(self) -> int:
        """Get count of high severity findings."""
        return len(self.get_findings_by_severity(Severity.HIGH))
    
    def get_medium_count(self) -> int:
        """Get count of medium severity findings."""
        return len(self.get_findings_by_severity(Severity.MEDIUM))
    
    def get_low_count(self) -> int:
        """Get count of low severity findings."""
        return len(self.get_findings_by_severity(Severity.LOW))
    
    def get_info_count(self) -> int:
        """Get count of informational findings."""
        return len(self.get_findings_by_severity(Severity.INFO))


@dataclass
class ErrorResponse:
    """Error response information."""
    error_code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    recoverable: bool = True
    
    def __post_init__(self) -> None:
        """Validate error response data."""
        if not self.error_code:
            raise ValueError("Error code cannot be empty")
        if not self.message:
            raise ValueError("Error message cannot be empty")


@dataclass
class Report:
    """Scan report information."""
    session: ScanSession
    format: ReportFormat
    generated_at: datetime = field(default_factory=datetime.now)
    executive_summary: str = ""
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate report data."""
        if not 0.0 <= self.risk_score <= 10.0:
            raise ValueError("Risk score must be between 0.0 and 10.0")
