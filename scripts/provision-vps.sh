#!/bin/bash

# VitaChain VPS Provisioning Script
# This script helps with the initial setup steps for DigitalOcean droplet creation

set -e

# Configuration
SSH_KEY_NAME="vitachain_do"
SSH_KEY_COMMENT="vitachain@vitachain.ma"
DROPLET_NAME="vitachain-vps"
DROPLET_SIZE="s-2vcpu-4gb"  # 2GB RAM, 1 CPU, 40GB SSD
DROPLET_REGION="ams3"  # Amsterdam (closest to Morocco)
DROPLET_IMAGE="ubuntu-24-04-x64"

echo "🚀 VitaChain VPS Provisioning Script"
echo "=================================="

# Step 1: Generate SSH key pair
echo ""
echo "Step 1: Generating SSH key pair..."
if [ ! -f "$HOME/.ssh/${SSH_KEY_NAME}" ]; then
    ssh-keygen -t ed25519 -C "${SSH_KEY_COMMENT}" -f "$HOME/.ssh/${SSH_KEY_NAME}" -N ""
    echo "✅ SSH key pair generated:"
    echo "   Private key: $HOME/.ssh/${SSH_KEY_NAME}"
    echo "   Public key:  $HOME/.ssh/${SSH_KEY_NAME}.pub"
else
    echo "ℹ️  SSH key already exists at $HOME/.ssh/${SSH_KEY_NAME}"
fi

# Display public key for copying
echo ""
echo "Public key (copy this for DigitalOcean):"
echo "========================================="
cat "$HOME/.ssh/${SSH_KEY_NAME}.pub"
echo "========================================="

# Step 2: DigitalOcean droplet creation instructions
echo ""
echo "Step 2: DigitalOcean Droplet Creation"
echo "======================================"
echo "Please follow these steps in the DigitalOcean console:"
echo ""
echo "1. Log in to your DigitalOcean dashboard"
echo "2. Click 'Create' → 'Droplets'"
echo "3. Choose region: ${DROPLET_REGION} (Amsterdam)"
echo "4. Select image: Ubuntu 24.04 LTS (x64)"
echo "5. Choose size: Basic - 2GB RAM / 1 CPU / 40GB SSD"
echo "6. Select authentication: SSH Key"
echo "7. Add the public key shown above"
echo "8. Hostname: ${DROPLET_NAME}"
echo "9. Click 'Create Droplet'"
echo "10. Wait for droplet creation (1-2 minutes)"
echo "11. Record the IP address when shown"
echo ""

# Step 3: Test SSH connection template
echo "Step 3: SSH Connection Test Template"
echo "===================================="
echo "Once the droplet is created, test SSH connection with:"
echo ""
echo "# Test as root (first time only)"
echo "ssh -i ~/.ssh/${SSH_KEY_NAME} root@<DROPLET_IP>"
echo ""
echo "# Replace <DROPLET_IP> with the actual IP address from DigitalOcean"
echo ""

# Step 4: Create SSH config entry
echo "Step 4: SSH Configuration (Optional)"
echo "==================================="
echo "Add this to your ~/.ssh/config for easier access:"
echo ""
echo "Host ${DROPLET_NAME}"
echo "    HostName <DROPLET_IP>"
echo "    User root"
echo "    IdentityFile ~/.ssh/${SSH_KEY_NAME}"
echo "    Port 22"
echo ""
echo "Then you can connect with: ssh ${DROPLET_NAME}"
echo ""

echo "✅ VPS provisioning preparation complete!"
echo "📝 Next steps:"
echo "   1. Create the droplet in DigitalOcean console"
echo "   2. Test SSH connection"
echo "   3. Run the system setup script"
