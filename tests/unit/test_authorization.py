"""
Unit tests for AuthorizationManager.
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from web_pen_test_framework.core.authorization import (
    AuthorizationManager,
    ValidationResult
)
from web_pen_test_framework.models import AuthorizationToken, Target


class TestAuthorizationManager:
    """Tests for AuthorizationManager class."""
    
    @pytest.fixture
    def temp_audit_log(self):
        """Create temporary audit log file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            yield Path(f.name)
            # Cleanup
            Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def auth_manager(self, temp_audit_log):
        """Create AuthorizationManager instance."""
        return AuthorizationManager(
            audit_log_path=temp_audit_log,
            secret_key="test-secret-key",
            require_signature=False  # Disable for basic tests
        )
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid authorization token."""
        now = datetime.now()
        future = now + timedelta(days=30)
        return AuthorizationToken(
            token="test-token-123",
            target_domain="example.com",
            issued_at=now,
            expires_at=future,
            scope=["reconnaissance", "vulnerability"]
        )
    
    @pytest.fixture
    def target(self):
        """Create a target."""
        return Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
    
    def test_validate_valid_token(self, auth_manager, valid_token, target):
        """Test validating a valid token."""
        result = auth_manager.validate_token(valid_token, target)
        
        assert result.is_valid is True
        assert result.token == valid_token
        assert result.error_code is None
        assert "successfully" in result.message.lower()
    
    def test_validate_expired_token(self, auth_manager, target):
        """Test validating an expired token."""
        past = datetime.now() - timedelta(days=30)
        yesterday = datetime.now() - timedelta(days=1)
        
        expired_token = AuthorizationToken(
            token="expired-token",
            target_domain="example.com",
            issued_at=past,
            expires_at=yesterday
        )
        
        result = auth_manager.validate_token(expired_token, target)
        
        assert result.is_valid is False
        assert result.error_code == "TOKEN_EXPIRED"
        assert "expired" in result.message.lower()
    
    def test_validate_domain_mismatch(self, auth_manager, valid_token):
        """Test validating token with domain mismatch."""
        wrong_target = Target(
            url="https://different.com",
            base_domain="different.com",
            scheme="https"
        )
        
        result = auth_manager.validate_token(valid_token, wrong_target)
        
        assert result.is_valid is False
        assert result.error_code == "DOMAIN_MISMATCH"
        assert "does not match" in result.message.lower()
    
    def test_check_domain_match_exact(self, auth_manager):
        """Test exact domain matching."""
        assert auth_manager._check_domain_match("example.com", "example.com") is True
        assert auth_manager._check_domain_match("example.com", "different.com") is False
    
    def test_check_domain_match_wildcard(self, auth_manager):
        """Test wildcard domain matching."""
        assert auth_manager._check_domain_match("*.example.com", "api.example.com") is True
        assert auth_manager._check_domain_match("*.example.com", "www.example.com") is True
        assert auth_manager._check_domain_match("*.example.com", "example.com") is False
        assert auth_manager._check_domain_match("*.example.com", "different.com") is False
    
    def test_log_authorization_attempt(self, auth_manager, valid_token, target, temp_audit_log):
        """Test logging authorization attempts."""
        # Log successful attempt
        auth_manager.log_authorization_attempt(
            valid_token,
            target,
            result=True,
            details="Test authorization"
        )
        
        # Check log file was created and contains entry
        assert temp_audit_log.exists()
        log_content = temp_audit_log.read_text()
        assert "SUCCESS" in log_content
        assert "example.com" in log_content
        
        # Log failed attempt
        auth_manager.log_authorization_attempt(
            valid_token,
            target,
            result=False,
            details="Test failure"
        )
        
        log_content = temp_audit_log.read_text()
        assert "FAILURE" in log_content
    
    def test_check_scope_with_permission(self, auth_manager, valid_token):
        """Test scope checking with permission."""
        assert auth_manager.check_scope(valid_token, "reconnaissance") is True
        assert auth_manager.check_scope(valid_token, "vulnerability") is True
    
    def test_check_scope_without_permission(self, auth_manager, valid_token):
        """Test scope checking without permission."""
        assert auth_manager.check_scope(valid_token, "destructive") is False
    
    def test_check_scope_empty_scope(self, auth_manager, target):
        """Test scope checking with empty scope (all permissions)."""
        now = datetime.now()
        future = now + timedelta(days=30)
        
        token_all_perms = AuthorizationToken(
            token="all-perms-token",
            target_domain="example.com",
            issued_at=now,
            expires_at=future,
            scope=[]  # Empty scope = all permissions
        )
        
        assert auth_manager.check_scope(token_all_perms, "any_scope") is True
    
    def test_check_scope_wildcard(self, auth_manager, target):
        """Test scope checking with wildcard."""
        now = datetime.now()
        future = now + timedelta(days=30)
        
        token_wildcard = AuthorizationToken(
            token="wildcard-token",
            target_domain="example.com",
            issued_at=now,
            expires_at=future,
            scope=["*"]
        )
        
        assert auth_manager.check_scope(token_wildcard, "any_scope") is True
    
    def test_generate_token(self, auth_manager):
        """Test token generation."""
        token = auth_manager.generate_token(
            target_domain="example.com",
            validity_days=30,
            scope=["reconnaissance", "vulnerability"]
        )
        
        assert token.target_domain == "example.com"
        assert token.is_valid()
        assert not token.is_expired()
        assert "reconnaissance" in token.scope
        assert "vulnerability" in token.scope
    
    def test_display_disclaimer(self, auth_manager, capsys):
        """Test disclaimer display."""
        auth_manager.display_disclaimer()
        
        captured = capsys.readouterr()
        assert "LEGAL DISCLAIMER" in captured.out
        assert "AUTHORIZED" in captured.out
        assert "ILLEGAL" in captured.out


class TestAuthorizationManagerWithSignature:
    """Tests for AuthorizationManager with signature verification."""
    
    @pytest.fixture
    def auth_manager_with_sig(self, tmp_path):
        """Create AuthorizationManager with signature verification."""
        audit_log = tmp_path / "audit.log"
        return AuthorizationManager(
            audit_log_path=audit_log,
            secret_key="test-secret-key",
            require_signature=True
        )
    
    @pytest.fixture
    def target(self):
        """Create a target."""
        return Target(
            url="https://example.com",
            base_domain="example.com",
            scheme="https"
        )
    
    def test_validate_token_with_valid_signature(self, auth_manager_with_sig, target):
        """Test validating token with valid signature."""
        # Generate token with signature
        token = auth_manager_with_sig.generate_token(
            target_domain="example.com",
            validity_days=30,
            scope=["reconnaissance"]
        )
        
        result = auth_manager_with_sig.validate_token(token, target)
        
        assert result.is_valid is True
        assert result.error_code is None
    
    def test_validate_token_with_invalid_signature(self, auth_manager_with_sig, target):
        """Test validating token with invalid signature."""
        now = datetime.now()
        future = now + timedelta(days=30)
        
        # Create token with invalid signature
        invalid_token = AuthorizationToken(
            token="invalid-signature-token",
            target_domain="example.com",
            issued_at=now,
            expires_at=future
        )
        
        result = auth_manager_with_sig.validate_token(invalid_token, target)
        
        assert result.is_valid is False
        assert result.error_code == "INVALID_SIGNATURE"
    
    def test_verify_signature_valid(self, auth_manager_with_sig):
        """Test signature verification with valid signature."""
        token = auth_manager_with_sig.generate_token(
            target_domain="example.com",
            validity_days=30
        )
        
        assert auth_manager_with_sig._verify_signature(token) is True
    
    def test_verify_signature_invalid(self, auth_manager_with_sig):
        """Test signature verification with invalid signature."""
        now = datetime.now()
        future = now + timedelta(days=30)
        
        invalid_token = AuthorizationToken(
            token="short",  # Too short to contain valid signature
            target_domain="example.com",
            issued_at=now,
            expires_at=future
        )
        
        assert auth_manager_with_sig._verify_signature(invalid_token) is False


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(
            is_valid=True,
            message="Token is valid"
        )
        
        assert result.is_valid is True
        assert result.message == "Token is valid"
        assert result.token is None
        assert result.error_code is None
    
    def test_invalid_result(self):
        """Test creating an invalid result."""
        result = ValidationResult(
            is_valid=False,
            message="Token expired",
            error_code="TOKEN_EXPIRED"
        )
        
        assert result.is_valid is False
        assert result.message == "Token expired"
        assert result.error_code == "TOKEN_EXPIRED"
