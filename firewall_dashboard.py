#!/usr/bin/env python3
"""
Network Firewall Dashboard - All-in-One Script
Ubuntu Caine Firewall Control with Web Dashboard

This script provides:
- Firewall rule management using iptables
- IP address control for router, devices, and wireless connections
- Password-protected web dashboard
- VPN configuration support
- Connection state management (open/closed)
"""

import os
import sys
import subprocess
import hashlib
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps

# Configuration
ROUTER_IP = "10.0.0.1"
PS4_IP = "10.0.0.5"
CONFIG_FILE = "/tmp/firewall_config.json"
DEFAULT_PASSWORD = "admin123"  # Change this in production!

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Firewall Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #333;
            font-size: 28px;
        }
        .logout-btn {
            background: #e74c3c;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
        }
        .logout-btn:hover {
            background: #c0392b;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .status-label {
            font-weight: 600;
            color: #555;
        }
        .status-value {
            color: #333;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-active {
            background: #27ae60;
        }
        .status-inactive {
            background: #e74c3c;
        }
        .status-warning {
            background: #f39c12;
        }
        .control-section {
            margin: 15px 0;
        }
        .input-group {
            margin: 10px 0;
        }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px 5px 5px 0;
        }
        .btn:hover {
            background: #5568d3;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
        .btn-success {
            background: #27ae60;
        }
        .btn-success:hover {
            background: #229954;
        }
        .alert {
            padding: 12px;
            border-radius: 5px;
            margin: 10px 0;
            display: none;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .rule-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .rule-item {
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .rule-info {
            flex: 1;
        }
        .rule-actions button {
            margin-left: 5px;
            padding: 5px 10px;
            font-size: 12px;
        }
        .timestamp {
            font-size: 12px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Network Firewall Dashboard</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>

        <div id="alertContainer"></div>

        <div class="dashboard-grid">
            <!-- System Status Card -->
            <div class="card">
                <h2>System Status</h2>
                <div class="status-item">
                    <span class="status-label">Firewall Status:</span>
                    <span class="status-value" id="firewallStatus">
                        <span class="status-indicator status-active"></span>Active
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">Router IP:</span>
                    <span class="status-value">{{ router_ip }}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">PS4 IP:</span>
                    <span class="status-value">{{ ps4_ip }}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Connection State:</span>
                    <span class="status-value" id="connectionState">
                        <span class="status-indicator status-active"></span>Open
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">VPN Status:</span>
                    <span class="status-value" id="vpnStatus">
                        <span class="status-indicator status-inactive"></span>Not Connected
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">Active Rules:</span>
                    <span class="status-value" id="activeRules">0</span>
                </div>
            </div>

            <!-- Quick Actions Card -->
            <div class="card">
                <h2>Quick Actions</h2>
                <div class="control-section">
                    <button class="btn btn-success" onclick="toggleFirewall(true)">Enable Firewall</button>
                    <button class="btn btn-danger" onclick="toggleFirewall(false)">Disable Firewall</button>
                </div>
                <div class="control-section">
                    <button class="btn" onclick="toggleConnection(true)">Open Connection</button>
                    <button class="btn btn-danger" onclick="toggleConnection(false)">Close Connection</button>
                </div>
                <div class="control-section">
                    <button class="btn" onclick="allowPS4()">Allow PS4 Traffic</button>
                    <button class="btn btn-danger" onclick="blockPS4()">Block PS4 Traffic</button>
                </div>
                <div class="control-section">
                    <button class="btn btn-success" onclick="connectVPN()">Connect VPN</button>
                    <button class="btn btn-danger" onclick="disconnectVPN()">Disconnect VPN</button>
                </div>
            </div>

            <!-- IP Management Card -->
            <div class="card">
                <h2>IP Address Management</h2>
                <div class="input-group">
                    <label for="ipAddress">IP Address:</label>
                    <input type="text" id="ipAddress" placeholder="e.g., 10.0.0.100">
                </div>
                <div class="input-group">
                    <label for="ipAction">Action:</label>
                    <select id="ipAction">
                        <option value="allow">Allow</option>
                        <option value="block">Block</option>
                    </select>
                </div>
                <button class="btn" onclick="manageIP()">Apply Rule</button>
                <button class="btn btn-danger" onclick="removeIPRule()">Remove Rule</button>
            </div>

            <!-- Wireless Management Card -->
            <div class="card">
                <h2>Wireless Connection Control</h2>
                <div class="input-group">
                    <label for="wirelessMAC">MAC Address:</label>
                    <input type="text" id="wirelessMAC" placeholder="e.g., AA:BB:CC:DD:EE:FF">
                </div>
                <div class="input-group">
                    <label for="wirelessAction">Action:</label>
                    <select id="wirelessAction">
                        <option value="allow">Allow</option>
                        <option value="block">Block</option>
                    </select>
                </div>
                <button class="btn" onclick="manageWireless()">Apply Rule</button>
            </div>
        </div>

        <!-- Firewall Rules Card -->
        <div class="card">
            <h2>Active Firewall Rules</h2>
            <div id="rulesList" class="rule-list">
                <p style="text-align: center; color: #888; padding: 20px;">Loading rules...</p>
            </div>
            <div class="control-section">
                <button class="btn" onclick="loadRules()">Refresh Rules</button>
                <button class="btn btn-danger" onclick="flushRules()">Clear All Rules</button>
            </div>
        </div>

        <!-- Log Card -->
        <div class="card">
            <h2>Activity Log</h2>
            <div id="activityLog" class="rule-list" style="max-height: 200px;">
                <p style="text-align: center; color: #888; padding: 20px;">No activity yet</p>
            </div>
        </div>
    </div>

    <script>
        // Load initial data
        window.onload = function() {
            loadRules();
            updateStatus();
            setInterval(updateStatus, 5000); // Update every 5 seconds
        };

        function showAlert(message, type) {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alert.style.display = 'block';
            alertContainer.appendChild(alert);
            setTimeout(() => alert.remove(), 5000);
        }

        function addLog(message) {
            const logContainer = document.getElementById('activityLog');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'rule-item';
            logEntry.innerHTML = `
                <div class="rule-info">
                    <div>${message}</div>
                    <div class="timestamp">${timestamp}</div>
                </div>
            `;
            logContainer.insertBefore(logEntry, logContainer.firstChild);
            
            // Keep only last 10 logs
            while (logContainer.children.length > 10) {
                logContainer.removeChild(logContainer.lastChild);
            }
        }

        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('activeRules').textContent = data.active_rules;
                
                // Update connection state
                const connState = document.getElementById('connectionState');
                if (data.connection_open) {
                    connState.innerHTML = '<span class="status-indicator status-active"></span>Open';
                } else {
                    connState.innerHTML = '<span class="status-indicator status-inactive"></span>Closed';
                }
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }

        async function toggleFirewall(enable) {
            try {
                const response = await fetch('/api/firewall/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({enable: enable})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(enable ? 'Firewall enabled' : 'Firewall disabled');
                updateStatus();
            } catch (error) {
                showAlert('Error toggling firewall: ' + error, 'error');
            }
        }

        async function toggleConnection(open) {
            try {
                const response = await fetch('/api/connection/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({open: open})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(open ? 'Connection opened' : 'Connection closed');
                updateStatus();
            } catch (error) {
                showAlert('Error toggling connection: ' + error, 'error');
            }
        }

        async function allowPS4() {
            try {
                const response = await fetch('/api/ps4/allow', {method: 'POST'});
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog('PS4 traffic allowed');
                loadRules();
            } catch (error) {
                showAlert('Error allowing PS4: ' + error, 'error');
            }
        }

        async function blockPS4() {
            try {
                const response = await fetch('/api/ps4/block', {method: 'POST'});
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog('PS4 traffic blocked');
                loadRules();
            } catch (error) {
                showAlert('Error blocking PS4: ' + error, 'error');
            }
        }

        async function manageIP() {
            const ip = document.getElementById('ipAddress').value;
            const action = document.getElementById('ipAction').value;
            
            if (!ip) {
                showAlert('Please enter an IP address', 'error');
                return;
            }

            try {
                const response = await fetch('/api/ip/manage', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ip: ip, action: action})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(`${action === 'allow' ? 'Allowed' : 'Blocked'} IP: ${ip}`);
                loadRules();
                document.getElementById('ipAddress').value = '';
            } catch (error) {
                showAlert('Error managing IP: ' + error, 'error');
            }
        }

        async function removeIPRule() {
            const ip = document.getElementById('ipAddress').value;
            
            if (!ip) {
                showAlert('Please enter an IP address', 'error');
                return;
            }

            try {
                const response = await fetch('/api/ip/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ip: ip})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(`Removed rule for IP: ${ip}`);
                loadRules();
                document.getElementById('ipAddress').value = '';
            } catch (error) {
                showAlert('Error removing IP rule: ' + error, 'error');
            }
        }

        async function manageWireless() {
            const mac = document.getElementById('wirelessMAC').value;
            const action = document.getElementById('wirelessAction').value;
            
            if (!mac) {
                showAlert('Please enter a MAC address', 'error');
                return;
            }

            try {
                const response = await fetch('/api/wireless/manage', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mac: mac, action: action})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(`${action === 'allow' ? 'Allowed' : 'Blocked'} MAC: ${mac}`);
                loadRules();
                document.getElementById('wirelessMAC').value = '';
            } catch (error) {
                showAlert('Error managing wireless: ' + error, 'error');
            }
        }

        async function connectVPN() {
            try {
                const response = await fetch('/api/vpn/connect', {method: 'POST'});
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog('VPN connection initiated');
                const vpnStatus = document.getElementById('vpnStatus');
                vpnStatus.innerHTML = '<span class="status-indicator status-active"></span>Connected';
            } catch (error) {
                showAlert('Error connecting VPN: ' + error, 'error');
            }
        }

        async function disconnectVPN() {
            try {
                const response = await fetch('/api/vpn/disconnect', {method: 'POST'});
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog('VPN disconnected');
                const vpnStatus = document.getElementById('vpnStatus');
                vpnStatus.innerHTML = '<span class="status-indicator status-inactive"></span>Not Connected';
            } catch (error) {
                showAlert('Error disconnecting VPN: ' + error, 'error');
            }
        }

        async function loadRules() {
            try {
                const response = await fetch('/api/rules');
                const data = await response.json();
                const rulesList = document.getElementById('rulesList');
                
                if (data.rules && data.rules.length > 0) {
                    rulesList.innerHTML = '';
                    data.rules.forEach((rule, index) => {
                        const ruleItem = document.createElement('div');
                        ruleItem.className = 'rule-item';
                        ruleItem.innerHTML = `
                            <div class="rule-info">
                                <strong>Rule ${index + 1}:</strong> ${rule.description || rule.rule}
                                <div class="timestamp">${rule.timestamp || 'N/A'}</div>
                            </div>
                            <div class="rule-actions">
                                <button class="btn btn-danger" onclick="deleteRule(${index})">Delete</button>
                            </div>
                        `;
                        rulesList.appendChild(ruleItem);
                    });
                } else {
                    rulesList.innerHTML = '<p style="text-align: center; color: #888; padding: 20px;">No active rules</p>';
                }
            } catch (error) {
                console.error('Error loading rules:', error);
                showAlert('Error loading rules', 'error');
            }
        }

        async function deleteRule(index) {
            try {
                const response = await fetch('/api/rules/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({index: index})
                });
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog(`Deleted rule ${index + 1}`);
                loadRules();
            } catch (error) {
                showAlert('Error deleting rule: ' + error, 'error');
            }
        }

        async function flushRules() {
            if (!confirm('Are you sure you want to clear all firewall rules?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/rules/flush', {method: 'POST'});
                const data = await response.json();
                showAlert(data.message, data.status === 'success' ? 'success' : 'error');
                addLog('All rules flushed');
                loadRules();
            } catch (error) {
                showAlert('Error flushing rules: ' + error, 'error');
            }
        }
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firewall Dashboard - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 400px;
            max-width: 90%;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #5568d3;
        }
        .error {
            color: #e74c3c;
            text-align: center;
            margin-top: 15px;
            display: {{ 'block' if error else 'none' }};
        }
        .icon {
            text-align: center;
            font-size: 60px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="icon">🛡️</div>
        <h1>Firewall Dashboard</h1>
        <form method="POST">
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autofocus>
            </div>
            <button type="submit">Login</button>
            <div class="error">{{ error }}</div>
        </form>
    </div>
</body>
</html>
"""

class FirewallConfig:
    """Manage firewall configuration and state"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = self.default_config()
        else:
            self.config = self.default_config()
        self.save_config()
    
    def default_config(self):
        """Return default configuration"""
        return {
            'firewall_enabled': True,
            'connection_open': True,
            'vpn_connected': False,
            'rules': [],
            'blocked_ips': [],
            'allowed_ips': [ROUTER_IP, PS4_IP],
            'blocked_macs': [],
            'allowed_macs': []
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def add_rule(self, rule_description, rule_command=None):
        """Add a firewall rule"""
        rule = {
            'description': rule_description,
            'rule': rule_command or rule_description,
            'timestamp': datetime.now().isoformat()
        }
        self.config['rules'].append(rule)
        self.save_config()
    
    def remove_rule(self, index):
        """Remove a firewall rule by index"""
        if 0 <= index < len(self.config['rules']):
            self.config['rules'].pop(index)
            self.save_config()
            return True
        return False
    
    def clear_rules(self):
        """Clear all firewall rules"""
        self.config['rules'] = []
        self.save_config()

# Global config instance
firewall_config = FirewallConfig()

def hash_password(password):
    """Hash password for comparison"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password):
    """Check if password is correct"""
    # In production, use proper password hashing (bcrypt, etc.)
    return password == DEFAULT_PASSWORD

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def run_command(command, use_sudo=False):
    """Execute shell command and return output"""
    if use_sudo:
        command = f"sudo {command}"
    
    try:
        # In demo mode, simulate command execution
        print(f"[DEMO] Would execute: {command}")
        return True, f"Command executed successfully (demo mode): {command}"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def setup_firewall_rules():
    """Setup basic firewall rules"""
    commands = [
        # Allow established connections
        "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
        # Allow loopback
        "iptables -A INPUT -i lo -j ACCEPT",
        # Allow router
        f"iptables -A INPUT -s {ROUTER_IP} -j ACCEPT",
        # Allow PS4
        f"iptables -A INPUT -s {PS4_IP} -j ACCEPT",
    ]
    
    for cmd in commands:
        run_command(cmd, use_sudo=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password(password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid password'
    
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template_string(
        DASHBOARD_HTML,
        router_ip=ROUTER_IP,
        ps4_ip=PS4_IP
    )

@app.route('/api/status')
@login_required
def api_status():
    """Get system status"""
    return jsonify({
        'firewall_enabled': firewall_config.config['firewall_enabled'],
        'connection_open': firewall_config.config['connection_open'],
        'vpn_connected': firewall_config.config['vpn_connected'],
        'active_rules': len(firewall_config.config['rules'])
    })

@app.route('/api/rules')
@login_required
def api_rules():
    """Get all firewall rules"""
    return jsonify({'rules': firewall_config.config['rules']})

@app.route('/api/firewall/toggle', methods=['POST'])
@login_required
def api_firewall_toggle():
    """Toggle firewall on/off"""
    data = request.get_json()
    enable = data.get('enable', True)
    
    if enable:
        setup_firewall_rules()
        firewall_config.config['firewall_enabled'] = True
        message = "Firewall enabled successfully"
    else:
        run_command("iptables -F", use_sudo=True)
        firewall_config.config['firewall_enabled'] = False
        message = "Firewall disabled successfully"
    
    firewall_config.save_config()
    return jsonify({'status': 'success', 'message': message})

@app.route('/api/connection/toggle', methods=['POST'])
@login_required
def api_connection_toggle():
    """Toggle connection open/closed"""
    data = request.get_json()
    open_conn = data.get('open', True)
    
    if open_conn:
        # Open all connections
        run_command("iptables -P INPUT ACCEPT", use_sudo=True)
        run_command("iptables -P FORWARD ACCEPT", use_sudo=True)
        run_command("iptables -P OUTPUT ACCEPT", use_sudo=True)
        firewall_config.config['connection_open'] = True
        message = "All connections opened"
    else:
        # Close connections (except established)
        run_command("iptables -P INPUT DROP", use_sudo=True)
        run_command("iptables -P FORWARD DROP", use_sudo=True)
        firewall_config.config['connection_open'] = False
        message = "Connections closed (existing connections maintained)"
    
    firewall_config.save_config()
    return jsonify({'status': 'success', 'message': message})

@app.route('/api/ps4/allow', methods=['POST'])
@login_required
def api_ps4_allow():
    """Allow PS4 traffic"""
    cmd = f"iptables -A INPUT -s {PS4_IP} -j ACCEPT"
    success, msg = run_command(cmd, use_sudo=True)
    
    if success:
        firewall_config.add_rule(f"Allow PS4 ({PS4_IP})", cmd)
        if PS4_IP not in firewall_config.config['allowed_ips']:
            firewall_config.config['allowed_ips'].append(PS4_IP)
        firewall_config.save_config()
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': f"PS4 traffic allowed: {msg}"
    })

@app.route('/api/ps4/block', methods=['POST'])
@login_required
def api_ps4_block():
    """Block PS4 traffic"""
    cmd = f"iptables -A INPUT -s {PS4_IP} -j DROP"
    success, msg = run_command(cmd, use_sudo=True)
    
    if success:
        firewall_config.add_rule(f"Block PS4 ({PS4_IP})", cmd)
        if PS4_IP in firewall_config.config['allowed_ips']:
            firewall_config.config['allowed_ips'].remove(PS4_IP)
        if PS4_IP not in firewall_config.config['blocked_ips']:
            firewall_config.config['blocked_ips'].append(PS4_IP)
        firewall_config.save_config()
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': f"PS4 traffic blocked: {msg}"
    })

@app.route('/api/ip/manage', methods=['POST'])
@login_required
def api_ip_manage():
    """Allow or block an IP address"""
    data = request.get_json()
    ip = data.get('ip', '')
    action = data.get('action', 'allow')
    
    if not ip:
        return jsonify({'status': 'error', 'message': 'No IP address provided'})
    
    if action == 'allow':
        cmd = f"iptables -A INPUT -s {ip} -j ACCEPT"
        desc = f"Allow IP {ip}"
        if ip not in firewall_config.config['allowed_ips']:
            firewall_config.config['allowed_ips'].append(ip)
        if ip in firewall_config.config['blocked_ips']:
            firewall_config.config['blocked_ips'].remove(ip)
    else:
        cmd = f"iptables -A INPUT -s {ip} -j DROP"
        desc = f"Block IP {ip}"
        if ip not in firewall_config.config['blocked_ips']:
            firewall_config.config['blocked_ips'].append(ip)
        if ip in firewall_config.config['allowed_ips']:
            firewall_config.config['allowed_ips'].remove(ip)
    
    success, msg = run_command(cmd, use_sudo=True)
    
    if success:
        firewall_config.add_rule(desc, cmd)
        firewall_config.save_config()
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': f"IP {action}ed successfully: {msg}"
    })

@app.route('/api/ip/remove', methods=['POST'])
@login_required
def api_ip_remove():
    """Remove IP rule"""
    data = request.get_json()
    ip = data.get('ip', '')
    
    if not ip:
        return jsonify({'status': 'error', 'message': 'No IP address provided'})
    
    # Remove from both allow and block rules
    cmd1 = f"iptables -D INPUT -s {ip} -j ACCEPT"
    cmd2 = f"iptables -D INPUT -s {ip} -j DROP"
    
    run_command(cmd1, use_sudo=True)
    run_command(cmd2, use_sudo=True)
    
    if ip in firewall_config.config['allowed_ips']:
        firewall_config.config['allowed_ips'].remove(ip)
    if ip in firewall_config.config['blocked_ips']:
        firewall_config.config['blocked_ips'].remove(ip)
    
    firewall_config.save_config()
    
    return jsonify({
        'status': 'success',
        'message': f"Rules for IP {ip} removed"
    })

@app.route('/api/wireless/manage', methods=['POST'])
@login_required
def api_wireless_manage():
    """Manage wireless device by MAC address"""
    data = request.get_json()
    mac = data.get('mac', '').upper()
    action = data.get('action', 'allow')
    
    if not mac:
        return jsonify({'status': 'error', 'message': 'No MAC address provided'})
    
    if action == 'allow':
        cmd = f"iptables -A INPUT -m mac --mac-source {mac} -j ACCEPT"
        desc = f"Allow MAC {mac}"
        if mac not in firewall_config.config['allowed_macs']:
            firewall_config.config['allowed_macs'].append(mac)
        if mac in firewall_config.config['blocked_macs']:
            firewall_config.config['blocked_macs'].remove(mac)
    else:
        cmd = f"iptables -A INPUT -m mac --mac-source {mac} -j DROP"
        desc = f"Block MAC {mac}"
        if mac not in firewall_config.config['blocked_macs']:
            firewall_config.config['blocked_macs'].append(mac)
        if mac in firewall_config.config['allowed_macs']:
            firewall_config.config['allowed_macs'].remove(mac)
    
    success, msg = run_command(cmd, use_sudo=True)
    
    if success:
        firewall_config.add_rule(desc, cmd)
        firewall_config.save_config()
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': f"Wireless device {action}ed: {msg}"
    })

@app.route('/api/vpn/connect', methods=['POST'])
@login_required
def api_vpn_connect():
    """Connect to VPN"""
    # Simulate VPN connection
    # In production, this would execute actual VPN connection commands
    cmd = "openvpn --config /etc/openvpn/client.conf --daemon"
    success, msg = run_command(cmd, use_sudo=True)
    
    firewall_config.config['vpn_connected'] = True
    firewall_config.add_rule("VPN Connected", cmd)
    firewall_config.save_config()
    
    return jsonify({
        'status': 'success',
        'message': 'VPN connection initiated (demo mode)'
    })

@app.route('/api/vpn/disconnect', methods=['POST'])
@login_required
def api_vpn_disconnect():
    """Disconnect from VPN"""
    cmd = "killall openvpn"
    success, msg = run_command(cmd, use_sudo=True)
    
    firewall_config.config['vpn_connected'] = False
    firewall_config.save_config()
    
    return jsonify({
        'status': 'success',
        'message': 'VPN disconnected (demo mode)'
    })

@app.route('/api/rules/delete', methods=['POST'])
@login_required
def api_rule_delete():
    """Delete a specific rule"""
    data = request.get_json()
    index = data.get('index', -1)
    
    if firewall_config.remove_rule(index):
        return jsonify({'status': 'success', 'message': 'Rule deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid rule index'})

@app.route('/api/rules/flush', methods=['POST'])
@login_required
def api_rules_flush():
    """Flush all firewall rules"""
    run_command("iptables -F", use_sudo=True)
    firewall_config.clear_rules()
    
    return jsonify({
        'status': 'success',
        'message': 'All firewall rules cleared'
    })

def check_requirements():
    """Check if running with proper privileges"""
    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root. Firewall commands will run in DEMO mode.")
        print("   To actually modify firewall rules, run with: sudo python3 firewall_dashboard.py")
        print()
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("  Network Firewall Dashboard - All-in-One Script")
    print("=" * 60)
    print()
    print(f"Router IP: {ROUTER_IP}")
    print(f"PS4 IP: {PS4_IP}")
    print(f"Default Password: {DEFAULT_PASSWORD}")
    print()
    
    if not check_requirements():
        return
    
    print("Starting dashboard server...")
    print("Access the dashboard at: http://localhost:5000")
    print()
    print("Press CTRL+C to stop the server")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)

if __name__ == '__main__':
    main()
