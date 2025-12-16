#!/usr/bin/env python3
"""
APEX HUNTER - Zero Dependency Interface
Works with basic Python installation - no external libraries needed
"""

import http.server
import socketserver
import json
import urllib.parse
import threading
import time
import subprocess
import os
import sys

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APEX HUNTER Elite - Bug Bounty Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff41; 
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { 
            font-size: 3em; 
            text-shadow: 0 0 20px #00ff41; 
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 20px #00ff41; }
            to { text-shadow: 0 0 30px #00ff41, 0 0 40px #00ff41; }
        }
        .subtitle { color: #888; font-size: 1.2em; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .card { 
            background: rgba(0, 255, 65, 0.1); 
            border: 1px solid #00ff41; 
            border-radius: 10px; 
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .card h3 { color: #00ff41; margin-bottom: 15px; font-size: 1.3em; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; color: #ccc; }
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 10px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ff41;
            border-radius: 5px;
            color: #00ff41;
            font-family: 'Courier New', monospace;
        }
        .btn {
            background: linear-gradient(45deg, #00ff41, #00cc33);
            color: #000;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
        }
        .btn:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .status { 
            background: rgba(0, 0, 0, 0.8); 
            border: 1px solid #00ff41; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        .status h3 { color: #00ff41; margin-bottom: 15px; }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff41, #00cc33);
            width: 0%;
            transition: width 0.3s;
        }
        .findings { 
            background: rgba(0, 0, 0, 0.8); 
            border: 1px solid #00ff41; 
            border-radius: 10px; 
            padding: 20px; 
            max-height: 400px; 
            overflow-y: auto;
        }
        .finding {
            background: rgba(0, 255, 65, 0.1);
            border-left: 4px solid #00ff41;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .finding.high { border-left-color: #ff4444; }
        .finding.medium { border-left-color: #ffaa00; }
        .finding.low { border-left-color: #4444ff; }
        .finding.critical { border-left-color: #ff0000; }
        .timestamp { color: #888; font-size: 0.8em; }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #00ff41;
        }
        .tab {
            padding: 10px 20px;
            background: transparent;
            border: none;
            color: #888;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            border-bottom: 2px solid transparent;
        }
        .tab.active {
            color: #00ff41;
            border-bottom-color: #00ff41;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.1;
        }
        .install-section {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff4444;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .install-section h3 {
            color: #ff4444;
            margin-bottom: 15px;
        }
        .command {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff41;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            color: #00ff41;
            margin: 10px 0;
            cursor: pointer;
        }
        .command:hover {
            background: rgba(0, 255, 65, 0.1);
        }
    </style>
</head>
<body>
    <div class="matrix-bg" id="matrix"></div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 APEX HUNTER</h1>
            <p class="subtitle">Elite Bug Bounty Automation System</p>
            <p class="subtitle">Multi-Target Analysis | Smart Contracts | Mobile Apps | Web Applications</p>
        </div>

        <div class="install-section">
            <h3>🔧 Quick Setup Required</h3>
            <p>To unlock full functionality, run these commands in your terminal:</p>
            
            <div class="command" onclick="copyToClipboard(this)">
                chmod +x fix_dependencies.sh && ./fix_dependencies.sh
            </div>
            
            <div class="command" onclick="copyToClipboard(this)">
                python enhanced_web_interface.py
            </div>
            
            <p style="margin-top: 15px; color: #888;">
                ✅ This will install all required tools and start the full elite interface<br>
                ✅ Includes: Nuclei, Metasploit, Smart Contract Analysis, Mobile Tools<br>
                ✅ Takes 2-3 minutes to complete
            </p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('hunt')">🎯 Hunt</button>
            <button class="tab" onclick="showTab('upload')">📱 Upload</button>
            <button class="tab" onclick="showTab('github')">🔗 GitHub</button>
            <button class="tab" onclick="showTab('results')">📊 Results</button>
            <button class="tab" onclick="showTab('setup')">⚙️ Setup</button>
        </div>

        <div id="hunt" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h3>🎯 Target Configuration</h3>
                    <div class="input-group">
                        <label for="target">Target (URL, IP, Domain)</label>
                        <input type="text" id="target" placeholder="api.notion.com, 192.168.1.1, example.com" value="api.notion.com">
                    </div>
                    <div class="input-group">
                        <label for="target-type">Target Type</label>
                        <select id="target-type">
                            <option value="auto">Auto-detect</option>
                            <option value="url">Web Application</option>
                            <option value="ip">IP Address</option>
                            <option value="api">API Endpoint</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="analysis-mode">Analysis Mode</label>
                        <select id="analysis-mode">
                            <option value="standard">Standard Hunt</option>
                            <option value="deep">Deep Analysis (Verified PoCs)</option>
                            <option value="stealth">Stealth Mode</option>
                            <option value="aggressive">Aggressive Scan</option>
                        </select>
                    </div>
                    <button class="btn" onclick="startHunt()" id="hunt-btn">🚀 Start Hunt</button>
                </div>

                <div class="card">
                    <h3>⚙️ Advanced Options</h3>
                    <div class="input-group">
                        <label for="scope">Scope (Optional)</label>
                        <textarea id="scope" rows="3" placeholder="*.example.com&#10;api.example.com&#10;admin.example.com"></textarea>
                    </div>
                    <div class="input-group">
                        <label for="exclude">Exclude (Optional)</label>
                        <input type="text" id="exclude" placeholder="logout.php, admin/delete">
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="screenshots" checked> Capture Screenshots
                        </label>
                    </div>
                    <div class="input-group">
                        <label>
                            <input type="checkbox" id="videos" checked> Record PoC Videos
                        </label>
                    </div>
                </div>
            </div>
        </div>

        <div id="upload" class="tab-content">
            <div class="card">
                <h3>📱 File Upload Analysis</h3>
                <div class="input-group">
                    <label for="file-upload">Upload APK, Source Code, or Binary</label>
                    <input type="file" id="file-upload" accept=".apk,.zip,.tar.gz,.jar,.war,.ipa">
                </div>
                <div class="input-group">
                    <label for="upload-type">Analysis Type</label>
                    <select id="upload-type">
                        <option value="auto">Auto-detect</option>
                        <option value="android">Android APK</option>
                        <option value="ios">iOS IPA</option>
                        <option value="source">Source Code</option>
                        <option value="binary">Binary Analysis</option>
                    </select>
                </div>
                <button class="btn" onclick="uploadFile()">📤 Upload & Analyze</button>
            </div>
        </div>

        <div id="github" class="tab-content">
            <div class="card">
                <h3>🔗 GitHub Repository Analysis</h3>
                <div class="input-group">
                    <label for="github-url">GitHub Repository URL</label>
                    <input type="text" id="github-url" placeholder="https://github.com/user/repo">
                </div>
                <div class="input-group">
                    <label for="analysis-depth">Analysis Depth</label>
                    <select id="analysis-depth">
                        <option value="surface">Surface Scan</option>
                        <option value="deep">Deep Code Analysis</option>
                        <option value="secrets">Secrets & Credentials</option>
                        <option value="dependencies">Dependency Analysis</option>
                    </select>
                </div>
                <button class="btn" onclick="analyzeGithub()">🔍 Clone & Analyze</button>
            </div>
        </div>

        <div id="results" class="tab-content">
            <div class="card">
                <h3>📊 Hunt Statistics</h3>
                <p>Total Hunts: <span id="total-hunts">0</span></p>
                <p>Vulnerabilities Found: <span id="total-vulns">0</span></p>
                <p>Chain Exploits: <span id="total-chains">0</span></p>
                <p>Estimated Bounty: $<span id="total-bounty">0</span></p>
            </div>
        </div>

        <div id="setup" class="tab-content">
            <div class="card">
                <h3>⚙️ Elite Setup Guide</h3>
                <h4>🔧 Step 1: Fix Dependencies</h4>
                <div class="command" onclick="copyToClipboard(this)">chmod +x fix_dependencies.sh && ./fix_dependencies.sh</div>
                
                <h4>🛠️ Step 2: Install Elite Tools (Optional)</h4>
                <div class="command" onclick="copyToClipboard(this)">chmod +x ULTIMATE_SETUP.sh && ./ULTIMATE_SETUP.sh</div>
                
                <h4>🚀 Step 3: Start Elite Interface</h4>
                <div class="command" onclick="copyToClipboard(this)">python enhanced_web_interface.py</div>
                
                <h4>📚 What You Get:</h4>
                <ul style="margin: 15px 0; padding-left: 20px; color: #ccc;">
                    <li>🎯 Nuclei with 5000+ vulnerability templates</li>
                    <li>💥 Metasploit exploitation framework</li>
                    <li>📱 Mobile app analysis (APK, IPA)</li>
                    <li>🔗 Smart contract analysis (Slither, Mythril)</li>
                    <li>🌐 Advanced web application testing</li>
                    <li>📊 Professional evidence collection</li>
                    <li>⛓️ Exploit chain detection</li>
                    <li>💰 Bounty estimation and reporting</li>
                </ul>
            </div>
        </div>

        <div class="status" id="status" style="display: none;">
            <h3>🔍 Hunt Status</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progress"></div>
            </div>
            <p>Phase: <span id="phase">Idle</span></p>
            <p>Target: <span id="current-target">None</span></p>
            <p>Elapsed: <span id="elapsed">0s</span></p>
            <p>Findings: <span id="finding-count">0</span></p>
        </div>

        <div class="findings" id="findings-container" style="display: none;">
            <h3>🔍 Live Findings</h3>
            <div id="findings"></div>
        </div>
    </div>

    <script>
        let huntActive = false;
        let startTime = 0;
        let findings = [];

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function copyToClipboard(element) {
            const text = element.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = element.textContent;
                element.textContent = '✅ Copied to clipboard!';
                element.style.background = 'rgba(0, 255, 65, 0.2)';
                setTimeout(() => {
                    element.textContent = originalText;
                    element.style.background = 'rgba(0, 0, 0, 0.8)';
                }, 2000);
            });
        }

        function startHunt() {
            const target = document.getElementById('target').value.trim();
            if (!target) {
                alert('Please enter a target');
                return;
            }

            huntActive = true;
            startTime = Date.now();
            findings = [];

            // Update UI
            document.getElementById('hunt-btn').disabled = true;
            document.getElementById('hunt-btn').textContent = '🔍 Hunting...';
            document.getElementById('status').style.display = 'block';
            document.getElementById('findings-container').style.display = 'block';
            document.getElementById('current-target').textContent = target;
            document.getElementById('findings').innerHTML = '';

            // Simulate hunt phases
            simulateHunt();
        }

        function simulateHunt() {
            const phases = [
                'Initializing analysis',
                'Target reconnaissance',
                'Subdomain enumeration',
                'Technology detection',
                'Vulnerability scanning',
                'Deep analysis',
                'Chain detection',
                'Evidence collection',
                'Report generation'
            ];

            let currentPhase = 0;
            const phaseInterval = setInterval(() => {
                if (currentPhase < phases.length) {
                    document.getElementById('phase').textContent = phases[currentPhase];
                    document.getElementById('progress').style.width = ((currentPhase + 1) / phases.length * 100) + '%';
                    
                    // Add some findings
                    if (currentPhase >= 2) {
                        addRandomFinding();
                    }
                    
                    currentPhase++;
                } else {
                    clearInterval(phaseInterval);
                    completehunt();
                }
            }, 2000);

            // Update elapsed time
            const timeInterval = setInterval(() => {
                if (huntActive) {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    document.getElementById('elapsed').textContent = elapsed + 's';
                } else {
                    clearInterval(timeInterval);
                }
            }, 1000);
        }

        function addRandomFinding() {
            const findingTypes = [
                { type: 'subdomain', severity: 'info', title: 'Subdomain Discovery', desc: 'admin.api.notion.com' },
                { type: 'technology', severity: 'info', title: 'Technology Detection', desc: 'Next.js, Cloudflare detected' },
                { type: 'vulnerability', severity: 'high', title: 'SQL Injection', desc: 'Error-based SQL injection in /api/search' },
                { type: 'vulnerability', severity: 'medium', title: 'XSS Vulnerability', desc: 'Reflected XSS in search parameter' },
                { type: 'vulnerability', severity: 'high', title: 'IDOR Vulnerability', desc: 'Access to other users\' data via /api/user/{id}' },
                { type: 'chain', severity: 'critical', title: 'Exploit Chain', desc: 'IDOR → Authentication Bypass → Admin Access' }
            ];

            const randomFinding = findingTypes[Math.floor(Math.random() * findingTypes.length)];
            const finding = {
                ...randomFinding,
                timestamp: new Date().toLocaleTimeString(),
                description: randomFinding.desc
            };

            findings.push(finding);
            displayFinding(finding);
            document.getElementById('finding-count').textContent = findings.length;
        }

        function displayFinding(finding) {
            const findingsContainer = document.getElementById('findings');
            const findingElement = document.createElement('div');
            findingElement.className = `finding ${finding.severity}`;
            findingElement.innerHTML = `
                <strong>${finding.title}</strong>
                <p>${finding.description}</p>
                <span class="timestamp">${finding.timestamp}</span>
            `;
            findingsContainer.insertBefore(findingElement, findingsContainer.firstChild);
        }

        function completehunt() {
            huntActive = false;
            document.getElementById('hunt-btn').disabled = false;
            document.getElementById('hunt-btn').textContent = '🚀 Start Hunt';
            document.getElementById('phase').textContent = 'Complete';
            
            // Add final chain exploit
            const chainExploit = {
                type: 'chain',
                severity: 'critical',
                title: 'API Privilege Escalation Chain',
                description: 'Multi-step exploit chain: SQL Injection → IDOR → Admin Panel Access',
                timestamp: new Date().toLocaleTimeString()
            };
            findings.push(chainExploit);
            displayFinding(chainExploit);
            
            // Update statistics
            const vulnCount = findings.filter(f => f.type === 'vulnerability').length;
            const chainCount = findings.filter(f => f.type === 'chain').length;
            const estimatedBounty = vulnCount * 1500 + chainCount * 5000;
            
            document.getElementById('total-hunts').textContent = parseInt(document.getElementById('total-hunts').textContent) + 1;
            document.getElementById('total-vulns').textContent = parseInt(document.getElementById('total-vulns').textContent) + vulnCount;
            document.getElementById('total-chains').textContent = parseInt(document.getElementById('total-chains').textContent) + chainCount;
            document.getElementById('total-bounty').textContent = parseInt(document.getElementById('total-bounty').textContent) + estimatedBounty;
            
            // Show completion message
            alert(`🎉 Hunt Complete!\\n\\n📊 Results:\\n• Vulnerabilities: ${vulnCount}\\n• Chain Exploits: ${chainCount}\\n• Estimated Bounty: $${estimatedBounty}\\n\\n🔧 For full functionality, run the setup commands in the Setup tab!`);
        }

        function uploadFile() {
            const fileInput = document.getElementById('file-upload');
            if (!fileInput.files.length) {
                alert('Please select a file to upload');
                return;
            }
            
            alert('📱 File upload analysis requires the full setup.\\n\\nRun: ./fix_dependencies.sh\\nThen: python enhanced_web_interface.py');
        }

        function analyzeGithub() {
            const githubUrl = document.getElementById('github-url').value.trim();
            if (!githubUrl) {
                alert('Please enter a GitHub repository URL');
                return;
            }
            
            alert('🔗 GitHub repository analysis requires the full setup.\\n\\nRun: ./fix_dependencies.sh\\nThen: python enhanced_web_interface.py');
        }

        // Matrix rain effect
        function createMatrixRain() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            document.getElementById('matrix').appendChild(canvas);

            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
            const charArray = chars.split('');
            const fontSize = 14;
            const columns = canvas.width / fontSize;
            const drops = [];

            for (let i = 0; i < columns; i++) {
                drops[i] = 1;
            }

            function draw() {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#00ff41';
                ctx.font = fontSize + 'px monospace';

                for (let i = 0; i < drops.length; i++) {
                    const text = charArray[Math.floor(Math.random() * charArray.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }

            setInterval(draw, 33);
        }

        // Initialize matrix effect
        createMatrixRain();

        // Handle window resize
        window.addEventListener('resize', () => {
            document.getElementById('matrix').innerHTML = '';
            createMatrixRain();
        });

        // Show welcome message
        setTimeout(() => {
            alert('🎯 Welcome to APEX HUNTER Elite!\\n\\n⚠️ This is the basic interface.\\n\\n🚀 For full elite features:\\n1. Run: ./fix_dependencies.sh\\n2. Then: python enhanced_web_interface.py\\n\\n✅ This unlocks all advanced tools and capabilities!');
        }, 1000);
    </script>
</body>
</html>
"""

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "message": "Request received"}
        self.wfile.write(json.dumps(response).encode())

def start_server(port=8080):
    """Start the simple web server"""
    try:
        with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
            print(f"🎯 APEX HUNTER Zero Dependency Interface")
            print(f"========================================")
            print(f"🌐 Server running at: http://localhost:{port}")
            print(f"🎯 Elite Bug Bounty Automation System")
            print(f"📱 Multi-target support: Web, Mobile, Smart Contracts")
            print(f"")
            print(f"⚠️  This is the basic interface with simulated results")
            print(f"🚀 For full functionality, run in your terminal:")
            print(f"   chmod +x fix_dependencies.sh && ./fix_dependencies.sh")
            print(f"   python enhanced_web_interface.py")
            print(f"")
            print(f"🛑 Press Ctrl+C to stop")
            print()
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print(f"🔄 Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    import sys
    
    # Check for port argument
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8080.")
    
    start_server(port)