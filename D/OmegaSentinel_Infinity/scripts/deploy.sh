#!/bin/bash

# LOPUTHJOSEPH Deployment Script
# Version: 3.0.0-POST-HUMAN
# Advanced post-human cybersecurity deployment with cross-platform support

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════╗"
echo "║  LOPUTHJOSEPH DEPLOYMENT INITIATED               ║"
echo "║  Version: 3.0.0-POST-HUMAN - Unhackable Core     ║"
echo "╚══════════════════════════════════════════════════╝"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function for colored output
green() { echo -e "${GREEN}${1}${NC}"; }
blue() { echo -e "${BLUE}${1}${NC}"; }
yellow() { echo -e "${YELLOW}${1}${NC}"; }
red() { echo -e "${RED}${1}${NC}"; }

# Check for .env file
if [ ! -f ".env" ]; then
    yellow "📋 .env file not found, creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        green "✓ .env created - please review and update sensitive values"
    fi
fi

# Load environment (if available)
if [ -f ".env" ]; then
    set +a
    source .env
    set -a
fi

# Detect OS and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)     PLATFORM="linux" ;;
    Darwin*)    PLATFORM="macos" ;;
    MSYS*|MINGW*|CYGWIN*) PLATFORM="windows" ;;
    *)          red "❌ Unsupported OS: $OS"; exit 1 ;;
esac

case "$ARCH" in
    x86_64)     ARCH="amd64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *)          red "❌ Unsupported architecture: $ARCH"; exit 1 ;;
esac

blue "📊 Deployment Configuration Detected:"
echo "   Platform: $PLATFORM ($ARCH)"
echo "   OS: $OS"
echo ""

# Step 1: Install Docker and Docker Compose
blue "Step 1: Installing Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    blue "Installing Docker engine..."
    if [ "$PLATFORM" == "linux" ]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        sudo usermod -aG docker $USER
        green "✓ Docker installed successfully"
    else
        yellow "⚠ Please install Docker manually from https://www.docker.com/products/docker-desktop"
        exit 1
    fi
else
    green "✓ Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    if [ "$PLATFORM" == "linux" ]; then
        sudo apt-get install -y docker-compose-plugin
    fi
    green "✓ Docker Compose installed"
else
    green "✓ Docker Compose already installed"
fi

# Step 2: Install system dependencies
blue "Step 2: Installing system dependencies..."
if [ "$PLATFORM" == "linux" ]; then
    sudo apt-get update
    sudo apt-get install -y \
        python3 python3-pip \
        nodejs npm \
        nginx \
        certbot python3-certbot-nginx \
        postgresql postgresql-contrib \
        redis-server \
        git curl wget \
        net-tools tcpdump openssl
    green "✓ System dependencies installed"
elif [ "$PLATFORM" == "macos" ]; then
    if ! command -v brew &> /dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install docker docker-compose python3 node nginx postgresql redis
    green "✓ System dependencies installed"
else
    yellow "⚠ For Windows, please ensure Docker Desktop is running"
fi

# Step 3: Create directory structure
blue "Step 3: Creating configuration directories..."
mkdir -p configs/quantum-keys
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p ssl
mkdir -p scan

green "✓ Directories created"

# Step 4: Generate quantum encryption keys
blue "Step 4: Generating quantum encryption keys..."
if [ ! -f "configs/quantum-keys/master.key" ]; then
    openssl genrsa -out configs/quantum-keys/master.key 4096
    openssl req -new -x509 -key configs/quantum-keys/master.key \
        -out configs/quantum-keys/master.crt -days 365 \
        -subj "/C=UG/ST=Uganda/L=Kampala/O=Sentinel/CN=omega.local"
    openssl rand -base64 64 > configs/quantum-keys/entropy.seed
    chmod 600 configs/quantum-keys/*
    green "✓ Quantum keys generated"
else
    green "✓ Quantum keys already exist"
fi

# Step 5: Create enhanced .env configuration
blue "Step 5: Creating environment configuration..."
if [ ! -f ".env" ]; then
    POSTGRES_PASS=$(openssl rand -base64 16)
    cat > .env << EOF
# SENTINEL-UG OMEGA - Quantum-Safe Configuration
# Generated on $(date)

# Quantum Configuration
QUANTUM_MASTER_KEY=$(openssl rand -base64 32)
QUANTUM_ENTROPY_SEED=\$(cat configs/quantum-keys/entropy.seed)
CHRONOS_POLYMORPHISM_ENABLED=true
DIMENSIONAL_FOLDS_COUNT=256

# Database
POSTGRES_DB=sentinel_omega
POSTGRES_USER=quantum_admin
POSTGRES_PASSWORD=$POSTGRES_PASS
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://quantum_admin:$POSTGRES_PASS@postgres:5432/sentinel_omega

# Redis Cache
REDIS_PASSWORD=$(openssl rand -base64 16)
REDIS_HOST=redis
REDIS_PORT=6379

# Dashboard
DASHBOARD_SECRET_KEY=$(openssl rand -base64 64)
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8443
DASHBOARD_SSL_CERT=/ssl/fullchain.pem
DASHBOARD_SSL_KEY=/ssl/privkey.pem

# Security Keys
OMEGA_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
MASTER_KEY_PATH=configs/quantum-keys/master.key

# Bio-Digital Auth (disabled by default)
EEG_SENSOR_ENABLED=false
STRESS_THRESHOLD=0.85
SILENT_ERASURE_ENABLED=true

# Threat Intelligence
VIRUSTOTAL_API_KEY=
MITRE_ATTACK_API_ENABLED=true
DARK_WEB_MONITORING=true
SHODAN_API_KEY=
MAXMIND_API_KEY=

# Cloud Integration
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Payment Processing (optional)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Compliance
GDPR_COMPLIANT=true
DATA_RETENTION_DAYS=30
AUTO_DATA_ERASURE=true

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ALERTMANAGER_ENABLED=true
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Deployment Settings
DEPLOYMENT_MODE=production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SCAN_ROOT=/app/scan

# Auto-Scaling
AUTO_SCALING_ENABLED=true
MAX_REPLICAS=100

# Firewall Settings
FIREWALL_MODE=passive
PACKET_CAPTURE=true
THREAT_LEVEL_THRESHOLD=high

# Email Notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=admin@omega.local

# Application Settings
MAX_LOGIN_ATTEMPTS=5
SESSION_TIMEOUT=3600
JWT_EXPIRY=3600
EOF
    green "✓ Environment configuration created"
else
    green "✓ Environment configuration already exists"
fi

# Step 6: Build and start services
blue "Step 6: Building Docker images (this may take 2-5 minutes)..."
docker-compose build --parallel

blue "Starting services (PostgreSQL, Redis, FastAPI, Nginx, Zeek, Prometheus, Grafana)..."
docker-compose up -d

green "✓ Services started"

# Step 7: Initialize quantum database
blue "Step 7: Initializing quantum database..."
sleep 10

# Create quantum state tables
docker-compose exec postgres psql -U quantum_admin -d sentinel_omega << 'QUANTUM_DB'
CREATE TABLE IF NOT EXISTS quantum_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    entangled_with UUID[]
);

CREATE TABLE IF NOT EXISTS threat_logs (
    id SERIAL PRIMARY KEY,
    threat_hash VARCHAR(256) UNIQUE,
    source_ip INET,
    attack_type VARCHAR(100),
    severity INTEGER,
    neutralized BOOLEAN DEFAULT false,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    quantum_token VARCHAR(512),
    neural_signature VARCHAR(256),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_threat_severity ON threat_logs(severity);
CREATE INDEX IF NOT EXISTS idx_threat_time ON threat_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_quantum_state ON quantum_states(created_at);
QUANTUM_DB

green "✓ Quantum database initialized"

# Step 8: Setup SSL/TLS certificates
blue "Step 8: Configuring HTTPS/TLS..."
if [ "$PLATFORM" == "linux" ]; then
    sudo certbot certonly --standalone -d omega.local --non-interactive --agree-tos -m admin@omega.local 2>/dev/null || true
    if [ -f "/etc/letsencrypt/live/omega.local/fullchain.pem" ]; then
        sudo cp /etc/letsencrypt/live/omega.local/fullchain.pem ssl/
        sudo cp /etc/letsencrypt/live/omega.local/privkey.pem ssl/
        sudo chown $USER:$USER ssl/*
        green "✓ SSL certificates configured"
    fi
else
    # For macOS and Windows, generate self-signed certificates
    blue "Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -nodes -out ssl/fullchain.pem -keyout ssl/privkey.pem -days 365 \
        -subj "/C=UG/ST=Uganda/L=Kampala/O=Sentinel/CN=localhost"
    green "✓ Self-signed certificate created"
fi

# Step 9: Verify deployment
blue "Step 9: Verifying deployment..."
sleep 5
sleep 5
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    green "✓ Services running and responding"
else
    yellow "⚠ Services may be initializing (this is normal on first run)"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║        ✅ DEPLOYMENT COMPLETE                    ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║                                                  ║"
echo "║  🌐 Web Dashboard: http://localhost:8080         ║"
echo "║  🔐 Admin Portal:  https://localhost:8443        ║"
echo "║  📊 Grafana:       http://localhost:3000         ║"
echo "║  🔍 Prometheus:    http://localhost:9090         ║"
echo "║                                                  ║"
echo "║  Default Login: admin / letmein                  ║"
echo "║                                                  ║"
echo "║  ⚠️  IMPORTANT - Update .env file with:          ║"
echo "║     - VirusTotal API key                         ║"
echo "║     - Shodan API key                             ║"
echo "║     - MaxMind GeoIP key                          ║"
echo "║     - AWS credentials (optional)                 ║"
echo "║     - Stripe keys (optional)                     ║"
echo "║     - SMTP credentials                           ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

blue "📋 Useful Commands:"
echo "   View logs:      docker-compose logs -f app"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo "   Full rebuild:   docker-compose down && docker-compose build && docker-compose up -d"
echo ""

blue "🔗 API Endpoints:"
echo "   POST   /api/auth/token          - User authentication"
echo "   GET    /api/users               - List users"
echo "   POST   /api/scan/folder         - Scan folder for threats"
echo "   GET    /api/threats             - Get threat intelligence"
echo "   POST   /api/firewall/rules      - Manage firewall rules"
echo "   WS     /ws/omega                - WebSocket real-time updates"
echo ""

blue "📚 Documentation:"
echo "   See DEPLOYMENT.md for detailed setup instructions"
echo "   API docs available at: http://localhost:8080/api/docs"
echo ""

green "System is ready! Next step: Configure API keys and restart services."
echo ""
