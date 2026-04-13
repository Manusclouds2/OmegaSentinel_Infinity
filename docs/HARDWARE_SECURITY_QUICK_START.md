# Hardware Security & Post-Quantum Cryptography - Quick Start Guide

## 🚀 Quick Start

### 1. Enable Hardware Security Monitoring

```bash
# Start the system
python app.py

# The system will automatically:
# ✅ Detect TPM 2.0 on your hardware
# ✅ Check Secure Boot status
# ✅ Initialize measured boot verification
# ✅ Enable auto-recovery capability
# ✅ Setup post-quantum cryptography
```

---

## 🔐 Hardware Root of Trust

### Check Hardware Security Status
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/hardware/root-of-trust-status
```

**Response Example:**
```json
{
  "timestamp": "2025-01-15T10:30:00",
  "system": "Windows",
  "architecture": "x86_64",
  "tpm": {
    "available": true,
    "version": "2.0"
  },
  "secure_boot": {
    "enabled": true,
    "status": "Active"
  },
  "measurements": 5,
  "integrity_status": "INTEGRITY_OK"
}
```

### Measure Boot Components
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/hardware/measure-boot-components
```

**What Gets Measured:**
- BIOS/UEFI firmware
- Boot configuration (BCD/GRUB)
- Bootloader integrity
- Kernel file hashes
- Driver signatures

### Create Golden Image (for Recovery)
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"path": ".recovery/golden_image.json"}' \
  http://localhost:8000/api/hardware/create-golden-image
```

---

## 🔒 Measured Boot Verification

### Perform Boot Integrity Check
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/measured-boot/perform-check
```

**Check Results:**
- ✅ PASS: All boot components authentic
- ❌ FAIL: Boot tampering detected → Auto-recovery triggered

### Store Boot Baseline
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"filepath": ".recovery/boot_baseline.json"}' \
  http://localhost:8000/api/measured-boot/store-baseline
```

### Compare with Baseline
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"baseline_path": ".recovery/boot_baseline.json"}' \
  http://localhost:8000/api/measured-boot/compare-baseline
```

**Use Case**: Detect boot-time rootkits or BIOS modifications

---

## 🔄 Auto-Recovery & Self-Healing

### Check Auto-Recovery Status
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/auto-recovery/status
```

**Response:**
```json
{
  "recovery_enabled": true,
  "consecutive_failures": 0,
  "recovery_threshold": 3,
  "total_recovery_attempts": 0,
  "golden_image_exists": true
}
```

### Enable Auto-Recovery
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/auto-recovery/enable
```

**When Auto-Recovery Triggers:**
- 3 consecutive integrity failures detected
- Critical boot tampering detected
- System compromise confirmed
- Admin-initiated manual recovery

### Create Recovery Snapshot
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"output_path": ".recovery/golden_image.json"}' \
  http://localhost:8000/api/auto-recovery/create-golden-image
```

### Manual Recovery Trigger (Emergency)
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Emergency: Detected rootkit"}' \
  http://localhost:8000/api/auto-recovery/manual-trigger
```

---

## 🌐 Post-Quantum Cryptography

### Check Quantum Security Status
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/security/quantum-status
```

**Response:**
```json
{
  "status": "Quantum-Resistant Protection Active",
  "active_algorithm": "ML-KEM-768",
  "supported_algorithms": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
  "harvested_attacks_resistance": "Enabled",
  "harvest_protection_active": true
}
```

### Generate ML-KEM Keypair
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"security_level": "ML-KEM-768"}' \
  http://localhost:8000/api/security/generate-ml-kem-keypair
```

**Security Levels:**
- `ML-KEM-512`: 512-bit quantum resistance
- `ML-KEM-768`: 768-bit (RECOMMENDED)
- `ML-KEM-1024`: 1024-bit (MAXIMUM)

### Perform Hybrid Key Exchange
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "classical_key": "RSA_KEY_HERE",
    "ml_kem_key": {"public_key": {...}}
  }' \
  http://localhost:8000/api/security/quantum-key-exchange
```

**Result**: Hybrid security combining:
- Classical RSA-4096 encryption
- Post-quantum ML-KEM encryption
- Protection against quantum computers

### Activate "Harvest Now, Decrypt Later" Protection
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"data": "sensitive_data_here"}' \
  http://localhost:8000/api/security/harvest-protection
```

**What This Does:**
- Protects data captured today against future quantum decryption
- Uses current quantum-resistant encryption
- Guards long-term secrets (e.g., government data, cryptographic keys)
- Prevents "Harvest Now, Decrypt Later" attacks

### Encrypt Data with Quantum-Resistant Key
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "confidential_message",
    "shared_secret": "generated_shared_secret_hash"
  }' \
  http://localhost:8000/api/security/encrypt-with-quantum-resistant
```

### Sign Data with Quantum-Resistant Signature
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "document_to_sign",
    "private_key": {"bytes": "..."}
  }' \
  http://localhost:8000/api/security/sign-data-quantum-resistant
```

### Create Post-Quantum Certificate
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_name": "Sentinel-UG Omega",
    "validity_days": 365
  }' \
  http://localhost:8000/api/security/create-pqc-certificate
```

---

## 🛡️ Real-World Usage Scenarios

### Scenario 1: Suspect Boot-Time Compromise
```bash
# Step 1: Perform integrity check
curl -X POST http://localhost:8000/api/measured-boot/perform-check

# If FAIL detected:
# Step 2: Trigger auto-recovery
curl -X POST http://localhost:8000/api/auto-recovery/manual-trigger

# Step 3: Monitor recovery progress
curl http://localhost:8000/api/auto-recovery/status
```

### Scenario 2: Protect Long-Term Secrets Against Quantum
```bash
# Generate quantum-resistant keys
curl -X POST http://localhost:8000/api/security/generate-ml-kem-keypair

# Protect sensitive data now
curl -X POST http://localhost:8000/api/security/harvest-protection

# Encrypt with post-quantum key
curl -X POST http://localhost:8000/api/security/encrypt-with-quantum-resistant

# Sign with quantum-resistant signature
curl -X POST http://localhost:8000/api/security/sign-data-quantum-resistant
```

### Scenario 3: Enterprise Deployment with Golden Image
```bash
# Create clean system snapshot
curl -X POST http://localhost:8000/api/hardware/create-golden-image

# Store boot baseline
curl -X POST http://localhost:8000/api/measured-boot/store-baseline

# Enable auto-recovery
curl -X POST http://localhost:8000/api/auto-recovery/enable

# System now automatically recovers on compromise
# Each boot verified against baseline
# Critical failures trigger self-healing
```

---

## 📊 Monitoring Dashboard

### Get Complete Security Status
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/status
```

### Components Monitored
```
✅ Hardware Root of Trust (TPM + Secure Boot)
✅ Measured Boot Verification (PCR-based)
✅ Auto-Recovery Status (Ready/Active/Disabled)
✅ Quantum Security (ML-KEM Active)
✅ Recent Boot Integrity Checks
✅ Recovery Attempts
✅ Threat Detection Status
```

---

## ⚙️ Configuration

### Auto-Recovery Sensitivity
**Default**: Recovery after 3 consecutive integrity failures

**To Change:**
```python
# In app.py, modify:
auto_recovery_system.recovery_threshold = 5  # Change as needed
```

### TPM PCR Monitoring
**Monitored PCRs:**
- PCR-0: BIOS code
- PCR-1: BIOS configuration
- PCR-4: Boot loader
- PCR-7: Secure Boot state
- PCR-8: Kernel command line
- PCR-9: Kernel modules

### Post-Quantum Algorithm Selection
**Recommended**: ML-KEM-768 (good balance of security and performance)

- ML-KEM-512: Fast, minimum security
- ML-KEM-768: Balanced (RECOMMENDED)
- ML-KEM-1024: Maximum security (slower)

---

## 🔍 Troubleshooting

### TPM Not Detected
```bash
# Windows: Check TPM service
Get-Service -Name TPM

# Linux: Check device
ls -la /dev/tpm*

# macOS: Check Secure Enclave
system_profiler SPiBridgeItem | grep Enclave
```

### Boot Integrity Fails
1. Verify baseline measurements are stored
2. Check BIOS hasn't been updated
3. Verify Secure Boot settings unchanged
4. If tampering suspected, trigger auto-recovery

### Auto-Recovery Won't Trigger
```bash
# Enable auto-recovery system
curl -X POST http://localhost:8000/api/auto-recovery/enable

# Verify it's enabled
curl http://localhost:8000/api/auto-recovery/status
```

---

## 🚨 Security Best Practices

1. **Store Golden Image Safely**
   - Keep `.recovery/golden_image.json` secure
   - Use encrypted storage
   - Version control snapshots

2. **Regular Baseline Updates**
   - Update boot baseline after patches
   - Store multiple baselines for comparison
   - Version each baseline

3. **Quantum-Ready Transition**
   - Start using ML-KEM for new keys
   - Protect long-term secrets with PQC
   - Gradually migrate to hybrid approach

4. **Monitor Integrity**
   - Run boot integrity checks regularly
   - Set auto-recovery sensitivity appropriately
   - Review recovery logs

5. **Backup Secrets**
   - Backup post-quantum keys securely
   - Use hardware security keys for storage
   - Implement key rotation

---

## 📚 Additional Resources

- **NIST Post-Quantum Cryptography**: https://csrc.nist.gov/projects/post-quantum-cryptography
- **ML-KEM (Kyber) Specification**: FIPS 203
- **TPM 2.0 Specification**: https://trustedcomputinggroup.org/
- **Measured Boot**: https://en.wikipedia.org/wiki/Measured_Boot

---

**Sentinel-UG Omega v6.0 - Enterprise Hardware Security Platform**
