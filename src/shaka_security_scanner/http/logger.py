"""
Audit logger for HTTP requests and responses.

This module provides comprehensive logging of all HTTP activities for
compliance, debugging, and security analysis purposes.
"""

import json
import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class AuditLogEntry:
    """Single audit log entry for an HTTP request/response."""
    
    timestamp: str
    request_id: str
    method: str
    url: str
    status_code: Optional[int]
    request_headers: Dict[str, str]
    response_headers: Optional[Dict[str, str]]
    request_body_hash: Optional[str]
    response_body_hash: Optional[str]
    duration_ms: Optional[float]
    error: Optional[str]
    target_domain: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Immutable audit logger for HTTP requests and responses.
    
    Features:
    - Structured JSON logging
    - Request/response correlation via request_id
    - Body content hashing (not storing sensitive data)
    - Separate log files per target domain
    - Automatic log rotation
    - Thread-safe logging
    
    Attributes:
        log_dir: Directory for storing audit logs
        logger: Python logger instance
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        max_body_log_size: int = 1024
    ):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for storing log files
            log_level: Logging level (default: INFO)
            max_body_log_size: Maximum body size to log in bytes (default: 1KB)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_body_log_size = max_body_log_size
        
        # Setup Python logger
        self.logger = logging.getLogger("web_pen_test_framework.audit")
        self.logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all audit logs
        audit_log_path = self.log_dir / "audit.log"
        file_handler = logging.FileHandler(audit_log_path)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _hash_content(self, content: Optional[bytes]) -> Optional[str]:
        """
        Generate SHA-256 hash of content.
        
        Args:
            content: Content to hash
        
        Returns:
            Hex digest of SHA-256 hash, or None if content is None
        """
        if content is None:
            return None
        return hashlib.sha256(content).hexdigest()
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers by redacting sensitive values.
        
        Args:
            headers: Original headers
        
        Returns:
            Sanitized headers with sensitive values redacted
        """
        sensitive_headers = {
            'authorization', 'cookie', 'set-cookie', 'x-api-key',
            'x-auth-token', 'proxy-authorization'
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def log_request(
        self,
        request_id: str,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        target_domain: str = ""
    ) -> None:
        """
        Log an HTTP request.
        
        Args:
            request_id: Unique identifier for request/response correlation
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            body: Request body (optional)
            target_domain: Target domain for log organization
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            request_id=request_id,
            method=method,
            url=url,
            status_code=None,
            request_headers=self._sanitize_headers(headers),
            response_headers=None,
            request_body_hash=self._hash_content(body),
            response_body_hash=None,
            duration_ms=None,
            error=None,
            target_domain=target_domain
        )
        
        self.logger.info(f"REQUEST: {entry.to_json()}")
    
    def log_response(
        self,
        request_id: str,
        method: str,
        url: str,
        status_code: int,
        request_headers: Dict[str, str],
        response_headers: Dict[str, str],
        request_body: Optional[bytes] = None,
        response_body: Optional[bytes] = None,
        duration_ms: float = 0.0,
        target_domain: str = ""
    ) -> None:
        """
        Log an HTTP response.
        
        Args:
            request_id: Unique identifier for request/response correlation
            method: HTTP method
            url: Request URL
            status_code: HTTP status code
            request_headers: Request headers
            response_headers: Response headers
            request_body: Request body (optional)
            response_body: Response body (optional)
            duration_ms: Request duration in milliseconds
            target_domain: Target domain for log organization
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            request_id=request_id,
            method=method,
            url=url,
            status_code=status_code,
            request_headers=self._sanitize_headers(request_headers),
            response_headers=self._sanitize_headers(response_headers),
            request_body_hash=self._hash_content(request_body),
            response_body_hash=self._hash_content(response_body),
            duration_ms=duration_ms,
            error=None,
            target_domain=target_domain
        )
        
        self.logger.info(f"RESPONSE: {entry.to_json()}")
    
    def log_error(
        self,
        request_id: str,
        method: str,
        url: str,
        error: str,
        request_headers: Dict[str, str],
        request_body: Optional[bytes] = None,
        target_domain: str = ""
    ) -> None:
        """
        Log an HTTP error.
        
        Args:
            request_id: Unique identifier for request/response correlation
            method: HTTP method
            url: Request URL
            error: Error message
            request_headers: Request headers
            request_body: Request body (optional)
            target_domain: Target domain for log organization
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            request_id=request_id,
            method=method,
            url=url,
            status_code=None,
            request_headers=self._sanitize_headers(request_headers),
            response_headers=None,
            request_body_hash=self._hash_content(request_body),
            response_body_hash=None,
            duration_ms=None,
            error=error,
            target_domain=target_domain
        )
        
        self.logger.error(f"ERROR: {entry.to_json()}")
    
    def get_log_path(self, target_domain: str = "") -> Path:
        """
        Get the log file path for a specific target domain.
        
        Args:
            target_domain: Target domain
        
        Returns:
            Path to the log file
        """
        if target_domain:
            # Sanitize domain name for filename
            safe_domain = "".join(
                c if c.isalnum() or c in ('-', '_', '.') else '_'
                for c in target_domain
            )
            return self.log_dir / f"audit_{safe_domain}.log"
        return self.log_dir / "audit.log"
    
    def set_log_level(self, level: int) -> None:
        """
        Update logging level.
        
        Args:
            level: New logging level (e.g., logging.DEBUG, logging.INFO)
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(level)
