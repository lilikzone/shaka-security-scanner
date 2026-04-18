"""
Authorization Manager for the Web Penetration Testing Framework.

This module handles authorization token validation, logging, and legal disclaimers
to ensure all scans are properly authorized.
"""

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import AuthorizationToken, Target


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of token validation."""
    is_valid: bool
    message: str
    token: Optional[AuthorizationToken] = None
    error_code: Optional[str] = None


class AuthorizationManager:
    """
    Manages authorization for penetration testing scans.
    
    This class is responsible for:
    - Validating authorization tokens
    - Logging all authorization attempts
    - Displaying legal disclaimers
    - Enforcing authorization policies
    """
    
    # Legal disclaimer text
    DISCLAIMER = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                          LEGAL DISCLAIMER                                ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║  This Web Penetration Testing Framework is designed for AUTHORIZED      ║
    ║  security testing ONLY. By using this tool, you acknowledge that:       ║
    ║                                                                          ║
    ║  1. You have EXPLICIT WRITTEN PERMISSION from the system owner          ║
    ║  2. You will comply with ALL applicable laws and regulations            ║
    ║  3. You will NOT use this tool for malicious purposes                   ║
    ║  4. You accept FULL RESPONSIBILITY for your actions                     ║
    ║  5. You will respect rate limits and avoid denial of service            ║
    ║                                                                          ║
    ║  UNAUTHORIZED USE IS ILLEGAL and may result in:                         ║
    ║  - Criminal prosecution                                                  ║
    ║  - Civil liability                                                       ║
    ║  - Significant fines and penalties                                       ║
    ║                                                                          ║
    ║  The developers of this tool are NOT RESPONSIBLE for any misuse         ║
    ║  or damage caused by unauthorized use.                                   ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    
    def __init__(
        self,
        audit_log_path: Optional[Path] = None,
        secret_key: Optional[str] = None,
        require_signature: bool = True
    ):
        """
        Initialize the Authorization Manager.
        
        Args:
            audit_log_path: Path to audit log file (default: logs/authorization_audit.log)
            secret_key: Secret key for token signature verification
            require_signature: Whether to require token signatures
        """
        self.audit_log_path = audit_log_path or Path("logs/authorization_audit.log")
        self.secret_key = secret_key or "default-secret-key-change-in-production"
        self.require_signature = require_signature
        
        # Ensure audit log directory exists
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup audit logger
        self._setup_audit_logger()
    
    def _setup_audit_logger(self) -> None:
        """Setup dedicated audit logger."""
        self.audit_logger = logging.getLogger("authorization_audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.audit_logger.handlers.clear()
        
        # Create file handler
        handler = logging.FileHandler(self.audit_log_path)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler
        self.audit_logger.addHandler(handler)
        
        # Prevent propagation to root logger
        self.audit_logger.propagate = False
    
    def validate_token(
        self,
        token: AuthorizationToken,
        target: Target
    ) -> ValidationResult:
        """
        Validate an authorization token for a target.
        
        This method performs comprehensive validation including:
        - Token expiry check
        - Domain matching
        - Signature verification (if required)
        - Scope validation
        
        Args:
            token: Authorization token to validate
            target: Target to scan
        
        Returns:
            ValidationResult with validation status and details
        """
        logger.info(f"Validating token for target: {target.base_domain}")
        
        # Check if token is expired
        if token.is_expired():
            message = f"Token expired at {token.expires_at}"
            logger.warning(message)
            return ValidationResult(
                is_valid=False,
                message=message,
                error_code="TOKEN_EXPIRED"
            )
        
        # Check domain matching
        if not self._check_domain_match(token.target_domain, target.base_domain):
            message = f"Token domain '{token.target_domain}' does not match target '{target.base_domain}'"
            logger.warning(message)
            return ValidationResult(
                is_valid=False,
                message=message,
                error_code="DOMAIN_MISMATCH"
            )
        
        # Verify signature if required
        if self.require_signature:
            if not self._verify_signature(token):
                message = "Token signature verification failed"
                logger.warning(message)
                return ValidationResult(
                    is_valid=False,
                    message=message,
                    error_code="INVALID_SIGNATURE"
                )
        
        # Token is valid
        message = f"Token validated successfully for {target.base_domain}"
        logger.info(message)
        return ValidationResult(
            is_valid=True,
            message=message,
            token=token
        )
    
    def _check_domain_match(self, token_domain: str, target_domain: str) -> bool:
        """
        Check if token domain matches target domain.
        
        Supports wildcard matching (e.g., *.example.com matches api.example.com)
        
        Args:
            token_domain: Domain from authorization token
            target_domain: Domain of target
        
        Returns:
            True if domains match, False otherwise
        """
        # Exact match
        if token_domain == target_domain:
            return True
        
        # Wildcard match (*.example.com)
        if token_domain.startswith("*."):
            base_domain = token_domain[2:]  # Remove *.
            # Must have subdomain (e.g., api.example.com, not example.com)
            return target_domain.endswith(f".{base_domain}")
        
        return False
    
    def _verify_signature(self, token: AuthorizationToken) -> bool:
        """
        Verify token signature using HMAC-SHA256.
        
        Args:
            token: Authorization token to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        # Create payload from token data
        payload = {
            "target_domain": token.target_domain,
            "issued_at": token.issued_at.isoformat(),
            "expires_at": token.expires_at.isoformat(),
            "scope": sorted(token.scope)  # Sort for consistency
        }
        
        # Generate expected signature
        payload_str = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Extract signature from token (last 64 chars)
        if len(token.token) < 64:
            return False
        
        token_signature = token.token[-64:]
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(token_signature, expected_signature)
    
    def log_authorization_attempt(
        self,
        token: AuthorizationToken,
        target: Target,
        result: bool,
        details: Optional[str] = None
    ) -> None:
        """
        Log an authorization attempt to the audit log.
        
        Args:
            token: Authorization token used
            target: Target that was attempted
            result: Whether authorization was successful
            details: Additional details about the attempt
        """
        status = "SUCCESS" if result else "FAILURE"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "token_domain": token.target_domain,
            "target_domain": target.base_domain,
            "target_url": target.url,
            "token_issued_at": token.issued_at.isoformat(),
            "token_expires_at": token.expires_at.isoformat(),
            "token_scope": token.scope,
            "details": details or ""
        }
        
        # Log to audit file
        self.audit_logger.info(json.dumps(log_entry))
        
        # Also log to main logger
        logger.info(
            f"Authorization {status}: {target.base_domain} "
            f"(token: {token.target_domain})"
        )
    
    def display_disclaimer(self) -> None:
        """
        Display legal disclaimer to the user.
        
        This must be shown before any scan begins to ensure users
        understand their legal obligations.
        """
        print(self.DISCLAIMER)
        logger.info("Legal disclaimer displayed to user")
    
    def require_acknowledgment(self) -> bool:
        """
        Require user to acknowledge the legal disclaimer.
        
        Returns:
            True if user acknowledges, False otherwise
        """
        self.display_disclaimer()
        
        try:
            response = input("\nDo you acknowledge and accept these terms? (yes/no): ").strip().lower()
            
            if response in ["yes", "y"]:
                logger.info("User acknowledged legal disclaimer")
                return True
            else:
                logger.warning("User declined legal disclaimer")
                return False
        except (KeyboardInterrupt, EOFError):
            logger.warning("User interrupted disclaimer acknowledgment")
            return False
    
    def check_scope(
        self,
        token: AuthorizationToken,
        required_scope: str
    ) -> bool:
        """
        Check if token has required scope.
        
        Args:
            token: Authorization token
            required_scope: Required scope (e.g., "vulnerability_scan")
        
        Returns:
            True if token has required scope, False otherwise
        """
        # Empty scope means all permissions
        if not token.scope:
            return True
        
        # Check if required scope is in token scope
        if required_scope in token.scope:
            return True
        
        # Check for wildcard scope
        if "*" in token.scope or "all" in token.scope:
            return True
        
        logger.warning(
            f"Token missing required scope: {required_scope}. "
            f"Token scope: {token.scope}"
        )
        return False
    
    def generate_token(
        self,
        target_domain: str,
        validity_days: int = 30,
        scope: Optional[list] = None
    ) -> AuthorizationToken:
        """
        Generate a new authorization token.
        
        This is a utility method for creating tokens. In production,
        tokens should be generated by a separate authorization service.
        
        Args:
            target_domain: Domain the token is valid for
            validity_days: Number of days the token is valid
            scope: List of allowed scopes
        
        Returns:
            New AuthorizationToken
        """
        from datetime import timedelta
        
        now = datetime.now()
        expires_at = now + timedelta(days=validity_days)
        
        # Create payload
        payload = {
            "target_domain": target_domain,
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "scope": sorted(scope or [])
        }
        
        # Generate signature
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Create token string (base64 encoded payload + signature)
        import base64
        token_data = base64.b64encode(payload_str.encode()).decode()
        token_string = f"{token_data}.{signature}"
        
        return AuthorizationToken(
            token=token_string,
            target_domain=target_domain,
            issued_at=now,
            expires_at=expires_at,
            scope=scope or []
        )
