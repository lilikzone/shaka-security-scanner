#!/usr/bin/env python3
"""
CMS Vulnerability Scanner Demo - Comprehensive CMS Security Testing

This demo showcases the CMS-specific vulnerability testing capabilities
of Shaka Security Scanner for WordPress, Drupal, Joomla, Magento, and other platforms.
"""

import asyncio
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the src directory to Python path
sys.path.insert(0, 'src')

from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import Target, Configuration, TestSuite, IntensityLevel


console = Console()


async def main():
    """Run CMS vulnerability scanning demo."""
    
    # Demo header
    console.print(Panel.fit(
        "[bold blue]🔥 Shaka Security Scanner - CMS Vulnerability Testing Demo[/bold blue]\n"
        "[yellow]Comprehensive CMS Security Testing for WordPress, Drupal, Joomla & More[/yellow]",
        border_style="blue"
    ))
    
    # Initialize framework
    console.print("\n[cyan]🚀 Initializing Shaka Security Scanner...[/cyan]")
    framework = FrameworkCore()
    
    # Display framework info
    info = framework.get_info()
    console.print(f"[green]✅ Framework initialized: {info['scanners_registered']} scanners registered[/green]")
    
    # Demo targets (replace with actual test targets you have permission to test)
    demo_targets = [
        {
            "name": "WordPress Demo Site",
            "url": "https://demo.wordpress.org",
            "description": "Official WordPress demo site"
        },
        {
            "name": "Local WordPress",
            "url": "http://localhost/wordpress",
            "description": "Local WordPress installation"
        },
        {
            "name": "Drupal Demo",
            "url": "https://simplytest.me/project/drupal",
            "description": "Drupal testing environment"
        }
    ]
    
    console.print("\n[cyan]🎯 Available Demo Targets:[/cyan]")
    target_table = Table(show_header=True, header_style="bold magenta")
    target_table.add_column("Name", style="cyan")
    target_table.add_column("URL", style="yellow")
    target_table.add_column("Description", style="green")
    
    for target in demo_targets:
        target_table.add_row(target["name"], target["url"], target["description"])
    
    console.print(target_table)
    
    # For demo purposes, we'll use httpbin.org as a safe target
    console.print("\n[yellow]⚠️  For demo safety, using httpbin.org as test target[/yellow]")
    console.print("[dim]In real usage, replace with your authorized test targets[/dim]")
    
    # Configure target
    target = Target(
        url="https://httpbin.org",
        base_domain="httpbin.org",
        scheme="https"
    )
    
    # Configure CMS-specific scan
    config = Configuration(
        test_suites=[TestSuite.CMS_VULNERABILITY, TestSuite.RECONNAISSANCE],
        intensity=IntensityLevel.ACTIVE,
        rate_limit=5,  # Be respectful to demo targets
        timeout=30
    )
    
    console.print(f"\n[cyan]🔍 Starting CMS vulnerability scan of {target.url}[/cyan]")
    console.print("[dim]Scan configuration:[/dim]")
    console.print(f"[dim]  • Test Suites: {', '.join(config.test_suites)}[/dim]")
    console.print(f"[dim]  • Intensity: {config.intensity}[/dim]")
    console.print(f"[dim]  • Rate Limit: {config.rate_limit} req/sec[/dim]")
    
    # Run scan with progress indicator
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scanning for CMS vulnerabilities...", total=None)
        
        try:
            # Execute scan
            session = await framework.scan(target, config)
            
            progress.update(task, description="Scan completed!")
            
        except Exception as e:
            progress.update(task, description=f"Scan failed: {e}")
            console.print(f"[red]❌ Scan failed: {e}[/red]")
            return
    
    scan_duration = time.time() - start_time
    
    # Display results
    console.print(f"\n[green]✅ CMS vulnerability scan completed in {scan_duration:.2f} seconds[/green]")
    console.print(f"[cyan]📊 Scan Results Summary:[/cyan]")
    console.print(f"  • Total Findings: {len(session.findings)}")
    console.print(f"  • Critical: {session.get_critical_count()}")
    console.print(f"  • High: {session.get_high_count()}")
    console.print(f"  • Medium: {session.get_medium_count()}")
    console.print(f"  • Low: {session.get_low_count()}")
    console.print(f"  • Info: {session.get_info_count()}")
    
    # Display detailed findings
    if session.findings:
        console.print("\n[cyan]🔍 Detailed Findings:[/cyan]")
        
        findings_table = Table(show_header=True, header_style="bold magenta")
        findings_table.add_column("Severity", style="red")
        findings_table.add_column("Title", style="cyan")
        findings_table.add_column("Category", style="yellow")
        findings_table.add_column("URL", style="green")
        
        for finding in session.findings[:10]:  # Show first 10 findings
            severity_color = {
                "critical": "bright_red",
                "high": "red",
                "medium": "yellow",
                "low": "blue",
                "info": "cyan"
            }.get(finding.severity.lower(), "white")
            
            findings_table.add_row(
                f"[{severity_color}]{finding.severity.upper()}[/{severity_color}]",
                finding.title[:50] + "..." if len(finding.title) > 50 else finding.title,
                finding.category,
                finding.affected_url[:40] + "..." if len(finding.affected_url) > 40 else finding.affected_url
            )
        
        console.print(findings_table)
        
        if len(session.findings) > 10:
            console.print(f"[dim]... and {len(session.findings) - 10} more findings[/dim]")
    else:
        console.print("\n[green]✅ No vulnerabilities detected![/green]")
        console.print("[dim]Note: httpbin.org is not a CMS, so no CMS-specific vulnerabilities were found.[/dim]")
    
    # CMS Testing Capabilities Overview
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold cyan]🎯 CMS Vulnerability Testing Capabilities[/bold cyan]\n\n"
        "[yellow]WordPress Testing:[/yellow]\n"
        "  • User enumeration (REST API, author parameter)\n"
        "  • XML-RPC interface detection\n"
        "  • Directory listing vulnerabilities\n"
        "  • Configuration file exposure\n"
        "  • Plugin vulnerability detection\n"
        "  • Version disclosure\n\n"
        "[yellow]Drupal Testing:[/yellow]\n"
        "  • Version disclosure detection\n"
        "  • Admin panel accessibility\n"
        "  • Module vulnerability scanning\n"
        "  • Configuration exposure\n\n"
        "[yellow]Joomla Testing:[/yellow]\n"
        "  • Administrator panel detection\n"
        "  • Configuration file exposure\n"
        "  • Extension vulnerability scanning\n"
        "  • Version disclosure\n\n"
        "[yellow]Magento Testing:[/yellow]\n"
        "  • Admin panel detection\n"
        "  • Downloader interface exposure\n"
        "  • Configuration vulnerabilities\n\n"
        "[yellow]Generic CMS Testing:[/yellow]\n"
        "  • Backup file detection\n"
        "  • Admin panel security\n"
        "  • Common misconfigurations\n"
        "  • Information disclosure",
        border_style="cyan"
    ))
    
    # Real-world usage examples
    console.print("\n[cyan]💡 Real-World Usage Examples:[/cyan]")
    
    examples = [
        {
            "scenario": "WordPress Security Audit",
            "command": "python cms_demo.py --target https://your-wordpress-site.com --cms wordpress",
            "description": "Comprehensive WordPress security testing"
        },
        {
            "scenario": "Multi-CMS Environment",
            "command": "python cms_demo.py --target-list sites.txt --all-cms",
            "description": "Scan multiple sites for various CMS vulnerabilities"
        },
        {
            "scenario": "Plugin Vulnerability Check",
            "command": "python cms_demo.py --target https://site.com --focus plugins",
            "description": "Focus on plugin/extension vulnerabilities"
        }
    ]
    
    for example in examples:
        console.print(f"\n[yellow]📋 {example['scenario']}:[/yellow]")
        console.print(f"[dim]Command: {example['command']}[/dim]")
        console.print(f"[dim]Description: {example['description']}[/dim]")
    
    # Security recommendations
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold red]⚠️  SECURITY RECOMMENDATIONS[/bold red]\n\n"
        "[yellow]1. Authorization:[/yellow] Only test systems you own or have explicit permission to test\n"
        "[yellow]2. Rate Limiting:[/yellow] Use appropriate rate limits to avoid disrupting services\n"
        "[yellow]3. Responsible Disclosure:[/yellow] Report vulnerabilities responsibly to site owners\n"
        "[yellow]4. Legal Compliance:[/yellow] Ensure compliance with local laws and regulations\n"
        "[yellow]5. Documentation:[/yellow] Keep detailed records of testing activities",
        border_style="red"
    ))
    
    console.print(f"\n[green]🎉 CMS Vulnerability Scanner Demo Completed![/green]")
    console.print(f"[cyan]📈 Framework Status: {info['scanners_registered']} scanners ready for enterprise testing[/cyan]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")