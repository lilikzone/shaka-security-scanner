"""
Shaka Security Scanner - A comprehensive security testing tool for web applications.

This package provides modular security testing capabilities including reconnaissance,
vulnerability detection, security analysis, and professional reporting with AWS Bedrock AI integration.
"""

__version__ = "0.1.0"
__author__ = "Shaka Security Scanner Team"
__license__ = "MIT"

# Core framework components
from .core.framework_core import FrameworkCore
from .core.authorization import AuthorizationManager
from .core.configuration import ConfigurationManager
from .core.scan_orchestrator import ScanOrchestrator

# AI components
from .ai import SecurityAnalysisEngine, BedrockAIClient, EnhancedFinding

# Data models
from .models import (
    Target, Configuration, Finding, AuthorizationToken,
    ScanSession, HTTPRequest, HTTPResponse, Report,
    Technology, InputField, Payload,
    # Enums
    ScanStatus, Severity, VulnerabilityCategory, IntensityLevel,
    TestSuite, PayloadCategory, ReportFormat
)

# Scanner modules
from .scanners import (
    ReconnaissanceScanner, VulnerabilityScanner, AdvancedVulnerabilityScanner, HeadersScanner,
    SSLTLSScanner, AuthenticationScanner, InputValidationScanner,
    APIScanner
)

# HTTP components
from .http import HTTPClient, RequestThrottler, AuditLogger

__all__ = [
    # Core
    "FrameworkCore",
    "AuthorizationManager", 
    "ConfigurationManager",
    "ScanOrchestrator",
    
    # AI Components
    "SecurityAnalysisEngine",
    "BedrockAIClient",
    "EnhancedFinding",
    
    # Models
    "Target",
    "Configuration", 
    "Finding",
    "AuthorizationToken",
    "ScanSession",
    "HTTPRequest",
    "HTTPResponse", 
    "Report",
    "Technology",
    "InputField",
    "Payload",
    
    # Enums
    "ScanStatus",
    "Severity",
    "VulnerabilityCategory", 
    "IntensityLevel",
    "TestSuite",
    "PayloadCategory",
    "ReportFormat",
    
    # Scanners
    "ReconnaissanceScanner",
    "VulnerabilityScanner",
    "AdvancedVulnerabilityScanner",
    "HeadersScanner", 
    "SSLTLSScanner",
    "AuthenticationScanner",
    "InputValidationScanner",
    "APIScanner",
    
    # HTTP
    "HTTPClient",
    "RequestThrottler",
    "AuditLogger"
]