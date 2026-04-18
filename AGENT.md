# 🤖 Shaka Security Scanner - Agent Development Guide

**Comprehensive Development, Architecture, and Contribution Guide**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Core Components](#core-components)
4. [Scanner Development](#scanner-development)
5. [AI Integration](#ai-integration)
6. [Testing Strategy](#testing-strategy)
7. [Contribution Guidelines](#contribution-guidelines)
8. [Deployment Guide](#deployment-guide)

---

## 🏗️ Architecture Overview

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Shaka Security Scanner                    │
├─────────────────────────────────────────────────────────────┤
│  FrameworkCore (Main Entry Point)                          │
├─────────────────────────────────────────────────────────────┤
│  ScanOrchestrator (Coordination Layer)                     │
├─────────────────────────────────────────────────────────────┤
│  Scanner Modules (7 Specialized Scanners)                  │
│  ├── ReconnaissanceScanner    ├── AuthenticationScanner    │
│  ├── VulnerabilityScanner     ├── InputValidationScanner   │
│  ├── HeadersScanner           ├── APIScanner               │
│  └── SSLTLSScanner                                         │
├─────────────────────────────────────────────────────────────┤
│  AI Analysis Engine (AWS Bedrock Integration)              │
├─────────────────────────────────────────────────────────────┤
│  Core Services                                             │
│  ├── HTTPClient (Async)       ├── AuditLogger             │
│  ├── RequestThrottler         ├── AuthorizationManager    │
│  └── ConfigurationManager                                  │
├─────────────────────────────────────────────────────────────┤
│  Data Models (Type-Safe Structures)                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
```
Target Input → Configuration → Authorization → Scanner Selection → 
Scan Execution → AI Analysis → Enhanced Findings → Report Generation
```

### Key Design Principles
- **Modular Architecture** - Loosely coupled components
- **Async-First** - Non-blocking I/O throughout
- **Type Safety** - Comprehensive type hints dan validation
- **Error Resilience** - Graceful error handling dan recovery
- **Extensibility** - Plugin-based scanner architecture
- **Security-First** - Authorization, audit logging, rate limiting

---

## 🛠️ Development Setup

### Prerequisites
```bash
# System requirements
Python 3.8+
Git 2.20+
AWS CLI (optional, for AI features)

# Development tools
poetry          # Dependency management
pytest          # Testing framework
black           # Code formatting
flake8          # Linting
mypy            # Type checking
```

### Local Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/shaka-security-scanner.git
cd shaka-security-scanner

# Install dependencies with poetry
poetry install --dev

# Activate virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
python -m pytest tests/ -v
```

### Development Dependencies
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.5.0"
pre-commit = "^3.3.0"
sphinx = "^7.1.0"
```

### Environment Configuration
```bash
# .env file for development
AWS_ACCESS_KEY_ID=your_dev_key
AWS_SECRET_ACCESS_KEY=your_dev_secret
AWS_DEFAULT_REGION=us-east-1
SHAKA_LOG_LEVEL=DEBUG
SHAKA_TEST_TARGET=https://httpbin.org
```

---

## 🧩 Core Components

### 1. FrameworkCore
**Location:** `src/shaka_security_scanner/core/framework_core.py`

**Responsibilities:**
- Main entry point untuk framework
- Component initialization dan lifecycle management
- High-level API untuk scanning operations
- Resource cleanup dan error handling

**Key Methods:**
```python
class FrameworkCore:
    def __init__(self, config_file=None, log_level=INFO)
    async def scan(self, target, config, auth_token=None) -> ScanSession
    def register_scanner(self, scanner: ScannerModule)
    def get_info(self) -> dict
    async def close(self)
```

### 2. ScanOrchestrator
**Location:** `src/shaka_security_scanner/core/scan_orchestrator.py`

**Responsibilities:**
- Koordinasi execution scanner modules
- Progress tracking dan callbacks
- AI analysis integration
- Error handling per scanner

**Key Features:**
- Sequential scanner execution
- Rate limiting enforcement
- Progress notifications
- Scan cancellation support

### 3. Scanner Base Classes
**Location:** `src/shaka_security_scanner/scanners/base.py`

**Class Hierarchy:**
```python
ScannerModule (Abstract Base)
├── PassiveScanner (Read-only testing)
└── ActiveScanner (Payload-based testing)
```

**Required Methods:**
```python
def get_name(self) -> str
def get_description(self) -> str
def get_test_suite(self) -> TestSuite
async def scan(self, target, config) -> ScanResult
```

### 4. AI Analysis Engine
**Location:** `src/shaka_security_scanner/ai/analyzer.py`

**Components:**
- **BedrockAIClient** - AWS Bedrock integration
- **SecurityAnalysisEngine** - Main AI analysis logic
- **EnhancedFinding** - AI-enriched findings
- **AIAnalysisResult** - Structured AI output

---

## 🔍 Scanner Development

### Creating a New Scanner

#### 1. Define Scanner Class
```python
from shaka_security_scanner.scanners.base import ActiveScanner
from shaka_security_scanner.models import TestSuite, ScanResult

class CustomScanner(ActiveScanner):
    def get_name(self) -> str:
        return "custom"
    
    def get_description(self) -> str:
        return "Custom security scanner"
    
    def get_test_suite(self) -> TestSuite:
        return TestSuite.OTHER
    
    async def scan(self, target: Target, config: Configuration) -> ScanResult:
        start_time = time.time()
        
        try:
            # Your scanning logic here
            response = await self.http_client.get(target.url)
            
            # Analyze response
            if self._detect_vulnerability(response):
                self.create_finding(
                    title="Custom Vulnerability",
                    description="Detailed description",
                    severity=Severity.HIGH,
                    category=VulnerabilityCategory.OTHER,
                    affected_url=target.url,
                    confidence=0.8,
                    proof_of_concept="Evidence here",
                    remediation="Fix instructions"
                )
            
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                findings=self.get_findings(),
                tests_performed=1,
                duration_seconds=time.time() - start_time
            )
            
        except Exception as e:
            return ScanResult(
                scanner_name=self.get_name(),
                test_suite=self.get_test_suite(),
                error=str(e),
                duration_seconds=time.time() - start_time
            )
```

#### 2. Add Comprehensive Tests
```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestCustomScanner:
    def test_scanner_initialization(self):
        scanner = CustomScanner()
        assert scanner.get_name() == "custom"
        assert scanner.get_test_suite() == TestSuite.OTHER
    
    @pytest.mark.asyncio
    async def test_scan_success(self):
        scanner = CustomScanner()
        scanner.http_client = Mock()
        scanner.http_client.get = AsyncMock(return_value=Mock(
            status_code=200,
            headers={},
            body="test response"
        ))
        
        target = Target("https://example.com", "example.com", "https")
        config = Configuration([TestSuite.OTHER])
        
        result = await scanner.scan(target, config)
        
        assert result.success
        assert result.scanner_name == "custom"
```

#### 3. Register Scanner
```python
# In framework_core.py _register_default_scanners method
def _register_default_scanners(self):
    scanners = [
        # ... existing scanners
        CustomScanner(),
    ]
    
    for scanner in scanners:
        self.register_scanner(scanner)
```

### Scanner Development Best Practices

#### Error Handling
```python
async def scan(self, target, config):
    try:
        # Scanning logic
        pass
    except httpx.TimeoutException:
        logger.warning(f"Timeout scanning {target.url}")
        return self._create_error_result("Timeout")
    except httpx.NetworkError as e:
        logger.error(f"Network error: {e}")
        return self._create_error_result(f"Network error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return self._create_error_result(f"Unexpected error: {e}")
```

#### Rate Limiting Compliance
```python
async def scan(self, target, config):
    # Respect rate limiting
    await self.throttler.acquire()
    
    # Make request
    response = await self.http_client.get(target.url)
    
    # Log for audit
    await self.audit_logger.log_request(request, response)
```

#### Finding Creation
```python
def create_finding(
    self,
    title: str,
    description: str,
    severity: Severity,
    category: VulnerabilityCategory,
    affected_url: str,
    affected_parameter: Optional[str] = None,
    proof_of_concept: str = "",
    remediation: str = "",
    confidence: float = 1.0,
    cvss_score: Optional[float] = None,
    cwe_id: Optional[str] = None,
    references: List[str] = None
):
    finding = Finding(
        id=f"{self.get_name()}-{len(self._findings)}",
        title=title,
        description=description,
        severity=severity,
        category=category,
        affected_url=affected_url,
        affected_parameter=affected_parameter,
        proof_of_concept=proof_of_concept,
        remediation=remediation,
        confidence=confidence,
        cvss_score=cvss_score,
        cwe_id=cwe_id,
        references=references or []
    )
    
    self._findings.append(finding)
    logger.info(f"Created finding: {title} ({severity})")
```

---

## 🤖 AI Integration

### AWS Bedrock Setup

#### 1. AWS Configuration
```bash
# Install boto3
pip install boto3

# Configure credentials
aws configure
# atau
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

#### 2. Bedrock Model Access
```bash
# Request model access in AWS Console
# Navigate to: AWS Bedrock > Model Access
# Request access to: Claude 3 Sonnet
```

#### 3. Custom AI Analysis
```python
from shaka_security_scanner.ai import SecurityAnalysisEngine, BedrockAIClient

# Custom AI client
custom_client = BedrockAIClient(
    region_name="us-west-2",
    model_id="anthropic.claude-3-haiku-20240307-v1:0"
)

# Custom analysis engine
ai_engine = SecurityAnalysisEngine(
    bedrock_client=custom_client,
    enable_ai=True
)

# Use in framework
framework = FrameworkCore()
framework.ai_engine = ai_engine
```

### AI Analysis Customization

#### Custom Analysis Prompts
```python
class CustomBedrockClient(BedrockAIClient):
    def _build_analysis_prompt(self, finding, context):
        # Custom prompt for specific use case
        return f"""
        Analyze this security finding for a {context.get('industry', 'general')} application:
        
        Finding: {finding.title}
        Description: {finding.description}
        
        Provide analysis focusing on:
        1. Industry-specific risks
        2. Compliance implications
        3. Business impact assessment
        
        Response format: JSON
        """
```

#### Custom Analysis Metrics
```python
class CustomAnalysisEngine(SecurityAnalysisEngine):
    def _apply_ai_insights(self, enhanced):
        # Custom risk scoring logic
        ai = enhanced.ai_analysis
        if not ai:
            return enhanced
        
        # Industry-specific risk calculation
        industry_factor = self._get_industry_factor()
        compliance_factor = self._get_compliance_factor()
        
        enhanced.risk_score = (
            ai.remediation_priority * industry_factor * compliance_factor
        ) / 10.0
        
        return enhanced
```

---

## 🧪 Testing Strategy

### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_scanners/      # Scanner-specific tests
│   ├── test_ai/            # AI integration tests
│   ├── test_core/          # Core component tests
│   └── test_models.py      # Data model tests
├── integration/            # Integration tests
│   ├── test_full_scan.py   # End-to-end scan tests
│   └── test_ai_flow.py     # AI workflow tests
└── fixtures/               # Test data dan mocks
    ├── responses/          # Mock HTTP responses
    └── configs/            # Test configurations
```

### Testing Guidelines

#### Unit Tests
```python
# Test scanner functionality
@pytest.mark.asyncio
async def test_scanner_detects_vulnerability():
    scanner = VulnerabilityScanner()
    scanner.http_client = create_mock_client(
        response_body="<script>alert('xss')</script>"
    )
    
    target = create_test_target()
    config = create_test_config()
    
    result = await scanner.scan(target, config)
    
    assert result.success
    assert len(result.findings) > 0
    assert any("XSS" in f.title for f in result.findings)
```

#### Integration Tests
```python
# Test full scan workflow
@pytest.mark.asyncio
async def test_full_scan_workflow():
    framework = FrameworkCore()
    target = Target("https://httpbin.org", "httpbin.org", "https")
    config = Configuration([TestSuite.HEADERS])
    
    session = await framework.scan(target, config)
    
    assert session.status == "completed"
    assert len(session.get_all_findings()) > 0
```

#### AI Tests
```python
# Test AI analysis
@pytest.mark.asyncio
async def test_ai_analysis():
    mock_client = Mock()
    mock_client.analyze_finding = AsyncMock(return_value=AIAnalysisResult(...))
    
    engine = SecurityAnalysisEngine(bedrock_client=mock_client)
    findings = [create_test_finding()]
    
    enhanced = await engine.analyze_findings(findings, target, config)
    
    assert len(enhanced) == 1
    assert enhanced[0].ai_analysis is not None
```

### Test Data Management
```python
# fixtures/test_data.py
def create_test_target():
    return Target(
        url="https://test.example.com",
        base_domain="example.com",
        scheme="https"
    )

def create_test_config():
    return Configuration(
        test_suites=[TestSuite.HEADERS],
        intensity=IntensityLevel.PASSIVE,
        rate_limit=5
    )

def create_mock_response(status=200, headers=None, body=""):
    return Mock(
        status_code=status,
        headers=headers or {},
        body=body
    )
```

### Performance Testing
```python
# Test performance benchmarks
@pytest.mark.performance
async def test_scan_performance():
    framework = FrameworkCore()
    target = create_test_target()
    config = create_test_config()
    
    start_time = time.time()
    session = await framework.scan(target, config)
    duration = time.time() - start_time
    
    # Performance assertions
    assert duration < 30.0  # Should complete within 30 seconds
    assert session.total_requests < 100  # Should not exceed request limit
```

---

## 🤝 Contribution Guidelines

### Code Style

#### Python Style Guide
```python
# Follow PEP 8
# Use black for formatting
# Use type hints throughout

from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """Example class with proper documentation."""
    
    def __init__(self, param: str) -> None:
        """Initialize with parameter."""
        self.param = param
    
    async def async_method(
        self, 
        target: Target, 
        config: Configuration
    ) -> Optional[ScanResult]:
        """Async method with proper typing."""
        try:
            # Implementation
            return result
        except Exception as e:
            logger.error(f"Error in async_method: {e}")
            return None
```

#### Documentation Standards
```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    param3: List[str] = None
) -> Dict[str, Any]:
    """
    Complex function with comprehensive documentation.
    
    Args:
        param1: Description of param1
        param2: Optional parameter with default None
        param3: List parameter with default empty list
    
    Returns:
        Dictionary containing results with keys:
        - 'status': Operation status
        - 'data': Result data
        - 'errors': List of errors if any
    
    Raises:
        ValueError: If param1 is empty
        RuntimeError: If operation fails
    
    Example:
        >>> result = complex_function("test", param2=42)
        >>> print(result['status'])
        'success'
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    # Implementation
    return {"status": "success", "data": {}, "errors": []}
```

### Git Workflow

#### Branch Strategy
```bash
# Feature development
git checkout -b feature/new-scanner
git checkout -b feature/ai-enhancement
git checkout -b bugfix/scanner-timeout

# Release preparation
git checkout -b release/v1.2.0

# Hotfixes
git checkout -b hotfix/critical-security-fix
```

#### Commit Messages
```bash
# Format: type(scope): description
feat(scanners): add new API security scanner
fix(ai): resolve Bedrock authentication issue
docs(readme): update installation instructions
test(scanners): add comprehensive XSS tests
refactor(core): improve error handling
perf(http): optimize connection pooling
```

#### Pull Request Process
1. **Create Feature Branch** dari main
2. **Implement Changes** dengan tests
3. **Run Full Test Suite** - semua tests harus pass
4. **Update Documentation** jika diperlukan
5. **Create Pull Request** dengan description lengkap
6. **Code Review** - address feedback
7. **Merge** setelah approval

### Code Review Checklist

#### Functionality
- [ ] Code implements requirements correctly
- [ ] Error handling is comprehensive
- [ ] Performance is acceptable
- [ ] Security considerations addressed

#### Code Quality
- [ ] Follows PEP 8 style guide
- [ ] Type hints are comprehensive
- [ ] Documentation is complete
- [ ] No code duplication

#### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests pass
- [ ] Edge cases are tested
- [ ] Performance tests included if relevant

#### Security
- [ ] Input validation implemented
- [ ] No hardcoded secrets
- [ ] Proper error messages (no info disclosure)
- [ ] Rate limiting respected

---

## 🚀 Deployment Guide

### Production Deployment

#### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 scanner
USER scanner

# Run application
CMD ["python", "-m", "shaka_security_scanner"]
```

#### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shaka-security-scanner
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shaka-scanner
  template:
    metadata:
      labels:
        app: shaka-scanner
    spec:
      containers:
      - name: scanner
        image: shaka-security-scanner:latest
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### AWS Lambda Deployment
```python
# lambda_handler.py
import json
import asyncio
from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite

def lambda_handler(event, context):
    """AWS Lambda handler for security scanning."""
    
    async def run_scan():
        framework = FrameworkCore()
        
        target = Target(
            url=event['target_url'],
            base_domain=event['domain'],
            scheme=event.get('scheme', 'https')
        )
        
        config = Configuration(
            test_suites=[TestSuite(suite) for suite in event['test_suites']],
            enable_ai_analysis=event.get('enable_ai', True)
        )
        
        session = await framework.scan(target, config)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'findings_count': len(session.get_all_findings()),
                'status': session.status,
                'duration': session.duration_seconds
            })
        }
    
    return asyncio.run(run_scan())
```

### Monitoring & Observability

#### Logging Configuration
```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(level=logging.INFO):
    """Setup structured logging."""
    
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
```

#### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
SCANS_TOTAL = Counter('shaka_scans_total', 'Total scans performed')
SCAN_DURATION = Histogram('shaka_scan_duration_seconds', 'Scan duration')
FINDINGS_TOTAL = Counter('shaka_findings_total', 'Total findings', ['severity'])
AI_ANALYSIS_TOTAL = Counter('shaka_ai_analysis_total', 'AI analyses performed')

class MetricsCollector:
    """Collect and export metrics."""
    
    def record_scan_start(self):
        SCANS_TOTAL.inc()
    
    def record_scan_duration(self, duration):
        SCAN_DURATION.observe(duration)
    
    def record_finding(self, severity):
        FINDINGS_TOTAL.labels(severity=severity).inc()
    
    def record_ai_analysis(self):
        AI_ANALYSIS_TOTAL.inc()
```

### Security Considerations

#### Secrets Management
```python
# secrets.py
import os
from typing import Optional

class SecretsManager:
    """Manage sensitive configuration."""
    
    @staticmethod
    def get_aws_credentials() -> tuple[Optional[str], Optional[str]]:
        """Get AWS credentials from environment."""
        return (
            os.getenv('AWS_ACCESS_KEY_ID'),
            os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    
    @staticmethod
    def get_signing_key() -> str:
        """Get HMAC signing key."""
        key = os.getenv('SHAKA_SIGNING_KEY')
        if not key:
            raise ValueError("SHAKA_SIGNING_KEY environment variable required")
        return key
```

#### Network Security
```python
# security.py
import ipaddress
from typing import List

class NetworkSecurity:
    """Network security utilities."""
    
    PRIVATE_NETWORKS = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),
    ]
    
    @classmethod
    def is_private_ip(cls, ip: str) -> bool:
        """Check if IP is in private range."""
        try:
            addr = ipaddress.ip_address(ip)
            return any(addr in network for network in cls.PRIVATE_NETWORKS)
        except ValueError:
            return False
    
    @classmethod
    def validate_target_url(cls, url: str) -> bool:
        """Validate target URL for security."""
        # Add validation logic
        return True
```

---

## 📚 Additional Resources

### Documentation
- **[API Reference](docs/api/)** - Complete API documentation
- **[Scanner Guide](docs/scanners/)** - Detailed scanner documentation
- **[AI Integration](docs/ai/)** - AI features dan configuration
- **[Deployment Guide](docs/deployment/)** - Production deployment

### Examples
- **[Basic Usage](examples/basic/)** - Simple scanning examples
- **[Advanced Usage](examples/advanced/)** - Complex scenarios
- **[Custom Scanners](examples/scanners/)** - Scanner development examples
- **[AI Integration](examples/ai/)** - AI usage examples

### Tools & Utilities
- **[Development Scripts](scripts/)** - Development automation
- **[Configuration Templates](config/templates/)** - Configuration examples
- **[Docker Compose](docker-compose.yml)** - Local development setup

---

## 🎯 Development Roadmap

### Phase 1: Core Enhancement (Q2 2026)
- [ ] Web UI Dashboard
- [ ] Advanced Reporting Engine
- [ ] Plugin System Architecture
- [ ] Performance Optimizations

### Phase 2: AI Enhancement (Q3 2026)
- [ ] Multiple AI Provider Support
- [ ] Custom Model Training
- [ ] Advanced False Positive Detection
- [ ] Automated Remediation Suggestions

### Phase 3: Enterprise Features (Q4 2026)
- [ ] Multi-tenant Architecture
- [ ] RBAC Implementation
- [ ] Compliance Reporting
- [ ] Enterprise Integrations

---

<div align="center">

**🛡️ Build Secure, Test Smart, Deploy Confidently 🛡️**

Happy Coding! 🚀

</div>