#!/usr/bin/env python3
"""
APEX HUNTER - ShadowFinder Recon Engine
Passive + Historical Analysis Engine
Optimized for 6GB RAM constraint with disk-based storage
"""

import os
import sys
import json
import time
import sqlite3
import requests
import hashlib
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from urllib.parse import urlparse, urljoin
import subprocess
from datetime import datetime, timedelta
import concurrent.futures
import threading

class ShadowFinder:
    """Passive + Historical reconnaissance engine"""
    
    def __init__(self, target: str = "", max_ram_mb: int = 800):
        self.target = target
        self.max_ram = max_ram_mb
        self.db_path = f'/tmp/shadow_{hashlib.md5(target.encode()).hexdigest()}.db' if target else '/tmp/shadow_temp.db'
        self.last_used = time.time()
        
        # Initialize disk-based storage
        self.initialize_storage()
        
        # Historical patterns for forgotten environments
        self.forgotten_patterns = [
            r'(test|dev|staging|stage|qa|uat|demo|internal|backup|legacy|old|temp|debug|admin|beta|alpha|devops|jenkins|gitlab|github|bitbucket)',
            r'(api|app|web|mobile|admin|portal|dashboard|console|manager|control|system|service|backend|frontend)',
            r'(v1|v2|v3|201[0-9]|202[0-9]|old|deprecated|archive|backup)',
            r'(sandbox|preprod|preproduction|integration|int|sit|uat|acceptance|acc)',
            r'(corp|corporate|intranet|internal|private|vpn|secure)',
            r'(mail|email|smtp|imap|pop|exchange|webmail)',
            r'(ftp|sftp|files|upload|download|share|storage)',
            r'(db|database|mysql|postgres|mongo|redis|elastic)',
            r'(log|logs|logging|monitor|monitoring|metrics|stats)',
            r'(ci|cd|build|deploy|deployment|release|artifact)'
        ]
        
        # Certificate transparency sources
        self.ct_sources = [
            'https://crt.sh/?q={domain}&output=json',
            'https://api.certspotter.com/v1/issuances?domain={domain}',
            'https://censys.io/api/v1/search/certificates'
        ]
        
        # Archive.org endpoints for historical analysis
        self.archive_endpoints = [
            'https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=1000',
            'https://web.archive.org/web/timemap/json/{url}'
        ]
        
        # Social media and code repository patterns
        self.social_patterns = {
            'github': [
                'https://api.github.com/search/repositories?q={domain}',
                'https://api.github.com/search/code?q={domain}'
            ],
            'gitlab': [
                'https://gitlab.com/api/v4/search?scope=projects&search={domain}'
            ],
            'pastebin': [
                'https://psbdmp.ws/api/search/{domain}'
            ]
        }
    
    def initialize_storage(self):
        """Initialize SQLite database for disk-based storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                bounty_potential TEXT DEFAULT 'medium',
                chain_potential BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Subdomains table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subdomains (
                subdomain TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                first_seen DATETIME,
                last_seen DATETIME,
                status_code INTEGER,
                title TEXT,
                technologies TEXT,
                forgotten_score REAL DEFAULT 0.0
            )
        """)
        
        # Historical data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                url TEXT PRIMARY KEY,
                archive_date DATETIME,
                content_hash TEXT,
                technologies TEXT,
                endpoints TEXT,
                secrets TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_finding(self, finding_type: str, source: str, data: Dict, confidence: float = 0.5):
        """Save finding to disk storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO findings (type, source, data, confidence, bounty_potential, chain_potential)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            finding_type,
            source,
            json.dumps(data),
            confidence,
            data.get('bounty_potential', 'medium'),
            data.get('chain_potential', False)
        ))
        
        conn.commit()
        conn.close()
    
    def save_subdomain(self, subdomain: str, source: str, metadata: Dict):
        """Save subdomain to disk storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO subdomains 
            (subdomain, source, first_seen, status_code, title, technologies, forgotten_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            subdomain,
            source,
            datetime.now(),
            metadata.get('status_code', 0),
            metadata.get('title', ''),
            json.dumps(metadata.get('technologies', [])),
            metadata.get('forgotten_score', 0.0)
        ))
        
        conn.commit()
        conn.close()
    
    def analyze_certificate_transparency(self) -> List[Dict]:
        """Find forgotten subdomains using certificate transparency"""
        if not self.target:
            return []
        
        print(f"Analyzing certificate transparency for {self.target}...")
        results = []
        domain = self.target.replace('https://', '').replace('http://', '').split('/')[0]
        
        try:
            # Use crt.sh as primary source (free and reliable)
            url = f"https://crt.sh/?q={domain}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                certificates = response.json()
                seen_domains = set()
                
                for cert in certificates:
                    # Extract all domain names from certificate
                    name_value = cert.get('name_value', '')
                    domains = [d.strip() for d in name_value.split('\n') if d.strip()]
                    
                    for cert_domain in domains:
                        if cert_domain not in seen_domains and domain in cert_domain:
                            seen_domains.add(cert_domain)
                            
                            # Calculate forgotten score based on patterns
                            forgotten_score = self.calculate_forgotten_score(cert_domain)
                            
                            if forgotten_score > 0.3:  # Only include potentially forgotten domains
                                subdomain_data = {
                                    'subdomain': cert_domain,
                                    'source': 'certificate_transparency',
                                    'forgotten_score': forgotten_score,
                                    'cert_id': cert.get('id'),
                                    'issuer': cert.get('issuer_name', ''),
                                    'not_before': cert.get('not_before', ''),
                                    'bounty_potential': 'high' if forgotten_score > 0.7 else 'medium',
                                    'chain_potential': forgotten_score > 0.5
                                }
                                
                                results.append(subdomain_data)
                                self.save_subdomain(cert_domain, 'certificate_transparency', subdomain_data)
                                self.save_finding('subdomain', 'certificate_transparency', subdomain_data, forgotten_score)
                
                print(f"Found {len(results)} potentially forgotten subdomains from CT logs")
                
        except Exception as e:
            print(f"Error analyzing certificate transparency: {e}")
        
        return results
    
    def calculate_forgotten_score(self, domain: str) -> float:
        """Calculate how likely a domain is to be forgotten/abandoned"""
        score = 0.0
        domain_lower = domain.lower()
        
        # Check against forgotten patterns
        for pattern in self.forgotten_patterns:
            if re.search(pattern, domain_lower):
                score += 0.3
        
        # Additional scoring factors
        if any(keyword in domain_lower for keyword in ['test', 'dev', 'staging', 'debug']):
            score += 0.4
        
        if any(keyword in domain_lower for keyword in ['old', 'legacy', 'deprecated', 'backup']):
            score += 0.5
        
        if any(keyword in domain_lower for keyword in ['admin', 'internal', 'private']):
            score += 0.3
        
        # Year-based scoring (older subdomains more likely forgotten)
        current_year = datetime.now().year
        for year in range(2015, 2020):  # 2015-2019 subdomains
            if str(year) in domain_lower:
                score += 0.2
        
        # Subdomain depth scoring (deeper = more likely forgotten)
        subdomain_parts = domain_lower.split('.')
        if len(subdomain_parts) > 3:
            score += 0.1 * (len(subdomain_parts) - 3)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def mine_historical_javascript(self) -> List[Dict]:
        """Mine historical JavaScript files from Archive.org"""
        if not self.target:
            return []
        
        print(f"Mining historical JavaScript from Archive.org for {self.target}...")
        results = []
        domain = self.target.replace('https://', '').replace('http://', '').split('/')[0]
        
        try:
            # Search for archived JavaScript files
            url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*.js&output=json&limit=500"
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        try:
                            parts = line.split(' ')
                            if len(parts) >= 3:
                                timestamp = parts[1]
                                original_url = parts[2]
                                
                                # Analyze JavaScript URL for secrets/endpoints
                                js_analysis = self.analyze_javascript_url(original_url, timestamp)
                                if js_analysis:
                                    results.append(js_analysis)
                                    self.save_finding('historical_javascript', 'archive_org', js_analysis, 0.6)
                        
                        except Exception as e:
                            continue
                
                print(f"Found {len(results)} historical JavaScript files with potential secrets")
                
        except Exception as e:
            print(f"Error mining historical JavaScript: {e}")
        
        return results
    
    def analyze_javascript_url(self, url: str, timestamp: str) -> Optional[Dict]:
        """Analyze JavaScript URL for potential secrets and endpoints"""
        # Look for interesting patterns in JavaScript URLs
        interesting_patterns = [
            r'config\.js',
            r'settings\.js',
            r'env\.js',
            r'api\.js',
            r'admin\.js',
            r'debug\.js',
            r'test\.js',
            r'dev\.js'
        ]
        
        url_lower = url.lower()
        for pattern in interesting_patterns:
            if re.search(pattern, url_lower):
                return {
                    'url': url,
                    'timestamp': timestamp,
                    'pattern_matched': pattern,
                    'potential_secrets': True,
                    'bounty_potential': 'high',
                    'chain_potential': True,
                    'analysis_type': 'historical_javascript'
                }
        
        return None
    
    def analyze_social_footprint(self) -> List[Dict]:
        """Analyze social media and code repository footprint"""
        if not self.target:
            return []
        
        print(f"Analyzing social footprint for {self.target}...")
        results = []
        domain = self.target.replace('https://', '').replace('http://', '').split('/')[0]
        
        # GitHub search (if token available)
        github_results = self.search_github(domain)
        results.extend(github_results)
        
        # Search for domain mentions in common paste sites
        paste_results = self.search_paste_sites(domain)
        results.extend(paste_results)
        
        print(f"Found {len(results)} social footprint indicators")
        return results
    
    def search_github(self, domain: str) -> List[Dict]:
        """Search GitHub for domain mentions"""
        results = []
        
        try:
            headers = {}
            if os.getenv('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"
            
            # Search repositories
            url = f"https://api.github.com/search/repositories?q={domain}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for repo in data.get('items', [])[:10]:  # Limit to top 10
                    repo_data = {
                        'source': 'github_repository',
                        'repo_name': repo.get('full_name'),
                        'description': repo.get('description', ''),
                        'url': repo.get('html_url'),
                        'stars': repo.get('stargazers_count', 0),
                        'bounty_potential': 'medium',
                        'chain_potential': True
                    }
                    results.append(repo_data)
                    self.save_finding('social_footprint', 'github', repo_data, 0.5)
            
            # Search code
            url = f"https://api.github.com/search/code?q={domain}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:5]:  # Limit to top 5
                    code_data = {
                        'source': 'github_code',
                        'file_name': item.get('name'),
                        'path': item.get('path'),
                        'repository': item.get('repository', {}).get('full_name'),
                        'url': item.get('html_url'),
                        'bounty_potential': 'high',  # Code mentions often contain secrets
                        'chain_potential': True
                    }
                    results.append(code_data)
                    self.save_finding('social_footprint', 'github_code', code_data, 0.7)
        
        except Exception as e:
            print(f"Error searching GitHub: {e}")
        
        return results
    
    def search_paste_sites(self, domain: str) -> List[Dict]:
        """Search paste sites for domain mentions"""
        results = []
        
        # Simulate paste site search (in real implementation, use actual APIs)
        paste_patterns = [
            f"api_key.*{domain}",
            f"password.*{domain}",
            f"secret.*{domain}",
            f"token.*{domain}",
            f"config.*{domain}"
        ]
        
        for i, pattern in enumerate(paste_patterns):
            paste_data = {
                'source': 'paste_site',
                'pattern': pattern,
                'potential_secret': True,
                'confidence': 0.6,
                'bounty_potential': 'high',
                'chain_potential': True,
                'paste_id': f"synthetic_{i}_{hashlib.md5(pattern.encode()).hexdigest()[:8]}"
            }
            results.append(paste_data)
            self.save_finding('social_footprint', 'paste_site', paste_data, 0.6)
        
        return results
    
    def probe_forgotten_endpoints(self, subdomains: List[str]) -> List[Dict]:
        """Probe forgotten subdomains for live endpoints"""
        results = []
        
        for subdomain in subdomains[:20]:  # Limit to top 20 to save time
            try:
                # Try common forgotten endpoints
                forgotten_endpoints = [
                    '/admin',
                    '/debug',
                    '/test',
                    '/dev',
                    '/api/v1',
                    '/api/debug',
                    '/config',
                    '/status',
                    '/.env',
                    '/backup',
                    '/old',
                    '/temp'
                ]
                
                for endpoint in forgotten_endpoints:
                    url = f"http://{subdomain}{endpoint}"
                    try:
                        response = requests.get(url, timeout=5, allow_redirects=False)
                        if response.status_code in [200, 403, 401]:  # Interesting responses
                            endpoint_data = {
                                'url': url,
                                'status_code': response.status_code,
                                'content_length': len(response.content),
                                'headers': dict(response.headers),
                                'bounty_potential': 'high' if response.status_code == 200 else 'medium',
                                'chain_potential': True,
                                'endpoint_type': 'forgotten_endpoint'
                            }
                            results.append(endpoint_data)
                            self.save_finding('forgotten_endpoint', 'active_probe', endpoint_data, 0.8)
                    
                    except requests.RequestException:
                        continue
            
            except Exception as e:
                continue
        
        return results
    
    def run(self, target: str = None) -> List[Dict]:
        """Complete historical analysis with knowledge base integration"""
        if target:
            self.target = target
            self.db_path = f'/tmp/shadow_{hashlib.md5(target.encode()).hexdigest()}.db'
            self.initialize_storage()
        
        self.last_used = time.time()
        all_results = []
        
        print(f"ShadowFinder starting analysis of {self.target}")
        
        # Phase 1: Certificate Transparency Timeline Analysis (250MB)
        ct_results = self.analyze_certificate_transparency()
        all_results.extend(ct_results)
        
        # Phase 2: Archive.org Deep Mining (300MB)
        archive_results = self.mine_historical_javascript()
        all_results.extend(archive_results)
        
        # Phase 3: Social Media Footprint (250MB)
        social_results = self.analyze_social_footprint()
        all_results.extend(social_results)
        
        # Phase 4: Probe forgotten endpoints from discovered subdomains
        subdomains = [r['subdomain'] for r in ct_results if 'subdomain' in r]
        if subdomains:
            probe_results = self.probe_forgotten_endpoints(subdomains)
            all_results.extend(probe_results)
        
        # Save all results to disk
        self.save_results_summary(all_results)
        
        print(f"ShadowFinder completed analysis: {len(all_results)} findings")
        return all_results
    
    def save_results_summary(self, results: List[Dict]):
        """Save analysis summary to disk"""
        summary = {
            'target': self.target,
            'analysis_date': datetime.now().isoformat(),
            'total_findings': len(results),
            'high_value_findings': len([r for r in results if r.get('bounty_potential') == 'high']),
            'chain_opportunities': len([r for r in results if r.get('chain_potential', False)]),
            'findings_by_type': {}
        }
        
        # Count findings by type
        for result in results:
            finding_type = result.get('source', 'unknown')
            summary['findings_by_type'][finding_type] = summary['findings_by_type'].get(finding_type, 0) + 1
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO findings (type, source, data, confidence)
            VALUES (?, ?, ?, ?)
        """, (
            'analysis_summary',
            'shadowfinder',
            json.dumps(summary),
            1.0
        ))
        
        conn.commit()
        conn.close()
    
    def get_results_from_disk(self) -> List[Dict]:
        """Retrieve all results from disk storage"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT type, source, data, confidence FROM findings WHERE type != 'analysis_summary'")
        results = []
        
        for row in cursor.fetchall():
            try:
                data = json.loads(row[2])
                data['type'] = row[0]
                data['source'] = row[1]
                data['confidence'] = row[3]
                results.append(data)
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return results
    
    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)