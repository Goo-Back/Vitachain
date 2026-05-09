#!/bin/bash

# VitaChain VPS Security Hardening Script
# This script applies security hardening measures

set -e

# Configuration
SSH_CONFIG="/etc/ssh/sshd_config"
FAIL2BAN_CONFIG="/etc/fail2ban/jail.local"
NON_ROOT_USER="vitachain"

echo "🔒 VitaChain VPS Security Hardening"
echo "================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo ./security-harden.sh"
    exit 1
fi

# Step 1: Install Fail2Ban
echo ""
echo "Step 1: Installing Fail2Ban..."
echo "============================="
apt update
apt install -y fail2ban
systemctl start fail2ban
systemctl enable fail2ban
echo "✅ Fail2Ban installed and enabled"

# Step 2: Configure Fail2Ban for SSH
echo ""
echo "Step 2: Configuring Fail2Ban for SSH..."
echo "======================================"
# Create Fail2Ban local configuration
cp /etc/fail2ban/jail.conf ${FAIL2BAN_CONFIG}

# Update SSH jail settings
sed -i 's/enabled = false/enabled = true/' ${FAIL2BAN_CONFIG}
sed -i 's/port = ssh/port = 22/' ${FAIL2BAN_CONFIG}
sed -i 's/maxretry = 5/maxretry = 3/' ${FAIL2BAN_CONFIG}
sed -i 's/bantime = 10m/bantime = 3600/' ${FAIL2BAN_CONFIG}
sed -i 's/findtime = 10m/findtime = 600/' ${FAIL2BAN_CONFIG}

# Restart Fail2Ban
systemctl restart fail2ban
echo "✅ Fail2Ban configured for SSH protection"
echo "   - Max retry attempts: 3"
echo "   - Ban time: 1 hour"
echo "   - Find time: 10 minutes"

# Step 3: Enable automatic security updates
echo ""
echo "Step 3: Enabling automatic security updates..."
echo "=========================================="
apt install -y unattended-upgrades
# Configure automatic updates
echo "unattended-upgrades unattended-upgrades/enable_auto_updates boolean true" | debconf-set-selections
echo "unattended-upgrades unattended-upgrades/automatic_reboot boolean false" | debconf-set-selections

# Configure 50unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
// Automatically upgrade packages from these origins
Unattended-Upgrade::Origins-Pattern {
    "origin=Ubuntu,codename=${distro_codename}";
    "origin=Ubuntu,codename=${distro_codename}-security";
};

// Automatically reboot if necessary (disabled for safety)
Unattended-Upgrade::Automatic-Reboot "false";

// Send email notification (optional, requires mail setup)
// Unattended-Upgrade::Mail "admin@vitachain.ma";

// Remove dependencies that are no longer needed
Unattended-Upgrade::Remove-Unused-Dependencies "true";

// Automatically remove unused kernels
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";

// System upgrade on shutdown
Unattended-Upgrade::Automatic-Reboot-WithUsers "true";
EOF

dpkg-reconfigure -f noninteractive unattended-upgrades
echo "✅ Automatic security updates enabled"

# Step 4: SSH Security Configuration
echo ""
echo "Step 4: Hardening SSH configuration..."
echo "===================================="
# Backup original SSH config
cp ${SSH_CONFIG} ${SSH_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)

# Update SSH configuration
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' ${SSH_CONFIG}
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' ${SSH_CONFIG}
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' ${SSH_CONFIG}
sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' ${SSH_CONFIG}
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' ${SSH_CONFIG}
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' ${SSH_CONFIG}
sed -i 's/#PermitEmptyPasswords yes/PermitEmptyPasswords no/' ${SSH_CONFIG}
sed -i 's/PermitEmptyPasswords yes/PermitEmptyPasswords no/' ${SSH_CONFIG}

# Add additional security settings
cat >> ${SSH_CONFIG} << 'EOF'

# VitaChain Security Hardening
Protocol 2
MaxAuthTries 3
MaxSessions 2
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

# Test SSH configuration
echo "Testing SSH configuration..."
sshd -t
if [ $? -eq 0 ]; then
    echo "✅ SSH configuration is valid"
else
    echo "❌ SSH configuration has errors"
    echo "Restoring backup..."
    cp ${SSH_CONFIG}.backup.$(date +%Y%m%d_%H%M%S) ${SSH_CONFIG}
    exit 1
fi

# Restart SSH service
echo "Restarting SSH service..."
systemctl restart sshd
echo "✅ SSH service restarted with security hardening"

# Step 5: Verify Fail2Ban status
echo ""
echo "Step 5: Verifying Fail2Ban status..."
echo "===================================="
systemctl status fail2ban --no-pager -l
echo ""
echo "Fail2Ban SSH jail status:"
fail2ban-client status sshd
echo ""

# Step 6: Security verification
echo ""
echo "Step 6: Security verification..."
echo "=============================="
echo "Checking SSH security settings..."
echo "Root login: $(grep -i '^PermitRootLogin' ${SSH_CONFIG} | awk '{print $2}')"
echo "Password auth: $(grep -i '^PasswordAuthentication' ${SSH_CONFIG} | awk '{print $2}')"
echo "Empty passwords: $(grep -i '^PermitEmptyPasswords' ${SSH_CONFIG} | awk '{print $2}')"
echo ""

# Step 7: System security status
echo ""
echo "Step 7: System security status..."
echo "==============================="
echo "Active services:"
systemctl list-units --type=service --state=running | grep -E "(ssh|docker|fail2ban|ufw)" | awk '{print "  - " $1 " (" $4 ")"}'
echo ""

echo "Firewall status:"
ufw status | head -10
echo ""

echo "Failed login attempts (last 10):"
grep "Failed password" /var/log/auth.log | tail -5 | awk '{print "  - " $0}' || echo "  No failed attempts found"
echo ""

# Step 8: Create security monitoring script
echo ""
echo "Step 8: Creating security monitoring script..."
echo "=============================================="
cat > /usr/local/bin/security-monitor.sh << 'EOF'
#!/bin/bash

# VitaChain Security Monitoring Script
echo "🔒 VitaChain Security Status - $(date)"
echo "====================================="

# Check Fail2Ban status
echo "Fail2Ban Status:"
systemctl is-active fail2ban && echo "  ✅ Running" || echo "  ❌ Stopped"
echo "  Banned IPs: $(fail2ban-client status sshd | grep -o 'IP list:.*' | cut -d':' -f2 | wc -w)"

# Check SSH security
echo ""
echo "SSH Security:"
echo "  Root login: $(grep '^PermitRootLogin' /etc/ssh/sshd_config | awk '{print $2}')"
echo "  Password auth: $(grep '^PasswordAuthentication' /etc/ssh/sshd_config | awk '{print $2}')"

# Check firewall
echo ""
echo "Firewall Status:"
ufw status | grep -E "(Status|Active)" | head -2

# Check recent failed attempts
echo ""
echo "Recent Security Events:"
echo "  Failed logins (last hour): $(grep "$(date '+%b %d')" /var/log/auth.log | grep -c 'Failed password' || echo 0)"
echo "  SSH connections (last hour): $(grep "$(date '+%b %d')" /var/log/auth.log | grep -c 'Accepted' || echo 0)"

echo ""
EOF

chmod +x /usr/local/bin/security-monitor.sh
echo "✅ Security monitoring script created at /usr/local/bin/security-monitor.sh"

echo ""
echo "🔒 Security hardening complete!"
echo ""
echo "🛡️ Security measures applied:"
echo "   ✅ Fail2Ban installed and configured for SSH"
echo "   ✅ Automatic security updates enabled"
echo "   ✅ Root SSH login disabled"
echo "   ✅ Password authentication disabled"
echo "   ✅ SSH security parameters tightened"
echo "   ✅ Security monitoring script created"
echo ""
echo "⚠️  Important security notes:"
echo "   - Root login via SSH is now disabled"
echo "   - Password authentication is disabled"
echo "   - Only SSH key authentication is allowed"
echo "   - Failed login attempts will be blocked after 3 tries"
echo "   - Security updates will be installed automatically"
echo ""
echo "📋 Next steps:"
echo "   1. Test SSH login as ${NON_ROOT_USER}: ssh ${NON_ROOT_USER}@<IP>"
echo "   2. Verify root login is disabled (should fail)"
echo "   3. Run verification script"
echo "   4. Document connection details"
echo ""
echo "🔍 Security monitoring:"
echo "   Run: /usr/local/bin/security-monitor.sh"
echo "   Check logs: tail -f /var/log/auth.log"
