"""
Unit tests for AuditLogger.
"""

import pytest
import json
import logging
from pathlib import Path
import tempfile
import shutil
from shaka_security_scanner.http.logger import AuditLogger, AuditLogEntry


class TestAuditLogEntry:
    """Test cases for AuditLogEntry dataclass."""
    
    def test_creation(self):
        """Test creating an audit log entry."""
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00Z",
            request_id="req-123",
            method="GET",
            url="https://example.com/api",
            status_code=200,
            request_headers={"User-Agent": "Test"},
            response_headers={"Content-Type": "application/json"},
            request_body_hash=None,
            response_body_hash="abc123",
            duration_ms=150.5,
            error=None,
            target_domain="example.com"
        )
        
        assert entry.request_id == "req-123"
        assert entry.method == "GET"
        assert entry.status_code == 200
        assert entry.duration_ms == 150.5
    
    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00Z",
            request_id="req-123",
            method="POST",
            url="https://example.com/api",
            status_code=201,
            request_headers={},
            response_headers={},
            request_body_hash="hash1",
            response_body_hash="hash2",
            duration_ms=100.0,
            error=None,
            target_domain="example.com"
        )
        
        data = entry.to_dict()
        assert isinstance(data, dict)
        assert data["request_id"] == "req-123"
        assert data["method"] == "POST"
        assert data["status_code"] == 201
    
    def test_to_json(self):
        """Test converting entry to JSON string."""
        entry = AuditLogEntry(
            timestamp="2024-01-01T00:00:00Z",
            request_id="req-123",
            method="GET",
            url="https://example.com",
            status_code=200,
            request_headers={},
            response_headers={},
            request_body_hash=None,
            response_body_hash=None,
            duration_ms=50.0,
            error=None,
            target_domain="example.com"
        )
        
        json_str = entry.to_json()
        assert isinstance(json_str, str)
        
        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data["request_id"] == "req-123"


class TestAuditLogger:
    """Test cases for AuditLogger class."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_log_dir):
        """Test logger initialization."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        assert logger.log_dir == Path(temp_log_dir)
        assert logger.log_dir.exists()
        assert logger.max_body_log_size == 1024
    
    def test_initialization_creates_directory(self, temp_log_dir):
        """Test that logger creates log directory if it doesn't exist."""
        log_path = Path(temp_log_dir) / "nested" / "logs"
        logger = AuditLogger(log_dir=str(log_path))
        
        assert log_path.exists()
    
    def test_hash_content(self, temp_log_dir):
        """Test content hashing."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        content = b"test content"
        hash_value = logger._hash_content(content)
        
        assert hash_value is not None
        assert len(hash_value) == 64  # SHA-256 hex digest length
        
        # Same content should produce same hash
        hash_value2 = logger._hash_content(content)
        assert hash_value == hash_value2
    
    def test_hash_content_none(self, temp_log_dir):
        """Test hashing None content."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        hash_value = logger._hash_content(None)
        assert hash_value is None
    
    def test_sanitize_headers(self, temp_log_dir):
        """Test header sanitization."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Authorization": "Bearer secret-token",
            "Cookie": "session=abc123",
            "Content-Type": "application/json",
            "X-API-Key": "secret-key"
        }
        
        sanitized = logger._sanitize_headers(headers)
        
        assert sanitized["User-Agent"] == "Mozilla/5.0"
        assert sanitized["Content-Type"] == "application/json"
        assert sanitized["Authorization"] == "[REDACTED]"
        assert sanitized["Cookie"] == "[REDACTED]"
        assert sanitized["X-API-Key"] == "[REDACTED]"
    
    def test_sanitize_headers_case_insensitive(self, temp_log_dir):
        """Test that header sanitization is case-insensitive."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        headers = {
            "AUTHORIZATION": "Bearer token",
            "cookie": "session=123",
            "X-Api-Key": "key123"
        }
        
        sanitized = logger._sanitize_headers(headers)
        
        assert sanitized["AUTHORIZATION"] == "[REDACTED]"
        assert sanitized["cookie"] == "[REDACTED]"
        assert sanitized["X-Api-Key"] == "[REDACTED]"
    
    def test_log_request(self, temp_log_dir):
        """Test logging a request."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        logger.log_request(
            request_id="req-001",
            method="GET",
            url="https://example.com/api",
            headers={"User-Agent": "Test"},
            body=b"request body",
            target_domain="example.com"
        )
        
        # Verify log file was created
        log_file = Path(temp_log_dir) / "audit.log"
        assert log_file.exists()
        
        # Verify log content
        content = log_file.read_text()
        assert "REQUEST:" in content
        assert "req-001" in content
        assert "GET" in content
        assert "https://example.com/api" in content
    
    def test_log_response(self, temp_log_dir):
        """Test logging a response."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        logger.log_response(
            request_id="req-002",
            method="POST",
            url="https://example.com/api",
            status_code=201,
            request_headers={"Content-Type": "application/json"},
            response_headers={"Content-Type": "application/json"},
            request_body=b'{"key": "value"}',
            response_body=b'{"id": 123}',
            duration_ms=150.5,
            target_domain="example.com"
        )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        assert "RESPONSE:" in content
        assert "req-002" in content
        assert "POST" in content
        assert "201" in content
        assert "150.5" in content
    
    def test_log_error(self, temp_log_dir):
        """Test logging an error."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        logger.log_error(
            request_id="req-003",
            method="GET",
            url="https://example.com/api",
            error="Connection timeout",
            request_headers={"User-Agent": "Test"},
            request_body=None,
            target_domain="example.com"
        )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        assert "ERROR:" in content
        assert "req-003" in content
        assert "Connection timeout" in content
    
    def test_log_request_sanitizes_sensitive_headers(self, temp_log_dir):
        """Test that sensitive headers are sanitized in request logs."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        logger.log_request(
            request_id="req-004",
            method="GET",
            url="https://example.com/api",
            headers={
                "Authorization": "Bearer secret-token",
                "User-Agent": "Test"
            },
            target_domain="example.com"
        )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        assert "[REDACTED]" in content
        assert "secret-token" not in content
        assert "User-Agent" in content
    
    def test_log_response_sanitizes_sensitive_headers(self, temp_log_dir):
        """Test that sensitive headers are sanitized in response logs."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        logger.log_response(
            request_id="req-005",
            method="POST",
            url="https://example.com/api",
            status_code=200,
            request_headers={"Content-Type": "application/json"},
            response_headers={
                "Set-Cookie": "session=abc123; HttpOnly",
                "Content-Type": "application/json"
            },
            duration_ms=100.0,
            target_domain="example.com"
        )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        assert "[REDACTED]" in content
        assert "session=abc123" not in content
    
    def test_get_log_path_default(self, temp_log_dir):
        """Test getting default log path."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        log_path = logger.get_log_path()
        assert log_path == Path(temp_log_dir) / "audit.log"
    
    def test_get_log_path_with_domain(self, temp_log_dir):
        """Test getting log path for specific domain."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        log_path = logger.get_log_path("example.com")
        assert log_path == Path(temp_log_dir) / "audit_example.com.log"
    
    def test_get_log_path_sanitizes_domain(self, temp_log_dir):
        """Test that domain name is sanitized for filename."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        log_path = logger.get_log_path("https://example.com:8080/path")
        
        # Should sanitize special characters
        assert ":" not in log_path.name
        assert "/" not in log_path.name
    
    def test_set_log_level(self, temp_log_dir):
        """Test setting log level."""
        logger = AuditLogger(log_dir=temp_log_dir, log_level=logging.INFO)
        
        logger.set_log_level(logging.DEBUG)
        assert logger.logger.level == logging.DEBUG
    
    def test_multiple_log_entries(self, temp_log_dir):
        """Test logging multiple entries."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        # Log multiple requests
        for i in range(5):
            logger.log_request(
                request_id=f"req-{i}",
                method="GET",
                url=f"https://example.com/api/{i}",
                headers={"User-Agent": "Test"},
                target_domain="example.com"
            )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        # Verify all requests are logged
        for i in range(5):
            assert f"req-{i}" in content
    
    def test_log_with_body_hashing(self, temp_log_dir):
        """Test that request/response bodies are hashed, not stored."""
        logger = AuditLogger(log_dir=temp_log_dir)
        
        request_body = b"sensitive request data"
        response_body = b"sensitive response data"
        
        logger.log_response(
            request_id="req-006",
            method="POST",
            url="https://example.com/api",
            status_code=200,
            request_headers={},
            response_headers={},
            request_body=request_body,
            response_body=response_body,
            duration_ms=100.0,
            target_domain="example.com"
        )
        
        log_file = Path(temp_log_dir) / "audit.log"
        content = log_file.read_text()
        
        # Body content should not be in logs
        assert b"sensitive request data".decode() not in content
        assert b"sensitive response data".decode() not in content
        
        # But hashes should be present
        assert "request_body_hash" in content
        assert "response_body_hash" in content
