"""
Unit tests for ConfigurationManager.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from web_pen_test_framework.core.configuration import (
    ConfigurationManager,
    ConfigurationError
)
from web_pen_test_framework.models import (
    IntensityLevel,
    TestSuite,
    Payload,
    PayloadCategory
)


class TestConfigurationManager:
    """Tests for ConfigurationManager class."""
    
    @pytest.fixture
    def sample_config_dict(self):
        """Sample configuration dictionary."""
        return {
            "test_suites": ["reconnaissance", "vulnerability"],
            "intensity": "active",
            "rate_limit": 10,
            "timeout": 30,
            "exclusions": ["/admin/*", "*.pdf"],
            "enable_destructive_tests": False,
            "enable_ai_analysis": True
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config_dict):
        """Create temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(sample_config_dict, f)
            yield Path(f.name)
            # Cleanup
            Path(f.name).unlink(missing_ok=True)
    
    def test_load_config_from_file(self, temp_config_file):
        """Test loading configuration from YAML file."""
        manager = ConfigurationManager()
        config = manager.load_config(temp_config_file)
        
        assert config is not None
        assert len(config.test_suites) == 2
        assert TestSuite.RECONNAISSANCE in config.test_suites
        assert TestSuite.VULNERABILITY in config.test_suites
        assert config.intensity == IntensityLevel.ACTIVE
        assert config.rate_limit == 10
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        manager = ConfigurationManager()
        
        with pytest.raises(ConfigurationError, match="not found"):
            manager.load_config("nonexistent.yaml")
    
    def test_load_config_invalid_format(self):
        """Test loading configuration with invalid format."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("invalid config")
            temp_file = Path(f.name)
        
        try:
            manager = ConfigurationManager()
            with pytest.raises(ConfigurationError, match="Unsupported configuration file format"):
                manager.load_config(temp_file)
        finally:
            temp_file.unlink(missing_ok=True)
    
    def test_set_test_suites(self, temp_config_file):
        """Test setting test suites."""
        manager = ConfigurationManager(temp_config_file)
        
        manager.set_test_suites([TestSuite.HEADERS, TestSuite.SSL_TLS])
        config = manager.get_configuration()
        
        assert len(config.test_suites) == 2
        assert TestSuite.HEADERS in config.test_suites
        assert TestSuite.SSL_TLS in config.test_suites
    
    def test_set_test_suites_from_strings(self, temp_config_file):
        """Test setting test suites from strings."""
        manager = ConfigurationManager(temp_config_file)
        
        manager.set_test_suites(["headers", "ssl_tls"])
        config = manager.get_configuration()
        
        assert len(config.test_suites) == 2
        assert TestSuite.HEADERS in config.test_suites
        assert TestSuite.SSL_TLS in config.test_suites
    
    def test_set_test_suites_invalid(self, temp_config_file):
        """Test setting invalid test suite."""
        manager = ConfigurationManager(temp_config_file)
        
        with pytest.raises(ConfigurationError, match="Invalid test suite"):
            manager.set_test_suites(["invalid_suite"])
    
    def test_set_intensity(self, temp_config_file):
        """Test setting intensity level."""
        manager = ConfigurationManager(temp_config_file)
        
        manager.set_intensity(IntensityLevel.AGGRESSIVE)
        config = manager.get_configuration()
        
        assert config.intensity == IntensityLevel.AGGRESSIVE
    
    def test_set_intensity_from_string(self, temp_config_file):
        """Test setting intensity from string."""
        manager = ConfigurationManager(temp_config_file)
        
        manager.set_intensity("passive")
        config = manager.get_configuration()
        
        assert config.intensity == IntensityLevel.PASSIVE
    
    def test_set_intensity_invalid(self, temp_config_file):
        """Test setting invalid intensity level."""
        manager = ConfigurationManager(temp_config_file)
        
        with pytest.raises(ConfigurationError, match="Invalid intensity level"):
            manager.set_intensity("invalid")
    
    def test_set_rate_limit(self, temp_config_file):
        """Test setting rate limit."""
        manager = ConfigurationManager(temp_config_file)
        
        manager.set_rate_limit(20)
        config = manager.get_configuration()
        
        assert config.rate_limit == 20
    
    def test_set_rate_limit_invalid(self, temp_config_file):
        """Test setting invalid rate limit."""
        manager = ConfigurationManager(temp_config_file)
        
        with pytest.raises(ConfigurationError, match="Rate limit must be positive"):
            manager.set_rate_limit(0)
        
        with pytest.raises(ConfigurationError, match="Rate limit must be positive"):
            manager.set_rate_limit(-5)
    
    def test_add_exclusions(self, temp_config_file):
        """Test adding exclusion patterns."""
        manager = ConfigurationManager(temp_config_file)
        
        initial_count = len(manager.get_configuration().exclusions)
        manager.add_exclusions(["/api/*", "*.jpg"])
        
        config = manager.get_configuration()
        assert len(config.exclusions) == initial_count + 2
        assert "/api/*" in config.exclusions
        assert "*.jpg" in config.exclusions
    
    def test_add_custom_payloads(self, temp_config_file):
        """Test adding custom payloads."""
        manager = ConfigurationManager(temp_config_file)
        
        payload_dict = {
            "value": "' OR '1'='1",
            "category": "sqli",
            "description": "Basic SQL injection"
        }
        
        manager.add_custom_payloads([payload_dict])
        config = manager.get_configuration()
        
        assert len(config.custom_payloads) == 1
        assert config.custom_payloads[0].value == "' OR '1'='1"
        assert config.custom_payloads[0].category == PayloadCategory.SQL_INJECTION
    
    def test_add_custom_payloads_object(self, temp_config_file):
        """Test adding custom payloads as Payload objects."""
        manager = ConfigurationManager(temp_config_file)
        
        payload = Payload(
            value="<script>alert('XSS')</script>",
            category=PayloadCategory.XSS,
            description="Basic XSS payload"
        )
        
        manager.add_custom_payloads([payload])
        config = manager.get_configuration()
        
        assert len(config.custom_payloads) == 1
        assert config.custom_payloads[0].value == "<script>alert('XSS')</script>"
    
    def test_is_url_excluded_exact_match(self, temp_config_file):
        """Test URL exclusion with exact match."""
        manager = ConfigurationManager(temp_config_file)
        
        assert manager.is_url_excluded("/admin/users") is True
        assert manager.is_url_excluded("/admin/settings") is True
        assert manager.is_url_excluded("/public/page") is False
    
    def test_is_url_excluded_wildcard(self, temp_config_file):
        """Test URL exclusion with wildcard patterns."""
        manager = ConfigurationManager(temp_config_file)
        
        # Test *.pdf pattern
        assert manager.is_url_excluded("document.pdf") is True
        assert manager.is_url_excluded("report.pdf") is True
        assert manager.is_url_excluded("page.html") is False
    
    def test_match_pattern_wildcard(self, temp_config_file):
        """Test pattern matching with wildcards."""
        manager = ConfigurationManager(temp_config_file)
        
        # Test * wildcard
        assert manager._match_pattern("hello world", "hello*") is True
        assert manager._match_pattern("hello", "hello*") is True
        assert manager._match_pattern("goodbye", "hello*") is False
        
        # Test ? wildcard
        assert manager._match_pattern("hello", "hell?") is True
        assert manager._match_pattern("hella", "hell?") is True
        assert manager._match_pattern("hello world", "hell?") is False
    
    def test_validate_configuration_warnings(self, temp_config_file):
        """Test configuration validation warnings."""
        manager = ConfigurationManager(temp_config_file)
        
        # Should have no warnings initially
        warnings = manager.validate_configuration()
        assert len(warnings) == 0
        
        # Set aggressive intensity
        manager.set_intensity(IntensityLevel.AGGRESSIVE)
        warnings = manager.validate_configuration()
        assert any("aggressive" in w.lower() for w in warnings)
        
        # Set high rate limit
        manager.set_rate_limit(100)
        warnings = manager.validate_configuration()
        assert any("rate limit" in w.lower() for w in warnings)
    
    def test_merge_config(self, temp_config_file):
        """Test merging configurations."""
        manager = ConfigurationManager(temp_config_file)
        
        original_rate = manager.get_configuration().rate_limit
        
        # Merge new config
        manager.merge_config({"rate_limit": 50})
        
        config = manager.get_configuration()
        assert config.rate_limit == 50
        assert config.rate_limit != original_rate
    
    def test_to_dict(self, temp_config_file):
        """Test converting configuration to dictionary."""
        manager = ConfigurationManager(temp_config_file)
        
        config_dict = manager.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "test_suites" in config_dict
        assert "intensity" in config_dict
        assert "rate_limit" in config_dict
        assert config_dict["rate_limit"] == 10
    
    def test_get_configuration_not_loaded(self):
        """Test getting configuration when not loaded."""
        manager = ConfigurationManager()
        
        with pytest.raises(ConfigurationError, match="Configuration not loaded"):
            manager.get_configuration()
    
    def test_parse_custom_payloads_invalid(self):
        """Test parsing invalid custom payloads."""
        manager = ConfigurationManager()
        
        # Missing required field
        with pytest.raises(ConfigurationError, match="missing field"):
            manager._parse_custom_payloads([{"category": "sqli"}])
    
    def test_empty_test_suites(self):
        """Test configuration with empty test suites."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump({"test_suites": []}, f)
            temp_file = Path(f.name)
        
        try:
            manager = ConfigurationManager()
            with pytest.raises(ConfigurationError, match="At least one test suite"):
                manager.load_config(temp_file)
        finally:
            temp_file.unlink(missing_ok=True)


class TestConfigurationDefaults:
    """Tests for default configuration values."""
    
    def test_default_values(self):
        """Test that default values are applied."""
        config_dict = {"test_suites": ["reconnaissance"]}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            yaml.dump(config_dict, f)
            temp_file = Path(f.name)
        
        try:
            manager = ConfigurationManager(temp_file)
            config = manager.get_configuration()
            
            # Check defaults are applied
            assert config.rate_limit == 10  # Default
            assert config.timeout == 30  # Default
            assert config.enable_ai_analysis is True  # Default
            assert config.user_agent == "WebPenTestFramework/0.1.0"  # Default
        finally:
            temp_file.unlink(missing_ok=True)
