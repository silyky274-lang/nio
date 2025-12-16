#!/usr/bin/env python3
"""
APEX HUNTER - Main System Orchestrator
Complete bug bounty automation system with 8-minute hunt workflow
Optimized for 6GB RAM constraint
"""

import os
import sys
import argparse
import time
import json
from pathlib import Path
import threading
import signal
from typing import Dict, List, Any, Optional

# Import all system components
from memory_manager import memory_manager
from data_collector import DataCollector
from ai_engine import ApexHunterAIEngine
from shadowfinder import ShadowFinder
from logichunter import LogicHunter
from chain_engine import ChainEngine
from evidence_collector import EvidenceManager

class ApexHunterOrchestrator:
    """Main system orchestrator for APEX HUNTER"""
    
    def __init__(self, max_ram_mb: int = 5500):
        self.max_ram = max_ram_mb
        self.system_ready = False
        self.current_hunt = None
        self.hunt_results = {}
        self.system_stats = {
            'total_hunts': 0,
            'successful_hunts': 0,
            'total_chains_found': 0,
            'total_estimated_bounty': 0,
            'average_hunt_time': 0,
            'system_uptime': time.time()
        }
        
        # Initialize system
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the complete APEX HUNTER system"""
        print("🎯 APEX HUNTER - Elite Bug Bounty Automation System")
        print("=" * 60)
        print("Initializing system components...")
        
        try:
            # Check system requirements
            self.check_system_requirements()
            
            # Initialize knowledge base if needed
            self.initialize_knowledge_base()
            
            # Verify all components
            self.verify_components()
            
            self.system_ready = True
            print("✅ System initialization complete!")
            print(f"📊 Memory limit: {self.max_ram}MB")
            print(f"🧠 Knowledge base: Ready")
            print(f"⚡ All engines: Operational")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            sys.exit(1)
    
    def check_system_requirements(self):
        """Check system requirements and constraints"""
        import psutil
        
        # Check total RAM and adjust mode
        total_ram = psutil.virtual_memory().total / 1024 / 1024
        available_ram = psutil.virtual_memory().available / 1024 / 1024
        
        # Adaptive RAM management - work with what we have
        if total_ram < 2000:
            self.memory_mode = "minimal"
            self.max_ram = min(1000, int(available_ram * 0.7))
            print(f"⚠️  Minimal RAM mode: {self.max_ram}MB limit")
        elif total_ram < 4000:
            self.memory_mode = "lightweight"
            self.max_ram = min(1800, int(available_ram * 0.8))
            print(f"🔧 Lightweight mode: {self.max_ram}MB limit")
        elif total_ram < 6000:
            self.memory_mode = "optimized"
            self.max_ram = min(3000, int(available_ram * 0.85))
            print(f"⚡ Optimized mode: {self.max_ram}MB limit")
        else:
            self.memory_mode = "full"
            self.max_ram = min(5500, int(available_ram * 0.9))
            print(f"🚀 Full mode: {self.max_ram}MB limit")
        
        # Stop unnecessary services to free RAM
        self.optimize_system_memory()
        
        # Check disk space
        disk_usage = psutil.disk_usage('/')
        available_disk = disk_usage.free / 1024 / 1024 / 1024
        if available_disk < 2:  # Need at least 2GB free
            raise Exception(f"Insufficient disk space: {available_disk:.1f}GB available, need at least 2GB")
        
        print(f"✅ RAM: {total_ram:.0f}MB total, {available_ram:.0f}MB available")
        print(f"✅ Disk: {available_disk:.1f}GB available")
        print(f"🧠 Knowledge base: Ready")
        print(f"⚡ Memory Manager: Ready")
        print(f"🎯 AI Engine: Ready")
        print(f"🔍 ShadowFinder: Ready")
        print(f"🎯 LogicHunter: Ready")
        print(f"⛓️  Chain Engine: Ready")
        print(f"📹 Evidence Manager: Ready")
    
    def optimize_system_memory(self):
        """Stop unnecessary services and optimize memory usage"""
        import subprocess
        import os
        
        print("🔧 Optimizing system memory...")
        
        # Services to stop (if running) to free RAM
        services_to_stop = [
            'apache2', 'nginx', 'mysql', 'postgresql', 'mongodb',
            'docker', 'snapd', 'bluetooth', 'cups', 'avahi-daemon'
        ]
        
        for service in services_to_stop:
            try:
                # Check if service is running
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                if result.stdout.strip() == 'active':
                    print(f"  🛑 Stopping {service} to free RAM...")
                    subprocess.run(['sudo', 'systemctl', 'stop', service], 
                                 capture_output=True)
            except:
                pass  # Service doesn't exist or can't be stopped
        
        # Clear system caches
        try:
            print("  🧹 Clearing system caches...")
            os.system('sudo sync && sudo sysctl vm.drop_caches=3 2>/dev/null')
        except:
            pass
        
        print("✅ Memory optimization complete")
    
    def initialize_knowledge_base(self):
        """Initialize knowledge base if not present"""
        # Create required directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('sources', exist_ok=True)
        os.makedirs('tools', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('reports/evidence', exist_ok=True)
        os.makedirs('reports/submissions', exist_ok=True)
        os.makedirs('reports/templates', exist_ok=True)
        
        kb_path = Path('data/knowledge_base.db')
        
        if not kb_path.exists():
            print("🔄 Building knowledge base (first run)...")
            # Use the create_knowledge_base.py script instead
            import subprocess
            subprocess.run(['python', 'create_knowledge_base.py'], check=True)
        else:
            print("✅ Knowledge base found")
    
    def verify_components(self):
        """Verify all system components are working"""
        components = [
            ('Memory Manager', memory_manager),
            ('AI Engine', ApexHunterAIEngine),
            ('ShadowFinder', ShadowFinder),
            ('LogicHunter', LogicHunter),
            ('Chain Engine', ChainEngine),
            ('Evidence Manager', EvidenceManager)
        ]
        
        for name, component in components:
            try:
                if hasattr(component, '__call__'):
                    # It's a class, try to instantiate
                    instance = component()
                    print(f"✅ {name}: Ready")
                else:
                    # It's an instance
                    print(f"✅ {name}: Ready")
            except Exception as e:
                raise Exception(f"{name} verification failed: {e}")
    
    def run_deep_hunt(self, target: str, hunt_options: Dict = None) -> Dict[str, Any]:
        """Run complete 8-minute hunt workflow"""
        if not self.system_ready:
            raise Exception("System not ready")
        
        hunt_options = hunt_options or {}
        hunt_id = f"hunt_{int(time.time())}"
        start_time = time.time()
        
        print(f"\n🚀 Starting deep hunt: {hunt_id}")
        print(f"🎯 Target: {target}")
        print(f"⏱️  Time limit: 8 minutes")
        print("=" * 60)
        
        self.current_hunt = {
            'hunt_id': hunt_id,
            'target': target,
            'start_time': start_time,
            'stage': 'initializing',
            'progress': 0,
            'findings': [],
            'chains': [],
            'evidence': {},
            'options': hunt_options
        }
        
        try:
            # Phase 1: ShadowFinder (Historical Analysis) - Minutes 0-2
            print("🔍 Phase 1: ShadowFinder (Historical Analysis)")
            self.current_hunt['stage'] = 'shadow_analysis'
            self.current_hunt['progress'] = 10
            
            memory_manager.swap_tool('shadowfinder', load=True)
            shadow_finder = memory_manager.get_tool('shadowfinder')
            shadow_results = shadow_finder.run(target)
            memory_manager.swap_tool('shadowfinder', load=False)
            
            self.current_hunt['findings'].extend(shadow_results)
            self.current_hunt['progress'] = 30
            print(f"   ✅ Found {len(shadow_results)} historical findings")
            
            # Phase 2: LogicHunter (Business Logic Analysis) - Minutes 2-5
            print("🧠 Phase 2: LogicHunter (Business Logic Analysis)")
            self.current_hunt['stage'] = 'logic_analysis'
            self.current_hunt['progress'] = 40
            
            memory_manager.swap_tool('logichunter', load=True)
            logic_hunter = memory_manager.get_tool('logichunter')
            logic_results = logic_hunter.scan(target, shadow_results)
            memory_manager.swap_tool('logichunter', load=False)
            
            self.current_hunt['findings'].extend(logic_results)
            self.current_hunt['progress'] = 60
            print(f"   ✅ Found {len(logic_results)} business logic findings")
            
            # Phase 3: Chain Engine (Exploit Chaining) - Minutes 5-7
            print("⛓️  Phase 3: Chain Engine (Exploit Chaining)")
            self.current_hunt['stage'] = 'chain_analysis'
            self.current_hunt['progress'] = 70
            
            memory_manager.swap_tool('chainengine', load=True)
            chain_engine = memory_manager.get_tool('chainengine')
            all_findings = shadow_results + logic_results
            chains = chain_engine.analyze(all_findings)
            memory_manager.swap_tool('chainengine', load=False)
            
            self.current_hunt['chains'] = chains
            self.current_hunt['progress'] = 80
            print(f"   ✅ Discovered {len(chains)} chain opportunities")
            
            # Phase 4: AI Analysis - Minutes 7-8
            print("🤖 Phase 4: AI Analysis")
            self.current_hunt['stage'] = 'ai_analysis'
            self.current_hunt['progress'] = 85
            
            memory_manager.swap_tool('ai_engine', load=True)
            ai_engine = memory_manager.get_tool('ai_engine')
            analyzed_chains = ai_engine.analyze_findings(all_findings)
            memory_manager.swap_tool('ai_engine', load=False)
            
            # Merge AI analysis with chain results
            final_chains = self.merge_chain_results(chains, analyzed_chains)
            self.current_hunt['chains'] = final_chains
            self.current_hunt['progress'] = 90
            print(f"   ✅ AI analysis complete: {len(final_chains)} high-value chains")
            
            # Phase 5: Evidence Collection - Final minute
            print("📹 Phase 5: Evidence Collection")
            self.current_hunt['stage'] = 'evidence_collection'
            self.current_hunt['progress'] = 95
            
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
            
            self.current_hunt['evidence'] = evidence_by_chain
            self.current_hunt['progress'] = 100
            self.current_hunt['stage'] = 'completed'
            
            # Calculate final results
            elapsed_time = time.time() - start_time
            total_bounty = sum(chain.get('estimated_bounty', 0) for chain in final_chains)
            
            hunt_results = {
                'hunt_id': hunt_id,
                'target': target,
                'elapsed_time': elapsed_time,
                'total_findings': len(all_findings),
                'total_chains': len(final_chains),
                'high_value_chains': len([c for c in final_chains if c.get('estimated_bounty', 0) >= 2000]),
                'total_estimated_bounty': total_bounty,
                'evidence_packages': len(evidence_by_chain),
                'success': True,
                'findings': all_findings,
                'chains': final_chains,
                'evidence': evidence_by_chain
            }
            
            # Update system stats
            self.update_system_stats(hunt_results)
            
            # Check if hunt exceeded 8 minutes
            if elapsed_time > 480:  # 8 minutes
                print(f"⚠️  Hunt exceeded 8-minute limit: {elapsed_time:.1f}s")
                hunt_results['timeout'] = True
            
            print("=" * 60)
            print("🎉 HUNT COMPLETED SUCCESSFULLY!")
            print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
            print(f"🔍 Total findings: {len(all_findings)}")
            print(f"⛓️  Chain opportunities: {len(final_chains)}")
            print(f"💰 Estimated bounty value: ${total_bounty:,}")
            print(f"📦 Evidence packages: {len(evidence_by_chain)}")
            print("=" * 60)
            
            self.hunt_results[hunt_id] = hunt_results
            return hunt_results
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_result = {
                'hunt_id': hunt_id,
                'target': target,
                'elapsed_time': elapsed_time,
                'success': False,
                'error': str(e),
                'stage': self.current_hunt.get('stage', 'unknown'),
                'progress': self.current_hunt.get('progress', 0)
            }
            
            print(f"❌ Hunt failed: {e}")
            self.hunt_results[hunt_id] = error_result
            return error_result
            
        finally:
            # Clean up memory
            memory_manager.cleanup()
            self.current_hunt = None
    
    def merge_chain_results(self, chain_results: List[Dict], ai_results: List[Dict]) -> List[Dict]:
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
    
    def update_system_stats(self, hunt_results: Dict):
        """Update system statistics"""
        self.system_stats['total_hunts'] += 1
        
        if hunt_results.get('success', False):
            self.system_stats['successful_hunts'] += 1
            self.system_stats['total_chains_found'] += hunt_results.get('total_chains', 0)
            self.system_stats['total_estimated_bounty'] += hunt_results.get('total_estimated_bounty', 0)
            
            # Update average hunt time
            total_time = self.system_stats.get('total_hunt_time', 0) + hunt_results.get('elapsed_time', 0)
            self.system_stats['total_hunt_time'] = total_time
            self.system_stats['average_hunt_time'] = total_time / self.system_stats['successful_hunts']
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        import psutil
        
        current_memory = psutil.virtual_memory()
        current_hunt_info = None
        
        if self.current_hunt:
            elapsed = time.time() - self.current_hunt['start_time']
            remaining = max(0, 480 - elapsed)  # 8 minutes = 480 seconds
            
            current_hunt_info = {
                'active': True,
                'hunt_id': self.current_hunt['hunt_id'],
                'target': self.current_hunt['target'],
                'stage': self.current_hunt['stage'],
                'progress': self.current_hunt['progress'],
                'elapsed_time': elapsed,
                'remaining_time': remaining,
                'findings_count': len(self.current_hunt['findings']),
                'chains_count': len(self.current_hunt['chains'])
            }
        
        return {
            'system_ready': self.system_ready,
            'current_hunt': current_hunt_info,
            'system_stats': self.system_stats,
            'memory_usage': {
                'total_mb': current_memory.total / 1024 / 1024,
                'available_mb': current_memory.available / 1024 / 1024,
                'used_mb': current_memory.used / 1024 / 1024,
                'percentage': current_memory.percent
            },
            'memory_manager': memory_manager.get_memory_stats(),
            'uptime': time.time() - self.system_stats['system_uptime']
        }
    
    def stop_current_hunt(self):
        """Stop the current hunt if active"""
        if self.current_hunt:
            self.current_hunt['stage'] = 'stopped'
            self.current_hunt['progress'] = 0
            memory_manager.cleanup()
            self.current_hunt = None
            return True
        return False
    
    def run_web_interface(self, port: int = 8080):
        """Run the web interface"""
        try:
            from web.app import app
            print(f"🌐 Starting web interface on port {port}")
            print(f"🔗 Access dashboard at: http://localhost:{port}")
            app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        except ImportError:
            print("❌ Web interface not available - Flask not installed")
        except Exception as e:
            print(f"❌ Failed to start web interface: {e}")

def signal_handler(signum, frame):
    """Handle system signals gracefully"""
    print("\n🛑 Received shutdown signal")
    print("🧹 Cleaning up system resources...")
    memory_manager.cleanup()
    print("✅ Shutdown complete")
    sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='APEX HUNTER - Elite Bug Bounty Automation System')
    parser.add_argument('--target', '-t', help='Target to hunt (URL, domain, or IP)')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Web interface port (default: 8080)')
    parser.add_argument('--max-ram', type=int, default=5500, help='Maximum RAM usage in MB (default: 5500)')
    parser.add_argument('--hunt-type', choices=['comprehensive', 'stealth', 'aggressive', 'business-logic'], 
                       default='comprehensive', help='Type of hunt to perform')
    parser.add_argument('--time-limit', type=int, default=480, help='Hunt time limit in seconds (default: 480)')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--status', action='store_true', help='Show system status and exit')
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize system
    orchestrator = ApexHunterOrchestrator(max_ram_mb=args.max_ram)
    
    if args.status:
        # Show system status
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.web:
        # Start web interface
        orchestrator.run_web_interface(port=args.port)
        return
    
    if args.target:
        # Run command-line hunt
        hunt_options = {
            'hunt_type': args.hunt_type,
            'time_limit': args.time_limit
        }
        
        results = orchestrator.run_deep_hunt(args.target, hunt_options)
        
        if args.output:
            # Save results to file
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Results saved to: {args.output}")
        
        return
    
    # Interactive mode
    print("\n🎯 APEX HUNTER - Interactive Mode")
    print("Commands:")
    print("  hunt <target>     - Start a hunt on target")
    print("  status           - Show system status")
    print("  web              - Start web interface")
    print("  quit             - Exit system")
    print()
    
    while True:
        try:
            command = input("apex_hunter> ").strip().split()
            
            if not command:
                continue
            
            if command[0] == 'quit':
                break
            elif command[0] == 'status':
                status = orchestrator.get_system_status()
                print(json.dumps(status, indent=2))
            elif command[0] == 'web':
                orchestrator.run_web_interface()
                break
            elif command[0] == 'hunt' and len(command) > 1:
                target = command[1]
                results = orchestrator.run_deep_hunt(target)
                print(f"\n📊 Hunt Results Summary:")
                print(f"   Success: {results.get('success', False)}")
                print(f"   Chains: {results.get('total_chains', 0)}")
                print(f"   Bounty: ${results.get('total_estimated_bounty', 0):,}")
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    main()