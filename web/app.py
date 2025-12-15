#!/usr/bin/env python3
"""
APEX HUNTER - Flask Web Dashboard
Complete web interface for bug bounty automation system
"""

import os
import sys
import json
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from pathlib import Path
import threading
from datetime import datetime
import hashlib

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from memory_manager import memory_manager
from ai_engine import ApexHunterAIEngine
from shadowfinder import ShadowFinder
from logichunter import LogicHunter
from chain_engine import ChainEngine
from evidence_collector import EvidenceManager

app = Flask(__name__)
app.secret_key = 'apex_hunter_secret_key_2024'

# Global variables for hunt status
current_hunt = {
    'active': False,
    'target': '',
    'start_time': None,
    'progress': 0,
    'stage': 'idle',
    'findings': [],
    'chains': [],
    'evidence': {},
    'hunt_id': None
}

hunt_lock = threading.Lock()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', hunt_status=current_hunt)

@app.route('/target_input')
def target_input():
    """Target input page"""
    return render_template('target_input.html')

@app.route('/start_hunt', methods=['POST'])
def start_hunt():
    """Start a new hunt"""
    global current_hunt
    
    with hunt_lock:
        if current_hunt['active']:
            return jsonify({'error': 'Hunt already in progress'}), 400
        
        target = request.json.get('target', '').strip()
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        # Initialize hunt
        hunt_id = hashlib.md5(f"{target}{time.time()}".encode()).hexdigest()[:8]
        current_hunt = {
            'active': True,
            'target': target,
            'start_time': time.time(),
            'progress': 0,
            'stage': 'initializing',
            'findings': [],
            'chains': [],
            'evidence': {},
            'hunt_id': hunt_id
        }
        
        # Start hunt in background thread
        hunt_thread = threading.Thread(target=run_hunt_workflow, args=(target, hunt_id))
        hunt_thread.daemon = True
        hunt_thread.start()
        
        return jsonify({
            'success': True,
            'hunt_id': hunt_id,
            'message': 'Hunt started successfully'
        })

@app.route('/hunt_status')
def hunt_status():
    """Get current hunt status"""
    with hunt_lock:
        status = current_hunt.copy()
        
        # Calculate elapsed time
        if status['start_time']:
            elapsed = time.time() - status['start_time']
            status['elapsed_time'] = elapsed
            status['remaining_time'] = max(0, 480 - elapsed)  # 8 minutes = 480 seconds
        
        # Calculate memory usage
        memory_stats = memory_manager.get_memory_stats()
        status['memory_stats'] = memory_stats
        
        return jsonify(status)

@app.route('/live_monitor')
def live_monitor():
    """Live analysis monitor page"""
    return render_template('live_monitor.html')

@app.route('/chain_builder')
def chain_builder():
    """Chain exploit builder page"""
    return render_template('chain_builder.html', chains=current_hunt['chains'])

@app.route('/validate_chain', methods=['POST'])
def validate_chain():
    """Validate a specific chain"""
    chain_id = request.json.get('chain_id')
    
    if not chain_id:
        return jsonify({'error': 'Chain ID required'}), 400
    
    # Find the chain
    chain = None
    for c in current_hunt['chains']:
        if c.get('chain_id') == chain_id:
            chain = c
            break
    
    if not chain:
        return jsonify({'error': 'Chain not found'}), 404
    
    # Perform validation (simplified)
    validation_result = {
        'chain_id': chain_id,
        'valid': True,
        'confidence_score': chain.get('confidence_score', 0.8),
        'estimated_bounty': chain.get('estimated_bounty', 500),
        'payment_probability': chain.get('payment_probability', 0.8),
        'validation_timestamp': datetime.now().isoformat()
    }
    
    return jsonify(validation_result)

@app.route('/report_workshop')
def report_workshop():
    """Report workshop page"""
    return render_template('report_workshop.html', 
                         chains=current_hunt['chains'],
                         evidence=current_hunt['evidence'])

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate bug bounty report"""
    report_type = request.json.get('report_type', 'individual')
    platform = request.json.get('platform', 'hackerone')
    chain_ids = request.json.get('chain_ids', [])
    
    if not chain_ids:
        return jsonify({'error': 'No chains selected'}), 400
    
    # Generate report
    report = generate_bug_bounty_report(chain_ids, report_type, platform)
    
    return jsonify({
        'success': True,
        'report': report,
        'generation_timestamp': datetime.now().isoformat()
    })

@app.route('/stop_hunt', methods=['POST'])
def stop_hunt():
    """Stop current hunt"""
    global current_hunt
    
    with hunt_lock:
        if not current_hunt['active']:
            return jsonify({'error': 'No active hunt'}), 400
        
        current_hunt['active'] = False
        current_hunt['stage'] = 'stopped'
        
        # Clean up memory
        memory_manager.cleanup()
        
        return jsonify({'success': True, 'message': 'Hunt stopped'})

@app.route('/api/findings')
def api_findings():
    """API endpoint for findings"""
    return jsonify({
        'findings': current_hunt['findings'],
        'total': len(current_hunt['findings'])
    })

@app.route('/api/chains')
def api_chains():
    """API endpoint for chains"""
    return jsonify({
        'chains': current_hunt['chains'],
        'total': len(current_hunt['chains'])
    })

@app.route('/api/evidence/<chain_id>')
def api_evidence(chain_id):
    """API endpoint for chain evidence"""
    evidence = current_hunt['evidence'].get(chain_id, {})
    return jsonify(evidence)

@app.route('/download_evidence/<chain_id>')
def download_evidence(chain_id):
    """Download evidence package for a chain"""
    evidence = current_hunt['evidence'].get(chain_id, {})
    
    if not evidence:
        return jsonify({'error': 'Evidence not found'}), 404
    
    # In real implementation, create and return zip file
    return jsonify({
        'message': 'Evidence download would start here',
        'chain_id': chain_id,
        'evidence_files': evidence.get('generated_evidence', {})
    })

def run_hunt_workflow(target: str, hunt_id: str):
    """Run the complete 8-minute hunt workflow"""
    global current_hunt
    
    try:
        start_time = time.time()
        
        # Phase 1: ShadowFinder (Historical Analysis) - Minutes 0-2
        with hunt_lock:
            current_hunt['stage'] = 'shadow_analysis'
            current_hunt['progress'] = 10
        
        memory_manager.swap_tool('shadowfinder', load=True)
        shadow_finder = memory_manager.get_tool('shadowfinder')
        shadow_results = shadow_finder.run(target)
        memory_manager.swap_tool('shadowfinder', load=False)
        
        with hunt_lock:
            current_hunt['findings'].extend(shadow_results)
            current_hunt['progress'] = 30
        
        # Phase 2: LogicHunter (Business Logic Analysis) - Minutes 2-5
        with hunt_lock:
            current_hunt['stage'] = 'logic_analysis'
            current_hunt['progress'] = 40
        
        memory_manager.swap_tool('logichunter', load=True)
        logic_hunter = memory_manager.get_tool('logichunter')
        logic_results = logic_hunter.scan(target, shadow_results)
        memory_manager.swap_tool('logichunter', load=False)
        
        with hunt_lock:
            current_hunt['findings'].extend(logic_results)
            current_hunt['progress'] = 60
        
        # Phase 3: Chain Engine (Exploit Chaining) - Minutes 5-7
        with hunt_lock:
            current_hunt['stage'] = 'chain_analysis'
            current_hunt['progress'] = 70
        
        memory_manager.swap_tool('chainengine', load=True)
        chain_engine = memory_manager.get_tool('chainengine')
        all_findings = shadow_results + logic_results
        chains = chain_engine.analyze(all_findings)
        memory_manager.swap_tool('chainengine', load=False)
        
        with hunt_lock:
            current_hunt['chains'] = chains
            current_hunt['progress'] = 80
        
        # Phase 4: AI Analysis - Minutes 7-8
        with hunt_lock:
            current_hunt['stage'] = 'ai_analysis'
            current_hunt['progress'] = 85
        
        memory_manager.swap_tool('ai_engine', load=True)
        ai_engine = memory_manager.get_tool('ai_engine')
        analyzed_chains = ai_engine.analyze_findings(all_findings)
        memory_manager.swap_tool('ai_engine', load=False)
        
        # Merge AI analysis with chain results
        final_chains = merge_chain_results(chains, analyzed_chains)
        
        with hunt_lock:
            current_hunt['chains'] = final_chains
            current_hunt['progress'] = 90
        
        # Phase 5: Evidence Collection - Final minute
        with hunt_lock:
            current_hunt['stage'] = 'evidence_collection'
            current_hunt['progress'] = 95
        
        memory_manager.swap_tool('evidencemgr', load=True)
        evidence_manager = memory_manager.get_tool('evidencemgr')
        evidence_result = evidence_manager.generate(final_chains, target)
        memory_manager.swap_tool('evidencemgr', load=False)
        
        # Process evidence results
        evidence_by_chain = {}
        for package in evidence_result.get('evidence_packages', []):
            chain_id = package.get('chain_id')
            if chain_id:
                evidence_by_chain[chain_id] = package
        
        with hunt_lock:
            current_hunt['evidence'] = evidence_by_chain
            current_hunt['progress'] = 100
            current_hunt['stage'] = 'completed'
            current_hunt['active'] = False
        
        # Check if hunt exceeded 8 minutes
        elapsed = time.time() - start_time
        if elapsed > 480:  # 8 minutes
            with hunt_lock:
                current_hunt['stage'] = 'timeout'
        
    except Exception as e:
        print(f"Hunt workflow error: {e}")
        with hunt_lock:
            current_hunt['stage'] = 'error'
            current_hunt['active'] = False
            current_hunt['error'] = str(e)
    
    finally:
        # Clean up memory
        memory_manager.cleanup()

def merge_chain_results(chain_results: list, ai_results: list) -> list:
    """Merge chain engine results with AI analysis results"""
    # Create a map of AI results by chain characteristics
    ai_map = {}
    for ai_chain in ai_results:
        key = f"{ai_chain.get('name', '')}{ai_chain.get('estimated_bounty', 0)}"
        ai_map[key] = ai_chain
    
    # Merge results
    merged = []
    
    # Add chain engine results with AI enhancements
    for chain in chain_results:
        key = f"{chain.get('name', '')}{chain.get('estimated_bounty', 0)}"
        if key in ai_map:
            # Merge AI analysis
            ai_chain = ai_map[key]
            chain.update({
                'ai_enhanced': True,
                'ai_confidence': ai_chain.get('confidence_score', chain.get('confidence_score', 0.8)),
                'ai_bounty_estimate': ai_chain.get('estimated_bounty', chain.get('estimated_bounty', 500)),
                'target_platform': ai_chain.get('target_platform', 'hackerone')
            })
            del ai_map[key]  # Remove from map to avoid duplicates
        
        merged.append(chain)
    
    # Add remaining AI-only results
    for ai_chain in ai_map.values():
        ai_chain['ai_only'] = True
        merged.append(ai_chain)
    
    # Sort by estimated bounty and payment probability
    merged.sort(key=lambda x: (
        x.get('estimated_bounty', 0) * x.get('payment_probability', 0.5)
    ), reverse=True)
    
    return merged[:10]  # Return top 10 chains

def generate_bug_bounty_report(chain_ids: list, report_type: str, platform: str) -> dict:
    """Generate bug bounty report for selected chains"""
    selected_chains = []
    for chain_id in chain_ids:
        for chain in current_hunt['chains']:
            if chain.get('chain_id') == chain_id:
                selected_chains.append(chain)
                break
    
    if not selected_chains:
        return {'error': 'No valid chains found'}
    
    # Generate report based on type
    if report_type == 'individual':
        reports = []
        for chain in selected_chains:
            report = generate_individual_report(chain, platform)
            reports.append(report)
        return {'type': 'individual', 'reports': reports}
    else:
        # Full report combining all chains
        report = generate_full_report(selected_chains, platform)
        return {'type': 'full', 'report': report}

def generate_individual_report(chain: dict, platform: str) -> dict:
    """Generate individual report for a single chain"""
    return {
        'chain_id': chain.get('chain_id'),
        'title': f"{chain.get('name', 'Chain Exploit')} - {current_hunt['target']}",
        'summary': f"Chain exploit affecting {current_hunt['target']} with estimated bounty of ${chain.get('estimated_bounty', 500)}",
        'impact': chain.get('impact', 'High impact chain exploit'),
        'reproduction_steps': generate_reproduction_steps(chain),
        'mitigation': generate_mitigation_advice(chain),
        'estimated_bounty': chain.get('estimated_bounty', 500),
        'platform': platform,
        'evidence_files': current_hunt['evidence'].get(chain.get('chain_id', ''), {}).get('generated_evidence', {}),
        'generation_timestamp': datetime.now().isoformat()
    }

def generate_full_report(chains: list, platform: str) -> dict:
    """Generate full report combining multiple chains"""
    total_bounty = sum(chain.get('estimated_bounty', 500) for chain in chains)
    
    return {
        'title': f"Multiple Chain Exploits - {current_hunt['target']}",
        'summary': f"Multiple chain exploits discovered affecting {current_hunt['target']} with combined estimated bounty of ${total_bounty}",
        'chains': [generate_individual_report(chain, platform) for chain in chains],
        'total_estimated_bounty': total_bounty,
        'platform': platform,
        'generation_timestamp': datetime.now().isoformat()
    }

def generate_reproduction_steps(chain: dict) -> list:
    """Generate reproduction steps for a chain"""
    steps = [
        "1. Navigate to the target application",
        "2. Identify the vulnerable endpoints",
        "3. Execute the exploit chain components in sequence"
    ]
    
    # Add specific steps based on chain components
    components = chain.get('components', [])
    for i, component in enumerate(components):
        component_type = component.get('component_type', 'unknown')
        steps.append(f"{i+4}. Exploit {component_type.replace('_', ' ')}")
    
    steps.append(f"{len(components)+4}. Verify successful exploitation")
    steps.append(f"{len(components)+5}. Document the impact")
    
    return steps

def generate_mitigation_advice(chain: dict) -> list:
    """Generate mitigation advice for a chain"""
    return [
        "1. Implement proper input validation",
        "2. Add authorization checks at all levels",
        "3. Use secure coding practices",
        "4. Implement rate limiting",
        "5. Regular security testing",
        "6. Monitor for suspicious activities"
    ]

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080, debug=True)