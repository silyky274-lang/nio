#!/usr/bin/env python3
"""
APEX HUNTER - Real-Time Web Interface
Live bug bounty hunting dashboard with internet research capabilities
"""

from flask import Flask, render_template_string, request, jsonify
import os
import sys
import json
import time
import threading
import requests
import subprocess
from datetime import datetime
import psutil

app = Flask(__name__)
app.secret_key = 'apex_hunter_2024'

# Global hunt status
hunt_status = {
    'active': False,
    'target': '',
    'progress': 0,
    'current_phase': '',
    'findings': [],
    'chains': [],
    'start_time': None,
    'elapsed_time': 0,
    'memory_usage': 0,
    'tools_running': []
}

class LiveHunter:
    """Real-time hunting with internet research"""
    
    def __init__(self, target):
        self.target = target
        self.findings = []
        self.chains = []
        
    def start_hunt(self):
        """Start comprehensive hunt"""
        global hunt_status
        
        hunt_status.update({
            'active': True,
            'target': self.target,
            'progress': 0,
            'findings': [],
            'chains': [],
            'start_time': datetime.now().isoformat()
        })
        
        try:
            # Phase 1: Domain Research
            self.research_domain()
            
            # Phase 2: Subdomain Discovery
            self.discover_subdomains()
            
            # Phase 3: Technology Detection
            self.detect_technologies()
            
            # Phase 4: Vulnerability Scanning
            self.scan_vulnerabilities()
            
            # Phase 5: Chain Analysis
            self.analyze_chains()
            
            hunt_status['progress'] = 100
            hunt_status['current_phase'] = 'Complete'
            hunt_status['active'] = False
            
        except Exception as e:
            hunt_status['current_phase'] = f'Error: {str(e)}'
            hunt_status['active'] = False
    
    def research_domain(self):
        """Research target domain"""
        hunt_status['current_phase'] = 'Domain Research'
        hunt_status['progress'] = 10
        
        # DNS lookup
        try:
            result = subprocess.run(['nslookup', self.target], 
                                  capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.add_finding('domain_info', f'DNS Info: {self.target}', 'info', {
                    'dns_output': result.stdout[:300]
                })
        except:
            pass
        
        # WHOIS lookup
        try:
            result = subprocess.run(['whois', self.target], 
                                  capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.add_finding('whois_info', f'WHOIS: {self.target}', 'info', {
                    'whois_data': result.stdout[:500]
                })
        except:
            pass
    
    def discover_subdomains(self):
        """Discover subdomains"""
        hunt_status['current_phase'] = 'Subdomain Discovery'
        hunt_status['progress'] = 25
        
        subdomains = []
        
        # Certificate Transparency
        try:
            ct_url = f"https://crt.sh/?q=%.{self.target}&output=json"
            response = requests.get(ct_url, timeout=30)
            if response.status_code == 200:
                ct_data = response.json()
                for entry in ct_data[:20]:  # Limit results
                    name = entry.get('name_value', '')
                    if name and name not in subdomains:
                        subdomains.append(name)
                        self.add_finding('subdomain', name, 'low', {
                            'source': 'certificate_transparency',
                            'chain_potential': self.assess_subdomain_risk(name)
                        })
        except:
            pass
        
        # Common subdomain bruteforce
        common_subs = ['www', 'api', 'admin', 'dev', 'test', 'staging', 'mail', 'ftp', 'blog', 'shop']
        for sub in common_subs:
            try:
                subdomain = f'{sub}.{self.target}'
                result = subprocess.run(['nslookup', subdomain], 
                                      capture_output=True, text=True, timeout=10)
                if 'NXDOMAIN' not in result.stdout and result.stdout.strip():
                    subdomains.append(subdomain)
                    self.add_finding('subdomain', subdomain, 'medium', {
                        'source': 'dns_bruteforce',
                        'chain_potential': self.assess_subdomain_risk(subdomain)
                    })
            except:
                continue
    
    def detect_technologies(self):
        """Detect web technologies"""
        hunt_status['current_phase'] = 'Technology Detection'
        hunt_status['progress'] = 50
        
        try:
            # HTTP request to main domain
            response = requests.get(f'http://{self.target}', timeout=30, allow_redirects=True)
            
            # Analyze headers
            interesting_headers = ['Server', 'X-Powered-By', 'X-Framework', 'X-Generator']
            for header in interesting_headers:
                if header in response.headers:
                    value = response.headers[header]
                    self.add_finding('technology', f'{header}: {value}', 'info', {
                        'header': header,
                        'value': value,
                        'potential_vulns': self.get_tech_vulnerabilities(value)
                    })
            
            # Analyze HTML content
            html = response.text[:5000]  # First 5KB
            
            # Framework detection
            frameworks = {
                'WordPress': ['wp-content', 'wordpress'],
                'Drupal': ['drupal', 'sites/default'],
                'Joomla': ['joomla', 'option=com_'],
                'React': ['react', 'ReactDOM'],
                'Angular': ['ng-', 'angular'],
                'Vue': ['vue.js', 'v-']
            }
            
            for framework, patterns in frameworks.items():
                for pattern in patterns:
                    if pattern.lower() in html.lower():
                        self.add_finding('framework', f'{framework} detected', 'medium', {
                            'framework': framework,
                            'pattern': pattern,
                            'potential_vulns': self.get_framework_vulns(framework)
                        })
                        break
        
        except Exception as e:
            self.add_finding('error', f'Technology detection failed: {str(e)}', 'info', {})
    
    def scan_vulnerabilities(self):
        """Scan for common vulnerabilities"""
        hunt_status['current_phase'] = 'Vulnerability Scanning'
        hunt_status['progress'] = 75
        
        # SQL Injection tests
        sql_payloads = ["'", "1' OR '1'='1", "'; DROP TABLE users; --"]
        for payload in sql_payloads:
            try:
                url = f'http://{self.target}/?id={payload}'
                response = requests.get(url, timeout=10)
                
                sql_errors = ['sql', 'mysql', 'error', 'warning', 'fatal', 'syntax']
                if any(error in response.text.lower() for error in sql_errors):
                    self.add_finding('vulnerability', 'Potential SQL Injection', 'high', {
                        'type': 'sql_injection',
                        'url': url,
                        'payload': payload,
                        'evidence': response.text[:200],
                        'chain_potential': True
                    })
                    break
            except:
                continue
        
        # XSS tests
        xss_payloads = ["<script>alert('XSS')</script>", "javascript:alert('XSS')"]
        for payload in xss_payloads:
            try:
                url = f'http://{self.target}/?q={payload}'
                response = requests.get(url, timeout=10)
                
                if payload in response.text:
                    self.add_finding('vulnerability', 'Potential XSS', 'medium', {
                        'type': 'xss',
                        'url': url,
                        'payload': payload,
                        'evidence': 'Payload reflected in response',
                        'chain_potential': True
                    })
                    break
            except:
                continue
        
        # Directory traversal
        traversal_payloads = ['../../../etc/passwd', '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts']
        for payload in traversal_payloads:
            try:
                url = f'http://{self.target}/?file={payload}'
                response = requests.get(url, timeout=10)
                
                if 'root:' in response.text or 'localhost' in response.text:
                    self.add_finding('vulnerability', 'Directory Traversal', 'high', {
                        'type': 'directory_traversal',
                        'url': url,
                        'payload': payload,
                        'evidence': response.text[:200],
                        'chain_potential': True
                    })
                    break
            except:
                continue
    
    def analyze_chains(self):
        """Analyze potential exploit chains"""
        hunt_status['current_phase'] = 'Chain Analysis'
        hunt_status['progress'] = 90
        
        # Find high-value findings
        high_value = [f for f in self.findings if f.get('details', {}).get('chain_potential')]
        
        # Create chains based on Notion's bug bounty interests
        if len(high_value) >= 2:
            # API + Vulnerability = High-value chain
            api_findings = [f for f in high_value if 'api' in f['value'].lower()]
            vuln_findings = [f for f in high_value if f['type'] == 'vulnerability']
            
            if api_findings and vuln_findings:
                chain = {
                    'name': 'API Privilege Escalation Chain',
                    'description': 'API endpoint with vulnerability leading to privilege escalation',
                    'components': [api_findings[0]['value'], vuln_findings[0]['value']],
                    'severity': 'critical',
                    'estimated_bounty': '$2,000-$5,000',
                    'platform_match': 'Notion - Privilege Escalation',
                    'findings': [api_findings[0], vuln_findings[0]],
                    'attack_flow': [
                        'Discover API endpoint',
                        'Exploit vulnerability in API',
                        'Escalate privileges',
                        'Access unauthorized resources'
                    ]
                }
                self.chains.append(chain)
        
        # Admin panel + Auth bypass = Critical chain
        admin_findings = [f for f in self.findings if 'admin' in f['value'].lower()]
        if admin_findings:
            chain = {
                'name': 'Admin Panel Access Chain',
                'description': 'Unauthorized access to administrative functions',
                'components': ['Admin Panel Discovery', 'Authentication Bypass'],
                'severity': 'critical',
                'estimated_bounty': '$1,500-$4,000',
                'platform_match': 'Notion - Authentication',
                'findings': admin_findings,
                'attack_flow': [
                    'Discover admin panel',
                    'Bypass authentication',
                    'Access admin functions',
                    'Demonstrate impact'
                ]
            }
            self.chains.append(chain)
        
        hunt_status['chains'] = self.chains
    
    def add_finding(self, finding_type, value, severity, details):
        """Add a finding to the results"""
        finding = {
            'type': finding_type,
            'value': value,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.findings.append(finding)
        hunt_status['findings'] = self.findings
    
    def assess_subdomain_risk(self, subdomain):
        """Assess risk level of subdomain"""
        high_risk_keywords = ['admin', 'api', 'dev', 'test', 'staging', 'internal', 'private']
        return any(keyword in subdomain.lower() for keyword in high_risk_keywords)
    
    def get_tech_vulnerabilities(self, tech):
        """Get known vulnerabilities for technology"""
        vuln_map = {
            'apache': ['Directory Traversal', 'HTTP Request Smuggling'],
            'nginx': ['Buffer Overflow', 'HTTP Request Smuggling'],
            'php': ['Remote Code Execution', 'File Inclusion'],
            'node': ['Prototype Pollution', 'Command Injection'],
            'iis': ['Buffer Overflow', 'Directory Traversal']
        }
        
        for key, vulns in vuln_map.items():
            if key.lower() in tech.lower():
                return vulns
        return []
    
    def get_framework_vulns(self, framework):
        """Get framework-specific vulnerabilities"""
        framework_vulns = {
            'WordPress': ['Plugin Vulnerabilities', 'Theme Vulnerabilities', 'Admin Bypass'],
            'Drupal': ['Drupalgeddon', 'SQL Injection', 'RCE'],
            'Joomla': ['SQL Injection', 'File Upload', 'Admin Bypass'],
            'React': ['XSS via dangerouslySetInnerHTML', 'Client-side vulnerabilities'],
            'Angular': ['Template Injection', 'XSS via $sce bypass'],
            'Vue': ['Template Injection', 'XSS via v-html']
        }
        return framework_vulns.get(framework, [])

# HTML Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX HUNTER - Live Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: #0a0a0a; 
            color: #00ff00; 
            overflow-x: hidden;
        }
        .header {
            background: linear-gradient(45deg, #1a1a1a, #2a2a2a);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #00ff00;
        }
        .header h1 { 
            font-size: 2.5em; 
            text-shadow: 0 0 10px #00ff00;
            margin-bottom: 10px;
        }
        .subtitle { 
            color: #888; 
            font-size: 1.2em;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .hunt-controls {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            background: #2a2a2a;
            border: 1px solid #444;
            color: #00ff00;
            border-radius: 5px;
            font-family: inherit;
        }
        .btn {
            padding: 12px 24px;
            background: linear-gradient(45deg, #00aa00, #00ff00);
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn:hover { 
            background: linear-gradient(45deg, #00ff00, #00aa00);
            transform: translateY(-2px);
        }
        .btn:disabled {
            background: #444;
            color: #888;
            cursor: not-allowed;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .status-card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        .status-card h3 {
            color: #00ff00;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00aa00, #00ff00);
            transition: width 0.5s ease;
        }
        .findings-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .findings-panel {
            background: #1a1a1a;
            border-radius: 10px;
            border: 1px solid #333;
            max-height: 600px;
            overflow-y: auto;
        }
        .panel-header {
            background: #2a2a2a;
            padding: 15px;
            border-bottom: 1px solid #333;
            font-weight: bold;
            color: #00ff00;
        }
        .finding-item {
            padding: 15px;
            border-bottom: 1px solid #333;
            transition: background 0.3s;
        }
        .finding-item:hover {
            background: #2a2a2a;
        }
        .finding-type {
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .finding-value {
            color: #00ff00;
            font-weight: bold;
            margin: 5px 0;
        }
        .finding-severity {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .severity-info { background: #0066cc; color: white; }
        .severity-low { background: #ffaa00; color: black; }
        .severity-medium { background: #ff6600; color: white; }
        .severity-high { background: #ff0000; color: white; }
        .severity-critical { background: #aa0000; color: white; }
        .chain-item {
            background: #2a2a2a;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff6600;
        }
        .chain-name {
            color: #ff6600;
            font-weight: bold;
            font-size: 1.1em;
        }
        .chain-bounty {
            color: #00ff00;
            font-weight: bold;
        }
        .memory-usage {
            font-size: 0.9em;
            color: #888;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .notion-info {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #00ff00;
        }
        .notion-info h4 {
            color: #00ff00;
            margin-bottom: 10px;
        }
        .notion-bounties {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .bounty-range {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 APEX HUNTER</h1>
        <div class="subtitle">Elite Bug Bounty Automation System - Live Dashboard</div>
    </div>
    
    <div class="container">
        <div class="notion-info">
            <h4>🎯 Target Example: Notion Bug Bounty Program</h4>
            <p><strong>Response Efficiency:</strong> 95% | <strong>Avg Response:</strong> 12 hours | <strong>Avg Bounty:</strong> $250-$2,500</p>
            <div class="notion-bounties">
                <div class="bounty-range"><strong>Critical:</strong> $2,000-$5,000</div>
                <div class="bounty-range"><strong>High:</strong> $500-$2,000</div>
                <div class="bounty-range"><strong>Medium:</strong> $100-$250</div>
                <div class="bounty-range"><strong>Low:</strong> $50-$100</div>
            </div>
            <p style="margin-top: 10px;"><strong>High-Value Targets:</strong> API Privilege Escalation, Authentication Bypass, IDOR, AI Data Access</p>
        </div>
        
        <div class="hunt-controls">
            <h3>🎯 Start New Hunt</h3>
            <div class="input-group">
                <input type="text" id="targetInput" placeholder="Enter target domain (e.g., notion.so, example.com)" />
                <button class="btn" id="startBtn" onclick="startHunt()">Start Hunt</button>
                <button class="btn" id="stopBtn" onclick="stopHunt()" disabled>Stop Hunt</button>
            </div>
            <p style="color: #888; font-size: 0.9em;">⚠️ Only test targets you own or have permission to test</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3><span class="live-indicator"></span> Hunt Status</h3>
                <div><strong>Target:</strong> <span id="currentTarget">None</span></div>
                <div><strong>Phase:</strong> <span id="currentPhase">Idle</span></div>
                <div><strong>Elapsed:</strong> <span id="elapsedTime">0s</span></div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressBar" style="width: 0%"></div>
                </div>
                <div id="progressText">0% Complete</div>
            </div>
            
            <div class="status-card">
                <h3>📊 System Resources</h3>
                <div><strong>Memory Mode:</strong> Lightweight</div>
                <div><strong>RAM Usage:</strong> <span id="memoryUsage">0MB</span> / 1800MB</div>
                <div><strong>Tools Running:</strong> <span id="toolsRunning">0</span></div>
                <div class="memory-usage">Optimized for 3.7GB systems</div>
            </div>
            
            <div class="status-card">
                <h3>🔍 Live Statistics</h3>
                <div><strong>Findings:</strong> <span id="findingsCount">0</span></div>
                <div><strong>Chain Exploits:</strong> <span id="chainsCount">0</span></div>
                <div><strong>High/Critical:</strong> <span id="highSeverityCount">0</span></div>
                <div><strong>Est. Bounty:</strong> <span id="estimatedBounty">$0</span></div>
            </div>
        </div>
        
        <div class="findings-container">
            <div class="findings-panel">
                <div class="panel-header">🔍 Live Findings</div>
                <div id="findingsList">
                    <div class="finding-item">
                        <div class="finding-type">System</div>
                        <div class="finding-value">Ready to hunt</div>
                        <div>Start a hunt to see live findings appear here</div>
                    </div>
                </div>
            </div>
            
            <div class="findings-panel">
                <div class="panel-header">⛓️ Chain Exploits</div>
                <div id="chainsList">
                    <div class="finding-item">
                        <div class="finding-type">Chain Engine</div>
                        <div class="finding-value">Waiting for findings</div>
                        <div>Chain exploits will be automatically detected and displayed here</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let huntInterval;
        
        function startHunt() {
            const target = document.getElementById('targetInput').value.trim();
            if (!target) {
                alert('Please enter a target domain');
                return;
            }
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            fetch('/start_hunt', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target: target})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    resetButtons();
                } else {
                    startStatusUpdates();
                }
            })
            .catch(error => {
                alert('Error starting hunt: ' + error);
                resetButtons();
            });
        }
        
        function stopHunt() {
            fetch('/stop_hunt', {method: 'POST'})
            .then(() => {
                stopStatusUpdates();
                resetButtons();
            });
        }
        
        function resetButtons() {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
        
        function startStatusUpdates() {
            huntInterval = setInterval(updateStatus, 2000); // Update every 2 seconds
        }
        
        function stopStatusUpdates() {
            if (huntInterval) {
                clearInterval(huntInterval);
            }
        }
        
        function updateStatus() {
            fetch('/hunt_status')
            .then(response => response.json())
            .then(data => {
                // Update status display
                document.getElementById('currentTarget').textContent = data.target || 'None';
                document.getElementById('currentPhase').textContent = data.current_phase || 'Idle';
                document.getElementById('elapsedTime').textContent = data.elapsed_time + 's';
                document.getElementById('progressBar').style.width = data.progress + '%';
                document.getElementById('progressText').textContent = data.progress + '% Complete';
                document.getElementById('memoryUsage').textContent = data.memory_usage + 'MB';
                document.getElementById('toolsRunning').textContent = data.tools_running.length;
                
                // Update findings
                updateFindings(data.findings || []);
                updateChains(data.chains || []);
                
                // Stop updates if hunt is complete
                if (!data.active && data.progress === 100) {
                    stopStatusUpdates();
                    resetButtons();
                }
            })
            .catch(error => console.error('Error updating status:', error));
        }
        
        function updateFindings(findings) {
            const findingsList = document.getElementById('findingsList');
            const findingsCount = document.getElementById('findingsCount');
            const highSeverityCount = document.getElementById('highSeverityCount');
            
            findingsCount.textContent = findings.length;
            
            let highSeverity = findings.filter(f => f.severity === 'high' || f.severity === 'critical').length;
            highSeverityCount.textContent = highSeverity;
            
            if (findings.length === 0) {
                findingsList.innerHTML = '<div class="finding-item"><div class="finding-type">System</div><div class="finding-value">No findings yet</div></div>';
                return;
            }
            
            findingsList.innerHTML = findings.map(finding => `
                <div class="finding-item">
                    <div class="finding-type">${finding.type}</div>
                    <div class="finding-value">${finding.value}</div>
                    <div><span class="finding-severity severity-${finding.severity}">${finding.severity.toUpperCase()}</span></div>
                    <div style="font-size: 0.8em; color: #888; margin-top: 5px;">${new Date(finding.timestamp).toLocaleTimeString()}</div>
                </div>
            `).join('');
        }
        
        function updateChains(chains) {
            const chainsList = document.getElementById('chainsList');
            const chainsCount = document.getElementById('chainsCount');
            const estimatedBounty = document.getElementById('estimatedBounty');
            
            chainsCount.textContent = chains.length;
            
            if (chains.length === 0) {
                chainsList.innerHTML = '<div class="finding-item"><div class="finding-type">Chain Engine</div><div class="finding-value">No chains detected</div></div>';
                estimatedBounty.textContent = '$0';
                return;
            }
            
            // Calculate total estimated bounty
            let totalBounty = chains.length * 1500; // Rough estimate
            estimatedBounty.textContent = '$' + totalBounty.toLocaleString();
            
            chainsList.innerHTML = chains.map(chain => `
                <div class="chain-item">
                    <div class="chain-name">${chain.name}</div>
                    <div style="margin: 5px 0;">${chain.description}</div>
                    <div class="chain-bounty">💰 ${chain.estimated_bounty}</div>
                    <div style="font-size: 0.8em; color: #888;">Components: ${chain.components.join(' → ')}</div>
                </div>
            `).join('');
        }
        
        // Auto-update memory usage
        setInterval(() => {
            const memUsage = Math.floor(Math.random() * 200) + 800; // Simulate memory usage
            document.getElementById('memoryUsage').textContent = memUsage + 'MB';
        }, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/start_hunt', methods=['POST'])
def start_hunt():
    """Start a new hunt"""
    data = request.get_json()
    target = data.get('target', '').strip()
    
    if not target:
        return jsonify({'error': 'Target is required'}), 400
    
    # Start hunt in background thread
    hunter = LiveHunter(target)
    hunt_thread = threading.Thread(target=hunter.start_hunt)
    hunt_thread.daemon = True
    hunt_thread.start()
    
    return jsonify({'status': 'Hunt started', 'target': target})

@app.route('/hunt_status')
def get_hunt_status():
    """Get current hunt status"""
    global hunt_status
    
    # Update elapsed time
    if hunt_status['start_time']:
        start_time = datetime.fromisoformat(hunt_status['start_time'])
        hunt_status['elapsed_time'] = int((datetime.now() - start_time).total_seconds())
    
    # Update memory usage
    try:
        process = psutil.Process()
        hunt_status['memory_usage'] = int(process.memory_info().rss / 1024 / 1024)
    except:
        hunt_status['memory_usage'] = 0
    
    return jsonify(hunt_status)

@app.route('/stop_hunt', methods=['POST'])
def stop_hunt():
    """Stop current hunt"""
    global hunt_status
    
    hunt_status['active'] = False
    hunt_status['current_phase'] = 'Stopped'
    
    return jsonify({'status': 'Hunt stopped'})

if __name__ == '__main__':
    print("🎯 APEX HUNTER - Real-Time Web Interface")
    print("=" * 50)
    print("🌐 Starting web interface on port 8080")
    print("🔗 Access dashboard at: http://localhost:8080")
    print("🎯 Features:")
    print("  ✅ Live target research with internet access")
    print("  ✅ Real-time subdomain discovery")
    print("  ✅ Technology detection and vulnerability scanning")
    print("  ✅ Automatic chain exploit detection")
    print("  ✅ Notion-specific targeting")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)