# SSH Connection Guide - VitaChain VPS

**Project:** VitaChain v2.0
**Purpose:** Team SSH access to production VPS
**Last Updated:** 2026-05-01

---

## Overview

This guide provides instructions for team members to connect to the VitaChain VPS via SSH.

---

## Prerequisites

- SSH key pair (contact DevOps team if you don't have one)
- VPS IP address (contact DevOps team)
- SSH client (OpenSSH on Linux/Mac, PuTTY on Windows)

---

## Connection Details

**VPS Information:**
- **Hostname:** vitachain-vps
- **IP Address:** `<REPLACE_WITH_ACTUAL_IP>`
- **SSH User:** vitachain
- **SSH Port:** 22
- **Authentication:** Key-based only (no password)

**Security Notes:**
- Root login is **disabled**
- Password authentication is **disabled**
- Only SSH key authentication is allowed
- Firewall allows only ports 22, 80, 443

---

## Linux / macOS Users

### Method 1: Using SSH Config (Recommended)

1. Edit your SSH config file:
   ```bash
   nano ~/.ssh/config
   ```

2. Add the following configuration:
   ```
   Host vitachain-vps
       HostName <REPLACE_WITH_ACTUAL_IP>
       User vitachain
       IdentityFile ~/.ssh/vitachain_do
       Port 22
       ServerAliveInterval 60
       ServerAliveCountMax 3
   ```

3. Save and exit (Ctrl+X, Y, Enter)

4. Connect with:
   ```bash
   ssh vitachain-vps
   ```

### Method 2: Direct Connection

```bash
ssh -i ~/.ssh/vitachain_do vitachain@<REPLACE_WITH_ACTUAL_IP>
```

---

## Windows Users

### Method 1: Using PowerShell (Windows 10/11)

1. Open PowerShell

2. Connect with:
   ```powershell
   ssh -i C:\Users\YourUsername\.ssh\vitachain_do vitachain@<REPLACE_WITH_ACTUAL_IP>
   ```

### Method 2: Using PuTTY

1. Download and install [PuTTY](https://www.putty.org/)

2. Configure PuTTY:
   - **Host Name:** `<REPLACE_WITH_ACTUAL_IP>`
   - **Port:** 22
   - **Connection Type:** SSH

3. Configure SSH key:
   - Go to Connection → SSH → Auth
   - Click "Browse" for "Private key file for authentication"
   - Select your private key (`.ppk` format for PuTTY)
   - Note: Convert OpenSSH key to PuTTY format using PuTTYgen if needed

4. Save session:
   - Go to Session
   - Enter "vitachain-vps" in "Saved Sessions"
   - Click "Save"

5. Click "Open" to connect

---

## First-Time Connection

When connecting for the first time, you'll see:

```
The authenticity of host '<IP>' can't be established.
ED25519 key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)?
```

Type `yes` and press Enter.

---

## Common SSH Commands

### Check System Status

```bash
# Check system uptime
uptime

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
top
```

### Docker Commands

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs <container_name>

# Execute command in container
docker exec -it <container_name> /bin/bash
```

### Docker Compose Commands

```bash
# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

---

## Troubleshooting

### Permission Denied (Publickey)

**Problem:** SSH connection fails with "Permission denied (publickey)"

**Solutions:**
1. Verify you're using the correct private key
2. Check file permissions: `chmod 600 ~/.ssh/vitachain_do`
3. Verify your public key is added to the VPS
4. Contact DevOps team if key needs to be updated

### Connection Timed Out

**Problem:** SSH connection times out

**Solutions:**
1. Check your internet connection
2. Verify the VPS IP address is correct
3. Check if firewall is blocking port 22
4. Contact DevOps team to verify VPS status

### Host Key Verification Failed

**Problem:** "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED"

**Solution:**
```bash
# Remove old host key
ssh-keygen -R <REPLACE_WITH_ACTUAL_IP>

# Try connecting again
ssh vitachain-vps
```

---

## Security Best Practices

1. **Never share your private SSH key**
2. **Use SSH config for easier connections**
3. **Keep your private key secure** (chmod 600)
4. **Report lost keys immediately** to DevOps team
5. **Use screen/tmux** for long-running sessions
6. **Exit sessions when not in use**

---

## Requesting Access

If you need SSH access to the VPS:

1. Generate an SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@vitachain.ma" -f ~/.ssh/vitachain_<username>
   ```

2. Send your **public key** to the DevOps team:
   ```bash
   cat ~/.ssh/vitachain_<username>.pub
   ```

3. Wait for confirmation that your key has been added to the VPS

4. Follow the connection instructions above

---

## Emergency Contact

If you encounter issues that cannot be resolved:

- **DevOps Team:** devops@vitachain.ma
- **Slack:** #devops-emergency
- **Phone:** +212 XXX XXX XXX (DevOps on-call)

---

## Related Documentation

- [VPS Setup Guide](./vps-setup.md)
- [Docker Compose Configuration](../docker-compose.yml)
- [Environment Variables](../.env.example)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-05-01 | Initial version | DevOps Team |
