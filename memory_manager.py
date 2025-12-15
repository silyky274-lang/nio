#!/usr/bin/env python3
"""
APEX HUNTER - Advanced Memory Management System
Optimized for 6GB RAM constraint with intelligent tool swapping
"""

import gc
import os
import sys
import time
import json
import sqlite3
import psutil
import pickle
from typing import Dict, Any, Optional, List
from pathlib import Path

class MemoryManager:
    """Advanced memory management for 6GB RAM constraint"""
    
    def __init__(self, max_ram_mb=5500):
        """Initialize memory manager with strict RAM limits"""
        self.max_ram = max_ram_mb
        self.current_usage = 0
        self.tool_registry = {}
        self.swap_threshold = 4500  # Start swapping at 4.5GB
        self.knowledge_base_cache = {}  # Cache for AI knowledge base
        self.tool_states_dir = Path('/tmp/apex_hunter_states')
        self.tool_states_dir.mkdir(exist_ok=True)
        
        # Tool memory footprints (MB)
        self.tool_sizes = {
            'shadowfinder': 800,    # MB - passive/historical recon
            'logichunter': 1200,    # MB - active/business logic analysis  
            'chainengine': 600,     # MB - exploit chain detection
            'evidencemgr': 300,     # MB - evidence collection
            'ai_engine': 1000,      # MB - AI decision engine (partial load)
            'report_generator': 400 # MB - report generation
        }
        
        # Knowledge base chunk sizes (MB)
        self.chunk_sizes = {
            'chain_templates': 400,
            'business_logic_rules': 300,
            'vulnerability_data': 500,
            'platform_intelligence': 200,
            'historical_patterns': 250,
            'forgotten_environments': 150,
            'naming_conventions': 100
        }
        
    def get_current_memory_usage(self):
        """Get current system memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def get_available_memory(self):
        """Get available system memory in MB"""
        return psutil.virtual_memory().available / 1024 / 1024
    
    def check_memory_pressure(self):
        """Check if system is under memory pressure"""
        current_usage = self.get_current_memory_usage()
        available = self.get_available_memory()
        
        if current_usage > self.swap_threshold or available < 1000:  # Less than 1GB available
            return True
        return False
    
    def load_knowledge_base_chunk(self, chunk_name: str) -> List[Dict]:
        """Load knowledge base chunks on-demand to save RAM"""
        if chunk_name in self.knowledge_base_cache:
            return self.knowledge_base_cache[chunk_name]
        
        # Calculate available RAM after loading chunk
        chunk_size = self.chunk_sizes.get(chunk_name, 200)
        if self.current_usage + chunk_size > self.swap_threshold:
            self.swap_out_least_used_knowledge_chunk()
        
        # Load only the required chunk from SQLite
        db_path = '/workspace/project/mr-mx-lee-/data/knowledge_base.db'
        if not os.path.exists(db_path):
            return []
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            chunk_data = []
            if chunk_name == 'chain_templates':
                cursor.execute("""
                    SELECT template_id, pattern, impact_score, bounty_range, payment_probability
                    FROM chain_templates 
                    WHERE minimum_bounty >= 500
                    ORDER BY impact_score DESC, payment_probability DESC
                    LIMIT 5000  -- Only top 5K templates
                """)
                for row in cursor.fetchall():
                    chunk_data.append({
                        'template_id': row[0],
                        'pattern': json.loads(row[1]) if row[1] else {},
                        'impact_score': row[2],
                        'bounty_range': row[3],
                        'payment_probability': row[4]
                    })
                    
            elif chunk_name == 'business_logic_rules':
                cursor.execute("""
                    SELECT rule_id, platform, pattern_type, detection_rules, impact_score, bounty_range
                    FROM business_logic_rules
                    ORDER BY impact_score DESC
                    LIMIT 3000  -- Only top 3K rules
                """)
                for row in cursor.fetchall():
                    chunk_data.append({
                        'rule_id': row[0],
                        'platform': row[1],
                        'pattern_type': row[2],
                        'detection_rules': json.loads(row[3]) if row[3] else {},
                        'impact_score': row[4],
                        'bounty_range': row[5]
                    })
                    
            elif chunk_name == 'vulnerability_data':
                cursor.execute("""
                    SELECT cve_id, description, cvss_score, affected_products, exploit_available
                    FROM vulnerability_data
                    WHERE cvss_score >= 7.0
                    ORDER BY cvss_score DESC
                    LIMIT 10000
                """)
                for row in cursor.fetchall():
                    chunk_data.append({
                        'cve_id': row[0],
                        'description': row[1],
                        'cvss_score': row[2],
                        'affected_products': json.loads(row[3]) if row[3] else [],
                        'exploit_available': row[4]
                    })
            
            conn.close()
            
            # Cache the chunk but limit cache size
            self.knowledge_base_cache[chunk_name] = chunk_data
            if len(self.knowledge_base_cache) > 3:  # Only keep 3 chunks in cache
                self.swap_out_oldest_knowledge_chunk()
            
            return chunk_data
            
        except Exception as e:
            print(f"Error loading knowledge chunk {chunk_name}: {e}")
            return []
    
    def swap_out_oldest_knowledge_chunk(self):
        """Remove oldest knowledge chunk from cache"""
        if not self.knowledge_base_cache:
            return
            
        # Remove the first (oldest) chunk
        oldest_chunk = list(self.knowledge_base_cache.keys())[0]
        del self.knowledge_base_cache[oldest_chunk]
        gc.collect()
    
    def swap_out_least_used_knowledge_chunk(self):
        """Swap out least used knowledge chunk"""
        if not self.knowledge_base_cache:
            return
            
        # For simplicity, remove the largest chunk
        largest_chunk = max(self.knowledge_base_cache.keys(), 
                          key=lambda x: self.chunk_sizes.get(x, 0))
        del self.knowledge_base_cache[largest_chunk]
        gc.collect()
    
    def save_tool_state(self, tool_name: str):
        """Save tool state to disk before unloading"""
        if tool_name not in self.tool_registry:
            return
            
        state_file = self.tool_states_dir / f"{tool_name}_state.pkl"
        try:
            with open(state_file, 'wb') as f:
                pickle.dump(self.tool_registry[tool_name], f)
        except Exception as e:
            print(f"Warning: Could not save state for {tool_name}: {e}")
    
    def load_tool_state(self, tool_name: str) -> Optional[Any]:
        """Load tool state from disk"""
        state_file = self.tool_states_dir / f"{tool_name}_state.pkl"
        if not state_file.exists():
            return None
            
        try:
            with open(state_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Could not load state for {tool_name}: {e}")
            return None
    
    def load_minimal_tool(self, tool_name: str):
        """Load minimal version of tool with knowledge base integration"""
        # Try to restore previous state first
        tool_state = self.load_tool_state(tool_name)
        if tool_state:
            return tool_state
        
        # Import and initialize tool
        if tool_name == 'shadowfinder':
            from shadowfinder import ShadowFinder
            tool = ShadowFinder(target="", max_ram_mb=self.tool_sizes[tool_name])
        elif tool_name == 'logichunter':
            from logichunter import LogicHunter
            tool = LogicHunter(target="", max_ram_mb=self.tool_sizes[tool_name])
        elif tool_name == 'chainengine':
            from chain_engine import ChainEngine
            tool = ChainEngine(max_ram_mb=self.tool_sizes[tool_name])
        elif tool_name == 'evidencemgr':
            from evidence_collector import EvidenceManager
            tool = EvidenceManager(max_ram_mb=self.tool_sizes[tool_name])
        elif tool_name == 'ai_engine':
            from ai_engine import ApexHunterAIEngine
            tool = ApexHunterAIEngine()
        elif tool_name == 'report_generator':
            from report_generator import ReportGenerator
            tool = ReportGenerator(max_ram_mb=self.tool_sizes[tool_name])
        else:
            return None
        
        # Set last used timestamp
        tool.last_used = time.time()
        return tool
    
    def swap_tool(self, tool_name: str, load: bool = True):
        """Advanced tool swapping with knowledge base awareness"""
        if not load and tool_name in self.tool_registry:
            tool_size = self.tool_sizes.get(tool_name, 200)
            # Save tool state to disk before unloading
            self.save_tool_state(tool_name)
            del self.tool_registry[tool_name]
            self.current_usage -= tool_size
            gc.collect()
            return
        
        # Check if we need to swap out least used tool first
        tool_size = self.tool_sizes.get(tool_name, 200)
        if self.current_usage + tool_size > self.swap_threshold:
            self.swap_out_least_used_tool()
        
        # Load minimal version of tool with knowledge base integration
        tool = self.load_minimal_tool(tool_name)
        if tool is None:
            print(f"Warning: Could not load tool {tool_name}")
            return
            
        self.tool_registry[tool_name] = tool
        
        # For AI engine, load only relevant knowledge chunks
        if tool_name == 'ai_engine':
            self.tool_registry[tool_name].chain_templates = self.load_knowledge_base_chunk('chain_templates')
            self.tool_registry[tool_name].business_logic_rules = self.load_knowledge_base_chunk('business_logic_rules')
        
        self.current_usage += tool_size
    
    def swap_out_least_used_tool(self):
        """Intelligently swap out least used tools"""
        if not self.tool_registry:
            return
        
        # Prioritize swapping AI engine knowledge chunks first
        if 'ai_engine' in self.tool_registry and len(self.knowledge_base_cache) > 1:
            # Swap out oldest knowledge chunk instead of entire tool
            self.swap_out_oldest_knowledge_chunk()
            return
        
        # Find least recently used tool
        oldest_tool = min(self.tool_registry.keys(), 
                         key=lambda x: getattr(self.tool_registry[x], 'last_used', 0))
        
        # Save state before unloading
        self.save_tool_state(oldest_tool)
        tool_size = self.tool_sizes.get(oldest_tool, 200)
        
        del self.tool_registry[oldest_tool]
        self.current_usage -= tool_size
        gc.collect()
    
    def get_tool_size(self, tool_name: str) -> int:
        """Get estimated tool size in MB"""
        return self.tool_sizes.get(tool_name, 200)
    
    def get_tool(self, tool_name: str):
        """Get tool from registry, loading if necessary"""
        if tool_name not in self.tool_registry:
            self.swap_tool(tool_name, load=True)
        
        # Update last used timestamp
        if tool_name in self.tool_registry:
            self.tool_registry[tool_name].last_used = time.time()
            return self.tool_registry[tool_name]
        
        return None
    
    def cleanup(self):
        """Clean up all tools and cache"""
        for tool_name in list(self.tool_registry.keys()):
            self.swap_tool(tool_name, load=False)
        
        self.knowledge_base_cache.clear()
        gc.collect()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        return {
            'current_usage_mb': self.get_current_memory_usage(),
            'available_mb': self.get_available_memory(),
            'loaded_tools': list(self.tool_registry.keys()),
            'cached_knowledge_chunks': list(self.knowledge_base_cache.keys()),
            'memory_pressure': self.check_memory_pressure(),
            'swap_threshold_mb': self.swap_threshold,
            'max_ram_mb': self.max_ram
        }

# Global memory manager instance
memory_manager = MemoryManager()