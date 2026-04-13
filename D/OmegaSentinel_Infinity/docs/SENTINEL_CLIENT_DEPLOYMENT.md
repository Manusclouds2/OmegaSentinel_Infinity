# Sentinel-UG Client Deployment Guide
## Advanced Quantum-Safe Protection Agent

**Version:** 2.1.0  
**Last Updated:** March 17, 2026  
**Status:** Production Ready

---

## Overview

The Sentinel-UG Client (sentinel-client) is an advanced quantum-safe protection agent that deploys alongside the Omega dashboard as a Docker service. It provides:

- **Quantum-Safe Cryptography** - Chronos polymorphism with dimensional fold encryption
- **Real-Time Threat Detection** - Continuous monitoring of system and network activity
- **Bio-Digital Authentication** - Optional EEG-based stress monitoring for adaptive security
- **Ghost Honeypots** - Decoy systems that attract and neutralize threats
- **Deep Packet Inspection** - Network-level threat analysis via Zeek IDS integration
- **Auto-Scaling Protection** - Dynamic resource allocation based on threat level

---

## Prerequisites

### System Requirements

- **OS:** Linux (recommended), macOS, or Windows with Docker Desktop
- **Docker:** version 20.10 or higher
- **Docker Compose:** version 2.0 or higher
- **Memory:** Minimum 4GB (8GB recommended)
- **CPU:** 2 cores minimum (4 cores recommended)
- **Network:** Outbound HTTPS access to orchestrator.sentinel.ug

### Required Capabilities

The client requires elevated Docker capabilities for deep system monitoring:

```
- NET_ADMIN: Network packet capture and inspection
- NET_RAW: Raw socket access for network analysis
- SYS_ADMIN: System administration and hardware access
- SYS_PTRACE: Process tracing and analysis
```

### Network Requirements

- **Orchestrator Connection:** WebSocket over TLS (wss://)
- **Outbound Port 443:** HTTPS for threat intelligence APIs
- **Local Port 9100:** Health check endpoint (internal only)

---

## Installation

### Step 1: Generate Client Credentials

Before deploying, generate unique credentials for your client:

```bash
# Generate a unique CLIENT_ID (use your hostname or custom identifier)
CLIENT_ID="omega-client-$(hostname)"

# Generate a secure CLIENT_TOKEN
CLIENT_TOKEN=$(openssl rand -base64 32)

echo "CLIENT_ID=$CLIENT_ID"
echo "CLIENT_TOKEN=$CLIENT_TOKEN"
```

### Step 2: Update .env Configuration

Add these values to your `.env` file:

```bash
# Client Identification
CLIENT_ID=omega-client-yourhost
CLIENT_TOKEN=your_generated_token_here
QUANTUM_ORCHESTRATOR_URL=wss://orchestrator.sentinel.ug/ws/client/omega-client-yourhost

# Protection Settings
PROTECTION_LEVEL=omega_full
NETWORK_MODE=bridge
CHRONOS_POLYMORPHISM_ENABLED=true
DIMENSIONAL_FOLDS_COUNT=256
AUTO_UPDATE_ENABLED=true
HEARTBEAT_INTERVAL=5s
THREAT_REPORTING=true
```

### Step 3: Deploy with Docker Compose

```bash
# Pull latest images
docker-compose pull

# Build and start all services including sentinel-client
docker-compose up -d

# Verify sentinel-client is running
docker-compose ps sentinel-client

# Check client health
docker-compose exec sentinel-client curl http://localhost:9100/health
```

### Step 4: Verify Deployment

```bash
# View client logs
docker-compose logs -f sentinel-client

# Expected output:
# sentinel-client-default | Sentinel-UG Client v2.1.0 starting...
# sentinel-client-default | Quantum orchestrator connected: wss://orchestrator.sentinel.ug
# sentinel-client-default | Protection level: OMEGA_FULL
# sentinel-client-default | Status: ACTIVE
```

---

## Configuration Options

### Environment Variables

#### Client Identity
| Variable | Default | Description |
|----------|---------|-------------|
| `CLIENT_ID` | omega-client-001 | Unique identifier for this client |
| `CLIENT_TOKEN` | change-me | Authentication token for orchestrator |
| `QUANTUM_ORCHESTRATOR_URL` | wss://orchestrator.sentinel.ug/ws/client/default | WebSocket endpoint for orchestrator |

#### Quantum Security
| Variable | Default | Description |
|----------|---------|-------------|
| `PROTECTION_LEVEL` | omega_full | Protection mode: omega_lite, omega_standard, omega_full |
| `CHRONOS_POLYMORPHISM_ENABLED` | true | Enable time-based polymorphic encryption |
| `DIMENSIONAL_FOLDS_COUNT` | 256 | Number of encryption dimensions (128, 256, 512) |
| `QUANTUM_ENTROPY_SEED` | (generated) | Entropy seed for quantum key generation |

#### Bio-Digital Features
| Variable | Default | Description |
|----------|---------|-------------|
| `EEG_SENSOR_ENABLED` | false | Enable EEG-based stress monitoring (requires hardware) |
| `STRESS_THRESHOLD` | 0.85 | Threat level trigger based on stress (0.0-1.0) |
| `SILENT_ERASURE_ENABLED` | true | Auto-erase sensitive data under duress |

#### Network & Monitoring
| Variable | Default | Description |
|----------|---------|-------------|
| `NETWORK_MODE` | bridge | Docker network mode: bridge, host, none |
| `AUTO_UPDATE_ENABLED` | true | Auto-update client to latest version |
| `HEARTBEAT_INTERVAL` | 5s | Health check interval sent to orchestrator |
| `THREAT_REPORTING` | true | Report detected threats to orchestrator |
| `DARK_WEB_MONITORING` | true | Monitor dark web for compromised credentials |

#### Threat Intelligence
| Variable | Default | Description |
|----------|---------|-------------|
| `MITRE_ATTACK_API_ENABLED` | true | Enable MITRE ATT&CK framework integration |
| `VIRUSTOTAL_API_KEY` | (empty) | VirusTotal API key for hash lookups |

---

## Network Modes

### Bridge Mode (Default)
```yaml
network_mode: bridge
```
- **Use Case:** Standard deployment with network isolation
- **Security:** Good - isolated from host network
- **Performance:** Medium
- **Capabilities:** Limited network access

### Host Mode
```yaml
network_mode: host
```
- **Use Case:** Advanced monitoring with full network access
- **Security:** High risk - shares host network namespace
- **Performance:** High
- **Capabilities:** Full packet capture capability
- **Warning:** Only use in trusted environments

### Custom Network
```yaml
networks:
  - omega-network
```
- **Use Case:** Multi-container orchestration with custom routing
- **Security:** Good - controlled network access
- **Performance:** Medium
- **Capabilities:** Inter-service communication

---

## Hardware Access

### Memory Access
```yaml
devices:
  - /dev/mem:/dev/mem:ro
```
Enables direct memory analysis for:
- Kernel module detection
- Root-kit identification
- Firmware integrity checking

### System Monitoring
```yaml
volumes:
  - /sys:/host/sys:ro
  - /proc:/host/proc:ro
```
Provides access to:
- CPU and memory metrics
- Process information
- Kernel parameters
- Device information

### Docker Access
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```
Enables container-level monitoring:
- Container image analysis
- Volume inspection
- Network bridge monitoring
- Runtime behavior analysis

---

## Security Capabilities

The sentinel-client requires specific Linux capabilities:

```yaml
cap_add:
  - NET_ADMIN          # Network packet inspection
  - NET_RAW            # Raw socket access
  - SYS_ADMIN          # System-level operations
  - SYS_PTRACE         # Process tracing
```

### Capability Details

| Capability | Purpose | Risk |
|-----------|---------|------|
| NET_ADMIN | Packet capture, interface management | Medium |
| NET_RAW | Raw socket creation for custom protocols | Medium |
| SYS_ADMIN | Kernel module loading, hardware access | High |
| SYS_PTRACE | Process inspection and debugger access | High |

### AppArmor Configuration
```yaml
security_opt:
  - apparmor=unconfined
```
Disables AppArmor restrictions to allow:
- Deep process analysis
- Kernel interaction
- Hardware monitoring
- Driver inspection

---

## Operational Management

### Starting the Client

```bash
# Start just the sentinel-client
docker-compose up -d sentinel-client

# Or start all services
docker-compose up -d
```

### Checking Status

```bash
# Service status
docker-compose ps sentinel-client

# Health metrics
docker-compose exec sentinel-client curl http://localhost:9100/health

# Real-time logs
docker-compose logs -f sentinel-client

# Log output example:
# Status: ACTIVE
# Quantum state: ENTANGLED
# Threats detected: 0
# Memory: 256MB / 512MB
# Network packets: 1,234,567
```

### Stopping the Client

```bash
# Stop sentinel-client
docker-compose stop sentinel-client

# Stop all services
docker-compose down
```

### Restarting the Client

```bash
# Restart with new configuration
docker-compose restart sentinel-client

# Full rebuild and restart
docker-compose up -d --force-recreate sentinel-client
```

---

## Threat Response

### Threat Levels

| Level | State | Response |
|-------|-------|----------|
| **GREEN** | Normal operation | Passive monitoring |
| **YELLOW** | Suspicious activity | Enhanced analysis |
| **RED** | Active threat | Automated defense |
| **CRITICAL** | System compromise | Emergency containment |

### Automatic Actions

When a threat is detected:

1. **Logging:** Threat signature recorded in PostgreSQL
2. **Honeynet:** Deploy ghost honeypot to contain threat
3. **Analysis:** Deep packet inspection via Zeek
4. **Reporting:** Alert sent to orchestrator
5. **Remediation:** Auto-update firewall rules
6. **Erasure:** Silent deletion of sensitive data (if enabled)

### Manual Threat Response

```bash
# Receive threat notifications
docker-compose exec app curl http://localhost:8080/api/threats?limit=10 \
  -H "Authorization: Bearer $JWT_TOKEN"

# Export threat logs for analysis
docker-compose exec postgres psql -U quantum_admin -d sentinel_omega \
  -c "SELECT * FROM threat_logs ORDER BY timestamp DESC LIMIT 100;" > threats.csv

# Trigger client re-scan
docker-compose exec sentinel-client curl -X POST http://localhost:9100/rescan
```

---

## Advanced Configuration

### Multi-Client Deployment

Deploy multiple sentinel-clients for distributed protection:

```bash
# Client 1 (Primary Server)
CLIENT_ID=omega-client-primary ./deploy.sh
docker-compose up -d sentinel-client

# Client 2 (Secondary Server)
CLIENT_ID=omega-client-secondary ./deploy.sh
docker-compose up -d sentinel-client

# Client 3 (IoT/Edge Device)
CLIENT_ID=omega-client-iot-001 ./deploy.sh
docker-compose up -d sentinel-client
```

### Custom Protection Chains

Create specialized protection pipelines:

```yaml
# .env configuration
PROTECTION_LEVEL=omega_custom

# Enable specific modules
DARK_WEB_MONITORING=true
MITRE_ATTACK_API_ENABLED=true
CHRONOS_POLYMORPHISM_ENABLED=true
DIMENSIONAL_FOLDS_COUNT=512  # Maximum encryption strength
```

### Performance Tuning

For resource-constrained environments:

```bash
# Lite mode (1 CPU, 512MB RAM)
PROTECTION_LEVEL=omega_lite
DIMENSIONAL_FOLDS_COUNT=128

# Docker limits
docker-compose up -d --memory 512m --cpus 1 sentinel-client
```

---

## Troubleshooting

### Client Won't Start

```bash
# Check Docker daemon
docker ps

# Review client logs
docker-compose logs sentinel-client

# Common issues:
# - "Permission denied": Run with sudo or add user to docker group
# - "Port already in use": Change NETWORK_MODE or kill conflicting process
# - "Image not found": Run docker-compose pull
```

### Connection Issues

```bash
# Test orchestrator connectivity
docker-compose exec sentinel-client \
  curl -v wss://orchestrator.sentinel.ug/health

# Check network configuration
docker-compose exec sentinel-client ip addr
docker-compose exec sentinel-client netstat -tuln

# Verify DNS resolution
docker-compose exec sentinel-client nslookup orchestrator.sentinel.ug
```

### Performance Problems

```bash
# Check resource usage
docker stats sentinel-client

# Monitor process list
docker-compose exec sentinel-client ps aux

# Check disk space
docker-compose exec sentinel-client df -h

# Reduce threat reporting frequency
THREAT_REPORTING=false
HEARTBEAT_INTERVAL=30s
```

### Logging and Debugging

```bash
# Enable debug logging
docker-compose stop sentinel-client
LOG_LEVEL=DEBUG docker-compose up sentinel-client

# Export logs for analysis
docker-compose logs sentinel-client > client_logs.txt

# Analyze threat database
docker-compose exec postgres psql -U quantum_admin -d sentinel_omega \
  -c "\d threat_logs"
```

---

## Security Best Practices

### 1. Credential Management
- [ ] Generate unique CLIENT_ID for each deployment
- [ ] Store CLIENT_TOKEN in secure secret manager
- [ ] Rotate CLIENT_TOKEN quarterly
- [ ] Never commit .env to version control

### 2. Network Security
- [ ] Use bridge mode in untrusted networks
- [ ] Enable firewall rules restricting port 9100
- [ ] Whitelist orchestrator IP addresses
- [ ] Monitor outbound connections

### 3. Data Protection
- [ ] Enable SILENT_ERASURE for sensitive systems
- [ ] Regularly backup threat logs
- [ ] Encrypt PostgreSQL database
- [ ] Implement data retention policies

### 4. Compliance
- [ ] Enable GDPR_COMPLIANT mode for EU systems
- [ ] Set DATA_RETENTION_DAYS appropriately
- [ ] Document threat response procedures
- [ ] Maintain audit logs for compliance

---

## API Endpoints

### Health Check
```
GET http://localhost:9100/health
Response: {"status": "active", "protection_level": "omega_full"}
```

### Client Status
```
GET http://localhost:9100/status
Response: {
  "client_id": "omega-client-001",
  "status": "ACTIVE",
  "threats_detected": 0,
  "memory_usage": "256MB",
  "uptime": "3600s"
}
```

### Manual Rescan
```
POST http://localhost:9100/rescan
Response: {"scan_id": "uuid", "status": "initiated"}
```

### Threat Export
```
GET http://localhost:9100/threats/export?format=json
Response: [...]
```

---

## Support & Resources

- **Documentation:** https://sentinel.ug/docs/client-v2
- **API Reference:** https://api.sentinel.ug/client
- **Community Forum:** https://community.sentinel.ug
- **Issue Tracker:** https://github.com/sentinel-ug/client-omega/issues
- **Security Advisories:** https://sentinel.ug/security

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2026-03-17 | Quantum orchestrator integration, bio-digital auth |
| 2.0.0 | 2026-01-01 | Initial Docker release, Zeek IDS integration |
| 1.5.0 | 2025-11-01 | Cross-platform support |

---

**© 2026 Sentinel-UG. All rights reserved.**  
*Quantum-safe cybersecurity for the future.*
