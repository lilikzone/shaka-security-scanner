"""
Framework core - main entry point for the penetration testing framework.

This module provides the high-level API for initializing and using the framework.
"""

import logging
from typing import Optional, List, Callable
from pathlib import Path

from ..models import Target, Configuration
from ..core.authorization import AuthorizationManager
from ..core.configuration import ConfigurationManager
from ..core.scan_orchestrator import ScanOrchestrator, ScanSession, ScanProgress
from ..scanners.base import ScannerModule, ScannerRegistry
from ..http import HTTPClient, RequestThrottler, AuditLogger
from ..ai import SecurityAnalysisEngine


logger = logging.getLogger(__name__)


class FrameworkCore:
    """
    Main framework core class.
    
    Provides high-level API for initializing and using the penetration testing
    framework. Manages all core components and their lifecycle.
    
    Example:
        ```python
        # Initialize framework
        framework = FrameworkCore()
        
        # Load configuration
        framework.load_config("config/scan-config.yaml")
        
        # Register scanners
        framework.register_scanner(ReconnaissanceScanner())
        framework.register_scanner(VulnerabilityScanner())
        
        # Run scan
        target = Target(url="https://example.com")
        session = await framework.scan(target, auth_token="...")
        
        # Get results
        findings = session.get_all_findings()
        ```
    
    Attributes:
        config_manager: Configuration manager
        auth_manager: Authorization manager
        orchestrator: Scan orchestrator
        http_client: HTTP client
        throttler: Request throttler
        audit_logger: Audit logger
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        log_level: int = logging.INFO,
        log_dir: str = "logs"
    ):
        """
        Initialize framework core.
        
        Args:
            config_file: Path to configuration file (optional)
            log_level: Logging level (default: INFO)
            log_dir: Directory for log files (default: "logs")
        """
        # Setup logging
        self._setup_logging(log_level)
        
        # Initialize core components
        self.config_manager = ConfigurationManager()
        self.auth_manager = AuthorizationManager()
        self.audit_logger = AuditLogger(log_dir=log_dir, log_level=log_level)
        self.http_client = HTTPClient()
        self.throttler = RequestThrottler()
        
        # Initialize scanner registry and orchestrator
        self.registry = ScannerRegistry()
        self.ai_engine = SecurityAnalysisEngine(enable_ai=True)
        self.orchestrator = ScanOrchestrator(
            registry=self.registry,
            auth_manager=self.auth_manager,
            http_client=self.http_client,
            throttler=self.throttler,
            audit_logger=self.audit_logger,
            ai_engine=self.ai_engine
        )
        
        # Auto-register all available scanners
        self._register_default_scanners()
        
        # Load configuration if provided
        if config_file:
            self.load_config(config_file)
        
        logger.info("Framework core initialized")
    
    def _register_default_scanners(self) -> None:
        """Register all default scanner modules."""
        from ..scanners import (
            ReconnaissanceScanner, VulnerabilityScanner, AdvancedVulnerabilityScanner, HeadersScanner,
            SSLTLSScanner, AuthenticationScanner, InputValidationScanner,
            APIScanner
        )
        
        # Register all scanners
        scanners = [
            ReconnaissanceScanner(),
            VulnerabilityScanner(),
            AdvancedVulnerabilityScanner(self.http_client),
            HeadersScanner(),
            SSLTLSScanner(),
            AuthenticationScanner(),
            InputValidationScanner(),
            APIScanner()
        ]
        
        for scanner in scanners:
            self.register_scanner(scanner)
        
        logger.info(f"Auto-registered {len(scanners)} default scanners")
    
    def _setup_logging(self, log_level: int) -> None:
        """
        Setup logging configuration.
        
        Args:
            log_level: Logging level
        """
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def load_config(self, config_file: str) -> Configuration:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
        
        Returns:
            Loaded Configuration object
        
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config file is invalid
        """
        config = self.config_manager.load_config(config_file)
        logger.info(f"Configuration loaded from {config_file}")
        
        # Configure throttler with rate limit from config
        self.throttler.set_rate_limit(config.rate_limit)
        
        return config
    
    def get_config(self) -> Configuration:
        """
        Get current configuration.
        
        Returns:
            Current Configuration object
        
        Raises:
            RuntimeError: If no configuration loaded
        """
        return self.config_manager.get_configuration()
    
    def register_scanner(self, scanner: ScannerModule) -> None:
        """
        Register a scanner module.
        
        Args:
            scanner: Scanner module to register
        """
        self.orchestrator.register_scanner(scanner)
        logger.info(f"Registered scanner: {scanner.get_name()}")
    
    def register_scanners(self, scanners: List[ScannerModule]) -> None:
        """
        Register multiple scanner modules.
        
        Args:
            scanners: List of scanner modules to register
        """
        for scanner in scanners:
            self.register_scanner(scanner)
    
    def get_scanner_count(self) -> int:
        """
        Get total number of registered scanners.
        
        Returns:
            Number of registered scanners
        """
        return self.orchestrator.get_scanner_count()
    
    def get_enabled_scanner_count(self) -> int:
        """
        Get number of enabled scanners.
        
        Returns:
            Number of enabled scanners
        """
        return self.orchestrator.get_enabled_scanner_count()
    
    def register_progress_callback(
        self,
        callback: Callable[[ScanProgress], None]
    ) -> None:
        """
        Register a callback for scan progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.orchestrator.register_progress_callback(callback)
    
    async def scan(
        self,
        target: Target,
        config: Optional[Configuration] = None,
        auth_token: Optional[str] = None
    ) -> ScanSession:
        """
        Execute a scan against the target.
        
        Args:
            target: Target to scan
            config: Scan configuration (uses loaded config if None)
            auth_token: Authorization token (optional)
        
        Returns:
            ScanSession with all results
        
        Raises:
            RuntimeError: If no configuration available
            PermissionError: If authorization fails
        """
        # Use provided config or get loaded config
        if config is None:
            config = self.get_config()
        
        logger.info(f"Starting scan of {target.url}")
        
        # Display legal disclaimer if auth token provided
        if auth_token:
            self.auth_manager.display_disclaimer()
        
        # Execute scan
        session = await self.orchestrator.scan(target, config, auth_token)
        
        logger.info(
            f"Scan completed: {session.total_findings} findings, "
            f"status: {session.status}"
        )
        
        return session
    
    def cancel_scan(self) -> None:
        """Cancel the current scan."""
        self.orchestrator.cancel()
        logger.info("Scan cancellation requested")
    
    def get_current_session(self) -> Optional[ScanSession]:
        """
        Get the current scan session.
        
        Returns:
            Current ScanSession or None
        """
        return self.orchestrator.get_current_session()
    
    async def close(self) -> None:
        """
        Close framework and cleanup resources.
        
        Should be called when done using the framework.
        """
        await self.orchestrator.close()
        logger.info("Framework core closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def get_version(self) -> str:
        """
        Get framework version.
        
        Returns:
            Version string
        """
        return "1.0.0"
    
    def get_info(self) -> dict:
        """
        Get framework information.
        
        Returns:
            Dictionary with framework info
        """
        return {
            "version": self.get_version(),
            "scanners_registered": self.get_scanner_count(),
            "scanners_enabled": self.get_enabled_scanner_count(),
            "config_loaded": self.config_manager._configuration is not None,
            "ai_enabled": self.ai_engine.is_ai_enabled(),
            "ai_model": self.ai_engine.bedrock_client.get_model_info() if self.ai_engine.bedrock_client else None
        }
