"""
Unit tests for core data models.
"""

import pytest
from datetime import datetime, timedelta
from web_pen_test_framework.models import (
    Target,
    Configuration,
    Finding,
    AuthorizationToken,
    ScanSession,
    HTTPRequest,
    HTTPResponse,
    Payload,
    ErrorResponse,
    Report,
    Technology,
    InputField,
    ScanStatus,
    Severity,
    VulnerabilityCategory,
    IntensityLevel,
    TestSuite,
    PayloadCategory,
    ReportFormat,
)


class TestTarget:
    """Tests for Target dataclass."""
    
    def test_valid_target(self):
        """Test creating a valid target."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        assert target.url == "https://example.com"
        assert target.base_domain == "example.com"
        assert target.scheme == "https"
        assert target.discovered_endpoints == []
        assert target.technologies == []
        assert target.input_fields == []
    
    def test_invalid_scheme(self):
        """Test that invalid scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid scheme"):
            Target(
                url="ftp://example.com",
                base_domain="example.com",
                scheme="ftp"
            )
    
    def test_empty_url(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Target URL cannot be empty"):
            Target(
                url="",
                base_domain="example.com",
                scheme="https"
            )


class TestConfiguration:
    """Tests for Configuration dataclass."""
    
    def test_valid_configuration(self):
        """Test creating a valid configuration."""
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE, TestSuite.VULNERABILITY],
            intensity=IntensityLevel.ACTIVE,
            rate_limit=10,
            timeout=30
        )
        assert config.intensity == IntensityLevel.ACTIVE
        assert config.rate_limit == 10
        assert config.timeout == 30
        assert len(config.test_suites) == 2
    
    def test_invalid_rate_limit(self):
        """Test that invalid rate limit raises ValueError."""
        with pytest.raises(ValueError, match="Rate limit must be positive"):
            Configuration(
                test_suites=[TestSuite.RECONNAISSANCE],
                rate_limit=0
            )
    
    def test_invalid_timeout(self):
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            Configuration(
                test_suites=[TestSuite.RECONNAISSANCE],
                timeout=-1
            )
    
    def test_empty_test_suites(self):
        """Test that empty test suites raises ValueError."""
        with pytest.raises(ValueError, match="At least one test suite must be specified"):
            Configuration(test_suites=[])


class TestAuthorizationToken:
    """Tests for AuthorizationToken dataclass."""
    
    def test_valid_token(self):
        """Test creating a valid authorization token."""
        now = datetime.now()
        future = now + timedelta(days=30)
        token = AuthorizationToken(
            token="test-token-123",
            target_domain="example.com",
            issued_at=now,
            expires_at=future
        )
        assert token.token == "test-token-123"
        assert token.target_domain == "example.com"
        assert token.is_valid()
        assert not token.is_expired()
    
    def test_expired_token(self):
        """Test expired token detection."""
        past = datetime.now() - timedelta(days=30)
        yesterday = datetime.now() - timedelta(days=1)
        token = AuthorizationToken(
            token="test-token-123",
            target_domain="example.com",
            issued_at=past,
            expires_at=yesterday
        )
        assert not token.is_valid()
        assert token.is_expired()
    
    def test_invalid_expiration(self):
        """Test that expiration before issue date raises ValueError."""
        now = datetime.now()
        past = now - timedelta(days=1)
        with pytest.raises(ValueError, match="Expiration date must be after issue date"):
            AuthorizationToken(
                token="test-token-123",
                target_domain="example.com",
                issued_at=now,
                expires_at=past
            )
    
    def test_empty_token(self):
        """Test that empty token raises ValueError."""
        now = datetime.now()
        future = now + timedelta(days=30)
        with pytest.raises(ValueError, match="Token cannot be empty"):
            AuthorizationToken(
                token="",
                target_domain="example.com",
                issued_at=now,
                expires_at=future
            )


class TestFinding:
    """Tests for Finding dataclass."""
    
    def test_valid_finding(self):
        """Test creating a valid finding."""
        finding = Finding(
            id="FIND-001",
            title="SQL Injection",
            description="SQL injection vulnerability found",
            severity=Severity.CRITICAL,
            category=VulnerabilityCategory.SQL_INJECTION,
            affected_url="https://example.com/login"
        )
        assert finding.id == "FIND-001"
        assert finding.severity == Severity.CRITICAL
        assert finding.category == VulnerabilityCategory.SQL_INJECTION
        assert finding.confidence == 1.0
    
    def test_invalid_confidence(self):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Finding(
                id="FIND-001",
                title="Test",
                description="Test",
                severity=Severity.LOW,
                category=VulnerabilityCategory.OTHER,
                affected_url="https://example.com",
                confidence=1.5
            )
    
    def test_invalid_cvss_score(self):
        """Test that invalid CVSS score raises ValueError."""
        with pytest.raises(ValueError, match="CVSS score must be between 0.0 and 10.0"):
            Finding(
                id="FIND-001",
                title="Test",
                description="Test",
                severity=Severity.LOW,
                category=VulnerabilityCategory.OTHER,
                affected_url="https://example.com",
                cvss_score=11.0
            )


class TestHTTPRequest:
    """Tests for HTTPRequest dataclass."""
    
    def test_valid_request(self):
        """Test creating a valid HTTP request."""
        request = HTTPRequest(
            method="GET",
            url="https://example.com/api/users"
        )
        assert request.method == "GET"
        assert request.url == "https://example.com/api/users"
        assert request.headers == {}
        assert request.params == {}
    
    def test_invalid_method(self):
        """Test that invalid HTTP method raises ValueError."""
        with pytest.raises(ValueError, match="Invalid HTTP method"):
            HTTPRequest(
                method="INVALID",
                url="https://example.com"
            )
    
    def test_empty_url(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            HTTPRequest(
                method="GET",
                url=""
            )


class TestHTTPResponse:
    """Tests for HTTPResponse dataclass."""
    
    def test_valid_response(self):
        """Test creating a valid HTTP response."""
        response = HTTPResponse(
            status_code=200,
            body="Success",
            elapsed_time=0.5
        )
        assert response.status_code == 200
        assert response.body == "Success"
        assert response.elapsed_time == 0.5
    
    def test_invalid_status_code(self):
        """Test that invalid status code raises ValueError."""
        with pytest.raises(ValueError, match="Invalid HTTP status code"):
            HTTPResponse(status_code=999)
    
    def test_negative_elapsed_time(self):
        """Test that negative elapsed time raises ValueError."""
        with pytest.raises(ValueError, match="Elapsed time cannot be negative"):
            HTTPResponse(
                status_code=200,
                elapsed_time=-1.0
            )


class TestScanSession:
    """Tests for ScanSession dataclass."""
    
    def test_valid_session(self):
        """Test creating a valid scan session."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        session = ScanSession(
            session_id="SESSION-001",
            target=target,
            config=config
        )
        assert session.session_id == "SESSION-001"
        assert session.status == ScanStatus.NOT_STARTED
        assert session.progress == 0.0
        assert session.findings == []
    
    def test_get_findings_by_severity(self):
        """Test filtering findings by severity."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        session = ScanSession(
            session_id="SESSION-001",
            target=target,
            config=config
        )
        
        # Add findings
        session.findings.append(Finding(
            id="FIND-001",
            title="Critical Issue",
            description="Test",
            severity=Severity.CRITICAL,
            category=VulnerabilityCategory.SQL_INJECTION,
            affected_url="https://example.com"
        ))
        session.findings.append(Finding(
            id="FIND-002",
            title="High Issue",
            description="Test",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        ))
        
        critical = session.get_findings_by_severity(Severity.CRITICAL)
        assert len(critical) == 1
        assert critical[0].id == "FIND-001"
        
        assert session.get_critical_count() == 1
        assert session.get_high_count() == 1
        assert session.get_medium_count() == 0
    
    def test_get_duration(self):
        """Test getting scan duration."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        session = ScanSession(
            session_id="SESSION-001",
            target=target,
            config=config
        )
        
        # No duration yet
        assert session.get_duration() is None
        
        # Set start time
        session.start_time = datetime.now()
        duration = session.get_duration()
        assert duration is not None
        assert duration >= 0
        
        # Set end time
        session.end_time = session.start_time + timedelta(seconds=10)
        duration = session.get_duration()
        assert duration is not None
        assert 9 <= duration <= 11  # Allow small variance
    
    def test_invalid_progress(self):
        """Test that invalid progress raises ValueError."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        with pytest.raises(ValueError, match="Progress must be between 0.0 and 1.0"):
            ScanSession(
                session_id="SESSION-001",
                target=target,
                config=config,
                progress=1.5
            )


class TestPayload:
    """Tests for Payload dataclass."""
    
    def test_valid_payload(self):
        """Test creating a valid payload."""
        payload = Payload(
            value="' OR '1'='1",
            category=PayloadCategory.SQL_INJECTION,
            description="Basic SQL injection payload"
        )
        assert payload.value == "' OR '1'='1"
        assert payload.category == PayloadCategory.SQL_INJECTION
    
    def test_empty_value(self):
        """Test that empty payload value raises ValueError."""
        with pytest.raises(ValueError, match="Payload value cannot be empty"):
            Payload(
                value="",
                category=PayloadCategory.SQL_INJECTION
            )


class TestErrorResponse:
    """Tests for ErrorResponse dataclass."""
    
    def test_valid_error(self):
        """Test creating a valid error response."""
        error = ErrorResponse(
            error_code="ERR-001",
            message="Connection timeout",
            details="Failed to connect to target after 30 seconds"
        )
        assert error.error_code == "ERR-001"
        assert error.message == "Connection timeout"
        assert error.recoverable is True
    
    def test_empty_error_code(self):
        """Test that empty error code raises ValueError."""
        with pytest.raises(ValueError, match="Error code cannot be empty"):
            ErrorResponse(
                error_code="",
                message="Test error"
            )


class TestReport:
    """Tests for Report dataclass."""
    
    def test_valid_report(self):
        """Test creating a valid report."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        session = ScanSession(
            session_id="SESSION-001",
            target=target,
            config=config
        )
        report = Report(
            session=session,
            format=ReportFormat.HTML,
            risk_score=7.5
        )
        assert report.format == ReportFormat.HTML
        assert report.risk_score == 7.5
    
    def test_invalid_risk_score(self):
        """Test that invalid risk score raises ValueError."""
        target = Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
        config = Configuration(
            test_suites=[TestSuite.RECONNAISSANCE]
        )
        session = ScanSession(
            session_id="SESSION-001",
            target=target,
            config=config
        )
        with pytest.raises(ValueError, match="Risk score must be between 0.0 and 10.0"):
            Report(
                session=session,
                format=ReportFormat.HTML,
                risk_score=11.0
            )


class TestTechnology:
    """Tests for Technology dataclass."""
    
    def test_valid_technology(self):
        """Test creating a valid technology."""
        tech = Technology(
            name="React",
            version="18.2.0",
            category="JavaScript Framework",
            confidence=0.95
        )
        assert tech.name == "React"
        assert tech.version == "18.2.0"
        assert tech.confidence == 0.95


class TestInputField:
    """Tests for InputField dataclass."""
    
    def test_valid_input_field(self):
        """Test creating a valid input field."""
        field = InputField(
            name="username",
            field_type="text",
            form_action="/login",
            method="POST"
        )
        assert field.name == "username"
        assert field.field_type == "text"
        assert field.method == "POST"
