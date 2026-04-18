#!/usr/bin/env python3
"""
Demo script to showcase the Web Penetration Testing Framework.
This demonstrates a complete security assessment workflow.
"""

import asyncio
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, 'src')

from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel


async def demo_security_assessment():
    """
    Demonstrate a complete security assessment using the framework.
    """
    print("🚀 Web Penetration Testing Framework - Demo")
    print("=" * 50)
    
    # Initialize framework
    framework = FrameworkCore()
    
    # Create target (using a safe test site)
    target = Target(
        url="https://httpbin.org",
        base_domain="httpbin.org",
        scheme="https"
    )
    
    print(f"🎯 Target: {target.url}")
    print(f"📊 Framework Info: {framework.get_info()}")
    print()
    
    # Phase 1: Passive reconnaissance
    print("🔍 Phase 1: Passive Reconnaissance")
    print("-" * 30)
    
    passive_config = Configuration(
        test_suites=[
            TestSuite.RECONNAISSANCE,
            TestSuite.HEADERS,
            TestSuite.SSL_TLS
        ],
        intensity=IntensityLevel.PASSIVE,
        rate_limit=5,
        timeout=15
    )
    
    try:
        passive_session = await framework.scan(target, passive_config)
        print(f"✅ Passive scan completed")
        print(f"   Findings: {len(passive_session.get_all_findings())}")
        print(f"   Duration: {passive_session.duration_seconds:.2f}s")
        print(f"   Requests: {len(passive_session.results)}")
        
        # Show findings by severity
        if passive_session.get_all_findings():
            findings = passive_session.get_all_findings()
            print("   Severity breakdown:")
            severity_counts = {}
            for finding in findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
            print(f"     Critical: {severity_counts.get('critical', 0)}")
            print(f"     High: {severity_counts.get('high', 0)}")
            print(f"     Medium: {severity_counts.get('medium', 0)}")
            print(f"     Low: {severity_counts.get('low', 0)}")
            print(f"     Info: {severity_counts.get('info', 0)}")
            
            # Show first few findings
            print("\n   Sample findings:")
            for i, finding in enumerate(findings[:3]):
                print(f"     {i+1}. [{finding.severity.upper()}] {finding.title}")
                print(f"        URL: {finding.affected_url}")
        
    except Exception as e:
        print(f"❌ Passive scan failed: {e}")
    
    print()
    
    # Phase 2: Active vulnerability testing (limited for demo)
    print("🎯 Phase 2: Active Security Testing")
    print("-" * 30)
    
    active_config = Configuration(
        test_suites=[
            TestSuite.VULNERABILITY,
            TestSuite.AUTHENTICATION
        ],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=3,  # Be gentle with test site
        timeout=10,
        enable_destructive_tests=False  # Keep it safe
    )
    
    try:
        active_session = await framework.scan(target, active_config)
        print(f"✅ Active scan completed")
        print(f"   Findings: {len(active_session.get_all_findings())}")
        print(f"   Duration: {active_session.duration_seconds:.2f}s")
        print(f"   Requests: {len(active_session.results)}")
        
        # Show findings by severity
        if active_session.get_all_findings():
            findings = active_session.get_all_findings()
            print("   Severity breakdown:")
            severity_counts = {}
            for finding in findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
            print(f"     Critical: {severity_counts.get('critical', 0)}")
            print(f"     High: {severity_counts.get('high', 0)}")
            print(f"     Medium: {severity_counts.get('medium', 0)}")
            print(f"     Low: {severity_counts.get('low', 0)}")
            print(f"     Info: {severity_counts.get('info', 0)}")
            
            # Show first few findings
            print("\n   Sample findings:")
            for i, finding in enumerate(findings[:3]):
                print(f"     {i+1}. [{finding.severity.upper()}] {finding.title}")
                print(f"        URL: {finding.affected_url}")
        
    except Exception as e:
        print(f"❌ Active scan failed: {e}")
    
    print()
    
    # Generate summary report
    print("📊 FINAL ASSESSMENT REPORT")
    print("=" * 30)
    
    try:
        all_findings = (passive_session.get_all_findings() if 'passive_session' in locals() else []) + \
                      (active_session.get_all_findings() if 'active_session' in locals() else [])
        
        print(f"Total findings: {len(all_findings)}")
        
        if all_findings:
            severity_counts = {}
            for finding in all_findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
            print("\nSeverity distribution:")
            for severity, count in severity_counts.items():
                print(f"  {severity.upper()}: {count}")
            
            # Calculate risk score (simplified)
            risk_score = (
                severity_counts.get('critical', 0) * 10 +
                severity_counts.get('high', 0) * 7 +
                severity_counts.get('medium', 0) * 4 +
                severity_counts.get('low', 0) * 2 +
                severity_counts.get('info', 0) * 1
            ) / max(len(all_findings), 1)
            
            print(f"\nRisk Score: {risk_score:.1f}/10")
            
            if risk_score >= 8:
                print("🚨 HIGH RISK - Immediate action required")
            elif risk_score >= 5:
                print("⚠️  MEDIUM RISK - Address critical issues")
            elif risk_score >= 2:
                print("🟡 LOW RISK - Monitor and improve")
            else:
                print("✅ MINIMAL RISK - Good security posture")
        else:
            print("✅ No security issues found")
    
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
    
    # Cleanup
    await framework.close()
    
    print(f"\n🎉 Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Framework is ready for production use!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_security_assessment())