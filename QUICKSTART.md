# Quick Start Guide - Network Firewall Dashboard

Get started with the Network Firewall Dashboard in 3 simple steps!

## Prerequisites

- Ubuntu system (tested on Ubuntu Caine)
- Python 3.7 or higher
- Root/sudo access for actual firewall control

## Installation (3 Steps)

### Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 2: Make Script Executable

```bash
chmod +x firewall_dashboard.py
```

### Step 3: Run the Dashboard

**Demo Mode (No root needed - for testing):**
```bash
python3 firewall_dashboard.py
```

**Full Mode (With firewall control - requires root):**
```bash
sudo python3 firewall_dashboard.py
```

## Accessing the Dashboard

1. Open your web browser
2. Go to: **http://localhost:5000**
3. Login with password: **admin123**

⚠️ **IMPORTANT**: Change the default password in `firewall_dashboard.py` before using in production!

## Quick Tour

### System Status Card
- View current firewall status
- Monitor router (10.0.0.1) and PS4 (10.0.0.5) connectivity
- Check connection state and VPN status

### Quick Actions
- **Enable/Disable Firewall**: Toggle firewall protection
- **Open/Close Connection**: Control network access
- **PS4 Controls**: Manage PS4 device access
- **VPN Controls**: Connect/disconnect VPN

### IP Address Management
Add an IP to allow/block list:
1. Enter IP address (e.g., 10.0.0.100)
2. Select "Allow" or "Block"
3. Click "Apply Rule"

### Wireless Control
Manage wireless devices by MAC address:
1. Enter MAC address (e.g., AA:BB:CC:DD:EE:FF)
2. Select "Allow" or "Block"
3. Click "Apply Rule"

## Common Tasks

### Block a Device by IP
1. Go to **IP Address Management**
2. Enter the IP address
3. Select **Block**
4. Click **Apply Rule**

### Allow PS4 Traffic
1. Go to **Quick Actions**
2. Click **Allow PS4 Traffic**
3. Check **Activity Log** to confirm

### Close All Connections (Emergency)
1. Go to **Quick Actions**
2. Click **Close Connection**
3. All new connections will be blocked

### View Active Rules
Scroll down to **Active Firewall Rules** section to see all current rules with timestamps.

## Configuration

Your settings are saved in: `~/.config/firewall-dashboard/`

This includes:
- Firewall rules
- Allowed/blocked IPs
- Allowed/blocked MAC addresses
- Connection state
- VPN status

## Network Setup

```
┌─────────────────────────────────────┐
│  Router: 10.0.0.1 (WiFi Router)     │
│  PS4:    10.0.0.5 (Wired)           │
│  Other:  10.0.0.x (Wireless)        │
└─────────────────────────────────────┘
```

## Demo vs Full Mode

### Demo Mode (Without sudo)
- ✅ Full dashboard functionality
- ✅ Configuration saved
- ✅ UI testing
- ❌ No actual firewall changes

### Full Mode (With sudo)
- ✅ All features
- ✅ Real firewall control
- ✅ Actual iptables modifications
- ⚠️ Changes affect your system

## Security Notes

1. **Change Default Password**: Edit the script and change `DEFAULT_PASSWORD`
2. **Restrict Access**: Use firewall rules to limit dashboard access
3. **Monitor Activity**: Check the Activity Log regularly
4. **Backup Rules**: Save your working configuration

## Troubleshooting

### Can't Login
- Default password is `admin123`
- Check browser cookies
- Try incognito/private mode

### Server Won't Start
- Check if port 5000 is available: `lsof -i :5000`
- Verify Flask is installed: `pip3 list | grep Flask`
- Check Python version: `python3 --version`

### Rules Not Working
- Are you running with sudo?
- Check system logs for errors
- Verify iptables is installed: `which iptables`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure VPN settings for your OpenVPN setup
- Customize router and PS4 IP addresses if different
- Set up as a systemd service for automatic startup

## Support

For more information, refer to the comprehensive README.md documentation.

## Security Warning

⚠️ This script controls your system firewall. Incorrect configuration can lock you out. Always test in demo mode first!

---

**Enjoy your new Network Firewall Dashboard! 🛡️**
