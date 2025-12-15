#!/usr/bin/env python3
"""
APEX HUNTER - Chain Engine
Exploit Chain Detection and Correlation Engine
Optimized for 6GB RAM constraint
"""

import os
import sys
import json
import time
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import itertools
from datetime import datetime
from memory_manager import memory_manager

class ChainEngine:
    """Exploit chain detection and correlation engine"""
    
    def __init__(self, max_ram_mb: int = 600):
        self.max_ram = max_ram_mb
        self.last_used = time.time()
        
        # High-value chain templates that guarantee payments
        self.chain_templates = [
            {
                'name': 'Silent Account Takeover Chain',
                'pattern': ['open_redirect', 'cors_misconfiguration', 'token_leakage'],
                'alternative_patterns': [
                    ['redirect', 'cors', 'session'],
                    ['url_redirect', 'cross_origin', 'auth_token'],
                    ['open_redirect', 'cors_misconfiguration', 'jwt']
                ],
                'impact_score': 9.5,
                'min_bounty': 2000,
                'max_bounty': 8000,
                'payment_probability': 0.90,
                'platforms': ['hackerone', 'bugcrowd', 'intigriti'],
                'attack_flow': [
                    'Victim clicks malicious link with open redirect',
                    'Redirect takes victim to attacker-controlled domain',
                    'Attacker domain makes CORS request to API endpoint',
                    'Browser sends authentication cookies due to CORS misconfiguration',
                    'Attacker extracts sensitive tokens from response',
                    'Attacker uses tokens to compromise victim account'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'token_proof']
            },
            {
                'name': 'Payment Bypass Cascade',
                'pattern': ['race_condition', 'validation_bypass', 'business_logic_flaw'],
                'alternative_patterns': [
                    ['timing', 'bypass', 'logic'],
                    ['race_condition_payment', 'negative_amount_bypass', 'payment'],
                    ['concurrent', 'validation', 'workflow']
                ],
                'impact_score': 8.5,
                'min_bounty': 1000,
                'max_bounty': 5000,
                'payment_probability': 0.88,
                'platforms': ['bugcrowd', 'intigriti', 'hackerone'],
                'attack_flow': [
                    'Attacker identifies race condition in checkout process',
                    'Finds insufficient validation on promo code application',
                    'Combines both to apply multiple high-value promo codes simultaneously',
                    'Race condition prevents proper validation of total amount',
                    'Payment processing logic fails to validate final price',
                    'Attacker completes order with $0 payment for premium items'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'payment_proof']
            },
            {
                'name': 'Shadow Path Compromise',
                'pattern': ['forgotten_debug_endpoint', 'ssrf', 'internal_network_access'],
                'alternative_patterns': [
                    ['debug', 'server_side_request_forgery', 'admin'],
                    ['forgotten_endpoint', 'ssrf', 'internal'],
                    ['test', 'ssrf', 'network']
                ],
                'impact_score': 9.8,
                'min_bounty': 3000,
                'max_bounty': 15000,
                'payment_probability': 0.92,
                'platforms': ['hackerone', 'intigriti'],
                'attack_flow': [
                    'Discover forgotten debug endpoint on development subdomain',
                    'Exploit SSRF vulnerability in image processing functionality',
                    'Use SSRF to access internal network resources',
                    'Gain access to admin interfaces on internal network',
                    'Extract sensitive data or gain administrative privileges'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'internal_access_proof']
            },
            {
                'name': 'API Token Escalation',
                'pattern': ['idor', 'missing_function_level_access_control', 'token_manipulation'],
                'alternative_patterns': [
                    ['insecure_direct_object_reference', 'access_control', 'jwt'],
                    ['idor_privilege_escalation', 'authorization_bypass', 'token'],
                    ['direct_object_reference', 'function_level_access', 'api_key']
                ],
                'impact_score': 9.0,
                'min_bounty': 2500,
                'max_bounty': 10000,
                'payment_probability': 0.87,
                'platforms': ['hackerone', 'bugcrowd', 'intigriti'],
                'attack_flow': [
                    'Identify IDOR vulnerability in user API endpoints',
                    'Discover missing access controls on admin API functions',
                    'Manipulate API tokens to escalate privileges',
                    'Access admin-level API functions with escalated token',
                    'Extract sensitive data or perform administrative actions'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'privilege_escalation_proof']
            },
            {
                'name': 'SSO Bypass Chain',
                'pattern': ['open_redirect', 'state_token_leakage', 'identity_provider_misconfiguration'],
                'alternative_patterns': [
                    ['redirect', 'oauth_state', 'saml'],
                    ['url_redirect', 'token_leakage', 'sso'],
                    ['open_redirect', 'oauth', 'identity']
                ],
                'impact_score': 9.7,
                'min_bounty': 4000,
                'max_bounty': 20000,
                'payment_probability': 0.95,
                'platforms': ['hackerone', 'intigriti'],
                'attack_flow': [
                    'Exploit open redirect in SSO authentication flow',
                    'Capture OAuth state tokens through redirect manipulation',
                    'Leverage identity provider misconfiguration',
                    'Bypass SSO authentication using captured tokens',
                    'Gain unauthorized access to target application'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'sso_bypass_proof']
            },
            {
                'name': 'Data Exfiltration Chain',
                'pattern': ['mass_data_exposure', 'filter_bypass', 'export_privilege_escalation'],
                'alternative_patterns': [
                    ['data_exposure', 'bypass', 'export'],
                    ['api_data_leak', 'filter', 'privilege'],
                    ['mass_assignment', 'validation_bypass', 'data_export']
                ],
                'impact_score': 8.8,
                'min_bounty': 2000,
                'max_bounty': 12000,
                'payment_probability': 0.85,
                'platforms': ['hackerone', 'bugcrowd', 'intigriti'],
                'attack_flow': [
                    'Discover API endpoint with mass data exposure',
                    'Bypass data filters using parameter manipulation',
                    'Escalate privileges in export functionality',
                    'Extract large amounts of sensitive user data',
                    'Demonstrate unauthorized access to PII/financial data'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'data_access_proof']
            },
            {
                'name': 'Workflow Manipulation Chain',
                'pattern': ['workflow_bypass', 'approval_manipulation', 'state_transition_bypass'],
                'alternative_patterns': [
                    ['business_workflow', 'approval', 'state'],
                    ['process_bypass', 'manipulation', 'transition'],
                    ['workflow', 'business_logic_flaw', 'state_manipulation']
                ],
                'impact_score': 8.3,
                'min_bounty': 1500,
                'max_bounty': 8000,
                'payment_probability': 0.82,
                'platforms': ['bugcrowd', 'hackerone', 'intigriti'],
                'attack_flow': [
                    'Identify business workflow with approval process',
                    'Manipulate approval parameters to bypass checks',
                    'Force illegal state transitions in workflow',
                    'Complete restricted business processes without authorization',
                    'Demonstrate business rule violations with financial impact'
                ],
                'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc', 'workflow_bypass_proof']
            }
        ]
        
        # Chain correlation rules
        self.correlation_rules = {
            'authentication_chains': {
                'triggers': ['auth', 'login', 'oauth', 'sso', 'saml'],
                'amplifiers': ['redirect', 'cors', 'token', 'session'],
                'multiplier': 2.5
            },
            'payment_chains': {
                'triggers': ['payment', 'checkout', 'billing', 'subscription'],
                'amplifiers': ['race', 'validation', 'logic', 'bypass'],
                'multiplier': 2.0
            },
            'privilege_chains': {
                'triggers': ['admin', 'privilege', 'role', 'authorization'],
                'amplifiers': ['idor', 'access_control', 'escalation', 'bypass'],
                'multiplier': 2.8
            },
            'data_chains': {
                'triggers': ['data', 'export', 'api', 'search'],
                'amplifiers': ['mass', 'filter', 'bypass', 'exposure'],
                'multiplier': 2.2
            }
        }
        
        # Vulnerability severity weights
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'info': 0.2
        }
    
    def analyze(self, findings: List[Dict]) -> List[Dict]:
        """Analyze findings for chain exploit opportunities"""
        self.last_used = time.time()
        
        if not findings:
            return []
        
        print(f"Chain Engine analyzing {len(findings)} findings for chain opportunities...")
        
        # Step 1: Categorize findings by type and impact
        categorized_findings = self.categorize_findings(findings)
        
        # Step 2: Find template-based chains
        template_chains = self.find_template_chains(categorized_findings)
        
        # Step 3: Find correlation-based chains
        correlation_chains = self.find_correlation_chains(categorized_findings)
        
        # Step 4: Find emergent chains (novel combinations)
        emergent_chains = self.find_emergent_chains(categorized_findings)
        
        # Step 5: Combine and rank all chains
        all_chains = template_chains + correlation_chains + emergent_chains
        ranked_chains = self.rank_chains(all_chains)
        
        print(f"Chain Engine identified {len(ranked_chains)} chain opportunities")
        return ranked_chains
    
    def categorize_findings(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize findings by vulnerability type and impact"""
        categories = {
            'authentication': [],
            'authorization': [],
            'business_logic': [],
            'injection': [],
            'configuration': [],
            'information_disclosure': [],
            'other': []
        }
        
        for finding in findings:
            category = self.determine_category(finding)
            categories[category].append(finding)
        
        return categories
    
    def determine_category(self, finding: Dict) -> str:
        """Determine the category of a finding"""
        vuln_type = finding.get('vulnerability_type', '').lower()
        endpoint = finding.get('endpoint', '').lower()
        description = finding.get('description', '').lower()
        
        # Combine all text for analysis
        text = f"{vuln_type} {endpoint} {description}"
        
        if any(keyword in text for keyword in ['auth', 'login', 'oauth', 'sso', 'saml', 'session']):
            return 'authentication'
        elif any(keyword in text for keyword in ['admin', 'privilege', 'role', 'authorization', 'access']):
            return 'authorization'
        elif any(keyword in text for keyword in ['business', 'logic', 'workflow', 'payment', 'checkout']):
            return 'business_logic'
        elif any(keyword in text for keyword in ['injection', 'sqli', 'xss', 'xxe', 'ssrf']):
            return 'injection'
        elif any(keyword in text for keyword in ['config', 'cors', 'csp', 'header', 'ssl']):
            return 'configuration'
        elif any(keyword in text for keyword in ['disclosure', 'exposure', 'leak', 'information']):
            return 'information_disclosure'
        else:
            return 'other'
    
    def find_template_chains(self, categorized_findings: Dict[str, List[Dict]]) -> List[Dict]:
        """Find chains matching predefined templates"""
        template_chains = []
        
        for template in self.chain_templates:
            chain_match = self.match_template(template, categorized_findings)
            if chain_match:
                template_chains.append(chain_match)
        
        return template_chains
    
    def match_template(self, template: Dict, categorized_findings: Dict[str, List[Dict]]) -> Optional[Dict]:
        """Match findings against a chain template"""
        pattern = template['pattern']
        alternative_patterns = template.get('alternative_patterns', [])
        all_patterns = [pattern] + alternative_patterns
        
        # Try to match each pattern
        for test_pattern in all_patterns:
            matched_components = []
            
            for component in test_pattern:
                # Find findings that match this component
                matching_findings = self.find_matching_findings(component, categorized_findings)
                if matching_findings:
                    matched_components.append({
                        'component_type': component,
                        'findings': matching_findings[:2]  # Limit to top 2 findings per component
                    })
            
            # Check if we have enough matches (at least 70% of pattern)
            match_ratio = len(matched_components) / len(test_pattern)
            if match_ratio >= 0.7:
                chain = self.create_chain_from_template(template, matched_components, match_ratio)
                return chain
        
        return None
    
    def find_matching_findings(self, component: str, categorized_findings: Dict[str, List[Dict]]) -> List[Dict]:
        """Find findings that match a component type"""
        matching_findings = []
        
        # Search across all categories
        for category, findings in categorized_findings.items():
            for finding in findings:
                if self.finding_matches_component(finding, component):
                    matching_findings.append(finding)
        
        # Sort by impact/confidence
        matching_findings.sort(key=lambda x: (
            self.severity_weights.get(x.get('bounty_potential', 'medium'), 0.6),
            x.get('confidence', 0.5),
            x.get('business_impact', 7.0)
        ), reverse=True)
        
        return matching_findings
    
    def finding_matches_component(self, finding: Dict, component: str) -> bool:
        """Check if a finding matches a component type"""
        # Get all text from finding
        vuln_type = finding.get('vulnerability_type', '').lower()
        endpoint = finding.get('endpoint', '').lower()
        description = finding.get('description', '').lower()
        source = finding.get('source', '').lower()
        finding_type = finding.get('type', '').lower()
        
        text = f"{vuln_type} {endpoint} {description} {source} {finding_type}"
        
        # Component matching rules
        component_keywords = {
            'open_redirect': ['redirect', 'open_redirect', 'url_redirect'],
            'cors_misconfiguration': ['cors', 'cross_origin', 'cors_misconfiguration'],
            'token_leakage': ['token', 'jwt', 'session', 'auth_token', 'api_key'],
            'race_condition': ['race', 'timing', 'race_condition', 'concurrent'],
            'validation_bypass': ['validation', 'bypass', 'input_validation'],
            'business_logic_flaw': ['logic', 'business', 'workflow', 'business_logic'],
            'forgotten_debug_endpoint': ['debug', 'test', 'dev', 'admin', 'forgotten'],
            'ssrf': ['ssrf', 'server_side_request_forgery'],
            'internal_network_access': ['internal', 'network', 'admin', 'private'],
            'idor': ['idor', 'direct_object_reference', 'authorization'],
            'missing_function_level_access_control': ['access_control', 'authorization', 'privilege'],
            'token_manipulation': ['token', 'jwt', 'manipulation', 'api_key'],
            'state_token_leakage': ['state', 'oauth', 'token', 'oauth_state'],
            'identity_provider_misconfiguration': ['saml', 'oauth', 'sso', 'identity'],
            'mass_data_exposure': ['mass', 'data', 'exposure', 'api_data_leak'],
            'filter_bypass': ['filter', 'bypass', 'validation'],
            'export_privilege_escalation': ['export', 'privilege', 'escalation'],
            'workflow_bypass': ['workflow', 'bypass', 'business_workflow'],
            'approval_manipulation': ['approval', 'manipulation', 'business'],
            'state_transition_bypass': ['state', 'transition', 'bypass']
        }
        
        keywords = component_keywords.get(component, [component])
        return any(keyword in text for keyword in keywords)
    
    def create_chain_from_template(self, template: Dict, matched_components: List[Dict], match_ratio: float) -> Dict:
        """Create a chain exploit from template and matched components"""
        chain_id = hashlib.md5(f"{template['name']}{time.time()}".encode()).hexdigest()[:8]
        
        # Calculate estimated bounty
        base_bounty = (template['min_bounty'] + template['max_bounty']) // 2
        estimated_bounty = int(base_bounty * match_ratio)
        
        # Calculate confidence score
        component_confidences = []
        for component in matched_components:
            for finding in component['findings']:
                component_confidences.append(finding.get('confidence', 0.5))
        
        avg_confidence = sum(component_confidences) / len(component_confidences) if component_confidences else 0.5
        confidence_score = avg_confidence * match_ratio
        
        # Calculate business impact
        component_impacts = []
        for component in matched_components:
            for finding in component['findings']:
                component_impacts.append(finding.get('business_impact', 7.0))
        
        max_impact = max(component_impacts) if component_impacts else template['impact_score']
        business_impact = min(max_impact, template['impact_score'])
        
        chain = {
            'chain_id': chain_id,
            'name': template['name'],
            'chain_type': 'template_based',
            'template_name': template['name'],
            'components': matched_components,
            'attack_flow': template['attack_flow'],
            'estimated_bounty': estimated_bounty,
            'min_bounty': template['min_bounty'],
            'max_bounty': template['max_bounty'],
            'payment_probability': template['payment_probability'] * match_ratio,
            'confidence_score': confidence_score,
            'business_impact': business_impact,
            'impact_score': template['impact_score'],
            'match_ratio': match_ratio,
            'platforms': template['platforms'],
            'evidence_requirements': template['evidence_requirements'],
            'chain_potential': True,
            'vulnerability_type': 'chain_exploit'
        }
        
        return chain
    
    def find_correlation_chains(self, categorized_findings: Dict[str, List[Dict]]) -> List[Dict]:
        """Find chains based on correlation rules"""
        correlation_chains = []
        
        for rule_name, rule_data in self.correlation_rules.items():
            triggers = rule_data['triggers']
            amplifiers = rule_data['amplifiers']
            multiplier = rule_data['multiplier']
            
            # Find trigger findings
            trigger_findings = []
            for category, findings in categorized_findings.items():
                for finding in findings:
                    if self.finding_matches_triggers(finding, triggers):
                        trigger_findings.append(finding)
            
            # Find amplifier findings
            amplifier_findings = []
            for category, findings in categorized_findings.items():
                for finding in findings:
                    if self.finding_matches_triggers(finding, amplifiers):
                        amplifier_findings.append(finding)
            
            # Create chains from trigger-amplifier combinations
            if trigger_findings and amplifier_findings:
                for trigger in trigger_findings[:3]:  # Limit to top 3 triggers
                    for amplifier in amplifier_findings[:2]:  # Limit to top 2 amplifiers
                        chain = self.create_correlation_chain(rule_name, trigger, amplifier, multiplier)
                        if chain:
                            correlation_chains.append(chain)
        
        return correlation_chains
    
    def finding_matches_triggers(self, finding: Dict, triggers: List[str]) -> bool:
        """Check if finding matches any trigger keywords"""
        text = f"{finding.get('vulnerability_type', '')} {finding.get('endpoint', '')} {finding.get('description', '')}".lower()
        return any(trigger in text for trigger in triggers)
    
    def create_correlation_chain(self, rule_name: str, trigger: Dict, amplifier: Dict, multiplier: float) -> Optional[Dict]:
        """Create a chain from correlated findings"""
        chain_id = hashlib.md5(f"{rule_name}{trigger.get('endpoint', '')}{amplifier.get('endpoint', '')}{time.time()}".encode()).hexdigest()[:8]
        
        # Calculate estimated bounty
        trigger_bounty = self.estimate_finding_bounty(trigger)
        amplifier_bounty = self.estimate_finding_bounty(amplifier)
        base_bounty = trigger_bounty + amplifier_bounty
        estimated_bounty = int(base_bounty * multiplier)
        
        # Calculate confidence and impact
        confidence_score = (trigger.get('confidence', 0.5) + amplifier.get('confidence', 0.5)) / 2
        business_impact = max(trigger.get('business_impact', 7.0), amplifier.get('business_impact', 7.0))
        
        chain = {
            'chain_id': chain_id,
            'name': f"{rule_name.replace('_', ' ').title()} Chain",
            'chain_type': 'correlation_based',
            'rule_name': rule_name,
            'components': [
                {'component_type': 'trigger', 'findings': [trigger]},
                {'component_type': 'amplifier', 'findings': [amplifier]}
            ],
            'estimated_bounty': max(estimated_bounty, 500),
            'payment_probability': min(confidence_score * 0.8, 0.95),
            'confidence_score': confidence_score,
            'business_impact': business_impact,
            'impact_score': business_impact,
            'multiplier': multiplier,
            'platforms': ['hackerone', 'bugcrowd', 'intigriti'],
            'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc'],
            'chain_potential': True,
            'vulnerability_type': 'chain_exploit'
        }
        
        return chain
    
    def estimate_finding_bounty(self, finding: Dict) -> int:
        """Estimate bounty value for a single finding"""
        bounty_potential = finding.get('bounty_potential', 'medium')
        business_impact = finding.get('business_impact', 7.0)
        
        base_bounties = {
            'critical': 2000,
            'high': 1000,
            'medium': 500,
            'low': 200
        }
        
        base_bounty = base_bounties.get(bounty_potential, 500)
        impact_multiplier = business_impact / 7.0  # Normalize to 7.0 baseline
        
        return int(base_bounty * impact_multiplier)
    
    def find_emergent_chains(self, categorized_findings: Dict[str, List[Dict]]) -> List[Dict]:
        """Find novel chain combinations not covered by templates"""
        emergent_chains = []
        
        # Look for interesting combinations across categories
        category_combinations = [
            ('authentication', 'authorization'),
            ('business_logic', 'injection'),
            ('configuration', 'information_disclosure'),
            ('authorization', 'business_logic'),
            ('injection', 'configuration')
        ]
        
        for cat1, cat2 in category_combinations:
            findings1 = categorized_findings.get(cat1, [])
            findings2 = categorized_findings.get(cat2, [])
            
            # Create chains from high-impact findings in different categories
            for finding1 in findings1[:3]:  # Top 3 from category 1
                for finding2 in findings2[:2]:  # Top 2 from category 2
                    if self.findings_have_synergy(finding1, finding2):
                        chain = self.create_emergent_chain(finding1, finding2, cat1, cat2)
                        if chain:
                            emergent_chains.append(chain)
        
        return emergent_chains
    
    def findings_have_synergy(self, finding1: Dict, finding2: Dict) -> bool:
        """Check if two findings have synergy for chaining"""
        # Check if both have high impact
        impact1 = finding1.get('business_impact', 7.0)
        impact2 = finding2.get('business_impact', 7.0)
        
        if impact1 < 7.5 or impact2 < 7.5:
            return False
        
        # Check if they target different aspects (good for chaining)
        endpoint1 = finding1.get('endpoint', '').lower()
        endpoint2 = finding2.get('endpoint', '').lower()
        
        # Different endpoints suggest different attack surfaces
        if endpoint1 and endpoint2 and endpoint1 != endpoint2:
            return True
        
        # Check for complementary vulnerability types
        type1 = finding1.get('vulnerability_type', '').lower()
        type2 = finding2.get('vulnerability_type', '').lower()
        
        complementary_pairs = [
            ('auth', 'idor'),
            ('bypass', 'escalation'),
            ('injection', 'configuration'),
            ('disclosure', 'manipulation')
        ]
        
        for pair in complementary_pairs:
            if (any(p in type1 for p in pair) and any(p in type2 for p in pair) and type1 != type2):
                return True
        
        return False
    
    def create_emergent_chain(self, finding1: Dict, finding2: Dict, cat1: str, cat2: str) -> Optional[Dict]:
        """Create an emergent chain from two synergistic findings"""
        chain_id = hashlib.md5(f"emergent_{cat1}_{cat2}_{time.time()}".encode()).hexdigest()[:8]
        
        # Calculate metrics
        bounty1 = self.estimate_finding_bounty(finding1)
        bounty2 = self.estimate_finding_bounty(finding2)
        estimated_bounty = int((bounty1 + bounty2) * 1.5)  # 1.5x multiplier for emergent chains
        
        confidence_score = (finding1.get('confidence', 0.5) + finding2.get('confidence', 0.5)) / 2
        business_impact = max(finding1.get('business_impact', 7.0), finding2.get('business_impact', 7.0))
        
        chain = {
            'chain_id': chain_id,
            'name': f"Emergent {cat1.title()}-{cat2.title()} Chain",
            'chain_type': 'emergent',
            'categories': [cat1, cat2],
            'components': [
                {'component_type': cat1, 'findings': [finding1]},
                {'component_type': cat2, 'findings': [finding2]}
            ],
            'estimated_bounty': max(estimated_bounty, 500),
            'payment_probability': min(confidence_score * 0.7, 0.85),  # Lower probability for novel chains
            'confidence_score': confidence_score,
            'business_impact': business_impact,
            'impact_score': business_impact,
            'platforms': ['hackerone', 'bugcrowd'],  # Conservative platform selection
            'evidence_requirements': ['screenshot', 'http_request_response', 'video_poc'],
            'chain_potential': True,
            'vulnerability_type': 'chain_exploit'
        }
        
        return chain
    
    def rank_chains(self, chains: List[Dict]) -> List[Dict]:
        """Rank chains by comprehensive scoring"""
        for chain in chains:
            # Calculate comprehensive score
            bounty_score = chain.get('estimated_bounty', 500) / 1000.0  # Normalize to 1000
            probability_score = chain.get('payment_probability', 0.5) * 100
            impact_score = chain.get('business_impact', 7.0) * 10
            confidence_score = chain.get('confidence_score', 0.5) * 100
            
            # Weighted comprehensive score
            comprehensive_score = (
                bounty_score * 0.3 +
                probability_score * 0.3 +
                impact_score * 0.25 +
                confidence_score * 0.15
            )
            
            chain['comprehensive_score'] = comprehensive_score
            
            # Add priority level
            if comprehensive_score >= 80:
                chain['priority'] = 'critical'
            elif comprehensive_score >= 60:
                chain['priority'] = 'high'
            elif comprehensive_score >= 40:
                chain['priority'] = 'medium'
            else:
                chain['priority'] = 'low'
        
        # Sort by comprehensive score
        chains.sort(key=lambda x: x.get('comprehensive_score', 0), reverse=True)
        
        # Return only high-value chains
        high_value_chains = [c for c in chains if c.get('estimated_bounty', 0) >= 500 and c.get('payment_probability', 0) >= 0.7]
        
        return high_value_chains[:15]  # Return top 15 chains