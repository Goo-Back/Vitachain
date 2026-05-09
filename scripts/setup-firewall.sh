#!/bin/bash

# VitaChain VPS Firewall Setup Script
# This script configures UFW firewall with comprehensive security hardening

set -e

# Configuration
SSH_PORT=22
HTTP_PORT=80
HTTPS_PORT=443
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔥 VitaChain VPS Firewall Setup with Security Hardening"
echo "======================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo ./setup-firewall.sh"
    exit 1
fi

# Step 1: Install UFW and security tools
echo ""
echo "Step 1: Installing UFW firewall and security tools..."
echo "===================================================="
apt update
apt install -y ufw fail2ban logwatch rkhunter chkrootkit
echo "✅ UFW and security tools installed"

# Step 2: SSH Hardening
echo ""
echo "Step 2: Hardening SSH configuration..."
echo "======================================"
SSH_CONFIG="/etc/ssh/sshd_config"

# Backup original SSH config
cp $SSH_CONFIG $SSH_CONFIG.backup.$(date +%Y%m%d)

# SSH security configurations
sed -i 's/#Port 22/Port 22/' $SSH_CONFIG
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' $SSH_CONFIG
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' $SSH_CONFIG
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' $SSH_CONFIG
sed -i 's/#PermitEmptyPasswords yes/PermitEmptyPasswords no/' $SSH_CONFIG
sed -i 's/#X11Forwarding yes/X11Forwarding no/' $SSH_CONFIG
sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' $SSH_CONFIG
sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 300/' $SSH_CONFIG
sed -i 's/#ClientAliveCountMax 3/ClientAliveCountMax 2/' $SSH_CONFIG

# Add additional SSH security settings
cat >> $SSH_CONFIG << 'EOF'

# Additional security hardening
Protocol 2
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group-exchange-sha256
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com
IgnoreRhosts yes
HostbasedAuthentication no
Banner /etc/ssh/banner.txt
EOF

# Create SSH banner
cat > /etc/ssh/banner.txt << 'EOF'
***************************************************************************
                            AUTHORIZED ACCESS ONLY
***************************************************************************
This system is for authorized users only. Individual use of this system
and/or network without authority, or in excess of your authority, is
strictly prohibited and may be punishable under applicable laws.
Unauthorized access is monitored and will be prosecuted.
***************************************************************************

EOF

# Restart SSH service
systemctl restart sshd
echo "✅ SSH configuration hardened"

# Step 3: Set default firewall policies
echo ""
echo "Step 3: Setting default firewall policies..."
echo "=========================================="
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw default deny forwarded
echo "✅ Default policies configured (deny incoming, allow outgoing, deny forwarded)"

# Step 4: Configure rate limiting for SSH
echo ""
echo "Step 4: Configuring SSH rate limiting..."
echo "======================================="
ufw limit ${SSH_PORT}/tcp comment 'SSH with rate limiting'
echo "✅ SSH rate limiting configured (max 6 connections per 30 seconds)"

# Step 5: Allow web traffic
echo ""
echo "Step 5: Allowing web traffic..."
echo "=============================="
ufw allow ${HTTP_PORT}/tcp comment 'HTTP'
ufw allow ${HTTPS_PORT}/tcp comment 'HTTPS'
echo "✅ HTTP and HTTPS ports allowed"

# Step 6: Block common attack patterns
echo ""
echo "Step 6: Blocking common attack patterns..."
echo "========================================="
# Block common attack ports
ufw deny 23/tcp comment 'Block Telnet'
ufw deny 135/tcp comment 'Block RPC'
ufw deny 137:139/tcp comment 'Block NetBIOS'
ufw deny 445/tcp comment 'Block SMB'
ufw deny 1433/tcp comment 'Block SQL Server'
ufw deny 3389/tcp comment 'Block RDP'
ufw deny 5432/tcp comment 'Block PostgreSQL'
ufw deny 6379/tcp comment 'Block Redis'

# Block IP ranges known for attacks
ufw deny from 0.0.0.0/8 comment 'Block invalid IPs'
ufw deny from 127.0.0.0/8 comment 'Block loopback'
ufw deny from 169.254.0.0/16 comment 'Block link-local'
ufw deny from 192.0.2.0/24 comment 'Block test network'
ufw deny from 224.0.0.0/4 comment 'Block multicast'

echo "✅ Common attack patterns blocked"

# Step 7: Configure logging
echo ""
echo "Step 7: Configuring firewall logging..."
echo "====================================="
ufw logging on
ufw logging medium
echo "✅ Firewall logging enabled (medium level)"

# Step 8: Setup Fail2Ban
echo ""
echo "Step 8: Configuring Fail2Ban..."
echo "==============================="
# Create Fail2Ban configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd
destemail = admin@vitachain.ma
sender = fail2ban@vitachain.ma
mta = sendmail
protocol = tcp
chain = INPUT
action = %(action_mw)s

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 600

[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400
EOF

# Create nginx filter for Fail2Ban
cat > /etc/fail2ban/filter.d/nginx-noscript.conf << 'EOF'
[Definition]
failregex = ^<HOST> -.*GET.*(\.php|\.asp|\.exe|\.pl|\.cgi|\.scgi).* HTTP.*$
ignoreregex =
EOF

# Start Fail2Ban
systemctl enable fail2ban
systemctl restart fail2ban
echo "✅ Fail2Ban configured and started"

# Step 9: Enable UFW
echo ""
echo "Step 9: Enabling UFW firewall..."
echo "=============================="
# Warning about SSH connection
echo "⚠️  WARNING: Enabling firewall may disconnect your current SSH session"
echo "   Make sure you have console access or can reconnect if needed"
echo "   SSH rate limiting is configured to prevent accidental lockout"
echo ""
read -p "Continue enabling UFW? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ufw --force enable
    echo "✅ UFW firewall enabled"
else
    echo "❌ UFW not enabled. Firewall setup aborted."
    exit 1
fi

# Step 10: Setup security monitoring
echo ""
echo "Step 10: Setting up security monitoring..."
echo "========================================"
# Create security monitoring script
cat > $PROJECT_DIR/scripts/security-monitor.sh << 'EOF'
#!/bin/bash
# Security Monitoring Script for VitaChain

LOG_FILE="/var/log/security-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log events
log_event() {
    echo "[$DATE] $1" >> $LOG_FILE
}

# Check for suspicious SSH activity
check_ssh_activity() {
    SUSPICIOUS_LOGINS=$(grep "Invalid user\|Failed password" /var/log/auth.log | grep "$(date '+%b %d')" | wc -l)
    if [ $SUSPICIOUS_LOGINS -gt 10 ]; then
        log_event "WARNING: High number of failed SSH attempts: $SUSPICIOUS_LOGINS"
    fi
}

# Check for firewall blocks
check_firewall_blocks() {
    BLOCKED_CONNECTIONS=$(ufw status | grep "DENY" | wc -l)
    if [ $BLOCKED_CONNECTIONS -gt 0 ]; then
        log_event "INFO: $BLOCKED_CONNECTIONS connections blocked by firewall"
    fi
}

# Check Fail2Ban status
check_fail2ban() {
    BANNED_IPS=$(fail2ban-client status sshd | grep "Currently banned:" | awk '{print $4}')
    if [ -n "$BANNED_IPS" ]; then
        log_event "INFO: $BANNED_IPS IPs currently banned by Fail2Ban"
    fi
}

# Check disk space
check_disk_space() {
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        log_event "WARNING: Disk usage at ${DISK_USAGE}%"
    fi
}

# Run all checks
check_ssh_activity
check_firewall_blocks
check_fail2ban
check_disk_space

echo "Security monitoring completed - check $LOG_FILE for details"
EOF

chmod +x $PROJECT_DIR/scripts/security-monitor.sh

# Add to crontab for hourly monitoring
CRON_JOB="0 * * * * $PROJECT_DIR/scripts/security-monitor.sh"
(crontab -l 2>/dev/null | grep -v "security-monitor"; echo "$CRON_JOB") | crontab -

echo "✅ Security monitoring configured"

# Step 11: Verify firewall status
echo ""
echo "Step 11: Verifying firewall status..."
echo "===================================="
ufw status verbose
echo ""

# Step 12: Show active rules
echo ""
echo "Step 12: Active firewall rules..."
echo "==============================="
ufw status numbered
echo ""

# Step 13: Test connectivity
echo ""
echo "Step 13: Connectivity test..."
echo "============================"
echo "Testing if current SSH connection will remain active..."
if ufw status | grep -q "${SSH_PORT}/tcp.*LIMIT.*Anywhere"; then
    echo "✅ SSH port ${SSH_PORT} is properly allowed with rate limiting"
else
    echo "❌ SSH port ${SSH_PORT} is not properly allowed"
    exit 1
fi

# Test Fail2Ban
if systemctl is-active --quiet fail2ban; then
    echo "✅ Fail2Ban is running"
else
    echo "❌ Fail2Ban is not running"
    exit 1
fi

echo ""
echo "🔥 Firewall setup complete!"
echo ""
echo "📝 Current firewall configuration:"
echo "   - SSH (port ${SSH_PORT}): ALLOWED with rate limiting"
echo "   - HTTP (port ${HTTP_PORT}): ALLOWED"
echo "   - HTTPS (port ${HTTPS_PORT}): ALLOWED"
echo "   - Common attack ports: BLOCKED"
echo "   - Suspicious IP ranges: BLOCKED"
echo "   - All other incoming: DENIED"
echo ""
echo "🔐 Security features enabled:"
echo "   ✅ UFW firewall with comprehensive rules"
echo "   ✅ SSH hardening (no root login, key-based auth only)"
echo "   ✅ Fail2Ban with SSH and NGINX protection"
echo "   ✅ Rate limiting to prevent brute force attacks"
echo "   ✅ Security monitoring with hourly checks"
echo "   ✅ Comprehensive logging and alerting"
echo ""
echo "📋 Next steps:"
echo "   1. Test SSH connectivity with key-based authentication"
echo "   2. Verify web application functionality"
echo "   3. Run security monitoring script manually"
echo "   4. Check logs: /var/log/security-monitor.log"
echo "   5. Review Fail2Ban logs: /var/log/fail2ban.log"
echo ""
echo "⚠️  IMPORTANT: Ensure you have SSH key access before logging out!"
