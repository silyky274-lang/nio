#!/usr/bin/env python3
"""
APEX HUNTER - Quick Test Hunt
Test the system with a safe target
"""

import sys
import time
import requests
import subprocess
from datetime import datetime

def test_hunt(target="testphp.vulnweb.com"):
    """Test hunt against a safe target"""
    
    print("🎯 APEX HUNTER - Test Hunt")
    print("=" * 40)
    print(f"🎯 Target: {target}")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 40)
    
    findings = []
    
    # Phase 1: Basic reconnaissance
    print("\n🔍 Phase 1: Reconnaissance")
    print("-" * 30)
    
    try:
        # DNS lookup
        result = subprocess.run(['nslookup', target], 
                              capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(f"✅ DNS resolved: {target}")
            findings.append({
                'type': 'dns_info',
                'value': f'DNS resolution successful for {target}',
                'severity': 'info'
            })
    except Exception as e:
        print(f"❌ DNS lookup failed: {e}")
    
    # Phase 2: HTTP analysis
    print("\n🌐 Phase 2: HTTP Analysis")
    print("-" * 30)
    
    try:
        response = requests.get(f'http://{target}', timeout=30, allow_redirects=True)
        print(f"✅ HTTP Status: {response.status_code}")
        
        # Check headers
        interesting_headers = ['Server', 'X-Powered-By', 'X-Framework']
        for header in interesting_headers:
            if header in response.headers:
                value = response.headers[header]
                print(f"✅ {header}: {value}")
                findings.append({
                    'type': 'technology',
                    'value': f'{header}: {value}',
                    'severity': 'info'
                })
        
        # Check for common vulnerabilities
        html = response.text.lower()
        
        # Framework detection
        if 'wordpress' in html or 'wp-content' in html:
            print("✅ WordPress detected")
            findings.append({
                'type': 'framework',
                'value': 'WordPress CMS detected',
                'severity': 'medium'
            })
        
        if 'drupal' in html:
            print("✅ Drupal detected")
            findings.append({
                'type': 'framework',
                'value': 'Drupal CMS detected',
                'severity': 'medium'
            })
            
    except Exception as e:
        print(f"❌ HTTP analysis failed: {e}")
    
    # Phase 3: Vulnerability testing
    print("\n🛡️  Phase 3: Vulnerability Testing")
    print("-" * 30)
    
    # SQL Injection test (safe payload)
    try:
        test_url = f'http://{target}/?id=1\''
        response = requests.get(test_url, timeout=10)
        
        sql_errors = ['sql', 'mysql', 'error', 'warning', 'syntax']
        if any(error in response.text.lower() for error in sql_errors):
            print("🚨 Potential SQL Injection detected!")
            findings.append({
                'type': 'vulnerability',
                'value': 'Potential SQL Injection',
                'severity': 'high'
            })
        else:
            print("✅ No obvious SQL injection")
            
    except Exception as e:
        print(f"❌ SQL injection test failed: {e}")
    
    # XSS test (safe payload)
    try:
        test_url = f'http://{target}/?q=<script>alert(1)</script>'
        response = requests.get(test_url, timeout=10)
        
        if '<script>alert(1)</script>' in response.text:
            print("🚨 Potential XSS detected!")
            findings.append({
                'type': 'vulnerability',
                'value': 'Potential Cross-Site Scripting (XSS)',
                'severity': 'medium'
            })
        else:
            print("✅ No obvious XSS")
            
    except Exception as e:
        print(f"❌ XSS test failed: {e}")
    
    # Phase 4: Chain analysis
    print("\n⛓️  Phase 4: Chain Analysis")
    print("-" * 30)
    
    chains = []
    high_value_findings = [f for f in findings if f['severity'] in ['medium', 'high', 'critical']]
    
    if len(high_value_findings) >= 2:
        chain = {
            'name': 'Multi-Vulnerability Chain',
            'components': [f['value'] for f in high_value_findings],
            'severity': 'high',
            'estimated_bounty': '$500-$2,000'
        }
        chains.append(chain)
        print(f"🔗 Chain detected: {chain['name']}")
        print(f"   💰 Estimated bounty: {chain['estimated_bounty']}")
    else:
        print("ℹ️  No chains detected (need 2+ medium+ findings)")
    
    # Results summary
    print("\n📊 Hunt Results")
    print("=" * 40)
    print(f"🎯 Target: {target}")
    print(f"🔍 Total findings: {len(findings)}")
    print(f"⛓️  Chain exploits: {len(chains)}")
    
    severity_counts = {}
    for finding in findings:
        severity = finding['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    for severity, count in severity_counts.items():
        print(f"   {severity.upper()}: {count}")
    
    if chains:
        total_bounty = len(chains) * 1000  # Rough estimate
        print(f"💰 Estimated total bounty: ${total_bounty:,}")
    
    print(f"⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 40)
    
    return findings, chains

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "testphp.vulnweb.com"
    
    print("⚠️  ETHICAL TESTING ONLY")
    print("Only test targets you own or have permission to test!")
    print("")
    
    if target != "testphp.vulnweb.com":
        confirm = input(f"Are you authorized to test {target}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Testing cancelled")
            sys.exit(1)
    
    findings, chains = test_hunt(target)
    
    print("\n🎯 Test completed! Use the web interface for advanced hunting:")
    print("   python web_interface.py")
    print("   Then open: http://localhost:8080")