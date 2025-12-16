#!/usr/bin/env python3
"""
APEX HUNTER - Enhanced Multi-Target Web Interface
Supports: URLs, IPs, APKs, Source Code, GitHub Repos with File Upload
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for
import os
import json
import time
import threading
import queue
import tempfile
import shutil
from pathlib import Path
import zipfile
import subprocess
from werkzeug.utils import secure_filename
from multi_target_analyzer import MultiTargetAnalyzer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Global variables for hunt status
hunt_status = {
    'active': False,
    'target': '',
    'target_type': '',
    'progress': 0,
    'phase': 'Idle',
    'findings': [],
    'chains': [],
    'evidence_files': [],
    'start_time': 0,
    'estimated_bounty': 0
}

hunt_queue = queue.Queue()
analyzer = None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template_string(ENHANCED_DASHBOARD_TEMPLATE)

@app.route('/start_hunt', methods=['POST'])
def start_hunt():
    global hunt_status, analyzer
    
    if hunt_status['active']:
        return jsonify({'error': 'Hunt already in progress'})
    
    data = request.get_json()
    target = data.get('target', '').strip()
    target_type = data.get('target_type', 'auto')
    analysis_mode = data.get('analysis_mode', 'standard')
    
    if not target:
        return jsonify({'error': 'Target is required'})
    
    # Auto-detect target type and fix URL scheme
    if target_type == 'auto':
        if target.startswith(("http://", "https://")) or "." in target:
            target_type = 'url'
            # Add https:// if no protocol specified
            if not target.startswith(("http://", "https://")):
                target = f"https://{target}"
        else:
            try:
                import ipaddress
                ipaddress.ip_address(target)
                target_type = 'ip'
            except:
                target_type = 'url'
                # Add https:// if no protocol specified
                if not target.startswith(("http://", "https://")):
                    target = f"https://{target}"
    
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
        'evidence_files': [],
        'start_time': time.time(),
        'estimated_bounty': 0
    })
    
    # Start hunt in background thread
    hunt_thread = threading.Thread(target=run_hunt, args=(target, target_type, analysis_mode))
    hunt_thread.daemon = True
    hunt_thread.start()
    
    return jsonify({'success': True, 'message': 'Hunt started'})

@app.route('/upload_target', methods=['POST'])
def upload_target():
    global hunt_status
    
    if hunt_status['active']:
        return jsonify({'error': 'Hunt already in progress'})
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Determine target type based on file extension
    target_type = 'file_upload'
    if filename.lower().endswith('.apk'):
        target_type = 'apk'
    elif filename.lower().endswith(('.zip', '.tar.gz', '.tar')):
        target_type = 'source_code'
    
    analysis_mode = request.form.get('analysis_mode', 'standard')
    
    # Reset hunt status
    hunt_status.update({
        'active': True,
        'target': filepath,
        'target_type': target_type,
        'analysis_mode': analysis_mode,
        'progress': 0,
        'phase': 'Analyzing uploaded file',
        'findings': [],
        'chains': [],
        'evidence_files': [],
        'start_time': time.time(),
        'estimated_bounty': 0
    })
    
    # Start hunt in background thread
    hunt_thread = threading.Thread(target=run_hunt, args=(filepath, target_type, analysis_mode))
    hunt_thread.daemon = True
    hunt_thread.start()
    
    return jsonify({'success': True, 'message': 'File uploaded and analysis started'})

@app.route('/clone_github', methods=['POST'])
def clone_github():
    global hunt_status
    
    if hunt_status['active']:
        return jsonify({'error': 'Hunt already in progress'})
    
    data = request.get_json()
    repo_url = data.get('repo_url', '').strip()
    analysis_mode = data.get('analysis_mode', 'standard')
    
    if not repo_url:
        return jsonify({'error': 'GitHub repository URL is required'})
    
    # Validate GitHub URL
    if 'github.com' not in repo_url:
        return jsonify({'error': 'Invalid GitHub repository URL'})
    
    # Reset hunt status
    hunt_status.update({
        'active': True,
        'target': repo_url,
        'target_type': 'github',
        'analysis_mode': analysis_mode,
        'progress': 0,
        'phase': 'Cloning repository',
        'findings': [],
        'chains': [],
        'evidence_files': [],
        'start_time': time.time(),
        'estimated_bounty': 0
    })
    
    # Start hunt in background thread
    hunt_thread = threading.Thread(target=run_hunt, args=(repo_url, 'github', analysis_mode))
    hunt_thread.daemon = True
    hunt_thread.start()
    
    return jsonify({'success': True, 'message': 'GitHub repository cloning started'})

def run_hunt(target, target_type, analysis_mode):
    global hunt_status, analyzer
    
    try:
        # Fix URL scheme if missing
        if target_type == 'url' and not target.startswith(('http://', 'https://')):
            target = f'https://{target}'
            hunt_status['target'] = target
        
        analyzer = MultiTargetAnalyzer()
        
        # Update progress phases
        phases = [
            'Initializing analysis',
            'Target reconnaissance', 
            'Vulnerability scanning',
            'Deep analysis',
            'Chain detection',
            'Evidence collection',
            'Report generation'
        ]
        
        for i, phase in enumerate(phases):
            if not hunt_status['active']:
                break
                
            hunt_status['phase'] = phase
            hunt_status['progress'] = int((i / len(phases)) * 100)
            
            # Simulate phase work
            time.sleep(2)
            
            # Run actual analysis
            if i == 1:  # Target reconnaissance
                if target_type == 'url':
                    findings = analyzer.web_reconnaissance(target)
                    hunt_status['findings'].extend(findings)
                elif target_type == 'ip':
                    findings = analyzer.port_scan(target)
                    hunt_status['findings'].extend(findings)
            
            elif i == 2:  # Vulnerability scanning
                if target_type in ['url', 'ip']:
                    if target_type == 'url':
                        findings = analyzer.scan_web_vulnerabilities(target)
                    else:
                        findings = analyzer.scan_ip_vulnerabilities(target)
                    hunt_status['findings'].extend(findings)
            
            elif i == 3:  # Deep analysis
                if analysis_mode == 'deep':
                    # Run comprehensive analysis
                    results = analyzer.analyze_target(target, target_type)
                    hunt_status['findings'] = analyzer.findings
                    hunt_status['chains'] = analyzer.chains
            
            elif i == 4:  # Chain detection
                chains = analyzer.generate_chains(hunt_status['findings'])
                hunt_status['chains'].extend(chains)
            
            elif i == 5:  # Evidence collection
                hunt_status['evidence_files'] = analyzer.evidence_files
            
            # Update estimated bounty
            hunt_status['estimated_bounty'] = calculate_bounty(hunt_status['findings'], hunt_status['chains'])
        
        # Complete hunt
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

@app.route('/hunt_status')
def get_hunt_status():
    return jsonify(hunt_status)

@app.route('/stop_hunt', methods=['POST'])
def stop_hunt():
    global hunt_status
    hunt_status['active'] = False
    hunt_status['phase'] = 'Stopped'
    return jsonify({'success': True, 'message': 'Hunt stopped'})

@app.route('/download_evidence')
def download_evidence():
    if analyzer and analyzer.session_dir:
        # Create zip file of all evidence
        zip_path = f"/tmp/evidence_{int(time.time())}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(analyzer.session_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, analyzer.session_dir)
                    zipf.write(file_path, arcname)
        
        return send_file(zip_path, as_attachment=True, download_name='apex_hunter_evidence.zip')
    
    return jsonify({'error': 'No evidence available'})

@app.route('/generate_report')
def generate_report():
    if not hunt_status['findings']:
        return jsonify({'error': 'No findings to report'})
    
    report = generate_professional_report(hunt_status)
    return jsonify({'report': report})

def generate_professional_report(status):
    """Generate professional vulnerability assessment report"""
    
    critical_findings = [f for f in status['findings'] if f.get('severity') == 'critical']
    high_findings = [f for f in status['findings'] if f.get('severity') == 'high']
    medium_findings = [f for f in status['findings'] if f.get('severity') == 'medium']
    low_findings = [f for f in status['findings'] if f.get('severity') == 'low']
    
    report = {
        'title': 'APEX HUNTER - Vulnerability Assessment Report',
        'target': status['target'],
        'target_type': status['target_type'],
        'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'executive_summary': {
            'total_findings': len(status['findings']),
            'critical_count': len(critical_findings),
            'high_count': len(high_findings),
            'medium_count': len(medium_findings),
            'low_count': len(low_findings),
            'chain_count': len(status['chains']),
            'estimated_bounty': status['estimated_bounty'],
            'risk_rating': calculate_risk_rating(status['findings'])
        },
        'findings': {
            'critical': critical_findings,
            'high': high_findings,
            'medium': medium_findings,
            'low': low_findings
        },
        'exploit_chains': status['chains'],
        'recommendations': generate_recommendations(status['findings']),
        'evidence_files': status['evidence_files']
    }
    
    return report

def calculate_risk_rating(findings):
    """Calculate overall risk rating"""
    critical_count = len([f for f in findings if f.get('severity') == 'critical'])
    high_count = len([f for f in findings if f.get('severity') == 'high'])
    
    if critical_count > 0:
        return 'Critical'
    elif high_count > 2:
        return 'High'
    elif high_count > 0:
        return 'Medium'
    else:
        return 'Low'

def generate_recommendations(findings):
    """Generate security recommendations"""
    recommendations = []
    
    finding_types = [f.get('type', '') for f in findings]
    
    if any('sql_injection' in t for t in finding_types):
        recommendations.append({
            'priority': 'Critical',
            'title': 'Fix SQL Injection Vulnerabilities',
            'description': 'Implement parameterized queries and input validation',
            'timeline': 'Immediate'
        })
    
    if any('xss' in t for t in finding_types):
        recommendations.append({
            'priority': 'High',
            'title': 'Implement XSS Protection',
            'description': 'Add output encoding and Content Security Policy',
            'timeline': '1-2 weeks'
        })
    
    if any('missing_security_headers' in t for t in finding_types):
        recommendations.append({
            'priority': 'Medium',
            'title': 'Add Security Headers',
            'description': 'Implement security headers for defense in depth',
            'timeline': '2-4 weeks'
        })
    
    return recommendations

# Enhanced Dashboard Template
ENHANCED_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX HUNTER - Multi-Target Analysis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff00;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
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
        
        .header p {
            font-size: 1.2em;
            color: #00cccc;
        }
        
        .target-input-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .target-tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #00ff00;
        }
        
        .tab-button {
            background: transparent;
            border: none;
            color: #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-family: inherit;
            font-size: 14px;
        }
        
        .tab-button.active {
            border-bottom-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .tab-content {
            display: none;
            margin-top: 20px;
        }
        
        .tab-content.active {
            display: block;
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
        
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 12px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff00;
            border-radius: 5px;
            color: #00ff00;
            font-family: inherit;
        }
        
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
            outline: none;
            border-color: #00cccc;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
        }
        
        .file-upload {
            border: 2px dashed #00ff00;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-upload:hover {
            background: rgba(0, 255, 0, 0.1);
            border-color: #00cccc;
        }
        
        .file-upload input[type="file"] {
            display: none;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
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
        
        .btn-danger {
            border-color: #ff0000;
            color: #ff0000;
        }
        
        .btn-danger:hover {
            background: #ff0000;
            color: #fff;
            box-shadow: 0 0 20px #ff0000;
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
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
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
        
        .findings-section {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .findings-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .findings-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .finding-item {
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        
        .finding-item.critical {
            border-left-color: #ff0000;
        }
        
        .finding-item.high {
            border-left-color: #ff6600;
        }
        
        .finding-item.medium {
            border-left-color: #ffff00;
        }
        
        .finding-item.low {
            border-left-color: #00ff00;
        }
        
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .finding-title {
            font-weight: bold;
            color: #00cccc;
        }
        
        .severity-badge {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background: #ff0000;
            color: #fff;
        }
        
        .severity-high {
            background: #ff6600;
            color: #fff;
        }
        
        .severity-medium {
            background: #ffff00;
            color: #000;
        }
        
        .severity-low {
            background: #00ff00;
            color: #000;
        }
        
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
        
        .chain-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .chain-title {
            font-weight: bold;
            color: #ff6666;
        }
        
        .bounty-estimate {
            color: #00ff00;
            font-weight: bold;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
        }
        
        .modal-content {
            background: #1a1a2e;
            margin: 5% auto;
            padding: 20px;
            border: 2px solid #00ff00;
            border-radius: 10px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .close {
            color: #ff0000;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #ff6666;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 5px #00ff00; }
            50% { box-shadow: 0 0 20px #00ff00; }
            100% { box-shadow: 0 0 5px #00ff00; }
        }
        
        .hunting {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 APEX HUNTER</h1>
            <p>Elite Multi-Target Bug Bounty Automation System</p>
            <p>Supports: URLs • IPs • APKs • Source Code • GitHub Repos</p>
        </div>
        
        <div class="target-input-section">
            <h3>🎯 Target Selection</h3>
            
            <div class="target-tabs">
                <button class="tab-button active" onclick="switchTab('url-tab')">🌐 URL/Domain</button>
                <button class="tab-button" onclick="switchTab('ip-tab')">🔍 IP Address</button>
                <button class="tab-button" onclick="switchTab('file-tab')">📱 File Upload</button>
                <button class="tab-button" onclick="switchTab('github-tab')">🐙 GitHub Repo</button>
            </div>
            
            <!-- URL/Domain Tab -->
            <div id="url-tab" class="tab-content active">
                <div class="input-group">
                    <label>🌐 Target URL or Domain:</label>
                    <input type="text" id="url-target" placeholder="https://example.com or example.com" />
                </div>
                <div class="input-group">
                    <label>🔧 Analysis Mode:</label>
                    <select id="url-analysis-mode">
                        <option value="standard">Standard Hunt (5-8 minutes)</option>
                        <option value="deep">Deep Analysis (15-20 minutes)</option>
                        <option value="stealth">Stealth Mode (10-15 minutes)</option>
                    </select>
                </div>
                <div class="action-buttons">
                    <button class="btn" onclick="startUrlHunt()">🚀 Start Web Hunt</button>
                </div>
            </div>
            
            <!-- IP Address Tab -->
            <div id="ip-tab" class="tab-content">
                <div class="input-group">
                    <label>🔍 Target IP Address:</label>
                    <input type="text" id="ip-target" placeholder="192.168.1.1 or 10.0.0.1" />
                </div>
                <div class="input-group">
                    <label>🔧 Scan Type:</label>
                    <select id="ip-scan-type">
                        <option value="standard">Standard Port Scan</option>
                        <option value="comprehensive">Comprehensive Scan</option>
                        <option value="stealth">Stealth Scan</option>
                    </select>
                </div>
                <div class="action-buttons">
                    <button class="btn" onclick="startIpHunt()">🚀 Start IP Hunt</button>
                </div>
            </div>
            
            <!-- File Upload Tab -->
            <div id="file-tab" class="tab-content">
                <div class="file-upload" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" accept=".apk,.zip,.tar.gz,.jar,.war" onchange="handleFileSelect(this)" />
                    <div>
                        <h3>📱 Drop APK or Source Code Archive</h3>
                        <p>Supported: .apk, .zip, .tar.gz, .jar, .war</p>
                        <p>Max size: 100MB</p>
                    </div>
                </div>
                <div id="file-info" style="margin-top: 15px; display: none;">
                    <p>Selected file: <span id="file-name"></span></p>
                    <p>Size: <span id="file-size"></span></p>
                </div>
                <div class="input-group" style="margin-top: 15px;">
                    <label>🔧 Analysis Type:</label>
                    <select id="file-analysis-type">
                        <option value="static">Static Analysis Only</option>
                        <option value="dynamic">Dynamic Analysis (APK only)</option>
                        <option value="comprehensive">Comprehensive Analysis</option>
                    </select>
                </div>
                <div class="action-buttons">
                    <button class="btn" onclick="startFileHunt()" disabled id="file-hunt-btn">🚀 Start File Analysis</button>
                </div>
            </div>
            
            <!-- GitHub Tab -->
            <div id="github-tab" class="tab-content">
                <div class="input-group">
                    <label>🐙 GitHub Repository URL:</label>
                    <input type="text" id="github-url" placeholder="https://github.com/user/repository" />
                </div>
                <div class="input-group">
                    <label>🔧 Analysis Scope:</label>
                    <select id="github-scope">
                        <option value="source_only">Source Code Only</option>
                        <option value="full_repo">Full Repository Analysis</option>
                        <option value="commit_history">Include Commit History</option>
                    </select>
                </div>
                <div class="action-buttons">
                    <button class="btn" onclick="startGithubHunt()">🚀 Start GitHub Hunt</button>
                </div>
            </div>
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
                <h3>📊 System Resources</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value" id="memory-usage">0MB</div>
                        <div class="stat-label">Memory</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="tools-running">0</div>
                        <div class="stat-label">Tools</div>
                    </div>
                </div>
                <p style="margin-top: 10px; text-align: center; color: #00cccc;">Optimized for multi-target analysis</p>
            </div>
        </div>
        
        <div class="status-section">
            <div class="status-card">
                <h3>🔍 Live Statistics</h3>
                <div class="stats-grid">
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
            
            <div class="status-card">
                <h3>🎮 Hunt Controls</h3>
                <div class="action-buttons">
                    <button class="btn" onclick="pauseHunt()" id="pause-btn" disabled>⏸️ Pause</button>
                    <button class="btn btn-danger" onclick="stopHunt()" id="stop-btn" disabled>🛑 Stop</button>
                    <button class="btn" onclick="downloadEvidence()" id="evidence-btn" disabled>📥 Evidence</button>
                    <button class="btn" onclick="generateReport()" id="report-btn" disabled>📄 Report</button>
                </div>
            </div>
        </div>
        
        <div class="findings-section">
            <div class="findings-header">
                <h3>🔍 Live Findings</h3>
                <button class="btn" onclick="clearFindings()">🗑️ Clear</button>
            </div>
            <div class="findings-list" id="findings-list">
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
    
    <!-- Report Modal -->
    <div id="report-modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('report-modal')">&times;</span>
            <h2>📄 Vulnerability Assessment Report</h2>
            <div id="report-content"></div>
        </div>
    </div>
    
    <script>
        let huntInterval;
        let startTime;
        
        function switchTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }
        
        function handleFileSelect(input) {
            const file = input.files[0];
            if (file) {
                document.getElementById('file-name').textContent = file.name;
                document.getElementById('file-size').textContent = formatFileSize(file.size);
                document.getElementById('file-info').style.display = 'block';
                document.getElementById('file-hunt-btn').disabled = false;
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function startUrlHunt() {
            const target = document.getElementById('url-target').value.trim();
            const mode = document.getElementById('url-analysis-mode').value;
            
            if (!target) {
                alert('Please enter a target URL or domain');
                return;
            }
            
            startHunt({
                target: target,
                target_type: 'url',
                analysis_mode: mode
            });
        }
        
        function startIpHunt() {
            const target = document.getElementById('ip-target').value.trim();
            const scanType = document.getElementById('ip-scan-type').value;
            
            if (!target) {
                alert('Please enter a target IP address');
                return;
            }
            
            startHunt({
                target: target,
                target_type: 'ip',
                analysis_mode: scanType
            });
        }
        
        function startFileHunt() {
            const fileInput = document.getElementById('file-input');
            const analysisType = document.getElementById('file-analysis-type').value;
            
            if (!fileInput.files[0]) {
                alert('Please select a file to analyze');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('analysis_mode', analysisType);
            
            fetch('/upload_target', {
                method: 'POST',
                body: formData
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
                alert('Upload failed: ' + error);
            });
        }
        
        function startGithubHunt() {
            const repoUrl = document.getElementById('github-url').value.trim();
            const scope = document.getElementById('github-scope').value;
            
            if (!repoUrl) {
                alert('Please enter a GitHub repository URL');
                return;
            }
            
            fetch('/clone_github', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repo_url: repoUrl,
                    analysis_mode: scope
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
                alert('GitHub clone failed: ' + error);
            });
        }
        
        function startHunt(huntData) {
            fetch('/start_hunt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(huntData)
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
            document.querySelector('.target-input-section').classList.add('hunting');
            document.getElementById('pause-btn').disabled = false;
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
                if (!status.active && status.progress === 100) {
                    stopHuntMonitoring();
                    document.getElementById('evidence-btn').disabled = false;
                    document.getElementById('report-btn').disabled = false;
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
                    <div class="finding-header">
                        <span class="finding-title">${finding.title || 'Unknown Finding'}</span>
                        <span class="severity-badge severity-${finding.severity}">${finding.severity}</span>
                    </div>
                    <p>${finding.description || 'No description available'}</p>
                    ${finding.poc ? '<span style="color: #00ff00;">✅ PoC Available</span>' : ''}
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
                    <div class="chain-header">
                        <span class="chain-title">${chain.name}</span>
                        <span class="bounty-estimate">${chain.bounty_estimate}</span>
                    </div>
                    <p>${chain.description}</p>
                    <p><strong>Impact:</strong> ${chain.impact}</p>
                    <p><strong>Components:</strong> ${chain.components.length} vulnerabilities</p>
                </div>
            `).join('');
        }
        
        function pauseHunt() {
            // Implement pause functionality
            alert('Pause functionality coming soon!');
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
            
            document.querySelector('.target-input-section').classList.remove('hunting');
            document.getElementById('pause-btn').disabled = true;
            document.getElementById('stop-btn').disabled = true;
        }
        
        function downloadEvidence() {
            window.open('/download_evidence', '_blank');
        }
        
        function generateReport() {
            fetch('/generate_report')
            .then(response => response.json())
            .then(data => {
                if (data.report) {
                    showReport(data.report);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Report generation failed: ' + error);
            });
        }
        
        function showReport(report) {
            const reportContent = document.getElementById('report-content');
            reportContent.innerHTML = `
                <h3>Executive Summary</h3>
                <p><strong>Target:</strong> ${report.target}</p>
                <p><strong>Analysis Date:</strong> ${report.analysis_date}</p>
                <p><strong>Risk Rating:</strong> ${report.executive_summary.risk_rating}</p>
                <p><strong>Total Findings:</strong> ${report.executive_summary.total_findings}</p>
                <p><strong>Estimated Bounty:</strong> $${report.executive_summary.estimated_bounty.toLocaleString()}</p>
                
                <h3>Findings Breakdown</h3>
                <ul>
                    <li>Critical: ${report.executive_summary.critical_count}</li>
                    <li>High: ${report.executive_summary.high_count}</li>
                    <li>Medium: ${report.executive_summary.medium_count}</li>
                    <li>Low: ${report.executive_summary.low_count}</li>
                </ul>
                
                <h3>Exploit Chains</h3>
                <p>${report.executive_summary.chain_count} exploit chains identified</p>
                
                <h3>Recommendations</h3>
                ${report.recommendations.map(rec => `
                    <div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid #00ff00;">
                        <strong>${rec.title}</strong> (${rec.priority})<br>
                        ${rec.description}<br>
                        <em>Timeline: ${rec.timeline}</em>
                    </div>
                `).join('')}
            `;
            
            document.getElementById('report-modal').style.display = 'block';
        }
        
        function clearFindings() {
            if (confirm('Clear all findings?')) {
                document.getElementById('findings-list').innerHTML = 
                    '<p style="text-align: center; color: #666; padding: 20px;">Findings cleared.</p>';
            }
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Simulate system resources
            setInterval(() => {
                const memUsage = Math.floor(Math.random() * 500) + 800;
                const toolsRunning = Math.floor(Math.random() * 3);
                
                document.getElementById('memory-usage').textContent = memUsage + 'MB';
                document.getElementById('tools-running').textContent = toolsRunning;
            }, 3000);
        });
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🎯 APEX HUNTER - Enhanced Multi-Target Web Interface")
    print("=" * 60)
    print("🌐 Starting web server...")
    print("📱 Supports: URLs, IPs, APKs, Source Code, GitHub Repos")
    print("🔗 Access at: http://localhost:12000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=12000, debug=False)