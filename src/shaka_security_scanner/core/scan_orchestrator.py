"""
Scan orchestrator for coordinating scanner module execution.

This module provides the main orchestration logic for running security scans,
managing scanner lifecycle, and collecting results.
"""

import asyncio
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging

from ..models import Target, Configuration, Finding, TestSuite, IntensityLevel
from ..scanners.base import ScannerModule, ScanResult, ScannerRegistry
from ..core.authorization import AuthorizationManager, ValidationResult
from ..http import HTTPClient, RequestThrottler, AuditLogger
from ..ai import SecurityAnalysisEngine, EnhancedFinding


logger = logging.getLogger(__name__)


@dataclass
class ScanProgress:
    """Progress information for an ongoing scan."""
    
    total_scanners: int
    completed_scanners: int
    current_scanner: Optional[str] = None
    total_findings: int = 0
    elapsed_seconds: float = 0.0
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_scanners == 0:
            return 0.0
        return (self.completed_scanners / self.total_scanners) * 100.0
    
    @property
    def is_complete(self) -> bool:
        """Check if scan is complete."""
        return self.completed_scanners >= self.total_scanners


@dataclass
class ScanSession:
    """Complete scan session with all results."""
    
    target: Target
    configuration: Configuration
    start_time: str
    end_time: Optional[str] = None
    results: List[ScanResult] = field(default_factory=list)
    enhanced_findings: List[EnhancedFinding] = field(default_factory=list)
    ai_analysis_summary: Dict[str, Any] = field(default_factory=dict)
    total_findings: int = 0
    duration_seconds: float = 0.0
    status: str = "running"  # running, completed, failed, cancelled
    error: Optional[str] = None
    
    def add_result(self, result: ScanResult) -> None:
        """Add a scan result to the session."""
        self.results.append(result)
        self.total_findings += result.finding_count
    
    def get_all_findings(self) -> List[Finding]:
        """Get all findings from all scanners."""
        findings = []
        for result in self.results:
            findings.extend(result.findings)
        return findings
    
    def get_successful_results(self) -> List[ScanResult]:
        """Get only successful scan results."""
        return [r for r in self.results if r.success]
    
    def get_failed_results(self) -> List[ScanResult]:
        """Get only failed scan results."""
        return [r for r in self.results if not r.success]
    
    def complete(self) -> None:
        """Mark session as completed."""
        self.end_time = datetime.now(UTC).isoformat()
        self.status = "completed"
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_seconds = (end - start).total_seconds()
    
    def fail(self, error: str) -> None:
        """Mark session as failed."""
        self.end_time = datetime.now(UTC).isoformat()
        self.status = "failed"
        self.error = error


class ScanOrchestrator:
    """
    Orchestrates the execution of scanner modules.
    
    Manages scanner lifecycle, authorization, rate limiting, and result collection.
    
    Attributes:
        registry: Scanner registry
        auth_manager: Authorization manager
        http_client: HTTP client for scanners to use
        throttler: Request throttler
        audit_logger: Audit logger
    """
    
    def __init__(
        self,
        registry: Optional[ScannerRegistry] = None,
        auth_manager: Optional[AuthorizationManager] = None,
        http_client: Optional[HTTPClient] = None,
        throttler: Optional[RequestThrottler] = None,
        audit_logger: Optional[AuditLogger] = None,
        ai_engine: Optional[SecurityAnalysisEngine] = None
    ):
        """
        Initialize scan orchestrator.
        
        Args:
            registry: Scanner registry (creates new if None)
            auth_manager: Authorization manager (creates new if None)
            http_client: HTTP client (creates new if None)
            throttler: Request throttler (creates new if None)
            audit_logger: Audit logger (creates new if None)
            ai_engine: AI analysis engine (creates new if None)
        """
        self.registry = registry or ScannerRegistry()
        self.auth_manager = auth_manager or AuthorizationManager()
        self.http_client = http_client or HTTPClient()
        self.throttler = throttler or RequestThrottler()
        self.audit_logger = audit_logger or AuditLogger()
        self.ai_engine = ai_engine or SecurityAnalysisEngine()
        
        self._progress_callbacks: List[Callable[[ScanProgress], None]] = []
        self._current_session: Optional[ScanSession] = None
        self._cancelled = False
    
    def register_scanner(self, scanner: ScannerModule) -> None:
        """
        Register a scanner module.
        
        Args:
            scanner: Scanner to register
        """
        self.registry.register(scanner)
        logger.info(f"Registered scanner: {scanner.get_name()}")
    
    def register_progress_callback(
        self, 
        callback: Callable[[ScanProgress], None]
    ) -> None:
        """
        Register a callback for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, progress: ScanProgress) -> None:
        """Notify all registered progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def scan(
        self,
        target: Target,
        config: Configuration,
        auth_token: Optional[str] = None
    ) -> ScanSession:
        """
        Execute a complete scan against the target.
        
        Args:
            target: Target to scan
            config: Scan configuration
            auth_token: Authorization token (optional)
        
        Returns:
            ScanSession with all results
        
        Raises:
            PermissionError: If authorization fails
        """
        # Validate authorization if token provided
        if auth_token:
            validation = self.auth_manager.validate_token(
                auth_token,
                target.domain
            )
            if not validation.is_valid:
                raise PermissionError(
                    f"Authorization failed: {validation.error_message}"
                )
            logger.info(f"Authorization validated for {target.domain}")
        
        # Create scan session
        session = ScanSession(
            target=target,
            configuration=config,
            start_time=datetime.now(UTC).isoformat()
        )
        self._current_session = session
        self._cancelled = False
        
        try:
            # Get scanners to run
            scanners = self._get_scanners_to_run(config)
            
            if not scanners:
                logger.warning("No scanners enabled for this configuration")
                session.complete()
                return session
            
            logger.info(
                f"Starting scan with {len(scanners)} scanners "
                f"against {target.url}"
            )
            
            # Initialize progress
            progress = ScanProgress(
                total_scanners=len(scanners),
                completed_scanners=0
            )
            
            # Configure throttler
            self.throttler.set_rate_limit(config.rate_limit)
            
            # Run scanners
            start_time = datetime.now(UTC)
            
            for scanner in scanners:
                if self._cancelled:
                    logger.info("Scan cancelled by user")
                    session.status = "cancelled"
                    break
                
                # Update progress
                progress.current_scanner = scanner.get_name()
                self._notify_progress(progress)
                
                # Run scanner
                try:
                    logger.info(f"Running scanner: {scanner.get_name()}")
                    result = await scanner.scan(target, config)
                    session.add_result(result)
                    
                    logger.info(
                        f"Scanner {scanner.get_name()} completed: "
                        f"{result.finding_count} findings"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Scanner {scanner.get_name()} failed: {e}",
                        exc_info=True
                    )
                    # Create error result
                    error_result = ScanResult(
                        scanner_name=scanner.get_name(),
                        test_suite=scanner.get_test_suite(),
                        error=str(e)
                    )
                    session.add_result(error_result)
                
                # Update progress
                progress.completed_scanners += 1
                progress.total_findings = session.total_findings
                progress.elapsed_seconds = (
                    datetime.now(UTC) - start_time
                ).total_seconds()
                self._notify_progress(progress)
            
            # Complete session
            if session.status == "running":
                # Perform AI analysis if enabled
                if config.enable_ai_analysis and session.get_all_findings():
                    logger.info("Starting AI analysis of findings...")
                    try:
                        all_findings = session.get_all_findings()
                        session.enhanced_findings = await self.ai_engine.analyze_findings(
                            all_findings, target, config
                        )
                        session.ai_analysis_summary = self.ai_engine.get_analysis_summary(
                            session.enhanced_findings
                        )
                        logger.info(
                            f"AI analysis completed: {session.ai_analysis_summary.get('ai_analyzed', 0)} "
                            f"findings analyzed, {session.ai_analysis_summary.get('false_positives_detected', 0)} "
                            f"false positives detected"
                        )
                    except Exception as e:
                        logger.error(f"AI analysis failed: {e}")
                        # Continue without AI analysis
                
                session.complete()
            
            logger.info(
                f"Scan completed: {session.total_findings} total findings "
                f"in {session.duration_seconds:.2f} seconds"
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            session.fail(str(e))
            return session
        
        finally:
            self._current_session = None
    
    def _get_scanners_to_run(
        self, 
        config: Configuration
    ) -> List[ScannerModule]:
        """
        Get list of scanners that should run based on configuration.
        
        Args:
            config: Scan configuration
        
        Returns:
            List of scanners to run
        """
        scanners = []
        
        for scanner in self.registry.get_enabled():
            # Check if scanner should run
            if not scanner.should_run(config):
                continue
            
            # Check if scanner supports configured intensity
            if not scanner.supports_intensity(config.intensity):
                logger.warning(
                    f"Scanner {scanner.get_name()} does not support "
                    f"intensity {config.intensity.value}, skipping"
                )
                continue
            
            scanners.append(scanner)
        
        return scanners
    
    def cancel(self) -> None:
        """Cancel the current scan."""
        self._cancelled = True
        logger.info("Scan cancellation requested")
    
    def get_current_session(self) -> Optional[ScanSession]:
        """
        Get the current scan session.
        
        Returns:
            Current ScanSession or None
        """
        return self._current_session
    
    def get_scanner_count(self) -> int:
        """
        Get total number of registered scanners.
        
        Returns:
            Number of scanners
        """
        return self.registry.count()
    
    def get_enabled_scanner_count(self) -> int:
        """
        Get number of enabled scanners.
        
        Returns:
            Number of enabled scanners
        """
        return len(self.registry.get_enabled())
    
    async def close(self) -> None:
        """Close all resources."""
        await self.http_client.close()
        logger.info("Scan orchestrator closed")
