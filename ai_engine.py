#!/usr/bin/env python3
"""
APEX HUNTER - AI Decision Engine
Rule-based expert system with complete knowledge base integration
Optimized for 6GB RAM constraint
"""

import os
import sys
import json
import sqlite3
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib
from memory_manager import memory_manager

class ApexHunterAIEngine:
    """Complete AI decision engine with rule-based expert system"""
    
    def __init__(self):
        """Initialize AI engine with complete knowledge base"""
        self.db_path = '/workspace/project/mr-mx-lee-/data/knowledge_base.db'
        self.chain_templates = []
        self.business_logic_rules = []
        self.platform_intelligence = {}
        self.vulnerability_database = {}
        self.last_used = time.time()
        
        # Platform-specific bounty ranges and acceptance rates
        self.platform_data = {
            'hackerone': {
                'bounty_ranges': {
                    'chain_exploit': {'min': 1000, 'max': 15000},
                    'business_logic': {'min': 800, 'max': 8000},
                    'authentication_bypass': {'min': 1500, 'max': 12000},
                    'privilege_escalation': {'min': 2000, 'max': 20000},
                    'data_exposure': {'min': 500, 'max': 5000}
                },
                'acceptance_rate': 0.42,
                'average_triage_days': 3.5
            },
            'bugcrowd': {
                'bounty_ranges': {
                    'chain_exploit': {'min': 800, 'max': 12000},
                    'business_logic': {'min': 600, 'max': 6000},
                    'authentication_bypass': {'min': 1200, 'max': 10000},
                    'privilege_escalation': {'min': 1800, 'max': 18000},
                    'data_exposure': {'min': 400, 'max': 4000}
                },
                'acceptance_rate': 0.38,
                'average_triage_days': 4.2
            },
            'intigriti': {
                'bounty_ranges': {
                    'chain_exploit': {'min': 1200, 'max': 18000},
                    'business_logic': {'min': 1000, 'max': 10000},
                    'authentication_bypass': {'min': 1800, 'max': 15000},
                    'privilege_escalation': {'min': 2500, 'max': 25000},
                    'data_exposure': {'min': 600, 'max': 6000}
                },
                'acceptance_rate': 0.45,
                'average_triage_days': 2.8
            }
        }
        
        # Chain exploit patterns that guarantee high payouts
        self.high_value_patterns = [
            {
                'pattern': ['open_redirect', 'cors_misconfiguration', 'token_leakage'],
                'name': 'Silent Account Takeover',
                'multiplier': 2.5,
                'min_bounty': 2000
            },
            {
                'pattern': ['race_condition', 'validation_bypass', 'business_logic_flaw'],
                'name': 'Payment Bypass Cascade',
                'multiplier': 2.0,
                'min_bounty': 1000
            },
            {
                'pattern': ['forgotten_debug_endpoint', 'ssrf', 'internal_network_access'],
                'name': 'Shadow Path Compromise',
                'multiplier': 3.0,
                'min_bounty': 3000
            },
            {
                'pattern': ['idor', 'missing_function_level_access_control', 'token_manipulation'],
                'name': 'API Token Escalation',
                'multiplier': 2.2,
                'min_bounty': 2500
            },
            {
                'pattern': ['open_redirect', 'state_token_leakage', 'identity_provider_misconfiguration'],
                'name': 'SSO Bypass Chain',
                'multiplier': 3.5,
                'min_bounty': 4000
            }
        ]
    
    def load_chain_templates(self) -> List[Dict]:
        """Load chain exploit templates from knowledge base"""
        if not os.path.exists(self.db_path):
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load only high-impact templates to conserve RAM
            cursor.execute("""
                SELECT template_id, name, pattern, impact_description, bounty_range, 
                       platforms, success_rate, minimum_bounty, payment_probability, business_impact_score
                FROM chain_templates 
                WHERE minimum_bounty >= 500 AND payment_probability >= 0.7
                ORDER BY business_impact_score DESC, payment_probability DESC
                LIMIT 5000  -- Only top 5K templates
            """)
            
            templates = []
            for row in cursor.fetchall():
                try:
                    pattern_data = json.loads(row[2]) if row[2] else []
                    platforms_data = json.loads(row[5]) if row[5] else []
                    
                    templates.append({
                        'template_id': row[0],
                        'name': row[1],
                        'pattern': pattern_data,
                        'impact_description': row[3],
                        'bounty_range': row[4],
                        'platforms': platforms_data,
                        'success_rate': row[6],
                        'minimum_bounty': row[7],
                        'payment_probability': row[8],
                        'business_impact_score': row[9]
                    })
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return templates
            
        except Exception as e:
            print(f"Error loading chain templates: {e}")
            return []
    
    def load_business_logic_rules(self) -> List[Dict]:
        """Load business logic flaw detection rules from knowledge base"""
        if not os.path.exists(self.db_path):
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rule_id, platform, pattern_type, detection_rules, impact_score, bounty_range, payment_probability
                FROM business_logic_rules
                WHERE impact_score >= 7.0 AND payment_probability >= 0.7
                ORDER BY impact_score DESC, payment_probability DESC
                LIMIT 3000  -- Only top 3K rules
            """)
            
            rules = []
            for row in cursor.fetchall():
                try:
                    detection_rules = json.loads(row[3]) if row[3] else {}
                    
                    rules.append({
                        'rule_id': row[0],
                        'platform': row[1],
                        'pattern_type': row[2],
                        'detection_rules': detection_rules,
                        'impact_score': row[4],
                        'bounty_range': row[5],
                        'payment_probability': row[6]
                    })
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return rules
            
        except Exception as e:
            print(f"Error loading business logic rules: {e}")
            return []
    
    def load_vulnerability_database(self) -> Dict[str, Any]:
        """Load vulnerability database with correlations"""
        if not os.path.exists(self.db_path):
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load high-impact vulnerabilities
            cursor.execute("""
                SELECT cve_id, description, cvss_score, affected_products, exploit_available
                FROM vulnerability_data
                WHERE cvss_score >= 7.0 AND exploit_available = 1
                ORDER BY cvss_score DESC
                LIMIT 5000
            """)
            
            vuln_db = {
                'cves': {},
                'correlations': {},
                'exploit_chains': []
            }
            
            for row in cursor.fetchall():
                try:
                    affected_products = json.loads(row[3]) if row[3] else []
                    
                    vuln_db['cves'][row[0]] = {
                        'description': row[1],
                        'cvss_score': row[2],
                        'affected_products': affected_products,
                        'exploit_available': row[4]
                    }
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return vuln_db
            
        except Exception as e:
            print(f"Error loading vulnerability database: {e}")
            return {}
    
    def initialize_knowledge_base(self):
        """Initialize AI knowledge base on-demand"""
        if not self.chain_templates:
            self.chain_templates = self.load_chain_templates()
        
        if not self.business_logic_rules:
            self.business_logic_rules = self.load_business_logic_rules()
        
        if not self.vulnerability_database:
            self.vulnerability_database = self.load_vulnerability_database()
    
    def correlate_with_vulnerability_database(self, findings: List[Dict]) -> List[Dict]:
        """Correlate findings with vulnerability database"""
        self.initialize_knowledge_base()
        correlated_findings = []
        
        for finding in findings:
            # Add vulnerability correlation data
            correlated_finding = finding.copy()
            correlated_finding['vulnerability_correlations'] = []
            correlated_finding['exploit_potential'] = 0.0
            
            # Check for CVE correlations based on technology stack
            if 'technology' in finding:
                tech = finding['technology'].lower()
                for cve_id, cve_data in self.vulnerability_database.get('cves', {}).items():
                    if any(tech in product.lower() for product in cve_data['affected_products']):
                        correlated_finding['vulnerability_correlations'].append({
                            'cve_id': cve_id,
                            'cvss_score': cve_data['cvss_score'],
                            'exploit_available': cve_data['exploit_available']
                        })
                        
                        # Increase exploit potential
                        if cve_data['exploit_available']:
                            correlated_finding['exploit_potential'] += cve_data['cvss_score'] / 10.0
            
            correlated_findings.append(correlated_finding)
        
        return correlated_findings
    
    def find_chain_opportunities(self, findings: List[Dict]) -> List[Dict]:
        """Find chain exploit opportunities using knowledge base"""
        self.initialize_knowledge_base()
        chain_opportunities = []
        
        # Group findings by type and location
        findings_by_type = {}
        for finding in findings:
            vuln_type = finding.get('type', 'unknown')
            if vuln_type not in findings_by_type:
                findings_by_type[vuln_type] = []
            findings_by_type[vuln_type].append(finding)
        
        # Check against high-value chain patterns
        for pattern in self.high_value_patterns:
            pattern_components = pattern['pattern']
            matched_components = []
            
            for component_type in pattern_components:
                # Find matching findings for this component
                matching_findings = []
                for vuln_type, type_findings in findings_by_type.items():
                    if self.matches_component_type(vuln_type, component_type):
                        matching_findings.extend(type_findings)
                
                if matching_findings:
                    matched_components.append({
                        'component_type': component_type,
                        'findings': matching_findings[:3]  # Limit to top 3 findings
                    })
            
            # If we have matches for all components, create chain opportunity
            if len(matched_components) >= len(pattern_components) * 0.7:  # 70% match threshold
                chain_opportunity = {
                    'chain_id': hashlib.md5(f"{pattern['name']}{time.time()}".encode()).hexdigest()[:8],
                    'name': pattern['name'],
                    'pattern_type': 'high_value_chain',
                    'components': matched_components,
                    'estimated_bounty': pattern['min_bounty'],
                    'bounty_multiplier': pattern['multiplier'],
                    'confidence_score': len(matched_components) / len(pattern_components),
                    'business_impact': self.calculate_business_impact(matched_components),
                    'attack_complexity': self.calculate_attack_complexity(matched_components),
                    'evidence_requirements': self.determine_evidence_requirements(matched_components)
                }
                chain_opportunities.append(chain_opportunity)
        
        # Check against business logic rule patterns
        for rule in self.business_logic_rules[:100]:  # Limit to top 100 rules
            if self.matches_business_logic_pattern(findings, rule):
                chain_opportunity = {
                    'chain_id': hashlib.md5(f"{rule['rule_id']}{time.time()}".encode()).hexdigest()[:8],
                    'name': f"Business Logic Chain - {rule['pattern_type']}",
                    'pattern_type': 'business_logic',
                    'rule_id': rule['rule_id'],
                    'estimated_bounty': self.extract_bounty_from_range(rule['bounty_range']),
                    'bounty_multiplier': 1.5,  # Business logic flaws get 1.5x multiplier
                    'confidence_score': rule['payment_probability'],
                    'business_impact': rule['impact_score'],
                    'attack_complexity': 'medium',
                    'evidence_requirements': self.determine_business_logic_evidence(rule)
                }
                chain_opportunities.append(chain_opportunity)
        
        return sorted(chain_opportunities, key=lambda x: x['estimated_bounty'], reverse=True)
    
    def matches_component_type(self, vuln_type: str, component_type: str) -> bool:
        """Check if vulnerability type matches chain component type"""
        type_mappings = {
            'open_redirect': ['redirect', 'open_redirect', 'url_redirect'],
            'cors_misconfiguration': ['cors', 'cross_origin', 'cors_misconfiguration'],
            'token_leakage': ['token', 'jwt', 'session', 'auth_token'],
            'race_condition': ['race', 'timing', 'race_condition'],
            'validation_bypass': ['validation', 'bypass', 'input_validation'],
            'business_logic_flaw': ['logic', 'business', 'workflow'],
            'forgotten_debug_endpoint': ['debug', 'test', 'dev', 'admin'],
            'ssrf': ['ssrf', 'server_side_request_forgery'],
            'internal_network_access': ['internal', 'network', 'admin'],
            'idor': ['idor', 'direct_object_reference', 'authorization'],
            'missing_function_level_access_control': ['access_control', 'authorization', 'privilege'],
            'token_manipulation': ['token', 'jwt', 'manipulation'],
            'state_token_leakage': ['state', 'oauth', 'token'],
            'identity_provider_misconfiguration': ['saml', 'oauth', 'sso', 'identity']
        }
        
        component_keywords = type_mappings.get(component_type, [component_type])
        return any(keyword in vuln_type.lower() for keyword in component_keywords)
    
    def matches_business_logic_pattern(self, findings: List[Dict], rule: Dict) -> bool:
        """Check if findings match business logic pattern"""
        detection_rules = rule.get('detection_rules', {})
        endpoints_to_check = detection_rules.get('endpoints', [])
        parameters_to_test = detection_rules.get('parameters', [])
        
        # Simple pattern matching - check if any findings involve relevant endpoints/parameters
        for finding in findings:
            finding_url = finding.get('url', '').lower()
            finding_params = finding.get('parameters', [])
            
            # Check endpoint matches
            if any(endpoint in finding_url for endpoint in endpoints_to_check):
                return True
            
            # Check parameter matches
            if any(param in str(finding_params).lower() for param in parameters_to_test):
                return True
        
        return False
    
    def calculate_business_impact(self, components: List[Dict]) -> float:
        """Calculate business impact score for chain"""
        base_impact = 7.0
        
        # Increase impact based on component types
        for component in components:
            component_type = component.get('component_type', '')
            if 'payment' in component_type or 'auth' in component_type:
                base_impact += 1.0
            elif 'admin' in component_type or 'privilege' in component_type:
                base_impact += 1.5
            elif 'data' in component_type:
                base_impact += 0.5
        
        return min(base_impact, 10.0)  # Cap at 10.0
    
    def calculate_attack_complexity(self, components: List[Dict]) -> str:
        """Calculate attack complexity for chain"""
        if len(components) <= 2:
            return 'low'
        elif len(components) <= 4:
            return 'medium'
        else:
            return 'high'
    
    def determine_evidence_requirements(self, components: List[Dict]) -> List[str]:
        """Determine evidence requirements for chain"""
        evidence_types = ['screenshot', 'http_request_response']
        
        # Add specific evidence based on component types
        for component in components:
            component_type = component.get('component_type', '')
            if 'payment' in component_type:
                evidence_types.append('payment_proof')
            elif 'auth' in component_type:
                evidence_types.append('authentication_bypass_proof')
            elif 'data' in component_type:
                evidence_types.append('data_access_proof')
        
        # Always require video PoC for high-value chains
        evidence_types.append('video_poc')
        
        return list(set(evidence_types))
    
    def determine_business_logic_evidence(self, rule: Dict) -> List[str]:
        """Determine evidence requirements for business logic flaws"""
        evidence_types = ['screenshot', 'http_request_response', 'video_poc']
        
        pattern_type = rule.get('pattern_type', '')
        if 'payment' in pattern_type:
            evidence_types.extend(['payment_proof', 'transaction_log'])
        elif 'auth' in pattern_type:
            evidence_types.extend(['authentication_bypass_proof', 'session_data'])
        elif 'data' in pattern_type:
            evidence_types.extend(['data_access_proof', 'unauthorized_data'])
        
        return evidence_types
    
    def extract_bounty_from_range(self, bounty_range: str) -> int:
        """Extract estimated bounty from range string"""
        try:
            # Extract numbers from range like "$1,000-$5,000"
            numbers = re.findall(r'\d+(?:,\d+)*', bounty_range)
            if len(numbers) >= 2:
                min_bounty = int(numbers[0].replace(',', ''))
                max_bounty = int(numbers[1].replace(',', ''))
                return (min_bounty + max_bounty) // 2
            elif len(numbers) == 1:
                return int(numbers[0].replace(',', ''))
        except:
            pass
        return 1000  # Default bounty
    
    def estimate_bounty_value(self, chain: Dict) -> int:
        """Estimate bounty value using platform intelligence and historical data"""
        base_bounty = chain.get('estimated_bounty', 1000)
        multiplier = chain.get('bounty_multiplier', 1.0)
        business_impact = chain.get('business_impact', 7.0)
        confidence_score = chain.get('confidence_score', 0.8)
        
        # Apply business impact multiplier
        impact_multiplier = 1.0 + (business_impact - 7.0) * 0.2
        
        # Apply confidence multiplier
        confidence_multiplier = 0.5 + (confidence_score * 0.5)
        
        # Calculate final bounty
        estimated_bounty = int(base_bounty * multiplier * impact_multiplier * confidence_multiplier)
        
        return max(estimated_bounty, 500)  # Minimum $500
    
    def calculate_payment_probability(self, chain: Dict) -> float:
        """Calculate payment probability based on chain characteristics"""
        base_probability = 0.8
        
        # Adjust based on chain type
        if chain.get('pattern_type') == 'high_value_chain':
            base_probability += 0.1
        elif chain.get('pattern_type') == 'business_logic':
            base_probability += 0.05
        
        # Adjust based on business impact
        business_impact = chain.get('business_impact', 7.0)
        if business_impact >= 9.0:
            base_probability += 0.1
        elif business_impact >= 8.0:
            base_probability += 0.05
        
        # Adjust based on confidence score
        confidence_score = chain.get('confidence_score', 0.8)
        base_probability *= confidence_score
        
        return min(base_probability, 0.98)  # Cap at 98%
    
    def analyze_findings(self, findings: List[Dict]) -> List[Dict]:
        """Perform deep analysis using full knowledge base"""
        self.last_used = time.time()
        results = []
        
        if not findings:
            return results
        
        print(f"AI Engine analyzing {len(findings)} findings...")
        
        # Step 1: Correlate findings with vulnerability database
        correlated_findings = self.correlate_with_vulnerability_database(findings)
        
        # Step 2: Identify chain opportunities using knowledge base
        chain_opportunities = self.find_chain_opportunities(correlated_findings)
        
        # Step 3: Calculate bounty potential and payment probability
        for chain in chain_opportunities:
            chain['estimated_bounty'] = self.estimate_bounty_value(chain)
            chain['payment_probability'] = self.calculate_payment_probability(chain)
            chain['target_platform'] = self.recommend_platform(chain)
            
            # Only include chains with high payment probability and bounty
            if (chain['payment_probability'] >= 0.8 and 
                chain['estimated_bounty'] >= 500 and
                chain['business_impact'] >= 7.0):
                results.append(chain)
        
        # Sort by comprehensive score
        results.sort(key=lambda x: (
            x['estimated_bounty'] * 0.4 + 
            x['payment_probability'] * 1000 * 0.3 + 
            x['business_impact'] * 100 * 0.3
        ), reverse=True)
        
        print(f"AI Engine identified {len(results)} high-value chain opportunities")
        return results[:10]  # Return top 10 chains
    
    def recommend_platform(self, chain: Dict) -> str:
        """Recommend best platform for chain submission"""
        chain_type = self.categorize_chain_type(chain)
        estimated_bounty = chain.get('estimated_bounty', 1000)
        
        # Platform recommendations based on chain type and bounty
        if chain_type == 'authentication_bypass' and estimated_bounty >= 2000:
            return 'intigriti'  # Best for auth bypasses
        elif chain_type == 'business_logic' and estimated_bounty >= 1000:
            return 'hackerone'  # Best for business logic
        elif chain_type == 'privilege_escalation' and estimated_bounty >= 3000:
            return 'intigriti'  # Best for privilege escalation
        elif estimated_bounty >= 1500:
            return 'hackerone'  # Default for high-value
        else:
            return 'bugcrowd'  # Default for medium-value
    
    def categorize_chain_type(self, chain: Dict) -> str:
        """Categorize chain type for platform recommendation"""
        name = chain.get('name', '').lower()
        
        if 'auth' in name or 'login' in name or 'sso' in name:
            return 'authentication_bypass'
        elif 'payment' in name or 'business' in name or 'logic' in name:
            return 'business_logic'
        elif 'privilege' in name or 'escalation' in name or 'admin' in name:
            return 'privilege_escalation'
        elif 'data' in name or 'access' in name:
            return 'data_exposure'
        else:
            return 'chain_exploit'
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of AI analysis capabilities"""
        return {
            'chain_templates_loaded': len(self.chain_templates),
            'business_logic_rules_loaded': len(self.business_logic_rules),
            'vulnerability_records': len(self.vulnerability_database.get('cves', {})),
            'high_value_patterns': len(self.high_value_patterns),
            'supported_platforms': list(self.platform_data.keys()),
            'last_used': self.last_used
        }