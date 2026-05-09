# VPS Setup Guide - VitaChain Infrastructure

**Project:** VitaChain v2.0
**Infrastructure:** DigitalOcean VPS
**OS:** Ubuntu 24.04 LTS
**Last Updated:** 2026-05-01

---

## Overview

This document provides step-by-step instructions for provisioning and configuring the DigitalOcean VPS for the VitaChain platform.

---

## Prerequisites

- DigitalOcean account with API access
- SSH key pair generated locally
- DigitalOcean API key (optional, for automation)
- Basic knowledge of Linux command line

---

## Step 1: Provision DigitalOcean Droplet

### 1.1 Create SSH Key (if not exists)

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "vitachain@vitachain.ma" -f ~/.ssh/vitachain_do

# Copy public key
cat ~/.ssh/vitachain_do.pub
```

### 1.2 Create Droplet via DigitalOcean Console

1. Log in to DigitalOcean dashboard
2. Click "Create" → "Droplets"
3. Choose region: **Amsterdam (AMS3)** or **Frankfurt (FRA1)** for Morocco proximity
4. Select image: **Ubuntu 24.04 LTS (x64)**
5. Choose size: **Basic - 2GB RAM / 1 CPU / 40GB SSD** (minimum for MVP)
6. Select authentication: **SSH Key**
7. Add your SSH public key
8. Hostname: `vitachain-vps`
9. Click "Create Droplet"
10. Wait for droplet creation (1-2 minutes)
11. Record the **IP address** (e.g., `164.90.123.45`)

### 1.3 Verify Droplet Creation

```bash
# Test SSH connection as root
ssh -i ~/.ssh/vitachain_do root@<DROPLET_IP>

# Example:
ssh -i ~/.ssh/vitachain_do root@164.90.123.45
```

---

## Step 2: Initial Server Setup

### 2.1 Connect to VPS

```bash
ssh -i ~/.ssh/vitachain_do root@<DROPLET_IP>
```

### 2.2 Update System

```bash
# Update package index
apt update

# Upgrade all packages
apt upgrade -y

# Remove unnecessary packages
apt autoremove -y

# Clean package cache
apt autoclean
```

### 2.3 Configure Timezone

```bash
# Set timezone to Africa/Casablanca
timedatectl set-timezone Africa/Casablanca

# Verify timezone
timedatectl
```

### 2.4 Set Hostname

```bash
# Set hostname
hostnamectl set-hostname vitachain-vps

# Update /etc/hosts
echo "127.0.1.1 vitachain-vps" >> /etc/hosts

# Verify hostname
hostname
```

### 2.5 Verify System Resources

```bash
# Check CPU
lscpu

# Check RAM
free -h

# Check disk space
df -h

# Check system info
neofetch  # Install if needed: apt install neofetch -y
```

---

## Step 3: Create Non-Root User

### 3.1 Create User

```bash
# Create user 'vitachain'
adduser vitachain

# Add user to sudo group
usermod -aG sudo vitachain

# Verify user was created
id vitachain
```

### 3.2 Configure Sudo Access

```bash
# Allow sudo without password for Docker commands
echo "vitachain ALL=(ALL) NOPASSWD: /usr/bin/docker" >> /etc/sudoers.d/vitachain
echo "vitachain ALL=(ALL) NOPASSWD: /usr/bin/docker-compose" >> /etc/sudoers.d/vitachain

# Set correct permissions
chmod 0440 /etc/sudoers.d/vitachain

# Verify sudoers file
visudo -c
```

### 3.3 Setup SSH for Non-Root User

```bash
# Create .ssh directory for vitachain user
mkdir -p /home/vitachain/.ssh

# Copy root's authorized_keys to vitachain user
cp /root/.ssh/authorized_keys /home/vitachain/.ssh/authorized_keys

# Set correct ownership
chown -R vitachain:vitachain /home/vitachain/.ssh

# Set correct permissions
chmod 700 /home/vitachain/.ssh
chmod 600 /home/vitachain/.ssh/authorized_keys
```

### 3.4 Test SSH Login as Non-Root User

```bash
# From your local machine
ssh -i ~/.ssh/vitachain_do vitachain@<DROPLET_IP>

# Test sudo access
sudo docker --version
```

---

## Step 4: Configure UFW Firewall

### 4.1 Install UFW

```bash
# Install UFW (usually pre-installed)
apt install ufw -y
```

### 4.2 Configure Firewall Rules

```bash
# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (port 22)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP (port 80)
ufw allow 80/tcp comment 'HTTP'

# Allow HTTPS (port 443)
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
ufw enable

# Verify status
ufw status verbose
```

### 4.3 Expected Output

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere                   # SSH
80/tcp                     ALLOW       Anywhere                   # HTTP
443/tcp                    ALLOW       Anywhere                   # HTTPS
22/tcp (v6)                ALLOW       Anywhere (v6)              # SSH
80/tcp (v6)                ALLOW       Anywhere (v6)              # HTTP
443/tcp (v6)               ALLOW       Anywhere (v6)              # HTTPS
```

---

## Step 5: Disable Root SSH Login

### 5.1 Configure SSH

```bash
# Edit SSH config
nano /etc/ssh/sshd_config
```

### 5.2 Update SSH Configuration

Find and modify these lines:

```
# Disable root login
PermitRootLogin no

# Disable password authentication (key-based only)
PasswordAuthentication no

# Disable empty passwords
PermitEmptyPasswords no
```

### 5.3 Restart SSH Service

```bash
# Restart SSH
systemctl restart sshd

# Verify SSH is running
systemctl status sshd
```

### 5.4 Test SSH Configuration

```bash
# From your local machine, test as non-root user
ssh -i ~/.ssh/vitachain_do vitachain@<DROPLET_IP>

# Try to login as root (should fail)
ssh -i ~/.ssh/vitachain_do root@<DROPLET_IP>
# Expected: Permission denied (publickey)
```

---

## Step 6: Install Docker

### 6.1 Prerequisites

```bash
# Install dependencies
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

### 6.2 Add Docker's Official GPG Key

```bash
# Create keyrings directory
mkdir -p /etc/apt/keyrings

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set permissions
chmod a+r /etc/apt/keyrings/docker.gpg
```

### 6.3 Add Docker Repository

```bash
# Add repository to APT sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 6.4 Install Docker Engine

```bash
# Update package index
apt update

# Install Docker Engine
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
systemctl start docker

# Enable Docker to start on boot
systemctl enable docker
```

### 6.5 Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker info
docker info

# Test Docker with hello-world
docker run hello-world

# Expected output: Hello from Docker!
```

### 6.6 Add Non-Root User to Docker Group

```bash
# Add vitachain user to docker group
usermod -aG docker vitachain

# Verify group membership
groups vitachain

# Test Docker without sudo (logout and login first)
exit
ssh -i ~/.ssh/vitachain_do vitachain@<DROPLET_IP>
docker run hello-world
```

---

## Step 7: Install Docker Compose

### 7.1 Download Docker Compose

```bash
# Download latest Docker Compose v2
curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose

# Set executable permissions
chmod +x /usr/local/bin/docker-compose

# Create symbolic link
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### 7.2 Verify Docker Compose Installation

```bash
# Check version
docker-compose --version

# Expected output: Docker Compose version v2.24.5
```

### 7.3 Test Docker Compose

```bash
# Create test directory
mkdir -p ~/test-compose
cd ~/test-compose

# Create docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  test:
    image: alpine
    command: echo "Docker Compose is working!"
EOF

# Run test
docker-compose up

# Expected output: test_1  | Docker Compose is working!

# Cleanup
cd ~
rm -rf ~/test-compose
```

---

## Step 8: Security Hardening

### 8.1 Install Fail2Ban

```bash
# Install fail2ban
apt install fail2ban -y

# Start fail2ban
systemctl start fail2ban

# Enable fail2ban on boot
systemctl enable fail2ban

# Check status
systemctl status fail2ban
```

### 8.2 Configure Fail2Ban for SSH

```bash
# Create local configuration
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit configuration
nano /etc/fail2ban/jail.local
```

Add/modify these settings:

```
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

Restart fail2ban:

```bash
systemctl restart fail2ban
```

### 8.3 Configure Automatic Security Updates

```bash
# Install unattended-upgrades
apt install unattended-upgrades -y

# Configure automatic updates
dpkg-reconfigure -plow unattended-upgrades
```

Select "Yes" for automatic security updates.

### 8.4 Verify All Services

```bash
# Check Docker
systemctl status docker

# Check fail2ban
systemctl status fail2ban

# Check UFW
ufw status

# Check disk space
df -h

# Check memory
free -h
```

---

## Step 9: Documentation

### 9.1 Record Connection Details

Store these details securely (use password manager):

```
VPS IP Address: <DROPLET_IP>
SSH User: vitachain
SSH Key: ~/.ssh/vitachain_do
Hostname: vitachain-vps
Region: AMS3 or FRA1
Droplet ID: <DROPLET_ID>
```

### 9.2 Create Connection Alias (Optional)

Add to your local `~/.ssh/config`:

```
Host vitachain-vps
    HostName <DROPLET_IP>
    User vitachain
    IdentityFile ~/.ssh/vitachain_do
    Port 22
```

Now you can connect with: `ssh vitachain-vps`

---

## Verification Checklist

- [ ] VPS is accessible via SSH as non-root user only
- [ ] Root login via SSH is disabled
- [ ] UFW firewall allows only ports 22, 80, 443
- [ ] Docker is installed and running
- [ ] Docker Compose is installed and functional
- [ ] Non-root user can run Docker without sudo
- [ ] Fail2ban is running and configured
- [ ] Automatic security updates are enabled
- [ ] System timezone is set to Africa/Casablanca
- [ ] Hostname is set to vitachain-vps
- [ ] All services start on boot

---

## Troubleshooting

### SSH Connection Issues

```bash
# Check SSH service status
systemctl status sshd

# Check SSH logs
tail -f /var/log/auth.log

# Test SSH connection with verbose output
ssh -vvv -i ~/.ssh/vitachain_do vitachain@<DROPLET_IP>
```

### Docker Issues

```bash
# Check Docker service status
systemctl status docker

# Check Docker logs
journalctl -u docker -n 50

# Restart Docker
systemctl restart docker
```

### Firewall Issues

```bash
# Check UFW status
ufw status verbose

# Reset UFW (if needed)
ufw --force reset
```

---

## Next Steps

After completing this setup:

1. **Story 0-2:** Configure Docker Compose network
2. **Story 0-3:** Configure NGINX reverse proxy
3. **Story 0-4:** Setup Supabase database tables
4. **Story 0-5:** Configure environment variables

---

## References

- [DigitalOcean Droplets Documentation](https://docs.digitalocean.com/products/droplets/)
- [Docker Installation Guide](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [UFW Documentation](https://help.ubuntu.com/community/UFW)
- [Fail2Ban Documentation](https://fail2ban.readthedocs.io/)
