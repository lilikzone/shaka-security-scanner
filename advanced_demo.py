#!/usr/bin/env python3
"""
Advanced Vulnerability Testing Demo - Showcase advanced security testing capabilities.

This demo demonstrates the enhanced vulnerability testing features including:
- Time-based blind SQL injection
- Union-based SQL injection
- NoSQL injection
- Advanced XSS (Stored, DOM-based, Filter bypass)
- SSRF (Server-Side Request Forgery)
- XXE (XML External Entity)
- Template Injection
- LDAP Injection
"""

import asyncio
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, 'src')

from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel


async def advanced_vulnerability_demo():
    """
    Demonstrate advanced vulnerability testing capabilities.
    """
    print("🔥 Shaka Security Scanner - Advanced Vulnerability Testing Demo")
    print("=" * 70)
    
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
    
    # Phase 1: Advanced SQL Injection Testing
    print("💉 Phase 1: Advanced SQL Injection Testing")
    print("-" * 45)
    
    advanced_config = Configuration(
        test_suites=[TestSuite.ADVANCED_VULNERABILITY],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=2,  # Be gentle with test site
        timeout=30,    # Longer timeout for time-based tests
        enable_destructive_tests=False,  # Keep it safe
        enable_ai_analysis=True
    )
    
    try:
        session = await framework.scan(target, advanced_config)
        
        print(f"✅ Advanced vulnerability scan completed")
        print(f"   Findings: {len(session.get_all_findings())}")
        print(f"   Duration: {session.duration_seconds:.2f}s")
        print(f"   Status: {session.status}")
        
        # Show findings by category
        if session.get_all_findings():
            findings = session.get_all_findings()
            print("\n   🔍 Advanced Vulnerability Findings:")
            
            # Group findings by category
            categories = {}
            for finding in findings:
                category = finding.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(finding)
            
            for category, category_findings in categories.items():
                print(f"\n   📂 {category.upper().replace('_', ' ')} ({len(category_findings)} findings)")
                
                for i, finding in enumerate(category_findings[:3], 1):  # Show first 3
                    print(f"     {i}. [{finding.severity.upper()}] {finding.title}")
                    print(f"        URL: {finding.affected_url}")
                    print(f"        Description: {finding.description[:100]}...")
                    if finding.proof_of_concept:
                        poc_preview = finding.proof_of_concept.replace('\n', ' ')[:80]
                        print(f"        PoC: {poc_preview}...")
                    print()
                
                if len(category_findings) > 3:
                    print(f"     ... and {len(category_findings) - 3} more findings")
        
        # AI Analysis Results (if available)
        if hasattr(session, 'enhanced_findings') and session.enhanced_findings:
            print(f"\n🤖 AI-Enhanced Analysis Results:")
            print(f"   Enhanced Findings: {len(session.enhanced_findings)}")
            
            if hasattr(session, 'ai_analysis_summary') and session.ai_analysis_summary:
                summary = session.ai_analysis_summary
                print(f"   AI Analysis Rate: {summary.get('ai_analysis_rate', 0):.1%}")
                print(f"   False Positives Detected: {summary.get('false_positives_detected', 0)}")
                print(f"   Average Risk Score: {summary.get('average_risk_score', 0):.1f}/10")
                
                # Show top AI-enhanced findings
                print(f"\n   🎯 Top AI-Enhanced Findings:")
                for i, enhanced in enumerate(session.enhanced_findings[:3], 1):
                    finding = enhanced.original_finding
                    print(f"     {i}. [{finding.severity.upper()}] {finding.title}")
                    print(f"        Risk Score: {enhanced.risk_score:.1f}/10")
                    
                    if enhanced.is_false_positive:
                        print(f"        ⚠️  Potential False Positive (Confidence: {enhanced.false_positive_confidence:.1%})")
                    
                    if enhanced.ai_analysis:
                        ai = enhanced.ai_analysis
                        print(f"        🎯 Remediation Priority: {ai.remediation_priority}/10")
                        print(f"        🔧 Exploit Complexity: {ai.exploit_complexity}")
                        print(f"        💼 Business Impact: {ai.business_impact[:80]}...")
                    print()
        else:
            print(f"\n🤖 AI Analysis: Not performed (AWS credentials required)")
        
    except Exception as e:
        print(f"❌ Advanced vulnerability scan failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Phase 2: Comprehensive Security Assessment
    print("🔍 Phase 2: Comprehensive Security Assessment")
    print("-" * 45)
    
    comprehensive_config = Configuration(
        test_suites=[
            TestSuite.RECONNAISSANCE,
            TestSuite.VULNERABILITY,
            TestSuite.ADVANCED_VULNERABILITY,
            TestSuite.HEADERS,
            TestSuite.SSL_TLS
        ],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=3,
        timeout=20,
        enable_ai_analysis=True
    )
    
    try:
        comprehensive_session = await framework.scan(target, comprehensive_config)
        
        print(f"✅ Comprehensive assessment completed")
        print(f"   Total Findings: {len(comprehensive_session.get_all_findings())}")
        print(f"   Duration: {comprehensive_session.duration_seconds:.2f}s")
        print(f"   Scanners Run: {len(comprehensive_session.results)}")
        
        # Advanced Risk Assessment
        if comprehensive_session.get_all_findings():
            findings = comprehensive_session.get_all_findings()
            
            # Severity distribution
            severity_counts = {}
            category_counts = {}
            
            for finding in findings:
                # Count by severity
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
                # Count by category
                category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
            
            print(f"\n   📊 Security Assessment Summary:")
            print(f"   Severity Distribution:")
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    print(f"     {severity.upper()}: {count}")
            
            print(f"\n   Vulnerability Categories:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                category_name = category.replace('_', ' ').title()
                print(f"     {category_name}: {count}")
            
            # Advanced Risk Calculation
            risk_weights = {
                'critical': 10,
                'high': 7,
                'medium': 4,
                'low': 2,
                'info': 1
            }
            
            total_risk_score = sum(
                severity_counts.get(severity, 0) * weight 
                for severity, weight in risk_weights.items()
            )
            
            max_possible_score = len(findings) * 10
            normalized_risk = (total_risk_score / max_possible_score) * 10 if max_possible_score > 0 else 0
            
            print(f"\n   🎯 Advanced Risk Assessment:")
            print(f"   Total Risk Score: {total_risk_score}")
            print(f"   Normalized Risk: {normalized_risk:.1f}/10")
            
            # Risk Level Classification
            if normalized_risk >= 8:
                risk_level = "🚨 CRITICAL RISK"
                recommendation = "Immediate remediation required"
            elif normalized_risk >= 6:
                risk_level = "🔴 HIGH RISK"
                recommendation = "Address critical and high severity issues immediately"
            elif normalized_risk >= 4:
                risk_level = "🟡 MEDIUM RISK"
                recommendation = "Plan remediation for high and medium severity issues"
            elif normalized_risk >= 2:
                risk_level = "🟢 LOW RISK"
                recommendation = "Monitor and address issues during regular maintenance"
            else:
                risk_level = "✅ MINIMAL RISK"
                recommendation = "Good security posture, continue monitoring"
            
            print(f"   Risk Level: {risk_level}")
            print(f"   Recommendation: {recommendation}")
            
            # Top Priority Findings
            high_priority_findings = [
                f for f in findings 
                if f.severity in ['critical', 'high']
            ]
            
            if high_priority_findings:
                print(f"\n   🚨 High Priority Findings (Top 5):")
                for i, finding in enumerate(high_priority_findings[:5], 1):
                    print(f"     {i}. [{finding.severity.upper()}] {finding.title}")
                    print(f"        Category: {finding.category.replace('_', ' ').title()}")
                    print(f"        URL: {finding.affected_url}")
                    print(f"        Remediation: {finding.remediation[:100]}...")
                    print()
        
    except Exception as e:
        print(f"❌ Comprehensive assessment failed: {e}")
    
    print()
    
    # Phase 3: Advanced Testing Capabilities Summary
    print("📋 Phase 3: Advanced Testing Capabilities")
    print("-" * 45)
    
    print("✅ Advanced SQL Injection Testing:")
    print("   • Time-based blind SQL injection (MySQL, PostgreSQL, MSSQL, Oracle, SQLite)")
    print("   • Union-based SQL injection with information extraction")
    print("   • Second-order SQL injection detection")
    print("   • NoSQL injection (MongoDB, etc.)")
    
    print("\n✅ Advanced Cross-Site Scripting (XSS):")
    print("   • Stored XSS with persistence testing")
    print("   • DOM-based XSS with sink detection")
    print("   • Filter bypass techniques and encoding")
    print("   • Context-aware XSS detection")
    
    print("\n✅ Server-Side Attacks:")
    print("   • SSRF with cloud metadata access")
    print("   • XXE with external entity exploitation")
    print("   • Template injection (Jinja2, Freemarker, Velocity, etc.)")
    print("   • LDAP injection testing")
    
    print("\n✅ AI-Powered Analysis:")
    print("   • False positive detection and filtering")
    print("   • Risk scoring and prioritization")
    print("   • Business impact assessment")
    print("   • Remediation guidance and complexity analysis")
    
    # Cleanup
    await framework.close()
    
    print()
    print("🎉 ADVANCED VULNERABILITY TESTING DEMO COMPLETED")
    print("=" * 55)
    print("🔥 Shaka Security Scanner now includes enterprise-grade")
    print("   advanced vulnerability testing capabilities!")
    print()
    print("📚 Key Features Demonstrated:")
    print("   ✅ 8+ Advanced Vulnerability Types")
    print("   ✅ 50+ Specialized Attack Payloads")
    print("   ✅ AI-Enhanced Analysis & Risk Scoring")
    print("   ✅ Professional Risk Assessment")
    print("   ✅ Comprehensive Reporting")
    print()
    print(f"🎯 Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Ready for professional penetration testing!")


if __name__ == "__main__":
    # Run the advanced demo
    asyncio.run(advanced_vulnerability_demo())