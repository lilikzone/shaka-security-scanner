"""
Unit tests for AI integration components.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from shaka_security_scanner.ai import BedrockAIClient, SecurityAnalysisEngine, EnhancedFinding, AIAnalysisResult
from shaka_security_scanner.models import Finding, Target, Configuration, TestSuite, IntensityLevel, Severity, VulnerabilityCategory


class TestBedrockAIClient:
    """Test AWS Bedrock AI client."""
    
    def test_client_initialization_no_boto3(self):
        """Test client initialization when boto3 is not available."""
        with patch('shaka_security_scanner.ai.bedrock_client.BOTO3_AVAILABLE', False):
            client = BedrockAIClient()
            assert not client.is_enabled()
            assert client.client is None
    
    @patch('shaka_security_scanner.ai.bedrock_client.boto3')
    def test_client_initialization_success(self, mock_boto3):
        """Test successful client initialization."""
        mock_session = Mock()
        mock_client = Mock()
        mock_session.client.return_value = mock_client
        mock_boto3.Session.return_value = mock_session
        
        # Mock successful test connection
        mock_client.invoke_model.return_value = {
            'body': Mock(read=Mock(return_value=b'{"content": [{"text": "OK"}]}'))
        }
        
        client = BedrockAIClient()
        assert client.is_enabled()
        assert client.client is not None
    
    @patch('shaka_security_scanner.ai.bedrock_client.boto3')
    def test_client_initialization_credentials_error(self, mock_boto3):
        """Test client initialization with credentials error."""
        from botocore.exceptions import NoCredentialsError
        mock_boto3.Session.side_effect = NoCredentialsError()
        
        client = BedrockAIClient()
        assert not client.is_enabled()
    
    def test_get_model_info(self):
        """Test getting model information."""
        client = BedrockAIClient()
        info = client.get_model_info()
        
        assert isinstance(info, dict)
        assert 'enabled' in info
        assert 'model_id' in info
        assert 'region' in info
        assert 'service' in info
        assert 'capabilities' in info
    
    @patch('shaka_security_scanner.ai.bedrock_client.boto3')
    @pytest.mark.asyncio
    async def test_analyze_finding_disabled(self, mock_boto3):
        """Test analyze_finding when AI is disabled."""
        client = BedrockAIClient()
        client.enabled = False
        
        finding = Finding(
            id="test-1",
            title="Test Finding",
            description="Test description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        )
        
        result = await client.analyze_finding(finding)
        assert result is None
    
    @patch('shaka_security_scanner.ai.bedrock_client.boto3')
    @pytest.mark.asyncio
    async def test_analyze_finding_success(self, mock_boto3):
        """Test successful finding analysis."""
        mock_session = Mock()
        mock_client = Mock()
        mock_session.client.return_value = mock_client
        mock_boto3.Session.return_value = mock_session
        
        # Mock test connection
        mock_client.invoke_model.side_effect = [
            {'body': Mock(read=Mock(return_value=b'{"content": [{"text": "OK"}]}'))},  # Test connection
            {'body': Mock(read=Mock(return_value=b'{"content": [{"text": "{\\"enhanced_description\\": \\"Test analysis\\", \\"risk_assessment\\": \\"High risk\\", \\"remediation_priority\\": 8, \\"false_positive_likelihood\\": 0.1, \\"exploit_complexity\\": \\"medium\\", \\"business_impact\\": \\"Data breach\\", \\"additional_context\\": \\"Additional info\\", \\"confidence_score\\": 0.9}"}]}'))}  # Analysis
        ]
        
        client = BedrockAIClient()
        
        finding = Finding(
            id="test-1",
            title="XSS Vulnerability",
            description="Cross-site scripting vulnerability",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        )
        
        result = await client.analyze_finding(finding)
        
        assert result is not None
        assert isinstance(result, AIAnalysisResult)
        assert result.enhanced_description == "Test analysis"
        assert result.risk_assessment == "High risk"
        assert result.remediation_priority == 8
        assert result.false_positive_likelihood == 0.1
        assert result.exploit_complexity == "medium"
        assert result.business_impact == "Data breach"
        assert result.confidence_score == 0.9


class TestSecurityAnalysisEngine:
    """Test security analysis engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        assert not engine.is_ai_enabled()
        assert engine.bedrock_client is None
    
    def test_engine_initialization_with_ai(self):
        """Test engine initialization with AI enabled."""
        mock_client = Mock()
        mock_client.is_enabled.return_value = True
        
        engine = SecurityAnalysisEngine(bedrock_client=mock_client, enable_ai=True)
        assert engine.is_ai_enabled()
        assert engine.bedrock_client is mock_client
    
    @pytest.mark.asyncio
    async def test_analyze_findings_empty_list(self):
        """Test analyzing empty findings list."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        
        target = Target(url="https://example.com", base_domain="example.com", scheme="https")
        config = Configuration(test_suites=[TestSuite.HEADERS])
        
        result = await engine.analyze_findings([], target, config)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_analyze_findings_ai_disabled(self):
        """Test analyzing findings with AI disabled."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        
        target = Target(url="https://example.com", base_domain="example.com", scheme="https")
        config = Configuration(test_suites=[TestSuite.HEADERS])
        
        findings = [
            Finding(
                id="test-1",
                title="Missing HSTS",
                description="HSTS header missing",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.SECURITY_HEADERS,
                affected_url="https://example.com"
            )
        ]
        
        result = await engine.analyze_findings(findings, target, config)
        
        assert len(result) == 1
        assert isinstance(result[0], EnhancedFinding)
        assert result[0].original_finding == findings[0]
        assert result[0].ai_analysis is None
    
    @pytest.mark.asyncio
    async def test_analyze_findings_with_ai(self):
        """Test analyzing findings with AI enabled."""
        mock_client = Mock()
        mock_client.is_enabled.return_value = True
        mock_client.analyze_finding = AsyncMock(return_value=AIAnalysisResult(
            enhanced_description="Enhanced description",
            risk_assessment="High risk",
            remediation_priority=8,
            false_positive_likelihood=0.1,
            exploit_complexity="medium",
            business_impact="Data breach",
            additional_context="Additional context",
            confidence_score=0.9
        ))
        
        engine = SecurityAnalysisEngine(bedrock_client=mock_client, enable_ai=True)
        
        target = Target(url="https://example.com", base_domain="example.com", scheme="https")
        config = Configuration(test_suites=[TestSuite.HEADERS])
        
        findings = [
            Finding(
                id="test-1",
                title="Missing HSTS",
                description="HSTS header missing",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.SECURITY_HEADERS,
                affected_url="https://example.com"
            )
        ]
        
        result = await engine.analyze_findings(findings, target, config)
        
        assert len(result) == 1
        enhanced = result[0]
        assert isinstance(enhanced, EnhancedFinding)
        assert enhanced.ai_analysis is not None
        assert enhanced.risk_score > 0
        assert not enhanced.is_false_positive  # Low false positive likelihood
    
    def test_get_analysis_summary_empty(self):
        """Test getting analysis summary for empty findings."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        summary = engine.get_analysis_summary([])
        
        assert summary["total_findings"] == 0
    
    def test_get_analysis_summary_with_findings(self):
        """Test getting analysis summary with findings."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        
        # Create enhanced findings
        finding1 = EnhancedFinding(
            original_finding=Finding(
                id="test-1",
                title="Test 1",
                description="Description 1",
                severity=Severity.HIGH,
                category=VulnerabilityCategory.XSS,
                affected_url="https://example.com"
            ),
            risk_score=8.0
        )
        
        finding2 = EnhancedFinding(
            original_finding=Finding(
                id="test-2",
                title="Test 2",
                description="Description 2",
                severity=Severity.LOW,
                category=VulnerabilityCategory.INFORMATION_DISCLOSURE,
                affected_url="https://example.com"
            ),
            risk_score=3.0,
            is_false_positive=True
        )
        
        enhanced_findings = [finding1, finding2]
        summary = engine.get_analysis_summary(enhanced_findings)
        
        assert summary["total_findings"] == 2
        assert summary["false_positives_detected"] == 1
        assert summary["false_positive_rate"] == 0.5
        assert summary["average_risk_score"] == 5.5
        assert summary["risk_distribution"]["critical_risk"] == 1  # finding1 with score 8.0
        assert summary["risk_distribution"]["low_risk"] == 1  # finding2 with score 3.0
    
    def test_cache_operations(self):
        """Test cache operations."""
        engine = SecurityAnalysisEngine(enable_ai=False)
        
        # Initially empty
        stats = engine.get_cache_stats()
        assert stats["cache_size"] == 0
        
        # Add to cache
        engine.analysis_cache["test-key"] = AIAnalysisResult(
            enhanced_description="Test",
            risk_assessment="Test",
            remediation_priority=5,
            false_positive_likelihood=0.5,
            exploit_complexity="medium",
            business_impact="Test",
            additional_context="Test",
            confidence_score=0.8
        )
        
        stats = engine.get_cache_stats()
        assert stats["cache_size"] == 1
        
        # Clear cache
        engine.clear_cache()
        stats = engine.get_cache_stats()
        assert stats["cache_size"] == 0


class TestEnhancedFinding:
    """Test enhanced finding class."""
    
    def test_enhanced_finding_creation(self):
        """Test creating enhanced finding."""
        original = Finding(
            id="test-1",
            title="Test Finding",
            description="Test description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        )
        
        enhanced = EnhancedFinding(original_finding=original)
        
        assert enhanced.original_finding == original
        assert enhanced.ai_analysis is None
        assert enhanced.enhanced_severity is None
        assert enhanced.risk_score == 0.0
        assert not enhanced.is_false_positive
    
    def test_get_effective_severity(self):
        """Test getting effective severity."""
        original = Finding(
            id="test-1",
            title="Test Finding",
            description="Test description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        )
        
        enhanced = EnhancedFinding(original_finding=original)
        
        # Without AI enhancement
        assert enhanced.get_effective_severity() == Severity.HIGH
        
        # With AI enhancement
        enhanced.enhanced_severity = Severity.CRITICAL
        assert enhanced.get_effective_severity() == Severity.CRITICAL
    
    def test_get_enhanced_description(self):
        """Test getting enhanced description."""
        original = Finding(
            id="test-1",
            title="Test Finding",
            description="Original description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com"
        )
        
        enhanced = EnhancedFinding(original_finding=original)
        
        # Without AI analysis
        assert enhanced.get_enhanced_description() == "Original description"
        
        # With AI analysis
        enhanced.ai_analysis = AIAnalysisResult(
            enhanced_description="AI enhanced description",
            risk_assessment="Test",
            remediation_priority=5,
            false_positive_likelihood=0.5,
            exploit_complexity="medium",
            business_impact="Test",
            additional_context="Test",
            confidence_score=0.8
        )
        
        description = enhanced.get_enhanced_description()
        assert "Original description" in description
        assert "AI Analysis: AI enhanced description" in description
    
    def test_get_enhanced_remediation(self):
        """Test getting enhanced remediation."""
        original = Finding(
            id="test-1",
            title="Test Finding",
            description="Test description",
            severity=Severity.HIGH,
            category=VulnerabilityCategory.XSS,
            affected_url="https://example.com",
            remediation="Original remediation"
        )
        
        enhanced = EnhancedFinding(original_finding=original)
        
        # Without AI analysis
        assert enhanced.get_enhanced_remediation() == "Original remediation"
        
        # With AI analysis
        enhanced.ai_analysis = AIAnalysisResult(
            enhanced_description="Test",
            risk_assessment="Test",
            remediation_priority=5,
            false_positive_likelihood=0.5,
            exploit_complexity="medium",
            business_impact="Test",
            additional_context="AI recommendations",
            confidence_score=0.8
        )
        
        remediation = enhanced.get_enhanced_remediation()
        assert "Original remediation" in remediation
        assert "AI Recommendations: AI recommendations" in remediation


class TestAIAnalysisResult:
    """Test AI analysis result dataclass."""
    
    def test_ai_analysis_result_creation(self):
        """Test creating AI analysis result."""
        result = AIAnalysisResult(
            enhanced_description="Enhanced description",
            risk_assessment="High risk assessment",
            remediation_priority=8,
            false_positive_likelihood=0.1,
            exploit_complexity="low",
            business_impact="Significant impact",
            additional_context="Additional context",
            confidence_score=0.9
        )
        
        assert result.enhanced_description == "Enhanced description"
        assert result.risk_assessment == "High risk assessment"
        assert result.remediation_priority == 8
        assert result.false_positive_likelihood == 0.1
        assert result.exploit_complexity == "low"
        assert result.business_impact == "Significant impact"
        assert result.additional_context == "Additional context"
        assert result.confidence_score == 0.9