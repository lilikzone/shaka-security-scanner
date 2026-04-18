# 🛡️ Shaka Security Scanner

**Advanced Web Application Security Testing Framework with AI-Powered Analysis**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock%20AI-orange.svg)](https://aws.amazon.com/bedrock/)
[![Tests](https://img.shields.io/badge/Tests-275%2B%20Passing-green.svg)](#testing)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Shaka Security Scanner** adalah framework penetration testing web application yang komprehensif dengan integrasi AI untuk analisis keamanan yang lebih cerdas dan akurat.

---

## 🚀 Features

### 🔍 **Comprehensive Security Testing**
- **9 Scanner Modules** - Reconnaissance, Vulnerability, Headers, SSL/TLS, Authentication, Input Validation, API, Advanced Vulnerability, CMS Vulnerability
- **35+ Vulnerability Categories** - SQL Injection, XSS, CSRF, SSRF, XXE, Template Injection, CMS-specific vulnerabilities, dan lainnya
- **3 Intensity Levels** - Passive, Active, Aggressive testing modes
- **Rate Limiting & Throttling** - Mencegah DoS pada target
- **CMS-Specific Testing** - WordPress, Drupal, Joomla, Magento vulnerability scanning

### 🤖 **AI-Powered Analysis**
- **AWS Bedrock Integration** - Claude 3 Sonnet untuk enhanced analysis
- **False Positive Detection** - AI mendeteksi potential false positives
- **Risk Scoring** - Intelligent risk assessment (0-10 scale)
- **Business Impact Analysis** - Analisis dampak bisnis
- **Remediation Prioritization** - AI-driven priority recommendations

### 🛡️ **Security & Compliance**
- **Authorization System** - HMAC-signed tokens dengan domain validation
- **Audit Logging** - Comprehensive request/response logging
- **Legal Compliance** - Built-in disclaimers dan ethical guidelines
- **Rate Limiting** - Configurable request throttling

### 📊 **Professional Reporting**
- **Multiple Formats** - HTML, JSON, PDF, Markdown
- **Risk Assessment** - Automated risk scoring dan categorization
- **Executive Summary** - Business-ready reports
- **Detailed Findings** - Technical details dengan remediation steps

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip atau poetry
- AWS credentials (optional, untuk AI features)

### Quick Install
```bash
git clone https://github.com/yourusername/shaka-security-scanner.git
cd shaka-security-scanner
pip install -e .
```

### With Poetry
```bash
git clone https://github.com/yourusername/shaka-security-scanner.git
cd shaka-security-scanner
poetry install
```

### AWS Bedrock Setup (Optional)
```bash
# Install boto3 for AI features
pip install boto3

# Configure AWS credentials
aws configure
# atau set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

---

## ⚡ Quick Start

### Basic Security Scan
```python
import asyncio
from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel

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
        test_suites=[TestSuite.HEADERS, TestSuite.SSL_TLS],
        intensity=IntensityLevel.PASSIVE,
        enable_ai_analysis=True  # Enable AI analysis
    )
    
    # Run scan
    session = await framework.scan(target, config)
    
    # Print results
    print(f"Scan completed: {len(session.get_all_findings())} findings")
    
    # AI-enhanced results (if available)
    if hasattr(session, 'enhanced_findings'):
        for enhanced in session.enhanced_findings[:3]:
            print(f"🔍 {enhanced.original_finding.title}")
            print(f"   Risk Score: {enhanced.risk_score:.1f}/10")
            if enhanced.is_false_positive:
                print(f"   ⚠️  Potential False Positive")

# Run the scan
asyncio.run(basic_scan())
```

### Command Line Usage
```bash
# Run demo scan
python demo_scan.py

# Run AI integration demo
python ai_demo.py

# Run advanced vulnerability demo
python advanced_demo.py

# Run CMS vulnerability demo
python cms_demo.py

# Run comprehensive test
python final_test.py
```

---

## 🔍 Scanner Modules

| Scanner | Type | Description | Detects |
|---------|------|-------------|---------|
| **Reconnaissance** | Passive | Information gathering | Technologies, endpoints, metadata |
| **Vulnerability** | Active | Core vulnerability testing | SQL injection, XSS, CSRF |
| **Headers** | Passive | Security headers analysis | Missing/weak security headers |
| **SSL/TLS** | Passive | SSL/TLS configuration | Weak protocols, certificates |
| **Authentication** | Active | Authentication security | Default credentials, brute force |
| **Input Validation** | Active | Input validation testing | Command injection, path traversal |
| **API** | Active | API security testing | OWASP API Top 10 |
| **Advanced Vulnerability** | Active | Advanced attack vectors | SSRF, XXE, Template Injection, NoSQL |
| **CMS Vulnerability** | Active | CMS-specific testing | WordPress, Drupal, Joomla, Magento |

---

## 🎯 CMS Vulnerability Testing

### Supported CMS Platforms

#### **WordPress Security Testing** 🔥
- **User Enumeration Detection**
  - REST API user enumeration (`/wp-json/wp/v2/users`)
  - Author parameter enumeration (`/?author=1`)
- **XML-RPC Interface Testing**
  - XML-RPC endpoint detection and vulnerability assessment
  - Brute force and DDoS amplification risk evaluation
- **Directory Listing Vulnerabilities**
  - Plugin, theme, and upload directory exposure testing
- **Configuration File Exposure**
  - `wp-config.php` accessibility and backup file detection
- **Plugin Vulnerability Detection**
  - Known vulnerable plugins (Revolution Slider, WP File Manager, Elementor, etc.)
- **Version Disclosure Testing**
  - `readme.html`, `license.txt`, and meta tag version detection

#### **Drupal Security Testing** 🎯
- **Version Disclosure Detection**
  - `CHANGELOG.txt`, `COPYRIGHT.txt`, `README.txt` analysis
- **Admin Panel Security**
  - `/user/login` accessibility and authentication testing
- **Module Vulnerability Scanning**
  - CKEditor, Views, and other module vulnerabilities

#### **Joomla Security Assessment** 🌐
- **Administrator Panel Testing**
  - `/administrator/` accessibility and security evaluation
- **Configuration Security**
  - `configuration.php` exposure and backup file detection
- **Extension Vulnerability Detection**
  - Fabrik, JCE, and other extension vulnerabilities

#### **Magento E-commerce Testing** 💰
- **Admin Panel Discovery**
  - Multiple admin path testing and security assessment
- **Downloader Interface Testing**
  - `/downloader/` accessibility and security evaluation
- **Configuration Vulnerabilities**
  - `app/etc/local.xml` exposure and log file accessibility

### CMS Testing Example
```python
import asyncio
from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel

async def cms_security_scan():
    framework = FrameworkCore()
    
    # WordPress security audit
    target = Target(
        url="https://your-wordpress-site.com",
        base_domain="your-wordpress-site.com",
        scheme="https"
    )
    
    config = Configuration(
        test_suites=[TestSuite.CMS_VULNERABILITY],
        intensity=IntensityLevel.ACTIVE,
        enable_ai_analysis=True
    )
    
    session = await framework.scan(target, config)
    
    print(f"CMS Scan completed: {len(session.get_all_findings())} findings")
    for finding in session.get_all_findings():
        print(f"  - {finding.title} ({finding.severity.value})")

asyncio.run(cms_security_scan())
```

---

## 🤖 AI-Enhanced Analysis

### Capabilities
- **Enhanced Descriptions** - Detailed technical explanations
- **Risk Assessment** - Comprehensive risk analysis
- **False Positive Detection** - 0.0-1.0 confidence scoring
- **Business Impact** - Business consequence analysis
- **Remediation Priority** - 1-10 scale prioritization
- **Exploit Complexity** - Low/Medium/High assessment

### Example AI Analysis
```python
# Access AI-enhanced findings
for enhanced in session.enhanced_findings:
    if enhanced.ai_analysis:
        ai = enhanced.ai_analysis
        print(f"Business Impact: {ai.business_impact}")
        print(f"Remediation Priority: {ai.remediation_priority}/10")
        print(f"False Positive Likelihood: {ai.false_positive_likelihood}")
        print(f"Exploit Complexity: {ai.exploit_complexity}")
```

---

## 📊 Configuration

### Basic Configuration
```python
config = Configuration(
    test_suites=[TestSuite.HEADERS, TestSuite.VULNERABILITY],
    intensity=IntensityLevel.ACTIVE,
    rate_limit=10,  # requests per second
    timeout=30,
    enable_ai_analysis=True,
    enable_destructive_tests=False  # Keep safe
)
```

### Advanced Configuration
```python
config = Configuration(
    test_suites=[TestSuite.VULNERABILITY, TestSuite.API],
    intensity=IntensityLevel.AGGRESSIVE,
    rate_limit=20,
    max_concurrent_requests=15,
    exclusions=[
        "*/admin/*",      # Skip admin paths
        "*/logout",       # Skip logout
        "*.pdf"           # Skip PDF files
    ],
    custom_payloads=[
        Payload(
            value="<script>alert('custom')</script>",
            category=PayloadCategory.XSS,
            description="Custom XSS payload"
        )
    ],
    proxy="http://127.0.0.1:8080",  # Burp Suite proxy
    enable_ai_analysis=True
)
```

---

## 🧪 Testing

### Run All Tests
```bash
# Run complete test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=shaka_security_scanner --cov-report=html

# Run specific test categories
python -m pytest tests/unit/test_ai_integration.py -v
python -m pytest tests/unit/test_scanners.py -v
```

### Test Results
- **275+ Tests** - Comprehensive test coverage
- **100% Pass Rate** - All tests passing
- **AI Integration** - 19 dedicated AI tests
- **Scanner Modules** - 91 scanner tests (including CMS and Advanced)
- **Core Framework** - 148 framework tests

---

## 📚 Documentation

### Core Documentation
- **[Usage Guide](USAGE_GUIDE.md)** - Comprehensive usage documentation
- **[AI Integration](AI_INTEGRATION_SUMMARY.md)** - AI features dan setup
- **[Advanced Vulnerability Testing](ADVANCED_UPGRADE_SUMMARY.md)** - Advanced attack vectors
- **[CMS Vulnerability Testing](CMS_UPGRADE_SUMMARY.md)** - CMS-specific security testing
- **[Agent Guide](AGENT.md)** - Development dan contribution guide
- **[API Reference](docs/)** - Complete API documentation

### Examples
- **[Demo Scripts](demo_scan.py)** - Basic usage examples
- **[AI Demo](ai_demo.py)** - AI integration examples
- **[Advanced Demo](advanced_demo.py)** - Advanced vulnerability testing
- **[CMS Demo](cms_demo.py)** - CMS vulnerability testing
- **[Advanced Examples](USAGE_GUIDE.md#examples)** - Complex scenarios

---

## 🔐 Security & Ethics

### Legal Requirements
⚠️ **IMPORTANT**: Hanya gunakan pada sistem yang Anda miliki atau memiliki izin tertulis untuk testing.

### Authorization System
```python
from shaka_security_scanner.core import AuthorizationManager

# Generate authorization token
auth_manager = AuthorizationManager()
token = auth_manager.generate_token(
    target_domain="example.com",
    expires_in_days=30,
    scope=["vulnerability", "authentication"]
)

# Use token in scan
session = await framework.scan(target, config, auth_token=token)
```

### Best Practices
1. **Dapatkan izin tertulis** sebelum testing
2. **Mulai dengan passive scan** untuk reconnaissance
3. **Gunakan rate limiting** yang wajar
4. **Monitor target** selama scanning
5. **Test di staging environment** terlebih dahulu

---

## 🚀 Performance

### Benchmarks
- **Async Architecture** - Non-blocking I/O untuk maximum throughput
- **Smart Rate Limiting** - Token bucket algorithm
- **Connection Pooling** - Efficient HTTP connection reuse
- **AI Caching** - Analysis results cached untuk performance

### Optimization Tips
- Sesuaikan `rate_limit` dengan kapasitas target
- Gunakan `exclusions` untuk skip unnecessary paths
- Enable `proxy` untuk debugging
- Monitor memory usage untuk large scans

---

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/yourusername/shaka-security-scanner.git
cd shaka-security-scanner
poetry install --dev

# Run tests
python -m pytest tests/ -v

# Run linting
flake8 src/
black src/
```

### Adding New Scanners
1. Extend `ScannerModule` base class
2. Implement required methods
3. Add comprehensive tests
4. Update documentation

### Contribution Guidelines
- Follow PEP 8 style guide
- Add tests untuk new features
- Update documentation
- Ensure all tests pass

---

## 📈 Roadmap

### Upcoming Features
- [ ] **Web UI Dashboard** - Browser-based interface
- [ ] **CI/CD Integration** - GitHub Actions, Jenkins plugins
- [ ] **More AI Models** - Support untuk multiple AI providers
- [ ] **Advanced Reporting** - Interactive HTML reports
- [ ] **Plugin System** - Custom scanner plugins
- [ ] **Distributed Scanning** - Multi-node scanning

### Version History
- **v1.0.0** - Initial release dengan 7 scanner modules
- **v1.1.0** - AWS Bedrock AI integration
- **v1.2.0** - Advanced vulnerability testing (SSRF, XXE, Template Injection, NoSQL)
- **v1.3.0** - CMS vulnerability testing (WordPress, Drupal, Joomla, Magento)
- **v1.4.0** - Enhanced reporting dan UI improvements (planned)

---

## 📞 Support

### Getting Help
- **Documentation** - Check [Usage Guide](USAGE_GUIDE.md)
- **Issues** - Report bugs di GitHub Issues
- **Discussions** - Join GitHub Discussions
- **Security** - Report security issues privately

### Common Issues
- **AWS Credentials** - Ensure proper AWS setup untuk AI features
- **Rate Limiting** - Adjust `rate_limit` jika target slow
- **Memory Usage** - Use `exclusions` untuk large sites
- **SSL Errors** - Set `verify_ssl=False` untuk self-signed certs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **AWS Bedrock** - AI-powered analysis capabilities
- **OWASP** - Security testing methodologies
- **Python Community** - Amazing libraries dan tools
- **Security Researchers** - Vulnerability research dan disclosure

---

## ⚠️ Disclaimer

**Shaka Security Scanner** adalah tool untuk ethical hacking dan authorized security testing. Pengguna bertanggung jawab untuk memastikan penggunaan yang legal dan ethical. Developers tidak bertanggung jawab atas penyalahgunaan tool ini.

---

<div align="center">

**🛡️ Secure the Web, One Scan at a Time 🛡️**

Made with ❤️ for the security community

[⭐ Star this repo](https://github.com/yourusername/shaka-security-scanner) | [🐛 Report Bug](https://github.com/yourusername/shaka-security-scanner/issues) | [💡 Request Feature](https://github.com/yourusername/shaka-security-scanner/issues)

</div>