#!/usr/bin/env python3
"""
APEX HUNTER - Simplified Web Interface (No OpenCV dependency)
Works immediately without complex dependencies
"""

from flask import Flask, render_template_string, request, jsonify
import os
import json
import time
import threading
import queue
import tempfile
import subprocess
import requests
import sqlite3
from pathlib import Path
import logging

app = Flask(__name__)

# Global variables for hunt status
hunt_status = {
    'active': False,
    'target': '',
    'target_type': '',
    'progress': 0,
    'phase': 'Idle',
    'findings': [],
    'chains': [],
    'start_time': 0,
    'estimated_bounty': 0
}

class SimpleAnalyzer:
    def __init__(self):
        self.findings = []
        self.chains = []
        
    def analyze_web_target(self, url):
        """Simple web analysis without complex dependencies"""
        findings = []
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        try:
            # Basic HTTP analysis
            response = requests.get(url, timeout=10, verify=False)
            
            findings.append({
                'type': 'web_info',
                'severity': 'info',
                'title': 'HTTP Response Analysis',
                'description': f'Status: {response.status_code}, Size: {len(response.content)} bytes',
                'timestamp': time.time()
            })
            
            # Check for server disclosure
            if 'Server' in response.headers:
                server = response.headers['Server']
                findings.append({
                    'type': 'server_disclosure',
                    'severity': 'low',
                    'title': 'Server Information Disclosure',
                    'description': f'Server header reveals: {server}',
                    'timestamp': time.time()
                })
            
            # Check for missing security headers
            security_headers = [
                'X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options',
                'Strict-Transport-Security', 'Content-Security-Policy'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                findings.append({
                    'type': 'missing_security_headers',
                    'severity': 'medium',
                    'title': 'Missing Security Headers',
                    'description': f'Missing headers: {", ".join(missing_headers)}',
                    'timestamp': time.time()
                })
            
            # Simple XSS test
            xss_payloads = ['<script>alert("XSS")</script>', '<img src=x onerror=alert("XSS")>']
            for payload in xss_payloads:
                try:
                    test_url = f"{url}?q={payload}"
                    test_response = requests.get(test_url, timeout=5, verify=False)
                    if payload in test_response.text:
                        findings.append({
                            'type': 'xss_reflected',
                            'severity': 'high',
                            'title': 'Potential Reflected XSS',
                            'description': f'XSS payload reflected: {payload}',
                            'timestamp': time.time()
                        })
                        break
                except:
                    continue
            
            # Simple SQL injection test
            sql_payloads = ["'", "' OR '1'='1", "'; DROP TABLE users; --"]
            for payload in sql_payloads:
                try:
                    test_url = f"{url}?id={payload}"
                    test_response = requests.get(test_url, timeout=5, verify=False)
                    
                    error_patterns = ['mysql_fetch_array', 'ORA-01756', 'SQLServer JDBC Driver']
                    for pattern in error_patterns:
                        if pattern.lower() in test_response.text.lower():
                            findings.append({
                                'type': 'sql_injection',
                                'severity': 'critical',
                                'title': 'Potential SQL Injection',
                                'description': f'SQL error detected with payload: {payload}',
                                'timestamp': time.time()
                            })
                            break
                except:
                    continue
            
        except Exception as e:
            findings.append({
                'type': 'connection_error',
                'severity': 'info',
                'title': 'Connection Error',
                'description': f'Failed to connect: {str(e)}',
                'timestamp': time.time()
            })
        
        return findings
    
    def analyze_ip_target(self, ip):
        """Simple IP analysis"""
        findings = []
        
        # Simple port scan using Python socket
        import socket
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 3306, 3389, 5432]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    service_names = {
                        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
                        80: 'HTTP', 110: 'POP3', 135: 'RPC', 139: 'NetBIOS', 143: 'IMAP',
                        443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL',
                        3389: 'RDP', 5432: 'PostgreSQL'
                    }
                    
                    findings.append({
                        'type': 'open_port',
                        'severity': 'info',
                        'title': f'Open Port: {port}',
                        'description': f'Port {port} ({service_names.get(port, "Unknown")}) is open',
                        'timestamp': time.time()
                    })
            except:
                continue
        
        return findings
    
    def generate_simple_chains(self, findings):
        """Generate simple exploit chains"""
        chains = []
        
        # Look for XSS + Missing Headers = Account Takeover
        xss_findings = [f for f in findings if f.get('type') == 'xss_reflected']
        header_findings = [f for f in findings if f.get('type') == 'missing_security_headers']
        
        if xss_findings and header_findings:
            chains.append({
                'name': 'XSS + Missing Security Headers Chain',
                'severity': 'high',
                'description': 'XSS vulnerability combined with missing security headers',
                'impact': 'Potential account takeover and session hijacking',
                'bounty_estimate': '$1,000-$3,000',
                'components': len(xss_findings) + len(header_findings),
                'timestamp': time.time()
            })
        
        # Look for SQL Injection = High Impact
        sql_findings = [f for f in findings if f.get('type') == 'sql_injection']
        if sql_findings:
            chains.append({
                'name': 'SQL Injection Data Extraction Chain',
                'severity': 'critical',
                'description': 'SQL injection vulnerability allowing data extraction',
                'impact': 'Complete database compromise and data breach',
                'bounty_estimate': '$2,000-$8,000',
                'components': len(sql_findings),
                'timestamp': time.time()
            })
        
        return chains

def run_hunt(target, target_type, analysis_mode):
    global hunt_status
    
    try:
        analyzer = SimpleAnalyzer()
        
        phases = [
            'Initializing analysis',
            'Target reconnaissance', 
            'Vulnerability scanning',
            'Chain detection',
            'Report generation'
        ]
        
        for i, phase in enumerate(phases):
            if not hunt_status['active']:
                break
                
            hunt_status['phase'] = phase
            hunt_status['progress'] = int((i / len(phases)) * 100)
            
            time.sleep(2)  # Simulate work
            
            if i == 1:  # Target reconnaissance
                if target_type == 'url':
                    findings = analyzer.analyze_web_target(target)
                    hunt_status['findings'].extend(findings)
                elif target_type == 'ip':
                    findings = analyzer.analyze_ip_target(target)
                    hunt_status['findings'].extend(findings)
            
            elif i == 3:  # Chain detection
                chains = analyzer.generate_simple_chains(hunt_status['findings'])
                hunt_status['chains'].extend(chains)
            
            # Update estimated bounty
            hunt_status['estimated_bounty'] = calculate_bounty(hunt_status['findings'], hunt_status['chains'])
        
        hunt_status['progress'] = 100
        hunt_status['phase'] = 'Complete'
        
    except Exception as e:
        hunt_status['phase'] = f'Error: {str(e)}'
        hunt_status['progress'] = 0
    
    finally:
        hunt_status['active'] = False

def calculate_bounty(findings, chains):
    """Calculate estimated bounty"""
    total = 0
    
    for finding in findings:
        severity = finding.get('severity', 'low')
        if severity == 'critical':
            total += 2500
        elif severity == 'high':
            total += 1000
        elif severity == 'medium':
            total += 300
        elif severity == 'low':
            total += 100
    
    for chain in chains:
        if chain.get('severity') == 'critical':
            total += 5000
        elif chain.get('severity') == 'high':
            total += 2000
    
    return total

@app.route('/')
def index():
    return render_template_string(SIMPLE_DASHBOARD_TEMPLATE)

@app.route('/start_hunt', methods=['POST'])
def start_hunt():
    global hunt_status
    
    if hunt_status['active']:
        return jsonify({'error': 'Hunt already in progress'})
    
    data = request.get_json()
    target = data.get('target', '').strip()
    target_type = data.get('target_type', 'auto')
    analysis_mode = data.get('analysis_mode', 'standard')
    
    if not target:
        return jsonify({'error': 'Target is required'})
    
    # Auto-detect target type
    if target_type == 'auto':
        if target.startswith(("http://", "https://")) or "." in target:
            target_type = 'url'
        else:
            try:
                import ipaddress
                ipaddress.ip_address(target)
                target_type = 'ip'
            except:
                target_type = 'url'
    
    # Reset hunt status
    hunt_status.update({
        'active': True,
        'target': target,
        'target_type': target_type,
        'analysis_mode': analysis_mode,
        'progress': 0,
        'phase': 'Initializing',
        'findings': [],
        'chains': [],
        'start_time': time.time(),
        'estimated_bounty': 0
    })
    
    # Start hunt in background thread
    hunt_thread = threading.Thread(target=run_hunt, args=(target, target_type, analysis_mode))
    hunt_thread.daemon = True
    hunt_thread.start()
    
    return jsonify({'success': True, 'message': 'Hunt started'})

@app.route('/hunt_status')
def get_hunt_status():
    return jsonify(hunt_status)

@app.route('/stop_hunt', methods=['POST'])
def stop_hunt():
    global hunt_status
    hunt_status['active'] = False
    hunt_status['phase'] = 'Stopped'
    return jsonify({'success': True, 'message': 'Hunt stopped'})

# Simple Dashboard Template
SIMPLE_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX HUNTER - Simplified Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff00;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border: 2px solid #00ff00;
            padding: 20px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 10px;
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00ff00;
            margin-bottom: 10px;
        }
        
        .input-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            color: #00cccc;
            font-weight: bold;
        }
        
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff00;
            border-radius: 5px;
            color: #00ff00;
            font-family: inherit;
        }
        
        .btn {
            padding: 12px 25px;
            border: 2px solid #00ff00;
            background: transparent;
            color: #00ff00;
            border-radius: 5px;
            cursor: pointer;
            font-family: inherit;
            font-size: 14px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .btn:hover {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 20px #00ff00;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .status-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
        }
        
        .status-card h3 {
            color: #00cccc;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ff00;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff00, #00cccc);
            width: 0%;
            transition: width 0.5s ease;
        }
        
        .findings-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .finding-item {
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        
        .finding-item.critical { border-left-color: #ff0000; }
        .finding-item.high { border-left-color: #ff6600; }
        .finding-item.medium { border-left-color: #ffff00; }
        .finding-item.low { border-left-color: #00ff00; }
        
        .chains-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
        }
        
        .chain-item {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff0000;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #00ff00;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #00cccc;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 APEX HUNTER</h1>
            <p>Simplified Bug Bounty Automation System</p>
            <p>Ready to hunt immediately - no complex setup required!</p>
        </div>
        
        <div class="input-section">
            <h3>🎯 Target Input</h3>
            <div class="input-group">
                <label>🌐 Target (URL or IP):</label>
                <input type="text" id="target-input" placeholder="https://example.com or 192.168.1.1" />
            </div>
            <div class="input-group">
                <label>🔧 Analysis Mode:</label>
                <select id="analysis-mode">
                    <option value="standard">Standard Hunt (Quick)</option>
                    <option value="deep">Deep Analysis (Thorough)</option>
                </select>
            </div>
            <button class="btn" onclick="startHunt()" id="start-btn">🚀 START HUNT</button>
            <button class="btn" onclick="stopHunt()" id="stop-btn" disabled style="margin-left: 10px;">🛑 STOP</button>
        </div>
        
        <div class="status-section">
            <div class="status-card">
                <h3>🎯 Hunt Status</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <p id="hunt-phase">Idle</p>
                <p id="hunt-target">No target selected</p>
                <p id="hunt-time">Elapsed: 00:00</p>
            </div>
            
            <div class="status-card">
                <h3>📊 Statistics</h3>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value" id="findings-count">0</div>
                        <div class="stat-label">Findings</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="chains-count">0</div>
                        <div class="stat-label">Chains</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="critical-count">0</div>
                        <div class="stat-label">Critical</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="bounty-estimate">$0</div>
                        <div class="stat-label">Est. Bounty</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="findings-section">
            <h3>🔍 Live Findings</h3>
            <div id="findings-list">
                <p style="text-align: center; color: #666; padding: 20px;">No findings yet. Start a hunt to see results.</p>
            </div>
        </div>
        
        <div class="chains-section">
            <h3>⛓️ Exploit Chains</h3>
            <div id="chains-list">
                <p style="text-align: center; color: #666; padding: 20px;">No exploit chains detected yet.</p>
            </div>
        </div>
    </div>
    
    <script>
        let huntInterval;
        let startTime;
        
        function startHunt() {
            const target = document.getElementById('target-input').value.trim();
            const mode = document.getElementById('analysis-mode').value;
            
            if (!target) {
                alert('Please enter a target');
                return;
            }
            
            fetch('/start_hunt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    target: target,
                    target_type: 'auto',
                    analysis_mode: mode
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startHuntMonitoring();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Hunt failed to start: ' + error);
            });
        }
        
        function startHuntMonitoring() {
            startTime = Date.now();
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
            
            huntInterval = setInterval(updateHuntStatus, 2000);
        }
        
        function updateHuntStatus() {
            fetch('/hunt_status')
            .then(response => response.json())
            .then(status => {
                // Update progress
                document.getElementById('progress-fill').style.width = status.progress + '%';
                document.getElementById('hunt-phase').textContent = status.phase;
                document.getElementById('hunt-target').textContent = 'Target: ' + status.target;
                
                // Update elapsed time
                if (status.active) {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    document.getElementById('hunt-time').textContent = 
                        `Elapsed: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }
                
                // Update statistics
                document.getElementById('findings-count').textContent = status.findings.length;
                document.getElementById('chains-count').textContent = status.chains.length;
                document.getElementById('critical-count').textContent = 
                    status.findings.filter(f => f.severity === 'critical').length;
                document.getElementById('bounty-estimate').textContent = '$' + status.estimated_bounty.toLocaleString();
                
                // Update findings list
                updateFindingsList(status.findings);
                updateChainsList(status.chains);
                
                // Check if hunt is complete
                if (!status.active) {
                    stopHuntMonitoring();
                }
            })
            .catch(error => {
                console.error('Status update failed:', error);
            });
        }
        
        function updateFindingsList(findings) {
            const findingsList = document.getElementById('findings-list');
            
            if (findings.length === 0) {
                findingsList.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No findings yet. Hunt in progress...</p>';
                return;
            }
            
            findingsList.innerHTML = findings.map(finding => `
                <div class="finding-item ${finding.severity}">
                    <strong>${finding.title || 'Unknown Finding'}</strong>
                    <span style="float: right; color: #00cccc;">${finding.severity.toUpperCase()}</span>
                    <p>${finding.description || 'No description available'}</p>
                </div>
            `).join('');
        }
        
        function updateChainsList(chains) {
            const chainsList = document.getElementById('chains-list');
            
            if (chains.length === 0) {
                chainsList.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No exploit chains detected yet.</p>';
                return;
            }
            
            chainsList.innerHTML = chains.map(chain => `
                <div class="chain-item">
                    <strong>${chain.name}</strong>
                    <span style="float: right; color: #00ff00;">${chain.bounty_estimate}</span>
                    <p>${chain.description}</p>
                    <p><strong>Impact:</strong> ${chain.impact}</p>
                    <p><strong>Components:</strong> ${chain.components} vulnerabilities</p>
                </div>
            `).join('');
        }
        
        function stopHunt() {
            if (confirm('Are you sure you want to stop the current hunt?')) {
                fetch('/stop_hunt', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    stopHuntMonitoring();
                });
            }
        }
        
        function stopHuntMonitoring() {
            if (huntInterval) {
                clearInterval(huntInterval);
                huntInterval = null;
            }
            
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🎯 APEX HUNTER - Simplified Web Interface")
    print("=========================================")
    print("🌐 Starting simplified web server...")
    print("🔗 Access at: http://localhost:12000")
    print("📱 Supports: URLs and IP addresses")
    print("⚡ No complex dependencies required!")
    print("=========================================")
    
    app.run(host='0.0.0.0', port=12000, debug=False)