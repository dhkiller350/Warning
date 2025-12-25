# Network Firewall Dashboard

A comprehensive all-in-one Python script for managing network firewall rules with a beautiful web-based dashboard. Designed for Ubuntu Caine to control IP addresses, manage router and device connections, and provide VPN support.

## Features

### 🛡️ Firewall Management
- **IP Address Control**: Allow or block specific IP addresses
- **MAC Address Filtering**: Control wireless devices by MAC address
- **Connection States**: Toggle between open and closed connection states
- **Real-time Monitoring**: View active firewall rules in real-time

### 🎮 Device Management
- **Router Control**: Manage access to personal WiFi router (10.0.0.1)
- **PS4 Management**: Quick controls for PS4 device (10.0.0.5)
- **Wireless Connections**: Control wireless device access through MAC filtering

### 🔒 Security Features
- **Password Protection**: Secure login system for dashboard access
- **Session Management**: Secure session handling
- **Rule Persistence**: Firewall rules saved across restarts

### 🌐 VPN Support
- **VPN Connection**: Connect/disconnect VPN with one click
- **Status Monitoring**: Real-time VPN connection status

### 📊 Dashboard Interface
- **Beautiful UI**: Modern, responsive web interface
- **Real-time Updates**: Auto-refresh system status every 5 seconds
- **Activity Log**: Track all firewall operations
- **Quick Actions**: One-click controls for common operations

## Network Configuration

```
Router IP:      10.0.0.1
PS4 IP (Wired): 10.0.0.5
Wireless:       Managed via MAC address filtering
```

## Requirements

- **Operating System**: Ubuntu (tested on Ubuntu Caine)
- **Python**: 3.7 or higher
- **Privileges**: Root access for firewall modifications
- **Dependencies**: Flask, Werkzeug (installed via requirements.txt)

## Installation

### 1. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

Or manually:

```bash
pip3 install Flask==3.0.0 Werkzeug==3.0.1
```

### 2. Make Script Executable

```bash
chmod +x firewall_dashboard.py
```

## Usage

### Starting the Dashboard

#### Demo Mode (No root required)
```bash
python3 firewall_dashboard.py
```

#### Full Mode (With firewall control)
```bash
sudo python3 firewall_dashboard.py
```

### Accessing the Dashboard

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. Login with default password: `admin123`

**⚠️ IMPORTANT**: Change the default password in the script before deploying!

## Dashboard Features

### Main Dashboard Sections

#### 1. System Status
- View firewall status
- Monitor router and PS4 connectivity
- Check connection state (Open/Closed)
- VPN connection status
- Count of active firewall rules

#### 2. Quick Actions
- **Enable/Disable Firewall**: Toggle firewall on/off
- **Open/Close Connection**: Control connection state
- **PS4 Controls**: Allow or block PS4 traffic
- **VPN Controls**: Connect or disconnect VPN

#### 3. IP Address Management
- Add IP addresses to allow list
- Block specific IP addresses
- Remove IP rules
- Supports any IP in the 10.0.0.0/24 subnet

#### 4. Wireless Connection Control
- Manage wireless devices by MAC address
- Allow or block specific wireless devices
- Useful for controlling which devices can connect

#### 5. Active Firewall Rules
- View all active firewall rules
- Delete individual rules
- Clear all rules at once
- Rules persist across dashboard restarts

#### 6. Activity Log
- Real-time log of all operations
- Timestamps for each action
- Keep track of last 10 activities

## Configuration

### Changing Default Settings

Edit the configuration section in `firewall_dashboard.py`:

```python
# Configuration
ROUTER_IP = "10.0.0.1"          # Your router IP
PS4_IP = "10.0.0.5"             # Your PS4 IP
CONFIG_FILE = "/tmp/firewall_config.json"  # Config storage
DEFAULT_PASSWORD = "admin123"    # Change this!
```

### Security Recommendations

1. **Change Default Password**: Modify `DEFAULT_PASSWORD` in the script
2. **Use HTTPS**: In production, use HTTPS with proper SSL certificates
3. **Restrict Access**: Only allow trusted IPs to access the dashboard
4. **Regular Backups**: Backup your firewall configuration regularly

## How It Works

### Firewall Rules (iptables)

The dashboard uses `iptables` to manage firewall rules:

- **Allow Rules**: `iptables -A INPUT -s <IP> -j ACCEPT`
- **Block Rules**: `iptables -A INPUT -s <IP> -j DROP`
- **MAC Filtering**: `iptables -A INPUT -m mac --mac-source <MAC> -j ACCEPT`

### Connection States

- **Open**: All connections allowed (INPUT, FORWARD, OUTPUT = ACCEPT)
- **Closed**: New connections blocked, existing maintained (INPUT, FORWARD = DROP)

### Configuration Storage

All settings are stored in `/tmp/firewall_config.json`:
- Firewall state
- Connection state
- Active rules
- Allowed/blocked IPs
- Allowed/blocked MAC addresses
- VPN status

## Common Use Cases

### 1. Block a Wireless Device
1. Find the device's MAC address
2. Go to "Wireless Connection Control"
3. Enter MAC address
4. Select "Block"
5. Click "Apply Rule"

### 2. Allow Only Specific IPs
1. Go to Quick Actions
2. Click "Close Connection"
3. Go to IP Management
4. Add allowed IPs one by one
5. Select "Allow" and click "Apply Rule"

### 3. Temporary PS4 Access
1. Click "Allow PS4 Traffic" in Quick Actions
2. When done, click "Block PS4 Traffic"

### 4. Emergency: Clear All Rules
1. Scroll to "Active Firewall Rules"
2. Click "Clear All Rules"
3. Confirm the action

## Troubleshooting

### Dashboard Won't Start
- Check if port 5000 is already in use
- Ensure Flask is installed: `pip3 list | grep Flask`
- Check Python version: `python3 --version`

### Can't Modify Firewall Rules
- Make sure you're running with `sudo`
- Check if iptables is installed: `which iptables`
- Verify you have root privileges: `id -u` (should return 0)

### Can't Login
- Default password is `admin123`
- Check browser console for errors
- Clear browser cookies and try again

### Rules Not Persisting
- Check permissions on `/tmp/firewall_config.json`
- Ensure the script has write access
- Check disk space: `df -h /tmp`

## Demo Mode

When running without root privileges, the dashboard operates in DEMO mode:
- All firewall commands are simulated
- Configuration changes are saved
- UI fully functional
- No actual firewall modifications

This is useful for:
- Testing the interface
- Training purposes
- Development and debugging

## Security Warning

⚠️ **IMPORTANT SECURITY CONSIDERATIONS**:

1. This script manages your system firewall
2. Incorrect configuration can lock you out of your system
3. Always test rules before deploying in production
4. Keep a backup of your working firewall configuration
5. Only allow trusted users to access the dashboard
6. Change the default password immediately
7. Consider using SSL/TLS for the web interface
8. Monitor the activity log regularly

## VPN Configuration

For VPN functionality to work in full mode:

1. Install OpenVPN: `sudo apt-get install openvpn`
2. Place your VPN configuration at: `/etc/openvpn/client.conf`
3. Configure credentials if needed
4. Test manually first: `sudo openvpn --config /etc/openvpn/client.conf`

## Advanced Usage

### Custom Port
Edit the last line in the script:
```python
app.run(host='0.0.0.0', port=8080, debug=False)  # Change port to 8080
```

### Remote Access
The dashboard listens on all interfaces (`0.0.0.0`), so you can access it from other devices on your network:
```
http://<your-ubuntu-ip>:5000
```

**Security Warning**: Ensure your firewall only allows trusted IPs to access port 5000!

### Persistent Service

To run as a systemd service:

1. Create `/etc/systemd/system/firewall-dashboard.service`:
```ini
[Unit]
Description=Network Firewall Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/firewall_dashboard.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl enable firewall-dashboard
sudo systemctl start firewall-dashboard
```

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or contributions, please refer to the repository documentation.

## Changelog

### Version 1.0.0
- Initial release
- Complete firewall management
- Web-based dashboard
- IP and MAC filtering
- VPN support
- Password protection
- Configuration persistence
- Activity logging
