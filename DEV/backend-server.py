#!/usr/bin/env python3
"""
Development Backend API Server for Shaka Security Scanner
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shaka_security_scanner import FrameworkCore
from shaka_security_scanner.models import (
    Target, Configuration, TestSuite, IntensityLevel,
    ScanStatus, Severity
)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend-logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Simple HTTP server using aiohttp
try:
    from aiohttp import web
except ImportError:
    logger.error("aiohttp not installed. Installing...")
    os.system("pip3 install aiohttp aiohttp-cors")
    from aiohttp import web

import aiohttp_cors

# Global framework instance
framework = None
active_scans: Dict[str, Any] = {}

async def init_framework():
    """Initialize the framework"""
    global framework
    logger.info("Initializing Shaka Security Scanner Framework...")
    framework = FrameworkCore()
    logger.info("Framework initialized successfully")

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "Shaka Security Scanner",
        "version": "1.3.0",
        "timestamp": datetime.now().isoformat(),
        "aws_profile": os.getenv("AWS_PROFILE", "default"),
        "ai_enabled": True
    })

async def list_scanners(request):
    """List available scanner modules"""
    scanners = [
        {
            "id": "reconnaissance",
            "name": "Reconnaissance",
            "description": "Technology detection, endpoint discovery",
            "type": "passive"
        },
        {
            "id": "vulnerability",
            "name": "Vulnerability Scanner",
            "description": "SQL injection, XSS, CSRF testing",
            "type": "active"
        },
        {
            "id": "advanced_vulnerability",
            "name": "Advanced Vulnerability",
            "description": "SSRF, XXE, Template Injection, NoSQL",
            "type": "active"
        },
        {
            "id": "cms_vulnerability",
            "name": "CMS Vulnerability",
            "description": "WordPress, Drupal, Joomla, Magento",
            "type": "active"
        },
        {
            "id": "headers",
            "name": "Security Headers",
            "description": "HSTS, CSP, X-Frame-Options analysis",
            "type": "passive"
        },
        {
            "id": "ssl_tls",
            "name": "SSL/TLS Scanner",
            "description": "Certificate and protocol analysis",
            "type": "passive"
        },
        {
            "id": "authentication",
            "name": "Authentication",
            "description": "Default credentials, brute force",
            "type": "active"
        },
        {
            "id": "input_validation",
            "name": "Input Validation",
            "description": "Command injection, path traversal",
            "type": "active"
        },
        {
            "id": "api",
            "name": "API Security",
            "description": "OWASP API Top 10 testing",
            "type": "active"
        }
    ]
    return web.json_response({"scanners": scanners})

async def create_scan(request):
    """Create a new scan"""
    try:
        data = await request.json()
        
        # Parse target
        target = Target(
            url=data["target"]["url"],
            base_domain=data["target"].get("base_domain", data["target"]["url"].split("//")[1].split("/")[0]),
            scheme=data["target"].get("scheme", "https")
        )
        
        # Parse configuration
        test_suites = [TestSuite(s) for s in data["config"]["test_suites"]]
        intensity = IntensityLevel(data["config"].get("intensity", "passive"))
        
        config = Configuration(
            test_suites=test_suites,
            intensity=intensity,
            rate_limit=data["config"].get("rate_limit", 10),
            timeout=data["config"].get("timeout", 30),
            enable_ai_analysis=data["config"].get("enable_ai_analysis", True)
        )
        
        # Start scan in background
        scan_id = f"scan-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Creating scan {scan_id} for {target.url}")
        
        # Store scan info
        active_scans[scan_id] = {
            "id": scan_id,
            "target": target,
            "config": config,
            "status": ScanStatus.QUEUED,
            "progress": 0.0,
            "start_time": datetime.now().isoformat(),
            "findings": []
        }
        
        # Start scan asynchronously
        asyncio.create_task(run_scan(scan_id, target, config))
        
        return web.json_response({
            "scan_id": scan_id,
            "status": "queued",
            "message": "Scan created successfully"
        })
        
    except Exception as e:
        logger.error(f"Error creating scan: {e}", exc_info=True)
        return web.json_response({
            "error": str(e)
        }, status=400)

async def run_scan(scan_id: str, target: Target, config: Configuration):
    """Run scan in background"""
    try:
        logger.info(f"Starting scan {scan_id}")
        active_scans[scan_id]["status"] = ScanStatus.RUNNING
        
        # Run the actual scan
        session = await framework.scan(target, config)
        
        # Update scan results
        active_scans[scan_id]["status"] = ScanStatus.COMPLETED
        active_scans[scan_id]["progress"] = 1.0
        active_scans[scan_id]["end_time"] = datetime.now().isoformat()
        active_scans[scan_id]["findings"] = [
            {
                "id": f.id,
                "title": f.title,
                "severity": f.severity.value,
                "category": f.category.value,
                "affected_url": f.affected_url,
                "description": f.description
            }
            for f in session.get_all_findings()
        ]
        
        logger.info(f"Scan {scan_id} completed with {len(session.get_all_findings())} findings")
        
    except Exception as e:
        logger.error(f"Error running scan {scan_id}: {e}", exc_info=True)
        active_scans[scan_id]["status"] = ScanStatus.FAILED
        active_scans[scan_id]["error"] = str(e)

async def get_scan(request):
    """Get scan status and results"""
    scan_id = request.match_info['scan_id']
    
    if scan_id not in active_scans:
        return web.json_response({
            "error": "Scan not found"
        }, status=404)
    
    scan = active_scans[scan_id]
    
    return web.json_response({
        "id": scan["id"],
        "status": scan["status"].value if hasattr(scan["status"], 'value') else scan["status"],
        "progress": scan["progress"],
        "start_time": scan["start_time"],
        "end_time": scan.get("end_time"),
        "findings_count": len(scan.get("findings", [])),
        "findings": scan.get("findings", [])
    })

async def list_scans(request):
    """List all scans"""
    scans = [
        {
            "id": scan["id"],
            "status": scan["status"].value if hasattr(scan["status"], 'value') else scan["status"],
            "progress": scan["progress"],
            "start_time": scan["start_time"],
            "findings_count": len(scan.get("findings", []))
        }
        for scan in active_scans.values()
    ]
    
    return web.json_response({"scans": scans})

async def on_startup(app):
    """Startup handler"""
    await init_framework()

def main():
    """Main entry point"""
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_get('/api/v1/scanners', list_scanners)
    app.router.add_post('/api/v1/scans', create_scan)
    app.router.add_get('/api/v1/scans', list_scans)
    app.router.add_get('/api/v1/scans/{scan_id}', get_scan)
    
    # Configure CORS on all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    # Startup handler
    app.on_startup.append(on_startup)
    
    # Run server
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
