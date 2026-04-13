# LOPUTH JOSEEPH OMEGA - Professional Cybersecurity Firewall Platform

**Enterprise-Grade Network Security & Intrusion Detection System**

---

## 🎯 System Overview

LOPUTH JOSEEPH OMEGA (LOMAG) is a **production-ready cybersecurity monitoring and firewall management platform** combining:

- **Real Network Intrusion Detection** (Zeek/Suricata)
- **Professional Firewall Management** (Windows Defender, UFW, iptables)
- **Live Traffic Analysis** (tcpdump, Wireshark integration)
- **Global Threat Intelligence** (VirusTotal, Shodan, MaxMind GeoIP)
- **Enterprise Dashboard** (FastAPI, PostgreSQL, Redis)
- **Metrics & Alerting** (Prometheus, Grafana)

---

## 📋 Prerequisites

- **Linux Server** (Ubuntu 20.04+ recommended) or Windows with WSL2
- **Docker & Docker Compose**
- **8GB+ RAM** (16GB recommended)
- **50GB+ storage** (for logs and databases)
- **Network admin access** (for firewall rules and packet capture)

---

## 🚀 Deployment

### **For Linux (Ubuntu/Debian)**

```bash
# 1. Download and run deployment script
curl -O https://your-repo/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh

# 2. Wait for services to initialize (2-5 minutes)

# 3. Access the dashboard
# Web UI: http://localhost:8080
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090

# 4. Login
# Username: admin
# Password: letmein (CHANGE THIS!)
```

### **For Windows**

```powershell
# 1. Install Docker Desktop
# 2. Open PowerShell as Administrator
# 3. Clone the repository
git clone https://github.com/sentinel-ug/omega.git
cd omega

# 4. Create .env file
Copy .env.example .env
# Edit .env with your settings

# 5. Run deployment
docker-compose up -d

# 6. Wait 2-5 minutes for initialization
# 7. Access http://localhost:8080 in your browser
```

### **For macOS**

```bash
# Same as Linux, ensure Docker Desktop is installed
# Follow Linux deployment steps
```

---

## ⚙️ Configuration

### **1. Generate Security Keys (Automatic)**

The deployment script automatically generates:
- RSA 4096-bit master key
- 64-byte entropy seed
- JWT secrets
- Database passwords

### **2. Configure API Keys**

Edit `.env` with your credentials:

```bash
# VirusTotal - malware detection
VIRUSTOTAL_API_KEY=your_api_key

# Shodan - network scanning
SHODAN_API_KEY=your_api_key

# MaxMind - IP geolocation
MAXMIND_API_KEY=your_api_key
```

Get free API keys:
- **VirusTotal**: https://www.virustotal.com/api/
- **Shodan**: https://www.shodan.io/api
- **MaxMind**: https://www.maxmind.com/

### **3. Enable SSL/TLS**

```bash
# Automatic (Let's Encrypt)
sudo certbot certonly --standalone -d your-domain.com

# Manual (self-signed)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

---

## 🔍 System Capabilities

### **Real Network Monitoring**
- ✅ Live packet capture and analysis (tcpdump)
- ✅ Network intrusion detection (Zeek)
- ✅ Traffic flow visualization
- ✅ Protocol analysis (TCP/UDP/ICMP)

### **Firewall Management**
- ✅ Create/modify/delete firewall rules
- ✅ View blocked connections in real-time
- ✅ IP whitelisting/blacklisting
- ✅ Port-based filtering
- ✅ Geo-IP blocking

### **Threat Intelligence**
- ✅ VirusTotal file/URL scanning
- ✅ Shodan network reconnaissance
- ✅ MaxMind IP geolocation
- ✅ Global threat map visualization
- ✅ Attack path tracking

### **Security Analytics**
- ✅ 24/7 traffic monitoring
- ✅ Anomaly detection
- ✅ Real-time dashboards
- ✅ Historical trend analysis
- ✅ Alert rules and thresholds

### **Compliance & Audit**
- ✅ Complete activity logging
- ✅ User attribution tracking
- ✅ Exportable audit trails
- ✅ GDPR/SOC2 ready

---

## 🎨 Dashboard Access

| Component | URL | Username | Password |
|-----------|-----|----------|----------|
| **Omega Dashboard** | http://localhost:8080 | admin | letmein |
| **Grafana** | http://localhost:3000 | admin | (from .env) |
| **Prometheus** | http://localhost:9090 | - | - |
| **PostgreSQL** | localhost:5432 | omega_user | (from .env) |
| **Redis** | localhost:6379 | - | (from .env) |

---

## 📊 Key Endpoints

```
GET  /health                    - System health check
POST /auth/token               - User login
GET  /users/me                 - Current user info
GET  /api/users/               - List all users (admin only)
POST /api/users/               - Create user (admin only)
POST /api/scan/folder          - Scan files for threats
POST /api/threats/scan         - VirusTotal lookup
GET  /api/firewall/rules       - Get firewall rules
POST /api/firewall/rules       - Add firewall rule
GET  /api/analytics/metrics    - Get metrics data
WS   /ws/omega                 - Real-time WebSocket feed
```

---

## 🔒 Security Best Practices

1. **Change default passwords immediately**
   ```bash
   docker-compose exec app python -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['pbkdf2_sha256']); print(pwd.hash('your-new-password'))"
   ```

2. **Enable HTTPS**
   - Use Let's Encrypt (automatic via certbot)
   - Update nginx config with SSL paths

3. **Restrict network access**
   - Use firewall rules to limit dashboard access
   - Only expose to trusted networks

4. **Regular backups**
   ```bash
   docker-compose exec db pg_dump -U omega_user omega_db > backup.sql
   ```

5. **Keep software updated**
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## 📈 Monitoring & Logs

### **View application logs**
```bash
docker-compose logs -f app
```

### **View system metrics**
```bash
# CPU, memory, disk
docker stats

# Network traffic
sudo iftop
```

### **Access Grafana dashboards**
- Open http://localhost:3000
- Pre-configured dashboards for:
  - System performance
  - Network traffic
  - Threat statistics
  - User activity

---

## 🛠️ Troubleshooting

### **Services won't start**
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up -d
```

### **Database connection errors**
```bash
# Check PostgreSQL
docker-compose exec db psql -U omega_user -d omega_db -c "SELECT 1"

# Recreate database
docker-compose exec db createdb -U omega_user omega_db
```

### **High memory usage**
```bash
# Check container sizes
docker-compose ps

# Limit resources in docker-compose.yml
# Add under each service:
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

---

## 📚 API Documentation

Visit `/docs` in the web UI for interactive Swagger API documentation.

---

## 🚨 Limitations & Disclaimer

This system is a **monitoring and analysis platform**, not a replacement for:
- **Hardware firewalls** (Cisco, Palo Alto, Fortinet)
- **Intrusion prevention systems** (IPS)
- **Advanced threat protection** (ATP)

For protection against advanced persistent threats (APT), combine with:
- Professional SIEM solutions
- Managed security services (MSS)
- Threat hunting services

---

## 📞 Support & Contributing

- **Issues**: Report via GitHub
- **Documentation**: https://omega.readthedocs.io
- **Community**: https://community.omega.local

---

## 📄 License

Enterprise Security License (ESL) - See LICENSE file

---

**LOPUTH JOSEEPH OMEGA v3.5** | Professional Cybersecurity Platform | 2026
