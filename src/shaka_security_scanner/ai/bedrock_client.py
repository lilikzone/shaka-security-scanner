"""
AWS Bedrock AI client for enhanced security analysis.

This module provides AI-powered analysis capabilities using AWS Bedrock
to enhance vulnerability detection and provide intelligent insights.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from ..models import Finding, Severity, VulnerabilityCategory


logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    """Result of AI analysis."""
    
    enhanced_description: str
    risk_assessment: str
    remediation_priority: int  # 1-10 scale
    false_positive_likelihood: float  # 0.0-1.0
    exploit_complexity: str  # low, medium, high
    business_impact: str
    additional_context: str
    confidence_score: float  # 0.0-1.0


class BedrockAIClient:
    """
    AWS Bedrock AI client for security analysis enhancement.
    
    Provides AI-powered analysis of security findings to:
    - Enhance vulnerability descriptions
    - Assess risk levels and business impact
    - Prioritize remediation efforts
    - Reduce false positives
    - Provide contextual insights
    """
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None
    ):
        """
        Initialize Bedrock AI client.
        
        Args:
            region_name: AWS region for Bedrock service
            model_id: Bedrock model ID to use
            aws_access_key_id: AWS access key (optional, uses default credentials)
            aws_secret_access_key: AWS secret key (optional)
            aws_session_token: AWS session token (optional)
        """
        self.region_name = region_name
        self.model_id = model_id
        self.enabled = False
        self.client = None
        
        if not BOTO3_AVAILABLE:
            logger.warning(
                "boto3 not available. AI analysis will be disabled. "
                "Install with: pip install boto3"
            )
            return
        
        try:
            # Initialize Bedrock client
            session_kwargs = {}
            if aws_access_key_id:
                session_kwargs['aws_access_key_id'] = aws_access_key_id
            if aws_secret_access_key:
                session_kwargs['aws_secret_access_key'] = aws_secret_access_key
            if aws_session_token:
                session_kwargs['aws_session_token'] = aws_session_token
            
            session = boto3.Session(**session_kwargs)
            self.client = session.client(
                'bedrock-runtime',
                region_name=region_name
            )
            
            # Test connection
            self._test_connection()
            self.enabled = True
            logger.info(f"AWS Bedrock AI client initialized successfully (region: {region_name})")
            
        except NoCredentialsError:
            logger.warning(
                "AWS credentials not found. AI analysis will be disabled. "
                "Configure AWS credentials using AWS CLI, environment variables, or IAM roles."
            )
        except ClientError as e:
            logger.warning(f"AWS Bedrock client initialization failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing Bedrock client: {e}")
    
    def _test_connection(self) -> None:
        """Test Bedrock connection with a simple request."""
        try:
            # Simple test prompt
            test_prompt = "Respond with 'OK' if you can process this request."
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ]
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            # If we get here, connection is working
            logger.debug("Bedrock connection test successful")
            
        except Exception as e:
            raise ClientError(
                error_response={'Error': {'Code': 'ConnectionTest', 'Message': str(e)}},
                operation_name='test_connection'
            )
    
    def is_enabled(self) -> bool:
        """Check if AI analysis is enabled and available."""
        return self.enabled and self.client is not None
    
    async def analyze_finding(self, finding: Finding, context: Dict[str, Any] = None) -> Optional[AIAnalysisResult]:
        """
        Analyze a security finding using AI to provide enhanced insights.
        
        Args:
            finding: Security finding to analyze
            context: Additional context (target info, scan results, etc.)
        
        Returns:
            AI analysis result or None if analysis fails
        """
        if not self.is_enabled():
            logger.debug("AI analysis disabled, skipping finding analysis")
            return None
        
        try:
            # Prepare analysis prompt
            prompt = self._build_analysis_prompt(finding, context or {})
            
            # Call Bedrock API
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.1,  # Low temperature for consistent analysis
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            # Parse AI analysis
            analysis = self._parse_ai_response(ai_response)
            
            logger.debug(f"AI analysis completed for finding: {finding.title}")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed for finding {finding.id}: {e}")
            return None
    
    def _build_analysis_prompt(self, finding: Finding, context: Dict[str, Any]) -> str:
        """Build analysis prompt for the AI model."""
        
        # Get context information
        target_url = context.get('target_url', 'Unknown')
        target_domain = context.get('target_domain', 'Unknown')
        scan_type = context.get('scan_type', 'Unknown')
        
        prompt = f"""
You are a cybersecurity expert analyzing a security vulnerability finding. Please provide a comprehensive analysis of this security issue.

VULNERABILITY DETAILS:
- Title: {finding.title}
- Description: {finding.description}
- Severity: {finding.severity}
- Category: {finding.category}
- Affected URL: {finding.affected_url}
- Affected Parameter: {finding.affected_parameter or 'N/A'}
- Proof of Concept: {finding.proof_of_concept}
- Current Remediation: {finding.remediation}
- Confidence: {finding.confidence}
- CVSS Score: {finding.cvss_score or 'N/A'}
- CWE ID: {finding.cwe_id or 'N/A'}

TARGET CONTEXT:
- Target URL: {target_url}
- Target Domain: {target_domain}
- Scan Type: {scan_type}

Please provide your analysis in the following JSON format:

{{
    "enhanced_description": "Detailed technical explanation of the vulnerability and its implications",
    "risk_assessment": "Comprehensive risk assessment including attack vectors and potential impact",
    "remediation_priority": 8,
    "false_positive_likelihood": 0.1,
    "exploit_complexity": "medium",
    "business_impact": "Description of potential business impact",
    "additional_context": "Additional insights, related vulnerabilities, or security considerations",
    "confidence_score": 0.9
}}

ANALYSIS GUIDELINES:
1. Enhanced Description: Provide technical details about how this vulnerability works and why it's dangerous
2. Risk Assessment: Analyze attack vectors, exploitability, and potential damage
3. Remediation Priority: Rate 1-10 (10 = critical, immediate action required)
4. False Positive Likelihood: Rate 0.0-1.0 (0.0 = definitely real, 1.0 = likely false positive)
5. Exploit Complexity: "low", "medium", or "high" based on skill/resources needed
6. Business Impact: Explain potential business consequences (data breach, downtime, compliance, etc.)
7. Additional Context: Provide related security insights, common attack patterns, or prevention strategies
8. Confidence Score: Rate 0.0-1.0 for overall analysis confidence

Focus on actionable insights and practical security implications. Consider the specific context of the target application.
"""
        
        return prompt.strip()
    
    def _parse_ai_response(self, response: str) -> AIAnalysisResult:
        """Parse AI response into structured analysis result."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis_data = json.loads(json_str)
                
                return AIAnalysisResult(
                    enhanced_description=analysis_data.get('enhanced_description', ''),
                    risk_assessment=analysis_data.get('risk_assessment', ''),
                    remediation_priority=int(analysis_data.get('remediation_priority', 5)),
                    false_positive_likelihood=float(analysis_data.get('false_positive_likelihood', 0.5)),
                    exploit_complexity=analysis_data.get('exploit_complexity', 'medium'),
                    business_impact=analysis_data.get('business_impact', ''),
                    additional_context=analysis_data.get('additional_context', ''),
                    confidence_score=float(analysis_data.get('confidence_score', 0.5))
                )
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse AI response: {e}")
            
            # Fallback: create basic analysis from raw response
            return AIAnalysisResult(
                enhanced_description=response[:500] + "..." if len(response) > 500 else response,
                risk_assessment="AI analysis parsing failed, manual review recommended",
                remediation_priority=5,
                false_positive_likelihood=0.5,
                exploit_complexity="medium",
                business_impact="Unknown - requires manual assessment",
                additional_context="AI response could not be parsed properly",
                confidence_score=0.3
            )
    
    async def analyze_findings_batch(
        self, 
        findings: List[Finding], 
        context: Dict[str, Any] = None
    ) -> Dict[str, AIAnalysisResult]:
        """
        Analyze multiple findings in batch for efficiency.
        
        Args:
            findings: List of findings to analyze
            context: Shared context for all findings
        
        Returns:
            Dictionary mapping finding IDs to analysis results
        """
        if not self.is_enabled():
            logger.debug("AI analysis disabled, skipping batch analysis")
            return {}
        
        results = {}
        
        for finding in findings:
            try:
                analysis = await self.analyze_finding(finding, context)
                if analysis:
                    results[finding.id] = analysis
            except Exception as e:
                logger.error(f"Batch analysis failed for finding {finding.id}: {e}")
                continue
        
        logger.info(f"AI batch analysis completed: {len(results)}/{len(findings)} findings analyzed")
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI model."""
        return {
            "enabled": self.enabled,
            "model_id": self.model_id,
            "region": self.region_name,
            "service": "AWS Bedrock",
            "capabilities": [
                "Vulnerability analysis",
                "Risk assessment", 
                "False positive detection",
                "Remediation prioritization",
                "Business impact analysis"
            ]
        }