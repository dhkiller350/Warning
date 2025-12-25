#!/bin/bash
#
# Network Firewall Dashboard - Installation Script
# This script sets up the firewall dashboard on Ubuntu systems
#

set -e

echo "================================================"
echo "  Network Firewall Dashboard - Installation"
echo "================================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script is designed for Linux systems"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Install with: sudo apt-get install python3"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip3 not found, installing..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make script executable
echo ""
echo "🔧 Making firewall_dashboard.py executable..."
chmod +x firewall_dashboard.py

# Check if iptables is installed
if ! command -v iptables &> /dev/null; then
    echo "⚠️  iptables not found, installing..."
    sudo apt-get install -y iptables
fi

echo "✅ iptables found: $(iptables --version 2>/dev/null || echo 'installed')"

# Create config directory
echo ""
echo "📁 Creating configuration directory..."
mkdir -p ~/.config/firewall-dashboard

echo ""
echo "================================================"
echo "  Installation Complete! ✅"
echo "================================================"
echo ""
echo "To start the dashboard:"
echo ""
echo "  Demo Mode (no root needed):"
echo "    python3 firewall_dashboard.py"
echo ""
echo "  Full Mode (with firewall control):"
echo "    sudo python3 firewall_dashboard.py"
echo ""
echo "Then open your browser to: http://localhost:5000"
echo "Login with password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the default password in"
echo "   firewall_dashboard.py before production use!"
echo ""
echo "📚 For more information, see:"
echo "   - QUICKSTART.md for quick start guide"
echo "   - README.md for full documentation"
echo ""
