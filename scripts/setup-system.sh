#!/bin/bash

# VitaChain VPS System Setup Script
# This script configures the Ubuntu 24.04 VPS after initial SSH connection

set -e

# Configuration
HOSTNAME="vitachain-vps"
TIMEZONE="Africa/Casablanca"
NON_ROOT_USER="vitachain"

echo "🔧 VitaChain VPS System Setup"
echo "============================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo ./setup-system.sh"
    exit 1
fi

# Step 1: Update system packages
echo ""
echo "Step 1: Updating system packages..."
echo "=================================="
apt update
apt upgrade -y
apt autoremove -y
apt autoclean
echo "✅ System packages updated"

# Step 2: Configure timezone
echo ""
echo "Step 2: Configuring timezone..."
echo "==============================="
timedatectl set-timezone ${TIMEZONE}
echo "✅ Timezone set to ${TIMEZONE}"
timedatectl

# Step 3: Set hostname
echo ""
echo "Step 3: Setting hostname..."
echo "=========================="
hostnamectl set-hostname ${HOSTNAME}
echo "127.0.1.1 ${HOSTNAME}" >> /etc/hosts
echo "✅ Hostname set to ${HOSTNAME}"
hostname

# Step 4: Verify system resources
echo ""
echo "Step 4: System resource verification..."
echo "======================================"
echo "CPU info:"
lscpu | grep -E "(Model name|CPU\(s\)|Thread)"
echo ""
echo "Memory info:"
free -h
echo ""
echo "Disk space:"
df -h
echo ""

# Step 5: Install basic utilities
echo ""
echo "Step 5: Installing basic utilities..."
echo "===================================="
apt install -y curl wget git vim htop neofetch
echo "✅ Basic utilities installed"

# Step 6: Create non-root user
echo ""
echo "Step 6: Creating non-root user..."
echo "================================"
if ! id "${NON_ROOT_USER}" &>/dev/null; then
    adduser ${NON_ROOT_USER} --gecos "VitaChain User"
    usermod -aG sudo ${NON_ROOT_USER}
    echo "✅ User ${NON_ROOT_USER} created and added to sudo group"
else
    echo "ℹ️  User ${NON_ROOT_USER} already exists"
fi

# Step 7: Setup SSH for non-root user
echo ""
echo "Step 7: Setting up SSH for non-root user..."
echo "=========================================="
mkdir -p /home/${NON_ROOT_USER}/.ssh
cp /root/.ssh/authorized_keys /home/${NON_ROOT_USER}/.ssh/authorized_keys
chown -R ${NON_ROOT_USER}:${NON_ROOT_USER} /home/${NON_ROOT_USER}/.ssh
chmod 700 /home/${NON_ROOT_USER}/.ssh
chmod 600 /home/${NON_ROOT_USER}/.ssh/authorized_keys
echo "✅ SSH access configured for ${NON_ROOT_USER}"

# Step 8: Configure sudo access for Docker (pre-configuration)
echo ""
echo "Step 8: Pre-configuring Docker sudo access..."
echo "============================================"
echo "${NON_ROOT_USER} ALL=(ALL) NOPASSWD: /usr/bin/docker" >> /etc/sudoers.d/${NON_ROOT_USER}
echo "${NON_ROOT_USER} ALL=(ALL) NOPASSWD: /usr/bin/docker-compose" >> /etc/sudoers.d/${NON_ROOT_USER}
chmod 0440 /etc/sudoers.d/${NON_ROOT_USER}
echo "✅ Docker sudo access configured"

# Step 9: Verify sudoers configuration
echo ""
echo "Step 9: Verifying sudoers configuration..."
echo "========================================"
visudo -c
echo "✅ Sudoers configuration is valid"

echo ""
echo "🎉 System setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Test SSH login as ${NON_ROOT_USER}: ssh ${NON_ROOT_USER}@<IP>"
echo "   2. Run the firewall setup script"
echo "   3. Run the Docker installation script"
echo ""
echo "🔐 Security reminder:"
echo "   - Root SSH login will be disabled in security hardening step"
echo "   - Password authentication will be disabled"
echo "   - Only SSH key authentication will be allowed"
