"""
Core components of the Web Penetration Testing Framework.
"""

from .authorization import AuthorizationManager, ValidationResult
from .configuration import ConfigurationManager
from .scan_orchestrator import ScanOrchestrator, ScanSession, ScanProgress
from .framework_core import FrameworkCore

__all__ = [
    'AuthorizationManager',
    'ValidationResult',
    'ConfigurationManager',
    'ScanOrchestrator',
    'ScanSession',
    'ScanProgress',
    'FrameworkCore',
]