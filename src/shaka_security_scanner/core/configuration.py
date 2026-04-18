"""
Configuration Manager for the Web Penetration Testing Framework.

This module handles loading, validating, and managing scan configurations
from various sources (files, CLI arguments, environment variables).
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from ..models import (
    Configuration,
    IntensityLevel,
    Payload,
    PayloadCategory,
    TestSuite,
)


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class ConfigurationManager:
    """
    Manages scan configuration for the framework.
    
    This class is responsible for:
    - Loading configuration from YAML/JSON files
    - Validating configuration parameters
    - Managing test suite selection
    - Handling exclusion patterns
    - Managing custom payloads
    - Merging configurations from multiple sources
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "intensity": "active",
        "rate_limit": 10,
        "timeout": 30,
        "enable_destructive_tests": False,
        "enable_ai_analysis": True,
        "max_concurrent_requests": 10,
        "user_agent": "WebPenTestFramework/0.1.0",
        "follow_redirects": True,
        "max_redirects": 10,
        "verify_ssl": True,
        "proxy": None,
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
        """
        self.config_file = config_file
        self._config_data: Dict[str, Any] = {}
        self._configuration: Optional[Configuration] = None
        
        # Load configuration if file provided
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, config_file: Union[str, Path]) -> Configuration:
        """
        Load configuration from a YAML or JSON file.
        
        Args:
            config_file: Path to configuration file
        
        Returns:
            Configuration object
        
        Raises:
            ConfigurationError: If file cannot be loaded or is invalid
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    self._config_data = yaml.safe_load(f) or {}
                elif config_path.suffix == '.json':
                    import json
                    self._config_data = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {config_path.suffix}. "
                        "Use .yaml, .yml, or .json"
                    )
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
        
        # Merge with defaults
        self._config_data = {**self.DEFAULT_CONFIG, **self._config_data}
        
        # Build Configuration object
        self._configuration = self._build_configuration()
        
        logger.info("Configuration loaded successfully")
        return self._configuration
    
    def _build_configuration(self) -> Configuration:
        """
        Build Configuration object from loaded data.
        
        Returns:
            Configuration object
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Parse test suites
            test_suites = self._parse_test_suites(
                self._config_data.get("test_suites", [])
            )
            
            if not test_suites:
                raise ConfigurationError("At least one test suite must be specified")
            
            # Parse intensity level
            intensity = self._parse_intensity(
                self._config_data.get("intensity", "active")
            )
            
            # Parse exclusions
            exclusions = self._config_data.get("exclusions", [])
            if not isinstance(exclusions, list):
                raise ConfigurationError("Exclusions must be a list")
            
            # Parse custom payloads
            custom_payloads = self._parse_custom_payloads(
                self._config_data.get("custom_payloads", [])
            )
            
            # Create Configuration object
            config = Configuration(
                test_suites=test_suites,
                intensity=intensity,
                rate_limit=self._config_data.get("rate_limit", 10),
                timeout=self._config_data.get("timeout", 30),
                exclusions=exclusions,
                custom_payloads=custom_payloads,
                enable_destructive_tests=self._config_data.get("enable_destructive_tests", False),
                enable_ai_analysis=self._config_data.get("enable_ai_analysis", True),
                max_concurrent_requests=self._config_data.get("max_concurrent_requests", 10),
                user_agent=self._config_data.get("user_agent", "WebPenTestFramework/0.1.0"),
                follow_redirects=self._config_data.get("follow_redirects", True),
                max_redirects=self._config_data.get("max_redirects", 10),
                verify_ssl=self._config_data.get("verify_ssl", True),
                proxy=self._config_data.get("proxy"),
            )
            
            return config
            
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration: {e}")
    
    def _parse_test_suites(self, suites: List[str]) -> List[TestSuite]:
        """
        Parse test suite names into TestSuite enums.
        
        Args:
            suites: List of test suite names
        
        Returns:
            List of TestSuite enums
        
        Raises:
            ConfigurationError: If invalid test suite name
        """
        parsed_suites = []
        
        for suite_name in suites:
            try:
                suite = TestSuite(suite_name.lower())
                parsed_suites.append(suite)
            except ValueError:
                valid_suites = [s.value for s in TestSuite]
                raise ConfigurationError(
                    f"Invalid test suite: '{suite_name}'. "
                    f"Valid options: {', '.join(valid_suites)}"
                )
        
        return parsed_suites
    
    def _parse_intensity(self, intensity: str) -> IntensityLevel:
        """
        Parse intensity level string into IntensityLevel enum.
        
        Args:
            intensity: Intensity level string
        
        Returns:
            IntensityLevel enum
        
        Raises:
            ConfigurationError: If invalid intensity level
        """
        try:
            return IntensityLevel(intensity.lower())
        except ValueError:
            valid_levels = [level.value for level in IntensityLevel]
            raise ConfigurationError(
                f"Invalid intensity level: '{intensity}'. "
                f"Valid options: {', '.join(valid_levels)}"
            )
    
    def _parse_custom_payloads(self, payloads: List[Dict[str, Any]]) -> List[Payload]:
        """
        Parse custom payload definitions.
        
        Args:
            payloads: List of payload dictionaries
        
        Returns:
            List of Payload objects
        
        Raises:
            ConfigurationError: If invalid payload definition
        """
        parsed_payloads = []
        
        for i, payload_data in enumerate(payloads):
            try:
                # Parse category
                category_str = payload_data.get("category", "other")
                try:
                    category = PayloadCategory(category_str.lower())
                except ValueError:
                    logger.warning(f"Invalid payload category '{category_str}', using 'other'")
                    category = PayloadCategory.OTHER
                
                payload = Payload(
                    value=payload_data["value"],
                    category=category,
                    encoding=payload_data.get("encoding"),
                    description=payload_data.get("description", "")
                )
                parsed_payloads.append(payload)
                
            except KeyError as e:
                raise ConfigurationError(
                    f"Invalid payload definition at index {i}: missing field {e}"
                )
            except ValueError as e:
                raise ConfigurationError(
                    f"Invalid payload definition at index {i}: {e}"
                )
        
        return parsed_payloads
    
    def set_test_suites(self, suites: List[Union[str, TestSuite]]) -> None:
        """
        Set test suites to execute.
        
        Args:
            suites: List of test suite names or TestSuite enums
        
        Raises:
            ConfigurationError: If configuration not loaded or invalid suite
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        # Convert strings to TestSuite enums
        parsed_suites = []
        for suite in suites:
            if isinstance(suite, TestSuite):
                parsed_suites.append(suite)
            elif isinstance(suite, str):
                parsed_suites.extend(self._parse_test_suites([suite]))
            else:
                raise ConfigurationError(f"Invalid test suite type: {type(suite)}")
        
        self._configuration.test_suites = parsed_suites
        logger.info(f"Test suites updated: {[s.value for s in parsed_suites]}")
    
    def set_intensity(self, level: Union[str, IntensityLevel]) -> None:
        """
        Set scan intensity level.
        
        Args:
            level: Intensity level (string or IntensityLevel enum)
        
        Raises:
            ConfigurationError: If configuration not loaded or invalid level
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        if isinstance(level, IntensityLevel):
            self._configuration.intensity = level
        elif isinstance(level, str):
            self._configuration.intensity = self._parse_intensity(level)
        else:
            raise ConfigurationError(f"Invalid intensity type: {type(level)}")
        
        logger.info(f"Intensity level updated: {self._configuration.intensity.value}")
    
    def set_rate_limit(self, rate: int) -> None:
        """
        Set request rate limit (requests per second).
        
        Args:
            rate: Requests per second
        
        Raises:
            ConfigurationError: If configuration not loaded or invalid rate
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        if rate <= 0:
            raise ConfigurationError("Rate limit must be positive")
        
        self._configuration.rate_limit = rate
        logger.info(f"Rate limit updated: {rate} requests/second")
    
    def add_exclusions(self, patterns: List[str]) -> None:
        """
        Add URL exclusion patterns.
        
        Args:
            patterns: List of URL patterns to exclude (supports wildcards)
        
        Raises:
            ConfigurationError: If configuration not loaded
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        self._configuration.exclusions.extend(patterns)
        logger.info(f"Added {len(patterns)} exclusion patterns")
    
    def add_custom_payloads(self, payloads: List[Union[Dict[str, Any], Payload]]) -> None:
        """
        Add custom payloads.
        
        Args:
            payloads: List of payload dictionaries or Payload objects
        
        Raises:
            ConfigurationError: If configuration not loaded or invalid payload
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        for payload in payloads:
            if isinstance(payload, Payload):
                self._configuration.custom_payloads.append(payload)
            elif isinstance(payload, dict):
                parsed = self._parse_custom_payloads([payload])
                self._configuration.custom_payloads.extend(parsed)
            else:
                raise ConfigurationError(f"Invalid payload type: {type(payload)}")
        
        logger.info(f"Added {len(payloads)} custom payloads")
    
    def is_url_excluded(self, url: str) -> bool:
        """
        Check if a URL matches any exclusion pattern.
        
        Supports wildcards:
        - * matches any characters
        - ? matches single character
        
        Args:
            url: URL to check
        
        Returns:
            True if URL should be excluded, False otherwise
        """
        if self._configuration is None:
            return False
        
        for pattern in self._configuration.exclusions:
            if self._match_pattern(url, pattern):
                logger.debug(f"URL excluded by pattern '{pattern}': {url}")
                return True
        
        return False
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """
        Match text against pattern with wildcard support.
        
        Args:
            text: Text to match
            pattern: Pattern with wildcards (* and ?)
        
        Returns:
            True if text matches pattern, False otherwise
        """
        # Convert wildcard pattern to regex
        # Escape special regex characters except * and ?
        regex_pattern = re.escape(pattern)
        regex_pattern = regex_pattern.replace(r'\*', '.*')  # * matches any characters
        regex_pattern = regex_pattern.replace(r'\?', '.')   # ? matches single character
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, text))
    
    def get_configuration(self) -> Configuration:
        """
        Get the current configuration.
        
        Returns:
            Configuration object
        
        Raises:
            ConfigurationError: If configuration not loaded
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        return self._configuration
    
    def merge_config(self, other_config: Dict[str, Any]) -> None:
        """
        Merge another configuration dictionary into current config.
        
        This is useful for CLI overrides or environment variable overrides.
        
        Args:
            other_config: Configuration dictionary to merge
        """
        if self._configuration is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        
        # Merge config data
        self._config_data.update(other_config)
        
        # Rebuild configuration
        self._configuration = self._build_configuration()
        
        logger.info("Configuration merged successfully")
    
    def validate_configuration(self) -> List[str]:
        """
        Validate current configuration and return any warnings.
        
        Returns:
            List of warning messages (empty if no warnings)
        """
        warnings = []
        
        if self._configuration is None:
            warnings.append("Configuration not loaded")
            return warnings
        
        # Check for aggressive settings
        if self._configuration.intensity == IntensityLevel.AGGRESSIVE:
            warnings.append(
                "Aggressive intensity level may cause high load on target. "
                "Ensure you have permission and target can handle the load."
            )
        
        if self._configuration.rate_limit > 50:
            warnings.append(
                f"High rate limit ({self._configuration.rate_limit} req/s) may cause "
                "denial of service. Consider reducing rate limit."
            )
        
        if self._configuration.enable_destructive_tests:
            warnings.append(
                "Destructive tests are enabled. These tests may modify or delete data. "
                "Ensure you have explicit permission and backups."
            )
        
        if not self._configuration.verify_ssl:
            warnings.append(
                "SSL verification is disabled. This may expose you to man-in-the-middle attacks."
            )
        
        return warnings
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        if self._configuration is None:
            return {}
        
        return {
            "test_suites": [s.value for s in self._configuration.test_suites],
            "intensity": self._configuration.intensity.value,
            "rate_limit": self._configuration.rate_limit,
            "timeout": self._configuration.timeout,
            "exclusions": self._configuration.exclusions,
            "custom_payloads": [
                {
                    "value": p.value,
                    "category": p.category.value,
                    "encoding": p.encoding,
                    "description": p.description
                }
                for p in self._configuration.custom_payloads
            ],
            "enable_destructive_tests": self._configuration.enable_destructive_tests,
            "enable_ai_analysis": self._configuration.enable_ai_analysis,
            "max_concurrent_requests": self._configuration.max_concurrent_requests,
            "user_agent": self._configuration.user_agent,
            "follow_redirects": self._configuration.follow_redirects,
            "max_redirects": self._configuration.max_redirects,
            "verify_ssl": self._configuration.verify_ssl,
            "proxy": self._configuration.proxy,
        }
