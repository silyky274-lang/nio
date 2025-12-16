#!/bin/bash

# APEX HUNTER - Quick Dependency Fix
# Fixes all import errors and missing modules

echo "🔧 APEX HUNTER - Fixing Dependencies"
echo "===================================="

# Activate virtual environment if it exists
if [ -d "apex_env" ]; then
    echo "📦 Activating virtual environment..."
    source apex_env/bin/activate
elif [ -d "../apex_env" ]; then
    echo "📦 Activating virtual environment..."
    source ../apex_env/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv apex_env
    source apex_env/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install \
    requests \
    beautifulsoup4 \
    lxml \
    selenium \
    flask \
    pillow \
    cryptography \
    pyyaml \
    psutil \
    click \
    rich \
    tqdm \
    colorama

# Install from requirements file if it exists
if [ -f "requirements_elite.txt" ]; then
    echo "📚 Installing elite requirements..."
    pip install -r requirements_elite.txt --no-deps --force-reinstall
elif [ -f "requirements.txt" ]; then
    echo "📚 Installing basic requirements..."
    pip install -r requirements.txt
fi

# Install additional security tools
echo "🛡️  Installing security tools..."
pip install \
    nuclei-python \
    python-nmap \
    python-masscan \
    bandit \
    safety \
    semgrep

# Install mobile analysis tools
echo "📱 Installing mobile analysis tools..."
pip install \
    frida-tools \
    objection \
    androguard

# Install blockchain tools
echo "🔗 Installing blockchain tools..."
pip install \
    web3 \
    eth-account \
    slither-analyzer \
    mythril

# Verify installations
echo "✅ Verifying installations..."
python3 -c "
import sys
modules = [
    'requests', 'bs4', 'lxml', 'selenium', 'flask', 
    'PIL', 'cryptography', 'yaml', 'psutil', 'click'
]

failed = []
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        failed.append(module)

if failed:
    print(f'\\n⚠️  Failed modules: {failed}')
    print('Run: pip install ' + ' '.join(failed))
else:
    print('\\n🎉 All core modules installed successfully!')
"

echo ""
echo "🎯 Dependencies fixed! You can now run:"
echo "  python enhanced_web_interface.py"
echo "  python multi_target_analyzer.py"
echo ""