"""
AI-powered security analysis engine.

This module provides the main AI analysis engine that integrates with
scanner modules to enhance vulnerability detection and assessment.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .bedrock_client import BedrockAIClient, AIAnalysisResult
from ..models import Finding, Target, Configuration, Severity


logger = logging.getLogger(__name__)


@dataclass
class EnhancedFinding:
    """Finding enhanced with AI analysis."""
    
    original_finding: Finding
    ai_analysis: Optional[AIAnalysisResult] = None
    enhanced_severity: Optional[Severity] = None
    risk_score: float = 0.0
    is_false_positive: bool = False
    
    def get_effective_severity(self) -> Severity:
        """Get the effective severity (AI-enhanced if available)."""
        return self.enhanced_severity or self.original_finding.severity
    
    def get_enhanced_description(self) -> str:
        """Get enhanced description with AI insights."""
        if self.ai_analysis and self.ai_analysis.enhanced_description:
            return f"{self.original_finding.description}\n\nAI Analysis: {self.ai_analysis.enhanced_description}"
        return self.original_finding.description
    
    def get_enhanced_remediation(self) -> str:
        """Get enhanced remediation with AI insights."""
        base_remediation = self.original_finding.remediation
        if self.ai_analysis and self.ai_analysis.additional_context:
            return f"{base_remediation}\n\nAI Recommendations: {self.ai_analysis.additional_context}"
        return base_remediation


class SecurityAnalysisEngine:
    """
    AI-powered security analysis engine.
    
    Enhances vulnerability findings with AI analysis to provide:
    - Improved risk assessment
    - False positive detection
    - Enhanced descriptions and remediation
    - Business impact analysis
    - Prioritization recommendations
    """
    
    def __init__(
        self,
        bedrock_client: Optional[BedrockAIClient] = None,
        enable_ai: bool = True,
        aws_profile: Optional[str] = None,
        aws_region: Optional[str] = None,
        model_id: Optional[str] = None
    ):
        """
        Initialize analysis engine.
        
        Args:
            bedrock_client: AWS Bedrock client (creates default if None)
            enable_ai: Whether to enable AI analysis
            aws_profile: AWS profile name (optional)
            aws_region: AWS region (optional)
            model_id: Bedrock model ID (optional)
        """
        self.enable_ai = enable_ai
        self.bedrock_client = bedrock_client
        
        if self.enable_ai and not self.bedrock_client:
            # Get configuration from environment or parameters
            import os
            profile = aws_profile or os.getenv('AWS_PROFILE')
            region = aws_region or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            model = model_id or os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
            
            self.bedrock_client = BedrockAIClient(
                region_name=region,
                model_id=model,
                profile_name=profile
            )
        
        self.analysis_cache: Dict[str, AIAnalysisResult] = {}
        
        logger.info(f"Security analysis engine initialized (AI enabled: {self.is_ai_enabled()})")
    
    def is_ai_enabled(self) -> bool:
        """Check if AI analysis is enabled and available."""
        return (
            self.enable_ai and 
            self.bedrock_client is not None and 
            self.bedrock_client.is_enabled()
        )
    
    async def analyze_findings(
        self,
        findings: List[Finding],
        target: Target,
        config: Configuration,
        scan_context: Optional[Dict[str, Any]] = None
    ) -> List[EnhancedFinding]:
        """
        Analyze findings with AI enhancement.
        
        Args:
            findings: List of security findings
            target: Target information
            config: Scan configuration
            scan_context: Additional scan context
        
        Returns:
            List of enhanced findings with AI analysis
        """
        if not findings:
            return []
        
        logger.info(f"Analyzing {len(findings)} findings with AI engine")
        
        enhanced_findings = []
        
        # Prepare context for AI analysis
        context = {
            'target_url': target.url,
            'target_domain': target.base_domain,
            'scan_type': ', '.join([suite.value for suite in config.test_suites]),
            'intensity': config.intensity.value,
            **(scan_context or {})
        }
        
        # Process each finding
        for finding in findings:
            enhanced = await self._analyze_single_finding(finding, context)
            enhanced_findings.append(enhanced)
        
        # Post-process: adjust priorities and detect patterns
        enhanced_findings = self._post_process_findings(enhanced_findings)
        
        logger.info(
            f"AI analysis completed: {len([f for f in enhanced_findings if f.ai_analysis])} "
            f"findings enhanced, {len([f for f in enhanced_findings if f.is_false_positive])} "
            f"potential false positives detected"
        )
        
        return enhanced_findings
    
    async def _analyze_single_finding(
        self,
        finding: Finding,
        context: Dict[str, Any]
    ) -> EnhancedFinding:
        """Analyze a single finding with AI."""
        
        enhanced = EnhancedFinding(original_finding=finding)
        
        ai_enabled = self.is_ai_enabled()
        logger.debug(f"Analyzing finding: {finding.title}, AI enabled: {ai_enabled}, enable_ai: {self.enable_ai}, bedrock_client: {self.bedrock_client is not None}, bedrock_enabled: {self.bedrock_client.is_enabled() if self.bedrock_client else False}")
        
        if not ai_enabled:
            logger.debug(f"AI disabled, skipping analysis for finding: {finding.title}")
            return enhanced
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(finding, context)
            if cache_key in self.analysis_cache:
                enhanced.ai_analysis = self.analysis_cache[cache_key]
                logger.debug(f"Using cached AI analysis for: {finding.title}")
            else:
                # Perform AI analysis
                enhanced.ai_analysis = await self.bedrock_client.analyze_finding(finding, context)
                
                # Cache the result
                if enhanced.ai_analysis:
                    self.analysis_cache[cache_key] = enhanced.ai_analysis
            
            # Apply AI insights
            if enhanced.ai_analysis:
                enhanced = self._apply_ai_insights(enhanced)
            
        except Exception as e:
            logger.error(f"AI analysis failed for finding {finding.id}: {e}")
        
        return enhanced
    
    def _apply_ai_insights(self, enhanced: EnhancedFinding) -> EnhancedFinding:
        """Apply AI analysis insights to enhance the finding."""
        
        ai = enhanced.ai_analysis
        if not ai:
            return enhanced
        
        # Calculate risk score (0-10 scale)
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 7,
            Severity.MEDIUM: 4,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        
        base_score = severity_weights.get(enhanced.original_finding.severity, 4)
        priority_factor = ai.remediation_priority / 10.0
        confidence_factor = ai.confidence_score
        fp_penalty = ai.false_positive_likelihood
        
        enhanced.risk_score = (base_score * priority_factor * confidence_factor) * (1 - fp_penalty)
        
        # Detect false positives
        enhanced.is_false_positive = ai.false_positive_likelihood > 0.7
        
        # Adjust severity based on AI analysis
        if ai.remediation_priority >= 9 and enhanced.original_finding.severity != Severity.CRITICAL:
            enhanced.enhanced_severity = Severity.CRITICAL
        elif ai.remediation_priority >= 7 and enhanced.original_finding.severity in [Severity.LOW, Severity.INFO]:
            enhanced.enhanced_severity = Severity.HIGH
        elif ai.remediation_priority <= 3 and enhanced.original_finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            enhanced.enhanced_severity = Severity.MEDIUM
        
        return enhanced
    
    def _post_process_findings(self, findings: List[EnhancedFinding]) -> List[EnhancedFinding]:
        """Post-process findings to detect patterns and adjust priorities."""
        
        if not findings:
            return findings
        
        # Sort by risk score (highest first)
        findings.sort(key=lambda f: f.risk_score, reverse=True)
        
        # Detect duplicate or related findings
        findings = self._deduplicate_findings(findings)
        
        # Adjust priorities based on finding patterns
        findings = self._adjust_priorities_by_patterns(findings)
        
        return findings
    
    def _deduplicate_findings(self, findings: List[EnhancedFinding]) -> List[EnhancedFinding]:
        """Remove or mark duplicate findings."""
        
        seen_signatures = set()
        deduplicated = []
        
        for finding in findings:
            # Create signature for deduplication
            signature = (
                finding.original_finding.category,
                finding.original_finding.affected_url,
                finding.original_finding.affected_parameter
            )
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                deduplicated.append(finding)
            else:
                logger.debug(f"Duplicate finding detected: {finding.original_finding.title}")
        
        return deduplicated
    
    def _adjust_priorities_by_patterns(self, findings: List[EnhancedFinding]) -> List[EnhancedFinding]:
        """Adjust priorities based on finding patterns."""
        
        # Count findings by category
        category_counts = {}
        for finding in findings:
            category = finding.original_finding.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Boost priority for categories with multiple findings
        for finding in findings:
            category = finding.original_finding.category
            if category_counts[category] > 3:  # Multiple instances suggest systemic issue
                finding.risk_score *= 1.2  # 20% boost
                logger.debug(f"Priority boosted for systemic issue: {category}")
        
        return findings
    
    def _get_cache_key(self, finding: Finding, context: Dict[str, Any]) -> str:
        """Generate cache key for AI analysis."""
        return f"{finding.category}:{finding.title}:{finding.affected_url}:{context.get('target_domain', '')}"
    
    def get_analysis_summary(self, enhanced_findings: List[EnhancedFinding]) -> Dict[str, Any]:
        """Generate analysis summary statistics."""
        
        if not enhanced_findings:
            return {"total_findings": 0}
        
        ai_analyzed = [f for f in enhanced_findings if f.ai_analysis]
        false_positives = [f for f in enhanced_findings if f.is_false_positive]
        severity_adjusted = [f for f in enhanced_findings if f.enhanced_severity]
        
        # Risk distribution
        risk_distribution = {
            "critical_risk": len([f for f in enhanced_findings if f.risk_score >= 8]),
            "high_risk": len([f for f in enhanced_findings if 6 <= f.risk_score < 8]),
            "medium_risk": len([f for f in enhanced_findings if 4 <= f.risk_score < 6]),
            "low_risk": len([f for f in enhanced_findings if f.risk_score < 4])
        }
        
        return {
            "total_findings": len(enhanced_findings),
            "ai_analyzed": len(ai_analyzed),
            "ai_analysis_rate": len(ai_analyzed) / len(enhanced_findings) if enhanced_findings else 0,
            "false_positives_detected": len(false_positives),
            "false_positive_rate": len(false_positives) / len(enhanced_findings) if enhanced_findings else 0,
            "severity_adjustments": len(severity_adjusted),
            "risk_distribution": risk_distribution,
            "average_risk_score": sum(f.risk_score for f in enhanced_findings) / len(enhanced_findings),
            "ai_enabled": self.is_ai_enabled(),
            "model_info": self.bedrock_client.get_model_info() if self.bedrock_client else None
        }
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self.analysis_cache.clear()
        logger.info("AI analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.analysis_cache),
            "cache_enabled": True
        }