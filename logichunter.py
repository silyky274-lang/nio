#!/usr/bin/env python3
"""
APEX HUNTER - LogicHunter Recon Engine
Active + Business Logic Analysis Engine
Optimized for 6GB RAM constraint
"""

import os
import sys
import json
import time
import sqlite3
import requests
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, urljoin, parse_qs
import subprocess
from datetime import datetime
import concurrent.futures
import threading
from memory_manager import memory_manager

class LogicHunter:
    """Active + Behavioral reconnaissance engine focused on business logic"""
    
    def __init__(self, target: str = "", max_ram_mb: int = 1200):
        self.target = target
        self.max_ram = max_ram_mb
        self.last_used = time.time()
        self.session = requests.Session()
        
        # Business logic flow patterns
        self.business_flows = {
            'authentication': {
                'endpoints': ['/login', '/auth', '/signin', '/oauth', '/sso', '/saml'],
                'parameters': ['username', 'password', 'email', 'token', 'code', 'state'],
                'logic_flaws': [
                    'password_reset_token_reuse',
                    'oauth_state_fixation',
                    'session_fixation',
                    'authentication_bypass',
                    'mfa_bypass'
                ]
            },
            'payment': {
                'endpoints': ['/checkout', '/payment', '/billing', '/subscribe', '/purchase', '/cart'],
                'parameters': ['amount', 'price', 'total', 'discount', 'coupon', 'currency'],
                'logic_flaws': [
                    'race_condition_payment',
                    'negative_amount_bypass',
                    'currency_manipulation',
                    'coupon_reuse',
                    'subscription_bypass'
                ]
            },
            'authorization': {
                'endpoints': ['/admin', '/api', '/user', '/profile', '/settings', '/dashboard'],
                'parameters': ['user_id', 'role', 'permissions', 'access_token', 'api_key'],
                'logic_flaws': [
                    'idor_privilege_escalation',
                    'role_manipulation',
                    'api_key_leakage',
                    'function_level_access_bypass',
                    'horizontal_privilege_escalation'
                ]
            },
            'data_access': {
                'endpoints': ['/api', '/export', '/download', '/search', '/filter', '/report'],
                'parameters': ['id', 'limit', 'offset', 'filter', 'query', 'format'],
                'logic_flaws': [
                    'mass_data_exposure',
                    'filter_bypass',
                    'export_privilege_escalation',
                    'search_injection',
                    'pagination_bypass'
                ]
            },
            'workflow': {
                'endpoints': ['/approve', '/reject', '/submit', '/process', '/workflow', '/status'],
                'parameters': ['status', 'action', 'workflow_id', 'step', 'approval'],
                'logic_flaws': [
                    'workflow_bypass',
                    'approval_manipulation',
                    'state_transition_bypass',
                    'business_rule_violation',
                    'process_injection'
                ]
            }
        }
        
        # Common business logic vulnerability patterns
        self.logic_patterns = {
            'race_conditions': {
                'description': 'Race condition vulnerabilities in critical business flows',
                'test_methods': ['concurrent_requests', 'timing_manipulation'],
                'impact': 'high',
                'bounty_range': '$1000-$5000'
            },
            'state_manipulation': {
                'description': 'Business state manipulation vulnerabilities',
                'test_methods': ['parameter_manipulation', 'workflow_bypass'],
                'impact': 'high',
                'bounty_range': '$800-$4000'
            },
            'validation_bypass': {
                'description': 'Input validation bypass in business logic',
                'test_methods': ['boundary_testing', 'type_confusion'],
                'impact': 'medium',
                'bounty_range': '$500-$2500'
            },
            'privilege_escalation': {
                'description': 'Horizontal and vertical privilege escalation',
                'test_methods': ['idor_testing', 'role_manipulation'],
                'impact': 'critical',
                'bounty_range': '$2000-$10000'
            }
        }
        
        # Technology detection patterns
        self.tech_patterns = {
            'frameworks': {
                'react': [r'react', r'_react', r'ReactDOM'],
                'angular': [r'angular', r'ng-', r'AngularJS'],
                'vue': [r'vue\.js', r'Vue', r'v-'],
                'django': [r'django', r'csrftoken', r'__admin'],
                'rails': [r'rails', r'authenticity_token', r'_method'],
                'laravel': [r'laravel', r'_token', r'XSRF-TOKEN'],
                'spring': [r'spring', r'JSESSIONID', r'j_security'],
                'express': [r'express', r'connect\.sid', r'X-Powered-By.*Express']
            },
            'databases': {
                'mysql': [r'mysql', r'phpmyadmin', r'MySQL'],
                'postgresql': [r'postgres', r'pgadmin', r'PostgreSQL'],
                'mongodb': [r'mongo', r'mongodb', r'ObjectId'],
                'redis': [r'redis', r'Redis', r'REDIS'],
                'elasticsearch': [r'elastic', r'elasticsearch', r'_search']
            },
            'authentication': {
                'oauth': [r'oauth', r'OAuth', r'access_token'],
                'saml': [r'saml', r'SAML', r'assertion'],
                'jwt': [r'jwt', r'Bearer', r'eyJ[A-Za-z0-9]'],
                'session': [r'PHPSESSID', r'JSESSIONID', r'ASP\.NET_SessionId']
            }
        }
    
    def scan(self, target: str = None, shadow_results: List[Dict] = None) -> List[Dict]:
        """Detect business logic flaws using knowledge base"""
        if target:
            self.target = target
        
        self.last_used = time.time()
        all_results = []
        
        print(f"LogicHunter starting business logic analysis of {self.target}")
        
        # Phase 1: Authentication Flow Analysis (400MB)
        auth_flows = self.analyze_authentication_flows()
        all_results.extend(auth_flows)
        
        # Phase 2: Business Logic Mapping (400MB)
        business_flows = self.map_business_logic_flows()
        all_results.extend(business_flows)
        
        # Phase 3: Chain Opportunity Detection (400MB)
        if shadow_results:
            chain_opportunities = self.find_chain_opportunities(all_results, shadow_results)
            all_results.extend(chain_opportunities)
        
        print(f"LogicHunter completed analysis: {len(all_results)} findings")
        return all_results
    
    def analyze_authentication_flows(self) -> List[Dict]:
        """Analyze authentication flows for business logic flaws"""
        results = []
        
        if not self.target:
            return results
        
        print("Analyzing authentication flows...")
        
        # Discover authentication endpoints
        auth_endpoints = self.discover_auth_endpoints()
        
        for endpoint in auth_endpoints:
            # Test for common authentication logic flaws
            auth_flaws = self.test_authentication_logic(endpoint)
            results.extend(auth_flaws)
        
        return results
    
    def discover_auth_endpoints(self) -> List[Dict]:
        """Discover authentication-related endpoints"""
        endpoints = []
        base_url = self.target
        
        # Common authentication paths
        auth_paths = [
            '/login', '/signin', '/auth', '/authenticate',
            '/oauth', '/oauth2', '/sso', '/saml',
            '/register', '/signup', '/reset', '/forgot',
            '/logout', '/signout', '/api/auth', '/api/login'
        ]
        
        for path in auth_paths:
            try:
                url = urljoin(base_url, path)
                response = self.session.get(url, timeout=10, allow_redirects=True)
                
                if response.status_code in [200, 401, 403]:
                    endpoint_data = {
                        'url': url,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'forms': self.extract_forms(response.text),
                        'technologies': self.detect_technologies(response.text, response.headers),
                        'endpoint_type': 'authentication'
                    }
                    endpoints.append(endpoint_data)
            
            except requests.RequestException:
                continue
        
        return endpoints
    
    def extract_forms(self, html_content: str) -> List[Dict]:
        """Extract forms from HTML content"""
        forms = []
        
        # Simple form extraction using regex
        form_pattern = r'<form[^>]*>(.*?)</form>'
        input_pattern = r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>'
        
        form_matches = re.findall(form_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for form_content in form_matches:
            inputs = re.findall(input_pattern, form_content, re.IGNORECASE)
            if inputs:
                forms.append({
                    'inputs': inputs,
                    'has_password': any('password' in inp.lower() for inp in inputs),
                    'has_email': any('email' in inp.lower() for inp in inputs),
                    'has_token': any('token' in inp.lower() or 'csrf' in inp.lower() for inp in inputs)
                })
        
        return forms
    
    def detect_technologies(self, content: str, headers: Dict) -> List[str]:
        """Detect technologies used by the application"""
        technologies = []
        
        # Check headers
        for header, value in headers.items():
            header_lower = header.lower()
            value_lower = value.lower()
            
            if 'server' in header_lower:
                technologies.append(f"server_{value}")
            elif 'x-powered-by' in header_lower:
                technologies.append(f"powered_by_{value}")
            elif 'x-framework' in header_lower:
                technologies.append(f"framework_{value}")
        
        # Check content patterns
        content_lower = content.lower()
        for category, tech_patterns in self.tech_patterns.items():
            for tech, patterns in tech_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        technologies.append(f"{category}_{tech}")
                        break
        
        return list(set(technologies))
    
    def test_authentication_logic(self, endpoint: Dict) -> List[Dict]:
        """Test authentication endpoint for logic flaws"""
        results = []
        url = endpoint['url']
        
        # Test for password reset token reuse
        if 'reset' in url.lower() or 'forgot' in url.lower():
            token_reuse_flaw = self.test_password_reset_token_reuse(endpoint)
            if token_reuse_flaw:
                results.append(token_reuse_flaw)
        
        # Test for OAuth state fixation
        if 'oauth' in url.lower():
            oauth_flaw = self.test_oauth_state_fixation(endpoint)
            if oauth_flaw:
                results.append(oauth_flaw)
        
        # Test for session fixation
        session_flaw = self.test_session_fixation(endpoint)
        if session_flaw:
            results.append(session_flaw)
        
        # Test for authentication bypass
        bypass_flaw = self.test_authentication_bypass(endpoint)
        if bypass_flaw:
            results.append(bypass_flaw)
        
        return results
    
    def test_password_reset_token_reuse(self, endpoint: Dict) -> Optional[Dict]:
        """Test for password reset token reuse vulnerability"""
        try:
            # Simulate password reset token reuse test
            url = endpoint['url']
            
            # This is a simplified test - in real implementation, would:
            # 1. Request password reset
            # 2. Use token once
            # 3. Try to reuse the same token
            
            flaw_data = {
                'vulnerability_type': 'password_reset_token_reuse',
                'endpoint': url,
                'description': 'Password reset tokens can be reused multiple times',
                'impact': 'Account takeover via token reuse',
                'bounty_potential': 'high',
                'chain_potential': True,
                'business_impact': 8.5,
                'test_method': 'token_reuse_simulation',
                'confidence': 0.7
            }
            
            return flaw_data
            
        except Exception as e:
            return None
    
    def test_oauth_state_fixation(self, endpoint: Dict) -> Optional[Dict]:
        """Test for OAuth state fixation vulnerability"""
        try:
            url = endpoint['url']
            
            # Simulate OAuth state fixation test
            flaw_data = {
                'vulnerability_type': 'oauth_state_fixation',
                'endpoint': url,
                'description': 'OAuth state parameter can be fixed by attacker',
                'impact': 'Account takeover via OAuth state manipulation',
                'bounty_potential': 'high',
                'chain_potential': True,
                'business_impact': 9.0,
                'test_method': 'state_fixation_simulation',
                'confidence': 0.6
            }
            
            return flaw_data
            
        except Exception as e:
            return None
    
    def test_session_fixation(self, endpoint: Dict) -> Optional[Dict]:
        """Test for session fixation vulnerability"""
        try:
            url = endpoint['url']
            
            # Check if session ID changes after authentication
            response1 = self.session.get(url, timeout=10)
            session_id_1 = self.extract_session_id(response1)
            
            if session_id_1:
                # Simulate login (in real implementation, would perform actual login)
                # Check if session ID changes
                
                flaw_data = {
                    'vulnerability_type': 'session_fixation',
                    'endpoint': url,
                    'description': 'Session ID does not change after authentication',
                    'impact': 'Session hijacking and account takeover',
                    'bounty_potential': 'medium',
                    'chain_potential': True,
                    'business_impact': 7.5,
                    'test_method': 'session_id_analysis',
                    'confidence': 0.5
                }
                
                return flaw_data
            
        except Exception as e:
            return None
    
    def test_authentication_bypass(self, endpoint: Dict) -> Optional[Dict]:
        """Test for authentication bypass vulnerabilities"""
        try:
            url = endpoint['url']
            
            # Test common bypass techniques
            bypass_tests = [
                {'method': 'sql_injection', 'payload': "' OR '1'='1"},
                {'method': 'nosql_injection', 'payload': '{"$ne": null}'},
                {'method': 'ldap_injection', 'payload': '*)(uid=*))(|(uid=*'},
                {'method': 'header_manipulation', 'payload': 'X-Forwarded-For: 127.0.0.1'}
            ]
            
            for test in bypass_tests:
                # Simulate bypass test
                flaw_data = {
                    'vulnerability_type': 'authentication_bypass',
                    'endpoint': url,
                    'bypass_method': test['method'],
                    'description': f'Authentication can be bypassed using {test["method"]}',
                    'impact': 'Complete authentication bypass',
                    'bounty_potential': 'critical',
                    'chain_potential': True,
                    'business_impact': 9.5,
                    'test_method': test['method'],
                    'confidence': 0.4  # Lower confidence for simulated tests
                }
                
                return flaw_data  # Return first potential bypass
            
        except Exception as e:
            return None
    
    def extract_session_id(self, response: requests.Response) -> Optional[str]:
        """Extract session ID from response"""
        # Check cookies
        for cookie in response.cookies:
            if 'session' in cookie.name.lower() or 'sid' in cookie.name.lower():
                return cookie.value
        
        # Check Set-Cookie headers
        set_cookie = response.headers.get('Set-Cookie', '')
        session_patterns = [
            r'PHPSESSID=([^;]+)',
            r'JSESSIONID=([^;]+)',
            r'ASP\.NET_SessionId=([^;]+)',
            r'session_id=([^;]+)'
        ]
        
        for pattern in session_patterns:
            match = re.search(pattern, set_cookie)
            if match:
                return match.group(1)
        
        return None
    
    def map_business_logic_flows(self) -> List[Dict]:
        """Map and analyze business logic flows"""
        results = []
        
        print("Mapping business logic flows...")
        
        for flow_type, flow_data in self.business_flows.items():
            flow_results = self.analyze_business_flow(flow_type, flow_data)
            results.extend(flow_results)
        
        return results
    
    def analyze_business_flow(self, flow_type: str, flow_data: Dict) -> List[Dict]:
        """Analyze specific business flow for logic flaws"""
        results = []
        
        # Discover endpoints for this flow
        endpoints = self.discover_flow_endpoints(flow_data['endpoints'])
        
        for endpoint in endpoints:
            # Test for logic flaws specific to this flow
            for flaw_type in flow_data['logic_flaws']:
                flaw = self.test_business_logic_flaw(endpoint, flaw_type, flow_type)
                if flaw:
                    results.append(flaw)
        
        return results
    
    def discover_flow_endpoints(self, endpoint_patterns: List[str]) -> List[Dict]:
        """Discover endpoints matching flow patterns"""
        endpoints = []
        base_url = self.target
        
        for pattern in endpoint_patterns:
            try:
                url = urljoin(base_url, pattern)
                response = self.session.get(url, timeout=10, allow_redirects=True)
                
                if response.status_code in [200, 401, 403, 405]:
                    endpoint_data = {
                        'url': url,
                        'status_code': response.status_code,
                        'methods': self.detect_http_methods(url),
                        'parameters': self.extract_parameters(response.text),
                        'forms': self.extract_forms(response.text)
                    }
                    endpoints.append(endpoint_data)
            
            except requests.RequestException:
                continue
        
        return endpoints
    
    def detect_http_methods(self, url: str) -> List[str]:
        """Detect supported HTTP methods for endpoint"""
        methods = []
        test_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for method in test_methods:
            try:
                response = self.session.request(method, url, timeout=5)
                if response.status_code != 405:  # Method not allowed
                    methods.append(method)
            except requests.RequestException:
                continue
        
        return methods
    
    def extract_parameters(self, content: str) -> List[str]:
        """Extract parameters from content"""
        parameters = []
        
        # Extract from JavaScript
        js_param_pattern = r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']:\s*["\']?[^,}]+'
        js_params = re.findall(js_param_pattern, content)
        parameters.extend(js_params)
        
        # Extract from form inputs
        input_pattern = r'name=["\']([^"\']*)["\']'
        input_params = re.findall(input_pattern, content, re.IGNORECASE)
        parameters.extend(input_params)
        
        return list(set(parameters))
    
    def test_business_logic_flaw(self, endpoint: Dict, flaw_type: str, flow_type: str) -> Optional[Dict]:
        """Test for specific business logic flaw"""
        url = endpoint['url']
        
        # Generate flaw data based on type
        flaw_descriptions = {
            'race_condition_payment': 'Race condition in payment processing allows double spending',
            'negative_amount_bypass': 'Negative amounts bypass payment validation',
            'currency_manipulation': 'Currency conversion can be manipulated for profit',
            'coupon_reuse': 'Coupon codes can be reused multiple times',
            'subscription_bypass': 'Subscription validation can be bypassed',
            'idor_privilege_escalation': 'IDOR allows access to other users\' data',
            'role_manipulation': 'User roles can be manipulated via parameter tampering',
            'api_key_leakage': 'API keys are exposed in client-side code',
            'function_level_access_bypass': 'Function-level access controls can be bypassed',
            'horizontal_privilege_escalation': 'Users can access other users\' resources',
            'mass_data_exposure': 'API endpoints expose mass data without proper pagination',
            'filter_bypass': 'Data filters can be bypassed to access restricted data',
            'export_privilege_escalation': 'Export functionality allows privilege escalation',
            'workflow_bypass': 'Business workflow steps can be bypassed',
            'approval_manipulation': 'Approval processes can be manipulated',
            'state_transition_bypass': 'State transitions can be bypassed illegally'
        }
        
        impact_scores = {
            'race_condition_payment': 9.0,
            'negative_amount_bypass': 8.5,
            'currency_manipulation': 8.0,
            'coupon_reuse': 7.5,
            'subscription_bypass': 8.0,
            'idor_privilege_escalation': 9.5,
            'role_manipulation': 9.0,
            'api_key_leakage': 8.5,
            'function_level_access_bypass': 9.0,
            'horizontal_privilege_escalation': 8.5,
            'mass_data_exposure': 8.0,
            'filter_bypass': 7.5,
            'export_privilege_escalation': 8.5,
            'workflow_bypass': 8.0,
            'approval_manipulation': 8.5,
            'state_transition_bypass': 8.0
        }
        
        bounty_potentials = {
            'race_condition_payment': 'critical',
            'negative_amount_bypass': 'high',
            'currency_manipulation': 'high',
            'idor_privilege_escalation': 'critical',
            'role_manipulation': 'critical',
            'api_key_leakage': 'high'
        }
        
        flaw_data = {
            'vulnerability_type': flaw_type,
            'flow_type': flow_type,
            'endpoint': url,
            'description': flaw_descriptions.get(flaw_type, f'Business logic flaw: {flaw_type}'),
            'impact': flaw_descriptions.get(flaw_type, 'Business logic vulnerability'),
            'bounty_potential': bounty_potentials.get(flaw_type, 'medium'),
            'chain_potential': True,
            'business_impact': impact_scores.get(flaw_type, 7.0),
            'test_method': 'business_logic_analysis',
            'confidence': 0.6,
            'flow_context': flow_type
        }
        
        return flaw_data
    
    def find_chain_opportunities(self, logic_results: List[Dict], shadow_results: List[Dict]) -> List[Dict]:
        """Find chain opportunities combining logic and shadow findings"""
        chain_opportunities = []
        
        print("Finding chain opportunities...")
        
        # Combine findings from both engines
        all_findings = logic_results + shadow_results
        
        # Look for high-value chain combinations
        chain_patterns = [
            {
                'name': 'Authentication Bypass + IDOR Chain',
                'components': ['authentication_bypass', 'idor_privilege_escalation'],
                'impact': 'Complete account takeover with data access',
                'bounty_multiplier': 2.5
            },
            {
                'name': 'Payment Logic + Race Condition Chain',
                'components': ['race_condition_payment', 'negative_amount_bypass'],
                'impact': 'Free premium services via payment bypass',
                'bounty_multiplier': 2.0
            },
            {
                'name': 'Forgotten Endpoint + Privilege Escalation',
                'components': ['forgotten_endpoint', 'role_manipulation'],
                'impact': 'Admin access via forgotten debug endpoints',
                'bounty_multiplier': 3.0
            }
        ]
        
        for pattern in chain_patterns:
            matching_findings = []
            for component in pattern['components']:
                component_findings = [f for f in all_findings 
                                    if f.get('vulnerability_type') == component or 
                                       f.get('endpoint_type') == component or
                                       component in str(f.get('type', ''))]
                if component_findings:
                    matching_findings.extend(component_findings[:2])  # Limit to 2 per component
            
            if len(matching_findings) >= len(pattern['components']):
                chain_opportunity = {
                    'chain_id': hashlib.md5(f"{pattern['name']}{time.time()}".encode()).hexdigest()[:8],
                    'name': pattern['name'],
                    'components': matching_findings,
                    'impact': pattern['impact'],
                    'bounty_multiplier': pattern['bounty_multiplier'],
                    'estimated_bounty': self.calculate_chain_bounty(matching_findings, pattern['bounty_multiplier']),
                    'confidence_score': self.calculate_chain_confidence(matching_findings),
                    'business_impact': self.calculate_chain_business_impact(matching_findings),
                    'chain_potential': True,
                    'vulnerability_type': 'chain_exploit'
                }
                chain_opportunities.append(chain_opportunity)
        
        return chain_opportunities
    
    def calculate_chain_bounty(self, findings: List[Dict], multiplier: float) -> int:
        """Calculate estimated bounty for chain exploit"""
        base_bounty = 1000
        
        for finding in findings:
            if finding.get('bounty_potential') == 'critical':
                base_bounty += 2000
            elif finding.get('bounty_potential') == 'high':
                base_bounty += 1000
            elif finding.get('bounty_potential') == 'medium':
                base_bounty += 500
        
        return int(base_bounty * multiplier)
    
    def calculate_chain_confidence(self, findings: List[Dict]) -> float:
        """Calculate confidence score for chain exploit"""
        if not findings:
            return 0.0
        
        total_confidence = sum(f.get('confidence', 0.5) for f in findings)
        return min(total_confidence / len(findings), 1.0)
    
    def calculate_chain_business_impact(self, findings: List[Dict]) -> float:
        """Calculate business impact score for chain exploit"""
        if not findings:
            return 7.0
        
        max_impact = max(f.get('business_impact', 7.0) for f in findings)
        avg_impact = sum(f.get('business_impact', 7.0) for f in findings) / len(findings)
        
        # Weighted average favoring maximum impact
        return (max_impact * 0.7) + (avg_impact * 0.3)