# 🚀 Web Penetration Testing Framework - Usage Guide

## 📋 Daftar Isi
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Usage](#basic-usage)
4. [Advanced Configuration](#advanced-configuration)
5. [Scanner Modules](#scanner-modules)
6. [Authorization](#authorization)
7. [Examples](#examples)
8. [API Reference](#api-reference)

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip atau poetry

### Install Dependencies
```bash
cd web-penetration-testing-framework
pip install -e .
```

Atau dengan poetry:
```bash
poetry install
```

## ⚡ Quick Start

### 1. Basic Scan
```python
import asyncio
from web_pen_test_framework import FrameworkCore
from web_pen_test_framework.models import Target, Configuration, TestSuite, IntensityLevel

async def basic_scan():
    # Initialize framework
    framework = FrameworkCore()
    
    # Create target
    target = Target(
        url="https://example.com",
        base_domain="example.com",
        scheme="https"
    )
    
    # Create configuration
    config = Configuration(
        test_suites=[TestSuite.RECONNAISSANCE, TestSuite.HEADERS],
        intensity=IntensityLevel.PASSIVE
    )
    
    # Run scan
    session = await framework.scan(target, config)
    
    # Print results
    print(f"Scan completed with {len(session.findings)} findings")
    for finding in session.findings:
        print(f"- {finding.severity.upper()}: {finding.title}")

# Run the scan
asyncio.run(basic_scan())
```

### 2. Command Line Usage
```bash
# Create a simple CLI script
python -c "
import asyncio
from web_pen_test_framework import *

async def scan():
    framework = FrameworkCore()
    target = Target('https://httpbin.org', 'httpbin.org', 'https')
    config = Configuration([TestSuite.HEADERS], IntensityLevel.PASSIVE)
    session = await framework.scan(target, config)
    print(f'Found {len(session.findings)} issues')

asyncio.run(scan())
"
```

## 📖 Basic Usage

### Target Definition
```python
from web_pen_test_framework.models import Target

# Basic target
target = Target(
    url="https://api.example.com",
    base_domain="example.com", 
    scheme="https"
)

# Target with discovered endpoints
target = Target(
    url="https://example.com",
    base_domain="example.com",
    scheme="https",
    discovered_endpoints=[
        "https://example.com/api",
        "https://example.com/admin"
    ]
)
```

### Configuration Options
```python
from web_pen_test_framework.models import Configuration, TestSuite, IntensityLevel

# Passive scan (safe)
config = Configuration(
    test_suites=[TestSuite.RECONNAISSANCE, TestSuite.HEADERS, TestSuite.SSL_TLS],
    intensity=IntensityLevel.PASSIVE,
    rate_limit=5,  # 5 requests per second
    timeout=30
)

# Active scan (more thorough)
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY, TestSuite.AUTHENTICATION],
    intensity=IntensityLevel.ACTIVE,
    rate_limit=10,
    timeout=60,
    enable_destructive_tests=False  # Keep safe
)

# Aggressive scan (comprehensive)
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY, TestSuite.INPUT_VALIDATION, TestSuite.API],
    intensity=IntensityLevel.AGGRESSIVE,
    rate_limit=20,
    max_concurrent_requests=15,
    enable_destructive_tests=True  # ⚠️ Use with caution
)
```

## 🔧 Advanced Configuration

### Custom Payloads
```python
from web_pen_test_framework.models import Payload, PayloadCategory

custom_payloads = [
    Payload(
        value="<script>alert('custom')</script>",
        category=PayloadCategory.XSS,
        description="Custom XSS payload"
    ),
    Payload(
        value="'; DROP TABLE users; --",
        category=PayloadCategory.SQL_INJECTION,
        description="Custom SQL injection"
    )
]

config = Configuration(
    test_suites=[TestSuite.VULNERABILITY],
    intensity=IntensityLevel.ACTIVE,
    custom_payloads=custom_payloads
)
```

### Exclusions and Filtering
```python
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY],
    intensity=IntensityLevel.ACTIVE,
    exclusions=[
        "*/admin/*",      # Skip admin paths
        "*/logout",       # Skip logout
        "*.pdf",          # Skip PDF files
    ],
    proxy="http://127.0.0.1:8080",  # Use Burp Suite proxy
    user_agent="Custom-Scanner/1.0"
)
```

## 🔍 Scanner Modules

### 1. Reconnaissance Scanner (Passive)
```python
from web_pen_test_framework.scanners import ReconnaissanceScanner

scanner = ReconnaissanceScanner()
result = await scanner.scan(target, config)

# Detects:
# - Technologies (Django, React, WordPress, etc.)
# - Endpoints and forms
# - Email addresses and phone numbers
# - Sensitive comments
# - Server information disclosure
```

### 2. Vulnerability Scanner (Active)
```python
from web_pen_test_framework.scanners import VulnerabilityScanner

scanner = VulnerabilityScanner()
result = await scanner.scan(target, config)

# Tests for:
# - SQL Injection (error-based, boolean-based, time-based)
# - Cross-Site Scripting (XSS)
# - Cross-Site Request Forgery (CSRF)
# - Query parameter vulnerabilities
```

### 3. Headers Scanner (Passive)
```python
from web_pen_test_framework.scanners import HeadersScanner

scanner = HeadersScanner()
result = await scanner.scan(target, config)

# Analyzes:
# - Missing security headers (HSTS, CSP, X-Frame-Options)
# - Information disclosure headers
# - Weak header configurations
# - Deprecated headers
```

### 4. SSL/TLS Scanner (Passive)
```python
from web_pen_test_framework.scanners import SSLTLSScanner

scanner = SSLTLSScanner()
result = await scanner.scan(target, config)

# Checks:
# - Certificate validity and expiration
# - Weak protocols (SSLv3, TLSv1.0, TLSv1.1)
# - Weak cipher suites
# - Self-signed certificates
```

### 5. Authentication Scanner (Active)
```python
from web_pen_test_framework.scanners import AuthenticationScanner

scanner = AuthenticationScanner()
result = await scanner.scan(target, config)

# Tests:
# - Default credentials (admin/admin, etc.)
# - Brute force protection
# - Username enumeration
# - Session cookie security
```

### 6. Input Validation Scanner (Active)
```python
from web_pen_test_framework.scanners import InputValidationScanner

scanner = InputValidationScanner()
result = await scanner.scan(target, config)

# Tests:
# - Command injection
# - Path traversal
# - Template injection
# - File upload vulnerabilities
```

### 7. API Scanner (Active)
```python
from web_pen_test_framework.scanners import APIScanner

scanner = APIScanner()
result = await scanner.scan(target, config)

# Tests:
# - Missing authentication
# - Broken authorization (BOLA/IDOR)
# - Excessive data exposure
# - Rate limiting
```

## 🔐 Authorization

### Generate Authorization Token
```python
from web_pen_test_framework.core import AuthorizationManager
from datetime import datetime, timedelta

auth_manager = AuthorizationManager()

# Generate token for testing
token = auth_manager.generate_token(
    target_domain="example.com",
    expires_in_days=30,
    scope=["vulnerability", "authentication"]
)

print(f"Authorization token: {token}")
```

### Use Authorization Token
```python
from web_pen_test_framework.models import AuthorizationToken

# Create token object
auth_token = AuthorizationToken(
    token="your-generated-token",
    target_domain="example.com",
    issued_at=datetime.now(),
    expires_at=datetime.now() + timedelta(days=30),
    scope=["vulnerability", "authentication"]
)

# Validate before scanning
auth_manager = AuthorizationManager()
validation_result = auth_manager.validate_token(auth_token, "example.com")

if validation_result.is_valid:
    print("✅ Authorization valid - proceeding with scan")
    # Run your scan here
else:
    print(f"❌ Authorization failed: {validation_result.error_message}")
```

## 🤖 AI-Powered Analysis

Framework ini dilengkapi dengan integrasi **AWS Bedrock AI** untuk analisis keamanan yang lebih canggih:

### Fitur AI Analysis:
- **Enhanced Vulnerability Assessment** - Analisis mendalam dengan AI
- **False Positive Detection** - Deteksi otomatis false positive
- **Risk Scoring** - Penilaian risiko berbasis AI
- **Business Impact Analysis** - Analisis dampak bisnis
- **Remediation Prioritization** - Prioritas perbaikan cerdas

### Setup AWS Bedrock:
```bash
# Install boto3
pip install boto3

# Configure AWS credentials
aws configure
# atau set environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret
```

### Menggunakan AI Analysis:
```python
from web_pen_test_framework import FrameworkCore, SecurityAnalysisEngine

# Framework dengan AI enabled
framework = FrameworkCore()

config = Configuration(
    test_suites=[TestSuite.HEADERS],
    enable_ai_analysis=True  # Enable AI analysis
)

session = await framework.scan(target, config)

# Akses enhanced findings
if hasattr(session, 'enhanced_findings'):
    for enhanced in session.enhanced_findings:
        print(f"Risk Score: {enhanced.risk_score}/10")
        print(f"False Positive: {enhanced.is_false_positive}")
        if enhanced.ai_analysis:
            print(f"Business Impact: {enhanced.ai_analysis.business_impact}")
```

## 📝 Examples

### Example 1: AI-Enhanced Security Assessment
```python
import asyncio
from web_pen_test_framework import FrameworkCore, SecurityAnalysisEngine
from web_pen_test_framework.models import *

async def ai_enhanced_assessment():
    framework = FrameworkCore()
    
    target = Target(
        url="https://example.com",
        base_domain="example.com",
        scheme="https"
    )
    
    # Configuration with AI enabled
    config = Configuration(
        test_suites=[TestSuite.HEADERS, TestSuite.VULNERABILITY],
        intensity=IntensityLevel.ACTIVE,
        enable_ai_analysis=True,  # Enable AI analysis
        rate_limit=5
    )
    
    print("🤖 Running AI-Enhanced Security Scan...")
    session = await framework.scan(target, config)
    
    # Regular findings
    print(f"Raw Findings: {len(session.get_all_findings())}")
    
    # AI-enhanced findings
    if hasattr(session, 'enhanced_findings') and session.enhanced_findings:
        print(f"AI Enhanced Findings: {len(session.enhanced_findings)}")
        
        # AI analysis summary
        if hasattr(session, 'ai_analysis_summary'):
            summary = session.ai_analysis_summary
            print(f"AI Analysis Rate: {summary.get('ai_analysis_rate', 0):.1%}")
            print(f"False Positives Detected: {summary.get('false_positives_detected', 0)}")
            print(f"Average Risk Score: {summary.get('average_risk_score', 0):.1f}/10")
        
        # Show enhanced findings
        for enhanced in session.enhanced_findings[:3]:
            finding = enhanced.original_finding
            print(f"\n🔍 [{finding.severity.upper()}] {finding.title}")
            print(f"   Risk Score: {enhanced.risk_score:.1f}/10")
            
            if enhanced.is_false_positive:
                print(f"   ⚠️  Potential False Positive")
            
            if enhanced.ai_analysis:
                ai = enhanced.ai_analysis
                print(f"   🎯 Remediation Priority: {ai.remediation_priority}/10")
                print(f"   💼 Business Impact: {ai.business_impact[:100]}...")
                print(f"   🔧 Exploit Complexity: {ai.exploit_complexity}")

asyncio.run(ai_enhanced_assessment())
```
```python
import asyncio
from web_pen_test_framework import FrameworkCore
from web_pen_test_framework.models import *

async def full_security_assessment():
    framework = FrameworkCore()
    
    target = Target(
        url="https://testphp.vulnweb.com",
        base_domain="testphp.vulnweb.com",
        scheme="https"
    )
    
    # Phase 1: Passive reconnaissance
    passive_config = Configuration(
        test_suites=[
            TestSuite.RECONNAISSANCE,
            TestSuite.HEADERS,
            TestSuite.SSL_TLS
        ],
        intensity=IntensityLevel.PASSIVE,
        rate_limit=5
    )
    
    print("🔍 Phase 1: Passive Reconnaissance")
    passive_session = await framework.scan(target, passive_config)
    print(f"Found {len(passive_session.findings)} passive findings")
    
    # Phase 2: Active vulnerability testing
    active_config = Configuration(
        test_suites=[
            TestSuite.VULNERABILITY,
            TestSuite.AUTHENTICATION,
            TestSuite.INPUT_VALIDATION
        ],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=10,
        timeout=30
    )
    
    print("🎯 Phase 2: Active Vulnerability Testing")
    active_session = await framework.scan(target, active_config)
    print(f"Found {len(active_session.findings)} active findings")
    
    # Phase 3: API testing (if APIs discovered)
    if any("api" in endpoint.lower() for endpoint in target.discovered_endpoints):
        api_config = Configuration(
            test_suites=[TestSuite.API],
            intensity=IntensityLevel.ACTIVE,
            rate_limit=15
        )
        
        print("🔌 Phase 3: API Security Testing")
        api_session = await framework.scan(target, api_config)
        print(f"Found {len(api_session.findings)} API findings")
    
    # Generate summary report
    all_findings = (passive_session.findings + 
                   active_session.findings + 
                   (api_session.findings if 'api_session' in locals() else []))
    
    print(f"\n📊 FINAL REPORT")
    print(f"Total findings: {len(all_findings)}")
    
    severity_counts = {}
    for finding in all_findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
    
    for severity, count in severity_counts.items():
        print(f"  {severity.upper()}: {count}")

asyncio.run(full_security_assessment())
```

### Example 2: Targeted SQL Injection Testing
```python
import asyncio
from web_pen_test_framework.scanners import VulnerabilityScanner
from web_pen_test_framework.models import *

async def sql_injection_test():
    scanner = VulnerabilityScanner()
    
    target = Target(
        url="http://testphp.vulnweb.com/artists.php?artist=1",
        base_domain="testphp.vulnweb.com",
        scheme="http"
    )
    
    config = Configuration(
        test_suites=[TestSuite.VULNERABILITY],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=5
    )
    
    print("🎯 Testing for SQL Injection vulnerabilities...")
    result = await scanner.scan(target, config)
    
    sql_findings = [f for f in result.findings if "SQL" in f.title]
    
    if sql_findings:
        print(f"🚨 Found {len(sql_findings)} SQL injection vulnerabilities!")
        for finding in sql_findings:
            print(f"  - {finding.title}")
            print(f"    Severity: {finding.severity}")
            print(f"    URL: {finding.affected_url}")
            print(f"    Proof: {finding.proof_of_concept}")
            print()
    else:
        print("✅ No SQL injection vulnerabilities found")

asyncio.run(sql_injection_test())
```

### Example 3: Custom Scanner Implementation
```python
from web_pen_test_framework.scanners.base import PassiveScanner, ScanResult
from web_pen_test_framework.models import *

class CustomScanner(PassiveScanner):
    def get_name(self) -> str:
        return "custom"
    
    def get_description(self) -> str:
        return "Custom security scanner"
    
    def get_test_suite(self) -> TestSuite:
        return TestSuite.OTHER
    
    async def scan(self, target: Target, config: Configuration) -> ScanResult:
        import time
        start_time = time.time()
        
        # Your custom scanning logic here
        response = await self.http_client.get(target.url)
        
        if "admin" in response.content.decode().lower():
            self.create_finding(
                title="Admin Interface Detected",
                description="Potential admin interface found",
                severity=Severity.INFO,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url=target.url,
                confidence=0.7,
                proof_of_concept="Response contains 'admin' keyword",
                remediation="Review admin interface security"
            )
        
        return ScanResult(
            scanner_name=self.get_name(),
            test_suite=self.get_test_suite(),
            findings=self.get_findings(),
            tests_performed=1,
            duration_seconds=time.time() - start_time
        )

# Use custom scanner
async def use_custom_scanner():
    scanner = CustomScanner()
    target = Target("https://example.com", "example.com", "https")
    config = Configuration([TestSuite.OTHER], IntensityLevel.PASSIVE)
    
    result = await scanner.scan(target, config)
    print(f"Custom scan found {len(result.findings)} findings")

asyncio.run(use_custom_scanner())
```

## 📚 API Reference

### Core Classes

#### FrameworkCore
```python
framework = FrameworkCore()
session = await framework.scan(target, config)
await framework.cleanup()
```

#### Target
```python
target = Target(
    url: str,                    # Target URL
    base_domain: str,           # Base domain
    scheme: str,                # http or https
    discovered_endpoints: List[str] = [],
    technologies: List[Technology] = [],
    input_fields: List[InputField] = []
)
```

#### Configuration
```python
config = Configuration(
    test_suites: List[TestSuite],           # Required
    intensity: IntensityLevel = ACTIVE,
    rate_limit: int = 10,
    timeout: int = 30,
    exclusions: List[str] = [],
    custom_payloads: List[Payload] = [],
    enable_destructive_tests: bool = False,
    max_concurrent_requests: int = 10,
    proxy: Optional[str] = None
)
```

### Test Suites
- `TestSuite.RECONNAISSANCE` - Passive information gathering
- `TestSuite.VULNERABILITY` - Active vulnerability testing
- `TestSuite.HEADERS` - Security headers analysis
- `TestSuite.SSL_TLS` - SSL/TLS configuration testing
- `TestSuite.AUTHENTICATION` - Authentication security
- `TestSuite.INPUT_VALIDATION` - Input validation testing
- `TestSuite.API` - API security testing

### Intensity Levels
- `IntensityLevel.PASSIVE` - Safe, read-only testing
- `IntensityLevel.ACTIVE` - Active testing with payloads
- `IntensityLevel.AGGRESSIVE` - Comprehensive testing

### Severity Levels
- `Severity.CRITICAL` - Immediate action required
- `Severity.HIGH` - High priority fix
- `Severity.MEDIUM` - Medium priority
- `Severity.LOW` - Low priority
- `Severity.INFO` - Informational

## ⚠️ Important Notes

### Legal and Ethical Usage
1. **HANYA gunakan pada sistem yang Anda miliki atau memiliki izin tertulis**
2. **Jangan gunakan untuk aktivitas ilegal**
3. **Selalu dapatkan authorization token yang valid**
4. **Patuhi rate limiting untuk menghindari DoS**

### Best Practices
1. **Mulai dengan passive scan** sebelum active testing
2. **Gunakan rate limiting** yang wajar
3. **Monitor target** selama scanning
4. **Backup data** sebelum testing
5. **Test di environment staging** terlebih dahulu

### Performance Tips
1. **Sesuaikan rate_limit** dengan kapasitas target
2. **Gunakan proxy** untuk debugging
3. **Set timeout** yang reasonable
4. **Monitor memory usage** untuk scan besar
5. **Gunakan exclusions** untuk skip path yang tidak perlu

## 🆘 Troubleshooting

### Common Issues

#### Connection Errors
```python
# Increase timeout
config = Configuration(
    test_suites=[TestSuite.HEADERS],
    timeout=60  # Increase from default 30s
)

# Use proxy for debugging
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY],
    proxy="http://127.0.0.1:8080"  # Burp Suite
)
```

#### Rate Limiting
```python
# Reduce rate limit
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY],
    rate_limit=2,  # Slower but safer
    max_concurrent_requests=3
)
```

#### Memory Issues
```python
# Process findings incrementally
async def process_large_scan():
    framework = FrameworkCore()
    
    # Split into smaller scans
    configs = [
        Configuration([TestSuite.RECONNAISSANCE], IntensityLevel.PASSIVE),
        Configuration([TestSuite.HEADERS], IntensityLevel.PASSIVE),
        Configuration([TestSuite.VULNERABILITY], IntensityLevel.ACTIVE)
    ]
    
    all_findings = []
    for config in configs:
        session = await framework.scan(target, config)
        all_findings.extend(session.findings)
        # Process findings here
        await asyncio.sleep(1)  # Brief pause
    
    return all_findings
```

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:

1. **Check logs** untuk error details
2. **Verify authorization** token dan permissions
3. **Test connectivity** ke target
4. **Review configuration** parameters
5. **Check rate limiting** settings

---

**Happy Ethical Hacking! 🔒✨**