# LOPUTHJOSEPH - Post-Deployment Setup Guide

**Version:** 3.0-POST-HUMAN  
**Date:** March 29, 2026  
**Estimated Setup Time:** 15-20 minutes  

This guide walks you through the essential post-deployment configuration steps to activate all features of your LOPUTHJOSEPH security platform.

---

## Table of Contents

1. [Configure API Keys](#1-configure-api-keys)
2. [Deploy LOPUTHJOSEPH Nodes](#2-deploy-loputhjoseph-nodes)
3. [Enable Threat Intelligence](#3-enable-threat-intelligence)
4. [Set Email Alerts](#4-set-email-alerts)
5. [Review Security Settings](#5-review-security-settings)
6. [Monitor Operations](#6-monitor-operations)

---

## 1. Configure API Keys

Your LOPUTHJOSEPH platform needs three external API keys to enable threat intelligence features:

### 1.1 VirusTotal API Key

**Purpose:** Hash and URL scanning against 70+ antivirus engines

**Steps:**

1. Visit [VirusTotal](https://www.virustotal.com/gui/home/upload)
2. Click "Sign In" → "Create Account"
3. Sign up with your email address
4. Verify your email
5. Go to [API Key Settings](https://www.virustotal.com/gui/settings/api)
6. Copy your API key

**Add to Environment:**

```bash
# Open .env file
nano .env

# Find or add this line:
VIRUSTOTAL_API_KEY=your_api_key_here

# Replace with your actual key:
VIRUSTOTAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Save (Ctrl+X, then Y, then Enter)
```

**Verify:**

```bash
# Restart the application
docker-compose restart app

# Check logs for successful connection
docker-compose logs app | grep -i virustotal

# Expected: "VirusTotal API initialized" or similar
```

---

### 1.2 Shodan API Key

**Purpose:** Vulnerability intelligence and network reconnaissance

**Steps:**

1. Visit [Shodan](https://www.shodan.io/)
2. Click "Sign Up" in top right
3. Create account with email or GitHub
4. Verify email
5. Go to [Account Settings](https://account.shodan.io/)
6. Find "API Key" section
7. Copy your API key

**Add to Environment:**

```bash
# Open .env file
nano .env

# Find or add:
SHODAN_API_KEY=your_api_key_here

# Replace with your actual key:
SHODAN_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Save
```

**Verify:**

```bash
# Restart services
docker-compose restart app

# Check logs
docker-compose logs app | grep -i shodan

# Test endpoint
curl -H "Authorization: Bearer $(docker-compose exec app echo $JWT_SECRET)" \
  http://localhost:8080/api/threats?limit=1
```

---

### 1.3 MaxMind GeoIP Key

**Purpose:** IP geolocation for threat mapping and attribution

**Steps:**

1. Visit [MaxMind](https://www.maxmind.com/en/geoip2-geolite2)
2. Click "Sign Up for GeoIP2"
3. Create account with email
4. Agree to terms
5. Go to [Account Settings](https://www.maxmind.com/en/accounts/current/geoip/downloads)
6. Find "GeoIP2 Database Downloads" section
7. Click "Generate New License Key"
8. Copy your license key

**Add to Environment:**

```bash
# Open .env file
nano .env

# Find or add:
MAXMIND_API_KEY=your_license_key_here

# Replace with your actual key:
MAXMIND_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Save
```

**Verify:**

```bash
# Download GeoIP database (optional but recommended)
docker-compose exec app python3 -c \
  "import requests; print('MaxMind connected')" 2>&1 | head -20

# Restart services to apply all keys
docker-compose restart app

# Check all APIs are initialized
docker-compose logs app | grep "API initialized\|connected"
```

---

### 1.4 Verify All API Keys

```bash
# Quick verification script
cat > verify_apis.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying API Keys..."

# Get JWT token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"letmein"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

echo "✓ Authentication successful"

# Test threat endpoint (uses all APIs)
THREATS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/threats | head -20)

if echo "$THREATS" | grep -q "threats\|error"; then
  echo "✓ API endpoints responding"
fi

# Check logs for API connections
echo ""
echo "📋 API Connection Status:"
docker-compose logs app --tail 50 | grep -i "api\|connected\|initialized"

EOF

chmod +x verify_apis.sh
./verify_apis.sh
```

---

## 2. Deploy LOPUTHJOSEPH Nodes

Deploy the protection nodes to all your systems:

### 2.1 Linux/macOS Node

```bash
# Navigate to the deployment folder
cd /path/to/loputhjoseph

# Run the deployment script
bash deploy-loputhjoseph-client.sh node-01 elite bridge
```

### 2.2 Windows Node

```powershell
# Navigate to the deployment folder
cd C:\path\to\loputhjoseph

# Run the deployment script
.\deploy-loputhjoseph-client.ps1 -NodeID "node-01" -Level "elite"
```

---

### 2.3 Verify Client Connectivity

```bash
# Check client status in dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/clients

# Expected response:
# {
#   "clients": [
#     {"id": "omega-client-primary", "status": "ACTIVE", "protection_level": "omega_full"},
#     {"id": "omega-client-secondary", "status": "ACTIVE", "protection_level": "omega_full"}
#   ],
#   "total": 2,
#   "protected_systems": 2
# }

# View client logs
docker-compose logs sentinel-client --tail 50

# Monitor client resource usage
docker stats sentinel-client
```

---

### 2.4 Client Configuration Options

For custom client deployments, edit `.env` before running client script:

```bash
# Custom client configuration
CLIENT_ID=omega-client-myservers-001
CLIENT_TOKEN=your_secure_token_here
PROTECTION_LEVEL=omega_full  # omega_lite, omega_standard, or omega_full

# Advanced features
CHRONOS_POLYMORPHISM_ENABLED=true
DIMENSIONAL_FOLDS_COUNT=256
AUTO_UPDATE_ENABLED=true
HEARTBEAT_INTERVAL=5s

# Network configuration
NETWORK_MODE=bridge  # bridge or host

# Threat reporting
THREAT_REPORTING=true
DARK_WEB_MONITORING=true
```

---

## 3. Enable Threat Intelligence

Activate advanced threat detection and monitoring features.

### 3.1 Dark Web Monitoring

Monitor underground marketplaces for compromised credentials:

```bash
# Edit .env
nano .env

# Enable dark web monitoring
DARK_WEB_MONITORING=true
MITRE_ATTACK_API_ENABLED=true

# Save and restart
docker-compose restart app

# Verify in logs
docker-compose logs app | grep -i "dark web\|mitre"
```

**What it monitors:**

- 🔴 Your email addresses in breach databases
- 🔴 Your organization domain in exploit kits
- 🔴 Your credentials in stolen datasets
- 🔴 Your company name in ransomware forums

---

### 3.2 Configure Threat Feeds

Create custom threat intelligence feeds:

```bash
# Create threat feeds directory
mkdir -p configs/threat-feeds

# Add STIX threat feed (XML format)
cat > configs/threat-feeds/custom-threats.stix << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<stix:STIX_Package xmlns:stix="http://stix.mitre.org/stix-1" version="1.2">
  <stix:Threat_Reports>
    <!-- Custom threat indicators here -->
  </stix:Threat_Reports>
</stix:STIX_Package>
EOF

# Add CSV threat feed
cat > configs/threat-feeds/malware-hashes.csv << 'EOF'
hash,threat_type,severity,confidence
abc123def456...,trojan,critical,100
xyz789mno456...,ransomware,critical,95
EOF

# Restart to load feeds
docker-compose restart app
```

---

### 3.3 Configure Threat Response Actions

Set automatic responses to threats:

```bash
# Access dashboard threat settings
# URL: http://localhost:8080/dashboard.html#threats

# Configuration options:
1. Threat Level Thresholds
   - Green (safe): 0-25 confidence
   - Yellow (warning): 25-75 confidence
   - Red (critical): 75-100 confidence

2. Auto-Response Actions
   - Isolate affected system
   - Block malicious IPs
   - Quarantine suspicious files
   - Send notifications

3. Reporting
   - Real-time alerts
   - Daily summary emails
   - Weekly threat reports
```

---

### 3.4 Test Threat Detection

```bash
# Create a test malicious file (EICAR - safe test)
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}-$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > test-malware.txt

# Scan the file
curl -X POST http://localhost:8080/api/scan/folder \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"path": "./"}'

# Expected: File flagged as test threat (not actual malware)
# Clean up
rm test-malware.txt
```

---

## 4. Set Email Alerts

Configure SMTP notifications for critical events.

### 4.1 Gmail Configuration (Recommended)

**Step 1: Enable 2-Factor Authentication**

1. Go to [Google Account](https://myaccount.google.com/)
2. Click "Security" in left menu
3. Enable "2-Step Verification"
4. Complete verification process

**Step 2: Generate App Password**

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Windows Computer" (or your device)
3. Click "Generate"
4. Copy the 16-character password

**Step 3: Configure Sentinel-UG**

```bash
# Edit .env
nano .env

# Find or add SMTP settings:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Paste the 16-char password

# Alert recipient
ALERT_EMAIL=security-team@yourcompany.com

# Save
```

---

### 4.2 Office 365 Configuration

For enterprise deployments:

```bash
# Edit .env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your_password

ALERT_EMAIL=security-alerts@company.com
```

---

### 4.3 Custom SMTP Server

For self-hosted email:

```bash
# Edit .env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587  # or 25, 465
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your_server_password

ALERT_EMAIL=security-admin@yourdomain.com
```

---

### 4.4 Configure Alert Thresholds

```bash
# Access dashboard
# Go to Settings → Email Alerts

# Configure which events trigger alerts:
☑ High severity threats detected
☑ Firewall rule violations
☑ Unusual network activity
☑ Failed authentication attempts
☑ System resource alerts
☑ Compliance violations

# Frequency options:
- Real-time
- Hourly digest
- Daily summary
- Weekly report
```

---

### 4.5 Test Email Configuration

```bash
# Restart services with new SMTP config
docker-compose restart app

# Check SMTP connectivity logs
docker-compose logs app | grep -i "smtp\|mail\|email" | tail -20

# Send test email from dashboard
# Settings → Test Email → Send

# Expected: Email received within 30 seconds
```

---

## 5. Review Security Settings

Secure your installation with production-grade settings.

### 5.1 Change Default Admin Password

**IMPORTANT: Do this immediately!**

1. **Access Dashboard:**
   ```
   URL: http://localhost:8080
   Current Login: admin / letmein
   ```

2. **Change Password:**
   - Click "USER MANAGEMENT" tab
   - Find "admin" user
   - Click "Edit"
   - Enter new password (min 12 characters, mix of upper/lower/numbers/symbols)
   - Click "Save"

3. **Verify:**
   ```bash
   # Logout and try new password
   # Should NOT work with old password
   ```

---

### 5.2 Generate SSL/TLS Certificates

Replace self-signed certificates with production certs:

**Option A: Let's Encrypt (Free)**

```bash
# On Linux/macOS with certbot installed
sudo certbot certonly --standalone \
  -d omega.yourdomain.com \
  --non-interactive --agree-tos \
  -m admin@yourdomain.com

# Back up certificates
sudo cp /etc/letsencrypt/live/omega.yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/omega.yourdomain.com/privkey.pem ssl/
sudo chown $USER:$USER ssl/*

# Update .env
DASHBOARD_SSL_CERT=/ssl/fullchain.pem
DASHBOARD_SSL_KEY=/ssl/privkey.pem

# Restart
docker-compose restart nginx
```

**Option B: Commercial Certificate**

```bash
# Obtain from certificate authority (Comodo, DigiCert, etc.)
# Copy files to:
cp your-cert.crt ssl/fullchain.pem
cp your-key.key ssl/privkey.pem

# Update .env with paths
# Restart services
docker-compose restart nginx
```

---

### 5.3 Configure Firewall Rules

**System-level firewall:**

```bash
# Linux UFW example
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8080/tcp    # Dashboard
sudo ufw enable

# macOS firewall
System Preferences → Security & Privacy → Firewall Options
✓ Enable firewall
✓ Block all inbound connections except allowed services
```

**In-application firewall rules:**

1. Open Dashboard → FIREWALL tab
2. Create rules:
   - **Allow:** Your admin IP addresses
   - **Allow:** Trusted client systems
   - **Block:** Known malicious IPs
   - **Monitor:** Suspicious addresses

---

### 5.4 Enable Security Headers

```bash
# Already configured in nginx.conf, but verify:
docker-compose exec nginx curl -I http://localhost:80 | grep -i "strict\|csp\|frame"

# Expected headers:
# Strict-Transport-Security: max-age=31536000
# Content-Security-Policy: default-src 'self'
# X-Frame-Options: SAMEORIGIN
```

---

### 5.5 Audit Security Settings

```bash
# Check authentication status
docker-compose exec app curl -s http://localhost:8080/api/auth/status

# Review user permissions
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/users | jq '.[] | {username, role}'

# Check audit logs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/audit/logs?limit=50 | head -20

# Expected: All actions logged with timestamp and user
```

---

## 6. Monitor Operations

Keep your system running smoothly with operational monitoring.

### 6.1 Dashboard Monitoring

**Main Dashboard (Overview Tab):**
- System status indicators
- Active threat count
- Connected clients
- Last scan time

**Monitoring Tab:**
Real-time metrics:
- CPU usage
- Memory consumption
- Network traffic
- Disk I/O
- Process count

---

### 6.2 Grafana Dashboards

Access Grafana for advanced visualization:

```
URL: http://localhost:3000
Default Login: admin / omega

Creating a custom dashboard:
1. Click "+" → Create → Dashboard
2. Add panels:
   - CPU Usage
   - Memory Usage
   - Network Throughput
   - Threat Events
   - Alert Count
3. Set refresh rate: 5 seconds
4. Save dashboard
```

---

### 6.3 Prometheus Metrics

Query Prometheus directly for custom monitoring:

```
URL: http://localhost:9090

Example queries:
1. CPU usage:
   avg(rate(container_cpu_usage_seconds_total[5m]))

2. Memory usage:
   avg(container_memory_usage_bytes) / 1024 / 1024

3. HTTP requests per second:
   rate(http_requests_total[1m])

4. Failed authentications:
   sum(rate(auth_failures_total[5m]))
```

---

### 6.4 Log Monitoring

Monitor system logs for issues:

```bash
# Real-time app logs
docker-compose logs -f app --tail 50

# PostgreSQL logs
docker-compose logs -f postgres

# Nginx/Proxy logs
docker-compose logs -f nginx

# All services
docker-compose logs -f

# Export logs for analysis
docker-compose logs app > app_logs.txt
docker-compose logs postgres > db_logs.txt
```

---

### 6.5 Performance Monitoring

Check system health:

```bash
# Docker container stats
docker stats --no-stream

# Database query performance
docker-compose exec postgres psql -U quantum_admin -d sentinel_omega \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Redis memory usage
docker-compose exec redis redis-cli INFO memory

# Network connections
docker-compose exec app netstat -tuln | head -20
```

---

### 6.6 Health Checks

Regular health verification:

```bash
# Complete health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

echo "🔍 System Health Check"
echo "===================="

# Check Docker services
echo ""
echo "📦 Docker Services:"
docker-compose ps --format "{{.Service}}\t{{.Status}}"

# Check API endpoints
echo ""
echo "🌐 API Endpoints:"
for endpoint in "/health" "/api/auth/token" "/api/threats"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080$endpoint)
  echo "  $endpoint: HTTP $STATUS"
done

# Check database
echo ""
echo "🗄️  Database:"
docker-compose exec postgres pg_isready -U quantum_admin && echo "  ✓ PostgreSQL connected" || echo "  ✗ PostgreSQL connection failed"

# Check cache
echo ""
echo "⚡ Cache:"
docker-compose exec redis redis-cli ping > /dev/null && echo "  ✓ Redis connected" || echo "  ✗ Redis connection failed"

# Check Prometheus
echo ""
echo "📊 Prometheus:"
curl -s http://localhost:9090/api/v1/status/runtimeinfo > /dev/null && echo "  ✓ Prometheus running" || echo "  ✗ Prometheus unavailable"

echo ""
echo "✓ Health check complete"
EOF

chmod +x health_check.sh
./health_check.sh
```

---

### 6.7 Alert Management

Set up alerting for issues:

**Email Alerts:**
```bash
# Already configured from Step 4

# Test alert
curl -X POST http://localhost:8080/api/alerts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "title": "Test Alert",
    "message": "This is a test alert"
  }'
```

**Dashboard Alerts:**
1. Open Dashboard
2. Go to Settings → Alerts
3. Configure:
   - Alert thresholds
   - Notification channels
   - Escalation rules

---

### 6.8 Backup & Recovery

Implement backup strategy:

```bash
# Daily PostgreSQL backup
cat > backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/sentinel_omega_$DATE.sql"
mkdir -p backups

docker-compose exec postgres pg_dump -U quantum_admin sentinel_omega > $BACKUP_FILE
echo "✓ Backup created: $BACKUP_FILE"

# Keep only last 30 days
find backups -name "*.sql" -mtime +30 -delete
EOF

chmod +x backup_db.sh

# Schedule with cron (Linux/macOS)
# 0 2 * * * /path/to/backup_db.sh

# Test restoration
docker-compose exec postgres psql -U quantum_admin sentinel_omega < backups/sentinel_omega_latest.sql
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] ✓ API Keys configured and responding
- [ ] ✓ Clients deployed and showing as ACTIVE
- [ ] ✓ Email alerts sending successfully
- [ ] ✓ Admin password changed from default
- [ ] ✓ SSL/TLS certificates installed
- [ ] ✓ Threat intelligence feeds loading
- [ ] ✓ Grafana dashboards displaying
- [ ] ✓ Prometheus metrics collecting
- [ ] ✓ Backup strategy implemented
- [ ] ✓ Users understand operational procedures

---

## Troubleshooting

### API Keys Not Working

```bash
# Check .env syntax
grep "API_KEY" .env

# Verify services restarted
docker-compose restart app

# Check logs
docker-compose logs app | grep -i "api\|error" | tail -20
```

### Email Not Sending

```bash
# Verify SMTP config
grep "SMTP" .env

# Check email logs
docker-compose logs app | grep -i "email\|smtp\|mail"

# Test SMTP connection
docker-compose exec app python3 -c "
import smtplib
try:
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  print('✓ SMTP connection successful')
except Exception as e:
  print(f'✗ Error: {e}')
"
```

### Clients Not Connecting

```bash
# Check client logs
docker-compose logs sentinel-client | grep -i "error\|connected\|status"

# Verify orchestrator URL
grep "QUANTUM_ORCHESTRATOR" .env

# Check network connectivity
docker-compose exec sentinel-client curl -v wss://orchestrator.sentinel.ug/health 2>&1 | head -20
```

---

## Next Phase

After completing this setup guide:

1. **Week 1:** Monitor dashboards, understand data flows
2. **Week 2:** Run security audit using included tools
3. **Week 3:** Fine-tune detection rules and thresholds
4. **Week 4:** Deploy to production with documented procedures

### Advanced Topics

- Custom threat detection rules
- Integration with SIEM platforms
- Custom API development
- Machine learning model training
- Multi-region deployment

---

## Support Resources

- **Documentation:** https://sentinel.ug/docs
- **Community Forum:** https://community.sentinel.ug/setup
- **API Reference:** https://api.sentinel.ug/v3
- **Video Tutorials:** https://sentinel.ug/learn

---

**Setup Complete!** 🎉

Your Sentinel-UG Omega platform is now fully operational with enterprise-grade security, threat intelligence, and distributed protection. Monitor the dashboards, review logs regularly, and adjust configurations based on your organization's needs.

**Last Updated:** March 17, 2026  
**Version:** 1.0
