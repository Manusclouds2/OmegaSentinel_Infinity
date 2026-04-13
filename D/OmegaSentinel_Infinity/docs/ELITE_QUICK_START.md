# ELITE MALWARE DEFENSE SYSTEM - QUICK START GUIDE

## 🚀 GETTING STARTED

### Prerequisites
```bash
# Python 3.13+
# All dependencies in requirements.txt installed
pip install -r requirements.txt
```

### Starting the Server
```bash
# Run Sentinel-UG Omega with elite defense
python app.py

# Or with Uvicorn
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🛡️ QUICK DEFENSE OPERATIONS

### 1. RUN FULL SYSTEM SCAN (Find All Malware)

```bash
# Login first
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=letmein"

# Extract token from response
TOKEN="<your-jwt-token>"

# Run full system scan
curl -X POST http://localhost:8000/api/elite/scan-system-wide \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_scan": true}'

# Response includes:
# - Total files scanned
# - Critical threats found
# - Quarantined files
# - Threat locations
```

### 2. DETECT ALL THREATS (Comprehensive)

```bash
curl -X POST http://localhost:8000/api/elite/detect-threats \
  -H "Authorization: Bearer $TOKEN"

# Detects:
# ✅ Malware in running processes
# ✅ Ransomware encrypting files  
# ✅ Zero-day attacks via behavior
# ✅ Suspicious process activity
```

### 3. RANSOMWARE PROTECTION CHECK

```bash
curl -X POST http://localhost:8000/api/elite/ransomware-protection \
  -H "Authorization: Bearer $TOKEN"

# Shows:
# - Encrypted files detected
# - Mass modification attempts
# - Ransom note presence
# - VSS deletion status
# - Overall risk level
```

### 4. ADVANCED FILE ANALYSIS

```bash
curl -X POST http://localhost:8000/api/elite/scan-file-advanced \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "C:\\downloads\\suspicious.exe"
  }'

# Analyzes:
# - Known malware database
# - File header signatures
# - Entropy (packing detection)
# - Behavioral scoring
# - ML threat prediction
```

---

## ⚡ IMMEDIATE THREAT RESPONSE

### Kill Malicious Process

```bash
# Option 1: Kill specific process by PID
curl -X POST http://localhost:8000/api/elite/immediate-kill/1234 \
  -H "Authorization: Bearer $TOKEN"

# Option 2: Detect and kill threats automatically
curl -X POST http://localhost:8000/api/elite/detect-threats \
  -H "Authorization: Bearer $TOKEN"
# (Elite responder automatically responds to detected threats)
```

### Enable Military-Grade Defense (Auto-Kill)

```bash
# WARNING: This enables automatic process termination!
curl -X POST http://localhost:8000/api/elite/enable-military-grade-defense \
  -H "Authorization: Bearer $TOKEN"

# System now:
# ✅ Auto-kills HIGH+ threats
# ✅ Auto-quarantines files
# ✅ Auto-blocks network
# ✅ Emergency isolation ready
```

### Emergency: Kill All Threats

```bash
# LAST RESORT ONLY
curl -X POST http://localhost:8000/api/elite/emergency-kill-all \
  -H "Authorization: Bearer $TOKEN"

# Actions:
# 🔴 Kill all detected threat processes
# 🔴 Isolate network
# 🔴 Emergency lockdown activated
# 🔴 System in full defense mode
```

---

## 📊 MONITORING & STATS

### Check Defense System Status

```bash
curl -X GET http://localhost:8000/api/elite/defense-status \
  -H "Authorization: Bearer $TOKEN"

# Shows:
# - Auto-kill status (enabled/disabled)
# - Defense mode (AGGRESSIVE/NORMAL)
# - Threats processed
# - Threat database size
# - Scan statistics
```

### View Threat Database

```bash
curl -X GET http://localhost:8000/api/elite/defense-status \
  -H "Authorization: Bearer $TOKEN" | jq '.threat_database'

# Shows:
# - Total known threats
# - Learned threats count
# - Last database update
```

---

## 🧪 TESTING THE SYSTEM

### Run Test Suite

```bash
# Run elite defense tests
python test_elite_defense.py

# Tests cover:
# ✅ Malware detection
# ✅ Ransomware detection
# ✅ System scanning
# ✅ Auto-response
# ✅ Zero-day detection
# ✅ Multi-layer integration
```

### Manual Threat Simulation (Safe Test)

```bash
# Create test file
echo "test malware" > test_threat.exe

# Scan the file
curl -X POST http://localhost:8000/api/elite/scan-file-advanced \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test_threat.exe"
  }'

# Check quarantine
# File should be moved to quarantine/ folder
```

---

## 🔍 TROUBLESHOOTING

### System Scan Too Slow
**Solution**: Use quick scan instead of full scan
```bash
-d '{"full_scan": false}'  # Only scans Downloads, Temp, etc
```

### False Positives (Legitimate Files Quarantined)
**Solution**: Check quarantine folder and restore
```bash
# Files are in: quarantine/ folder
# Move them back if safe
mv quarantine/filename.quarantine original_location/filename
```

### Auto-Kill Not Working
**Check**:
1. Is auto-kill enabled? `GET /api/elite/defense-status`
2. Is user admin? Only admins can enable auto-kill
3. Are processes killable? Some system processes cannot be killed

### Zero-Day Detection False Alarms
**These are normal**:
- System baseline takes time to stabilize
- Large downloads = network spikes
- Updates = CPU spikes
Monitor for patterns, not single events

---

## 📋 DEFENSE WORKFLOW

### Standard Protection (Always On)

```
1. Real-time file monitoring (FileMonitor)
2. Process monitoring (ProcessMonitor)  
3. Network monitoring (NetworkMonitor)
4. Threat detection (AdvancedMalwareDetector)
5. Ransomware detection (RansomwareDetector)
6. Zero-day detection (ZeroDayDetector)
7. Auto-quarantine enabled (EliteAutoResponder)
```

### Aggressive Defense (When Threat Detected)

```
1. Detect threat (all 5 detection engines)
2. Analyze threat level (LOW/MEDIUM/HIGH/CRITICAL)
3. Response based on level:
   - CRITICAL: Kill + Quarantine + Isolate
   - HIGH: Kill + Quarantine + Firewall
   - MEDIUM: Alert + Quarantine
   - LOW: Log
4. Update threat database
5. Log audit trail
```

### Military-Grade Defense (When Enabled)

```
1. All threats auto-killed
2. Auto-quarantine all suspicious files
3. Firewall blocks all detected threats
4. Network isolation available
5. Emergency lockdown can be triggered
6. Zero tolerance - instant response
```

---

## 🔐 SECURITY BEST PRACTICES

1. **Regular Scans**: Run full system scan weekly
2. **Monitor Quarantine**: Check quarantine/ folder regularly
3. **Update Threat DB**: Keep installed via auto-learn
4. **Review Logs**: Check logs/app.log for threat activity
5. **Backup Important Files**: Before aggressive scanning
6. **Test Policies**: Use test files before enabling auto-kill
7. **Document Changes**: Keep records of threat responses

---

## 📞 SUPPORT

**If System Overwhelmed**:
```bash
# Disable military mode
POST /api/elite/disable-military-grade-defense

# Reboot system
# Clear quarantine/ folder  
# Review logs in logs/app.log
```

**For Complete Reset**:
```bash
# Remove threat database
rm threat_database.json

# Clear scan history
# System reinitializes on restart

# Restart server
```

---

## 🎯 COMMAND REFERENCE

| Command | Purpose | Risk |
|---------|---------|------|
| `scan-system-wide` | Full disk scan | Low |
| `detect-threats` | Comprehensive detection | Low |
| `ransomware-protection` | Check for encryption | Low |
| `immediate-kill/{pid}` | Kill one process | Medium |
| `emergency-kill-all` | Kill all threats | High |
| `enable-military-grade-defense` | Auto-kill enabled | High |
| `emergency-kill-all` | System lockdown | Critical |

---

## ⚠️ REMEMBER

🔴 **Never enable military-grade defense without understanding implications**  
🔴 **Backup important files before aggressive scanning**  
🔴 **Monitor quarantine for false positives**  
🔴 **Review logs for attack patterns**  
🔴 **Only admins can enable dangerous features**  

**Your system is now protected by military-grade malware defense.**

---

*Elite Malware Defense System v4.0*  
*Sentinel-UG Omega*  
*Stop all malware instantly and automatically*
