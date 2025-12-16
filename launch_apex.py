#!/usr/bin/env python3
"""
APEX HUNTER - Simple Launcher
Bypasses complex installation and gets you hunting immediately
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def create_directories():
    """Create all required directories"""
    dirs = [
        'data', 'sources', 'tools', 'config', 'logs',
        'reports/evidence', 'reports/submissions', 'reports/templates'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        # Create .gitkeep files
        gitkeep = Path(dir_path) / '.gitkeep'
        gitkeep.touch()

def check_knowledge_base():
    """Check and create knowledge base if needed"""
    kb_path = Path('data/knowledge_base.db')
    
    if not kb_path.exists():
        print("🧠 Creating knowledge base...")
        subprocess.run([sys.executable, 'create_knowledge_base.py'], check=True)
        print(f"✅ Knowledge base created: {kb_path.stat().st_size / 1024 / 1024:.2f}MB")
    else:
        print(f"✅ Knowledge base found: {kb_path.stat().st_size / 1024 / 1024:.2f}MB")

def create_config():
    """Create minimal configuration"""
    config_path = Path('config/system_config.json')
    
    if not config_path.exists():
        config = {
            "system": {
                "max_ram_mb": 1800,
                "memory_mode": "lightweight",
                "max_hunt_time_seconds": 600,
                "auto_cleanup": True
            },
            "web_interface": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False
            }
        }
        
        import json
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration created")

def launch_web_interface():
    """Launch the web interface"""
    print("\n🚀 Starting APEX HUNTER Web Interface...")
    print("=" * 50)
    
    # Import and start the web app
    try:
        from web.app import app
        print("🌐 Starting web interface on port 8080")
        print("🔗 Access dashboard at: http://localhost:8080")
        print("=" * 50)
        app.run(host='0.0.0.0', port=8080, debug=False)
    except ImportError:
        print("❌ Web interface not available")
        print("💡 Try: python apex_hunter.py --help")

def main():
    """Main launcher function"""
    print("🎯 APEX HUNTER - Simple Launcher")
    print("=" * 40)
    
    # Step 1: Create directories
    print("📁 Creating directories...")
    create_directories()
    
    # Step 2: Check knowledge base
    check_knowledge_base()
    
    # Step 3: Create config
    create_config()
    
    # Step 4: Launch
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        launch_web_interface()
    else:
        print("\n🎯 APEX HUNTER Ready!")
        print("=" * 30)
        print("🌐 Web Interface: python launch_apex.py --web")
        print("🎯 Hunt Target: python apex_hunter.py --target example.com")
        print("📊 System Status: python apex_hunter.py --status")

if __name__ == "__main__":
    main()