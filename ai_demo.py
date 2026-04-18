#!/usr/bin/env python3
"""
Demo script untuk menguji integrasi AWS Bedrock AI dalam Web Penetration Testing Framework.
"""

import asyncio
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, 'src')

from shaka_security_scanner import FrameworkCore, SecurityAnalysisEngine, BedrockAIClient
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel


async def ai_integration_demo():
    """
    Demo integrasi AI dengan AWS Bedrock untuk analisis keamanan.
    """
    print("🤖 Web Penetration Testing Framework - AI Integration Demo")
    print("=" * 60)
    
    # Initialize framework with AI
    framework = FrameworkCore()
    
    print(f"🔧 Framework Status:")
    info = framework.get_info()
    print(f"   Version: {info['version']}")
    print(f"   Scanners: {info['scanners_registered']}")
    print(f"   AI Enabled: {info['ai_enabled']}")
    
    if info['ai_enabled']:
        ai_info = info['ai_model']
        print(f"   AI Model: {ai_info['model_id']}")
        print(f"   AI Region: {ai_info['region']}")
        print(f"   AI Service: {ai_info['service']}")
    else:
        print("   AI Status: Disabled (AWS credentials not configured)")
    
    print()
    
    # Test target
    target = Target(
        url="https://httpbin.org",
        base_domain="httpbin.org",
        scheme="https"
    )
    
    # Configuration with AI enabled
    config = Configuration(
        test_suites=[TestSuite.HEADERS, TestSuite.SSL_TLS],
        intensity=IntensityLevel.PASSIVE,
        rate_limit=3,
        timeout=15,
        enable_ai_analysis=True  # Enable AI analysis
    )
    
    print("🔍 Running Security Scan with AI Analysis")
    print("-" * 45)
    
    try:
        # Run scan with AI analysis
        session = await framework.scan(target, config)
        
        print(f"✅ Scan completed successfully")
        print(f"   Duration: {session.duration_seconds:.2f}s")
        print(f"   Status: {session.status}")
        print(f"   Raw Findings: {len(session.get_all_findings())}")
        
        # Check if AI analysis was performed
        if hasattr(session, 'enhanced_findings') and session.enhanced_findings:
            print(f"   AI Enhanced Findings: {len(session.enhanced_findings)}")
            
            # Show AI analysis summary
            if hasattr(session, 'ai_analysis_summary') and session.ai_analysis_summary:
                summary = session.ai_analysis_summary
                print(f"\n🤖 AI Analysis Summary:")
                print(f"   AI Analysis Rate: {summary.get('ai_analysis_rate', 0):.1%}")
                print(f"   False Positives Detected: {summary.get('false_positives_detected', 0)}")
                print(f"   Severity Adjustments: {summary.get('severity_adjustments', 0)}")
                print(f"   Average Risk Score: {summary.get('average_risk_score', 0):.1f}/10")
                
                # Risk distribution
                risk_dist = summary.get('risk_distribution', {})
                print(f"   Risk Distribution:")
                print(f"     Critical: {risk_dist.get('critical_risk', 0)}")
                print(f"     High: {risk_dist.get('high_risk', 0)}")
                print(f"     Medium: {risk_dist.get('medium_risk', 0)}")
                print(f"     Low: {risk_dist.get('low_risk', 0)}")
            
            # Show enhanced findings
            print(f"\n📊 Enhanced Security Findings:")
            for i, enhanced in enumerate(session.enhanced_findings[:5], 1):
                finding = enhanced.original_finding
                print(f"\n   {i}. [{finding.severity.upper()}] {finding.title}")
                print(f"      URL: {finding.affected_url}")
                print(f"      Risk Score: {enhanced.risk_score:.1f}/10")
                
                if enhanced.is_false_positive:
                    print(f"      ⚠️  Potential False Positive")
                
                if enhanced.enhanced_severity:
                    print(f"      🤖 AI Adjusted Severity: {enhanced.enhanced_severity.upper()}")
                
                if enhanced.ai_analysis:
                    ai = enhanced.ai_analysis
                    print(f"      🎯 Remediation Priority: {ai.remediation_priority}/10")
                    print(f"      🔧 Exploit Complexity: {ai.exploit_complexity}")
                    print(f"      💼 Business Impact: {ai.business_impact[:100]}...")
        else:
            print("   AI Analysis: Not performed (AWS credentials required)")
            
            # Show regular findings
            findings = session.get_all_findings()
            if findings:
                print(f"\n📊 Regular Security Findings:")
                for i, finding in enumerate(findings[:5], 1):
                    print(f"   {i}. [{finding.severity.upper()}] {finding.title}")
                    print(f"      URL: {finding.affected_url}")
                    print(f"      Description: {finding.description[:100]}...")
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
    
    print()
    
    # Test AI client directly (if available)
    print("🧪 Direct AI Client Test")
    print("-" * 25)
    
    ai_client = BedrockAIClient()
    if ai_client.is_enabled():
        print("✅ AWS Bedrock AI client is available")
        model_info = ai_client.get_model_info()
        print(f"   Model: {model_info['model_id']}")
        print(f"   Region: {model_info['region']}")
        print(f"   Capabilities: {', '.join(model_info['capabilities'][:3])}...")
    else:
        print("❌ AWS Bedrock AI client not available")
        print("   Reasons:")
        print("   - boto3 not installed (pip install boto3)")
        print("   - AWS credentials not configured")
        print("   - AWS Bedrock not available in region")
        print("   - Network connectivity issues")
    
    # Cleanup
    await framework.close()
    
    print()
    print("🎯 AI Integration Status Summary")
    print("=" * 35)
    
    if info['ai_enabled']:
        print("✅ AI Integration: FULLY FUNCTIONAL")
        print("✅ AWS Bedrock: Connected")
        print("✅ Enhanced Analysis: Available")
        print("✅ Risk Assessment: AI-Powered")
        print("✅ False Positive Detection: Active")
    else:
        print("⚠️  AI Integration: CONFIGURED BUT INACTIVE")
        print("❌ AWS Bedrock: Not Connected")
        print("⚠️  Enhanced Analysis: Fallback to Basic")
        print("⚠️  Risk Assessment: Rule-Based Only")
        print("❌ False Positive Detection: Disabled")
    
    print()
    print("📋 Setup Instructions for Full AI Integration:")
    print("1. Install boto3: pip install boto3")
    print("2. Configure AWS credentials:")
    print("   - AWS CLI: aws configure")
    print("   - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
    print("   - IAM roles (for EC2/Lambda)")
    print("3. Ensure AWS Bedrock access in your region")
    print("4. Request model access in AWS Bedrock console")
    
    print(f"\n🎉 Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(ai_integration_demo())