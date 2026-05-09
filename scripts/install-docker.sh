#!/bin/bash

# VitaChain VPS Docker Installation Script
# This script installs Docker Engine and Docker Compose

set -e

# Configuration
DOCKER_COMPOSE_VERSION="v2.24.5"
NON_ROOT_USER="vitachain"

echo "🐳 VitaChain VPS Docker Installation"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo ./install-docker.sh"
    exit 1
fi

# Step 1: Install prerequisites
echo ""
echo "Step 1: Installing Docker prerequisites..."
echo "========================================"
apt update
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
echo "✅ Prerequisites installed"

# Step 2: Add Docker's official GPG key
echo ""
echo "Step 2: Adding Docker GPG key..."
echo "==============================="
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "✅ Docker GPG key added"

# Step 3: Add Docker repository
echo ""
echo "Step 3: Adding Docker repository..."
echo "================================="
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
echo "✅ Docker repository added"

# Step 4: Install Docker Engine
echo ""
echo "Step 4: Installing Docker Engine..."
echo "=================================="
apt update
apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
echo "✅ Docker Engine installed"

# Step 5: Start and enable Docker service
echo ""
echo "Step 5: Starting Docker service..."
echo "================================="
systemctl start docker
systemctl enable docker
echo "✅ Docker service started and enabled on boot"

# Step 6: Add non-root user to Docker group
echo ""
echo "Step 6: Adding ${NON_ROOT_USER} to Docker group..."
echo "=============================================="
usermod -aG docker ${NON_ROOT_USER}
echo "✅ ${NON_ROOT_USER} added to Docker group"

# Step 7: Test Docker installation
echo ""
echo "Step 7: Testing Docker installation..."
echo "===================================="
docker run hello-world
echo "✅ Docker test successful"

# Step 8: Verify Docker info
echo ""
echo "Step 8: Docker installation details..."
echo "==================================="
echo "Docker version:"
docker --version
echo ""
echo "Docker info:"
docker info | head -20
echo ""

# Step 9: Download Docker Compose
echo ""
echo "Step 9: Installing Docker Compose..."
echo "===================================="
curl -SL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
echo "✅ Docker Compose ${DOCKER_COMPOSE_VERSION} installed"

# Step 10: Test Docker Compose
echo ""
echo "Step 10: Testing Docker Compose..."
echo "================================="
docker-compose --version
echo "✅ Docker Compose test successful"

# Step 11: Test Docker Compose functionality
echo ""
echo "Step 11: Testing Docker Compose functionality..."
echo "=============================================="
# Create temporary test directory
TEST_DIR="/tmp/docker-compose-test"
mkdir -p ${TEST_DIR}
cd ${TEST_DIR}

# Create test compose file
cat > docker-compose.yml << EOF
version: '3.8'
services:
  test:
    image: alpine
    command: echo "Docker Compose is working!"
EOF

# Run test
echo "Running Docker Compose test..."
docker-compose up
echo "✅ Docker Compose functionality test successful"

# Cleanup
cd /
rm -rf ${TEST_DIR}
echo "✅ Test files cleaned up"

# Step 12: Verify user can run Docker without sudo
echo ""
echo "Step 12: Verifying non-root Docker access..."
echo "=========================================="
echo "Testing Docker access for ${NON_ROOT_USER} user..."
# Note: This will only work after user logout/login
echo "ℹ️  Note: ${NON_ROOT_USER} will need to logout and login again"
echo "   to use Docker without sudo due to group membership change"

# Step 13: Show Docker status
echo ""
echo "Step 13: Docker service status..."
echo "==============================="
systemctl status docker --no-pager -l
echo ""

echo ""
echo "🐳 Docker installation complete!"
echo ""
echo "📝 Installation summary:"
echo "   - Docker Engine: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
echo "   - Docker Compose: $(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)"
echo "   - Docker service: Enabled and running"
echo "   - User ${NON_ROOT_USER}: Added to docker group"
echo ""
echo "🔐 Security status:"
echo "   ✅ Docker installed from official repositories"
echo "   ✅ Docker service configured to start on boot"
echo "   ✅ Non-root user granted Docker access"
echo ""
echo "📋 Next steps:"
echo "   1. ${NON_ROOT_USER} should logout and login again"
echo "   2. Test Docker without sudo: docker run hello-world"
echo "   3. Run the security hardening script"
echo "   4. Deploy application containers"
