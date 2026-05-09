#!/bin/bash

# VitaChain VPS Setup Verification Script
# This script verifies all components are properly configured

set -e

# Configuration
HOSTNAME="vitachain-vps"
TIMEZONE="Africa/Casablanca"
NON_ROOT_USER="vitachain"
EXPECTED_DOCKER_VERSION="24.0"
EXPECTED_DOCKER_COMPOSE_VERSION="v2.24.5"

echo "✅ VitaChain VPS Setup Verification"
echo "=================================="

# Initialize verification counters
TOTAL_CHECKS=12
PASSED_CHECKS=0
FAILED_CHECKS=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    
    if [ "$expected" = "$actual" ]; then
        echo "✅ $test_name: PASSED"
        ((PASSED_CHECKS++))
        return 0
    else
        echo "❌ $test_name: FAILED (Expected: $expected, Actual: $actual)"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Check 1: VPS accessible via SSH as non-root user
echo ""
echo "Check 1: SSH access as non-root user..."
echo "====================================="
if id "${NON_ROOT_USER}" &>/dev/null; then
    echo "✅ Non-root user ${NON_ROOT_USER} exists"
    ((PASSED_CHECKS++))
else
    echo "❌ Non-root user ${NON_ROOT_USER} does not exist"
    ((FAILED_CHECKS++))
fi

# Check 2: Root login disabled
echo ""
echo "Check 2: Root SSH login disabled..."
echo "=================================="
ROOT_LOGIN=$(grep "^PermitRootLogin" /etc/ssh/sshd_config | awk '{print $2}')
check_result "Root SSH login disabled" "no" "$ROOT_LOGIN"

# Check 3: UFW firewall configuration
echo ""
echo "Check 3: UFW firewall configuration..."
echo "===================================="
if ufw status | grep -q "Status: active"; then
    echo "✅ UFW firewall is active"
    
    # Check allowed ports
    SSH_ALLOWED=$(ufw status | grep -c "22.*ALLOW")
    HTTP_ALLOWED=$(ufw status | grep -c "80.*ALLOW")
    HTTPS_ALLOWED=$(ufw status | grep -c "443.*ALLOW")
    
    if [ "$SSH_ALLOWED" -gt 0 ] && [ "$HTTP_ALLOWED" -gt 0 ] && [ "$HTTPS_ALLOWED" -gt 0 ]; then
        echo "✅ Required ports (22, 80, 443) are allowed"
        ((PASSED_CHECKS++))
    else
        echo "❌ Not all required ports are allowed"
        echo "   SSH (22): $SSH_ALLOWED rules"
        echo "   HTTP (80): $HTTP_ALLOWED rules"
        echo "   HTTPS (443): $HTTPS_ALLOWED rules"
        ((FAILED_CHECKS++))
    fi
else
    echo "❌ UFW firewall is not active"
    ((FAILED_CHECKS++))
fi

# Check 4: Docker installation
echo ""
echo "Check 4: Docker installation..."
echo "=============================="
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    echo "✅ Docker is installed (version: $DOCKER_VERSION)"
    ((PASSED_CHECKS++))
else
    echo "❌ Docker is not installed"
    ((FAILED_CHECKS++))
fi

# Check 5: Docker Compose installation
echo ""
echo "Check 5: Docker Compose installation..."
echo "======================================"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION=$(docker-compose --version | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+')
    echo "✅ Docker Compose is installed (version: $DOCKER_COMPOSE_VERSION)"
    ((PASSED_CHECKS++))
else
    echo "❌ Docker Compose is not installed"
    ((FAILED_CHECKS++))
fi

# Check 6: Non-root user in Docker group
echo ""
echo "Check 6: Non-root user Docker access..."
echo "======================================"
if groups "${NON_ROOT_USER}" | grep -q docker; then
    echo "✅ ${NON_ROOT_USER} is in Docker group"
    ((PASSED_CHECKS++))
else
    echo "❌ ${NON_ROOT_USER} is not in Docker group"
    ((FAILED_CHECKS++))
fi

# Check 7: Fail2Ban installation and configuration
echo ""
echo "Check 7: Fail2Ban configuration..."
echo "================================="
if systemctl is-active --quiet fail2ban; then
    echo "✅ Fail2Ban is running"
    
    # Check SSH jail configuration
    if fail2ban-client status sshd &>/dev/null; then
        echo "✅ Fail2Ban SSH jail is configured"
        ((PASSED_CHECKS++))
    else
        echo "❌ Fail2Ban SSH jail is not configured"
        ((FAILED_CHECKS++))
    fi
else
    echo "❌ Fail2Ban is not running"
    ((FAILED_CHECKS++))
fi

# Check 8: Automatic security updates
echo ""
echo "Check 8: Automatic security updates..."
echo "===================================="
if dpkg -l | grep -q unattended-upgrades; then
    if [ -f /etc/apt/apt.conf.d/50unattended-upgrades ]; then
        echo "✅ Automatic security updates are configured"
        ((PASSED_CHECKS++))
    else
        echo "❌ Automatic security updates not configured"
        ((FAILED_CHECKS++))
    fi
else
    echo "❌ unattended-upgrades package not installed"
    ((FAILED_CHECKS++))
fi

# Check 9: System timezone
echo ""
echo "Check 9: System timezone..."
echo "=========================="
CURRENT_TIMEZONE=$(timedatectl | grep "Time zone" | awk '{print $3}')
check_result "System timezone" "$TIMEZONE" "$CURRENT_TIMEZONE"

# Check 10: Hostname configuration
echo ""
echo "Check 10: Hostname configuration..."
echo "=================================="
CURRENT_HOSTNAME=$(hostname)
check_result "Hostname" "$HOSTNAME" "$CURRENT_HOSTNAME"

# Check 11: Service startup on boot
echo ""
echo "Check 11: Services enabled on boot..."
echo "===================================="
SERVICES_ENABLED=0
TOTAL_SERVICES=3

# Check Docker
if systemctl is-enabled --quiet docker; then
    echo "✅ Docker service enabled on boot"
    ((SERVICES_ENABLED++))
else
    echo "❌ Docker service not enabled on boot"
fi

# Check Fail2Ban
if systemctl is-enabled --quiet fail2ban; then
    echo "✅ Fail2Ban service enabled on boot"
    ((SERVICES_ENABLED++))
else
    echo "❌ Fail2Ban service not enabled on boot"
fi

# Check UFW
if systemctl is-enabled --quiet ufw; then
    echo "✅ UFW service enabled on boot"
    ((SERVICES_ENABLED++))
else
    echo "❌ UFW service not enabled on boot"
fi

if [ "$SERVICES_ENABLED" -eq "$TOTAL_SERVICES" ]; then
    ((PASSED_CHECKS++))
else
    ((FAILED_CHECKS++))
fi

# Check 12: System resources
echo ""
echo "Check 12: System resource availability..."
echo "======================================"
# Check memory (should have at least 1GB available)
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_GB=$((MEMORY_KB / 1024 / 1024))

if [ "$MEMORY_GB" -ge 1 ]; then
    echo "✅ Sufficient memory available (${MEMORY_GB}GB)"
    ((PASSED_CHECKS++))
else
    echo "❌ Insufficient memory (${MEMORY_GB}GB < 1GB)"
    ((FAILED_CHECKS++))
fi

# Check disk space (should have at least 10GB free)
DISK_FREE=$(df / | tail -1 | awk '{print $4}')
DISK_FREE_GB=$((DISK_FREE / 1024 / 1024))

if [ "$DISK_FREE_GB" -ge 10 ]; then
    echo "✅ Sufficient disk space available (${DISK_FREE_GB}GB)"
else
    echo "❌ Insufficient disk space (${DISK_FREE_GB}GB < 10GB)"
    ((FAILED_CHECKS++))
fi

# Final verification summary
echo ""
echo "📊 Verification Summary"
echo "======================"
echo "Total checks: $((PASSED_CHECKS + FAILED_CHECKS))"
echo "Passed: $PASSED_CHECKS"
echo "Failed: $FAILED_CHECKS"
echo "Success rate: $(( PASSED_CHECKS * 100 / (PASSED_CHECKS + FAILED_CHECKS) ))%"

if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo ""
    echo "🎉 ALL CHECKS PASSED! VPS is ready for deployment."
    echo ""
    echo "✅ VPS Setup Complete:"
    echo "   - SSH access configured for ${NON_ROOT_USER}"
    echo "   - Security hardening applied"
    echo "   - Docker and Docker Compose installed"
    echo "   - Firewall configured"
    echo "   - All services running and enabled"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Update connection guide with actual IP address"
    echo "   2. Test application deployment"
    echo "   3. Configure monitoring and backups"
    exit 0
else
    echo ""
    echo "⚠️  SOME CHECKS FAILED! Please address the issues above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Review failed checks and fix configuration issues"
    echo "   2. Re-run this verification script"
    echo "   3. Check logs for error details"
    exit 1
fi
