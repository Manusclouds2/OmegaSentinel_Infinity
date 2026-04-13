#!/bin/bash

# LOPUTHJOSEPH Client Quick Deployment Script
# Version: 3.0.0-POST-HUMAN
# Deploys LOPUTHJOSEPH node with automatic configuration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Helper functions
green() { echo -e "${GREEN}✓ ${1}${NC}"; }
blue() { echo -e "${BLUE}→ ${1}${NC}"; }
yellow() { echo -e "${YELLOW}⚠ ${1}${NC}"; }
red() { echo -e "${RED}✗ ${1}${NC}"; }

echo "╔════════════════════════════════════════════════════╗"
echo "║   LOPUTHJOSEPH CLIENT DEPLOYMENT SCRIPT v3.0      ║"
echo "║   Post-Human Protection Node Installation         ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Parse command line arguments
NODE_ID="${1:-"loputhjoseph-node-$(hostname)"}"
PROTECTION_LEVEL="${2:-elite}"
NETWORK_MODE="${3:-bridge}"

blue "Configuration detected:"
echo "  Node ID: $NODE_ID"
echo "  Protection Level: $PROTECTION_LEVEL"
echo "  Network Mode: $NETWORK_MODE"
echo ""

# Check prerequisites
blue "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    red "Docker is not installed"
    echo "   Install from: https://docs.docker.com/engine/install/"
    exit 1
fi
green "Docker installed"

if ! command -v docker-compose &> /dev/null; then
    red "Docker Compose is not installed"
    exit 1
fi
green "Docker Compose installed"

# Check if main docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    red "docker-compose.yml not found in current directory"
    yellow "Please run this script from the directory containing docker-compose.yml"
    exit 1
fi
green "docker-compose.yml found"

echo ""
blue "Step 1: Generating node credentials..."

# Check if NODE_TOKEN already exists
if grep -q "^NODE_TOKEN=" .env 2>/dev/null; then
    yellow "NODE_TOKEN already exists in .env"
    EXISTING_TOKEN=$(grep "^NODE_TOKEN=" .env | cut -d '=' -f2)
    echo "  Using existing token: ${EXISTING_TOKEN:0:20}..."
    NODE_TOKEN="$EXISTING_TOKEN"
else
    # Generate new token
    NODE_TOKEN=$(openssl rand -base64 32)
    green "Generated new NODE_TOKEN (${NODE_TOKEN:0:20}...)"
fi

echo ""
blue "Step 2: Creating/updating .env configuration..."

# Create or update .env file with client settings
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || yellow ".env.example not found, creating minimal .env"
fi

# Update node-specific variables
sed -i.bak "s|^NODE_ID=.*|NODE_ID=$NODE_ID|" .env || echo "NODE_ID=$NODE_ID" >> .env
sed -i.bak "s|^NODE_TOKEN=.*|NODE_TOKEN=$NODE_TOKEN|" .env || echo "NODE_TOKEN=$NODE_TOKEN" >> .env
sed -i.bak "s|^LOPUTHJOSEPH_ORCHESTRATOR_URL=.*|LOPUTHJOSEPH_ORCHESTRATOR_URL=wss://orchestrator.loputhjoseph.ug/ws/node/$NODE_ID|" .env || echo "LOPUTHJOSEPH_ORCHESTRATOR_URL=wss://orchestrator.loputhjoseph.ug/ws/node/$NODE_ID" >> .env
sed -i.bak "s|^PROTECTION_LEVEL=.*|PROTECTION_LEVEL=$PROTECTION_LEVEL|" .env || echo "PROTECTION_LEVEL=$PROTECTION_LEVEL" >> .env
sed -i.bak "s|^NETWORK_MODE=.*|NETWORK_MODE=$NETWORK_MODE|" .env || echo "NETWORK_MODE=$NETWORK_MODE" >> .env

# Clean up backup
rm -f .env.bak 2>/dev/null || true

green ".env configuration updated"

echo ""
blue "Step 3: Creating loputhjoseph-node directories..."

mkdir -p logs/loputhjoseph-node
mkdir -p configs/threat-feeds
mkdir -p data/loputhjoseph-node

green "Directories created"

echo ""
blue "Step 4: Starting LOPUTHJOSEPH protection node..."
docker-compose up -d loputhjoseph-node

# Wait for service to start
sleep 5

echo ""
blue "Step 6: Verifying deployment..."

# Check if service is running
if [ "$(docker-compose ps -q loputhjoseph-node 2>/dev/null)" ]; then
    green "LOPUTHJOSEPH Node ($NODE_ID) is now ACTIVE"
    echo "  Protection Level: $PROTECTION_LEVEL"
    echo "  Status: PROTECTING"
else
    red "Failed to start LOPUTHJOSEPH Node"
    echo "  Check logs with: docker-compose logs loputhjoseph-node"
    exit 1
fi

# Check health status
if docker-compose exec sentinel-client curl -s http://localhost:9100/health > /dev/null 2>&1; then
    green "Health check passed"
else
    yellow "Health check endpoint not available yet (service initializing)"
fi

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║    ✓ CLIENT DEPLOYMENT COMPLETE                   ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║                                                    ║"
echo "║  Client ID: $CLIENT_ID"
echo "║  Status: RUNNING"
echo "║  Protection Level: $PROTECTION_LEVEL"
echo "║                                                    ║"
echo "║  View logs:                                        ║"
echo "║  $ docker-compose logs -f sentinel-client          ║"
echo "║                                                    ║"
echo "║  Check status:                                     ║"
echo "║  $ docker-compose ps sentinel-client               ║"
echo "║                                                    ║"
echo "║  Verify health:                                    ║"
echo "║  $ docker-compose exec sentinel-client \\          ║"
echo "║    curl http://localhost:9100/health               ║"
echo "║                                                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

blue "Quick start commands:"
echo ""
echo "  # View real-time logs"
echo "  docker-compose logs -f sentinel-client"
echo ""
echo "  # Check client status"
echo "  docker-compose exec sentinel-client curl http://localhost:9100/status"
echo ""
echo "  # Stop client"
echo "  docker-compose stop sentinel-client"
echo ""
echo "  # Restart client"
echo "  docker-compose restart sentinel-client"
echo ""
echo "  # Remove client"
echo "  docker-compose down"
echo ""

green "Setup complete! Your sentinel-client is now protecting your system."
echo ""
blue "Next steps:"
echo "  1. Monitor client logs: docker-compose logs -f sentinel-client"
echo "  2. Access Omega dashboard: http://localhost:8080"
echo "  3. View threat intelligence: http://localhost:8080/dashboard.html#threats"
echo "  4. Configure threat feeds: Configure in configs/threat-feeds/"
echo ""
echo "📚 Documentation: See SENTINEL_CLIENT_DEPLOYMENT.md for detailed information"
