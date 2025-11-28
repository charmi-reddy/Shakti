import socket
import threading
import logging
import re
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)

HOST = "127.0.0.1"
PORT = 9000
MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")

# In-memory blocklist (simulates firewall blocking)
# In production, this would integrate with actual Windows Firewall
blocked_macs = set()
block_log_file = "logs/blocked_macs.json"

def load_blocklist():
    """Load previously blocked MACs from file"""
    global blocked_macs
    try:
        with open(block_log_file, 'r') as f:
            data = json.load(f)
            blocked_macs = set(data.get('blocked_macs', []))
            logging.info(f"📋 Loaded {len(blocked_macs)} previously blocked MACs")
    except FileNotFoundError:
        blocked_macs = set()
        logging.info("📋 No previous blocklist found, starting fresh")
    except Exception as e:
        logging.error(f"Error loading blocklist: {e}")
        blocked_macs = set()

def save_blocklist():
    """Save blocked MACs to file"""
    try:
        import os
        os.makedirs('logs', exist_ok=True)
        
        data = {
            'blocked_macs': list(blocked_macs),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_blocked': len(blocked_macs)
        }
        
        with open(block_log_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        logging.error(f"Error saving blocklist: {e}")

def is_valid_mac(mac):
    """Validate MAC address format"""
    return MAC_REGEX.match(mac) is not None

def block_mac(mac):
    """
    Block MAC address (Windows-compatible simulation)
    
    Note: Real Windows firewall blocking by MAC requires:
    - Network driver support
    - Advanced firewall rules
    - Or third-party tools
    
    This implementation maintains a blocklist that can be used by:
    1. The detection engine to ignore/alert on blocked MACs
    2. Integration with network equipment
    3. Export to actual firewall solutions
    """
    try:
        mac_lower = mac.lower()
        
        if mac_lower in blocked_macs:
            return True, f"MAC {mac} already blocked (total: {len(blocked_macs)})"
        
        # Add to blocklist
        blocked_macs.add(mac_lower)
        
        # Save to persistent storage
        save_blocklist()
        
        # Log the block
        logging.info(f"✅ Added {mac} to blocklist")
        
        return True, f"Successfully added {mac} to blocklist (total: {len(blocked_macs)})"
        
    except Exception as e:
        return False, f"Exception: {str(e)}"

def is_blocked(mac):
    """Check if MAC is in blocklist"""
    return mac.lower() in blocked_macs

def get_blocklist():
    """Get current blocklist"""
    return list(blocked_macs)

def unblock_mac(mac):
    """Remove MAC from blocklist"""
    try:
        mac_lower = mac.lower()
        if mac_lower in blocked_macs:
            blocked_macs.remove(mac_lower)
            save_blocklist()
            return True, f"Removed {mac} from blocklist"
        else:
            return False, f"MAC {mac} not in blocklist"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def handle_client(conn, addr):
    """Handle client connection and blocking requests"""
    logging.info(f"🔗 New connection from {addr}")
    
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        
        if not data:
            return
        
        # Handle different commands
        parts = data.split()
        command = parts[0].upper() if parts else ""
        mac = parts[1] if len(parts) > 1 else data.strip()
        
        if command == "UNBLOCK":
            # Unblock command
            if not is_valid_mac(mac):
                response = f"Invalid MAC address format: {mac}\n"
                logging.warning(f"⚠️  {response.strip()}")
            else:
                success, message = unblock_mac(mac)
                response = f"{message}\n"
                if success:
                    logging.info(f"♻️  {message}")
                else:
                    logging.warning(f"⚠️  {message}")
                    
        elif command == "LIST":
            # List all blocked MACs
            macs = get_blocklist()
            response = f"Blocked MACs ({len(macs)}): {', '.join(macs)}\n"
            logging.info(f"📋 Sent blocklist: {len(macs)} MACs")
            
        elif command == "CHECK":
            # Check if MAC is blocked
            if not is_valid_mac(mac):
                response = f"Invalid MAC address format: {mac}\n"
            else:
                blocked = is_blocked(mac)
                response = f"MAC {mac}: {'BLOCKED' if blocked else 'NOT BLOCKED'}\n"
                
        else:
            # Default: Block MAC
            mac = data.strip()
            logging.info(f"🚫 Block request for MAC: {mac}")
            
            if not is_valid_mac(mac):
                response = f"Invalid MAC address format: {mac}\n"
                logging.warning(f"⚠️  {response.strip()}")
            else:
                success, message = block_mac(mac)
                
                if success:
                    response = f"Blocked MAC: {mac}\n"
                    logging.info(f"✅ {message}")
                else:
                    response = f"Failed to block {mac}: {message}\n"
                    logging.error(f"❌ {response.strip()}")
        
        conn.sendall(response.encode('utf-8'))
        
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        conn.close()

def start_firewall_server():
    """Start the firewall server"""
    print("=" * 70)
    print("🔥 Shakti Firewall Server (Windows Edition)")
    print("=" * 70)
    print(f"🌐 Listening on {HOST}:{PORT}")
    print()
    print("📝 Commands:")
    print("   <MAC>          - Block MAC address")
    print("   UNBLOCK <MAC>  - Unblock MAC address")
    print("   LIST           - Show all blocked MACs")
    print("   CHECK <MAC>    - Check if MAC is blocked")
    print()
    print("ℹ️  Note: This maintains a persistent blocklist in logs/blocked_macs.json")
    print("   Integrate with your network equipment for actual blocking")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    # Load existing blocklist
    load_blocklist()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        logging.info(f"✅ Server started successfully")
        
        while True:
            conn, addr = server_socket.accept()
            # Handle each client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down firewall server...")
        print(f"📊 Final stats: {len(blocked_macs)} MACs blocked")
        save_blocklist()
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        server_socket.close()
        logging.info("✅ Server stopped")

if __name__ == "__main__":
    start_firewall_server()

# Add this to the end of firewall_server.py

import flask
from flask import Flask, jsonify
app = Flask("blocklist_api")

@app.route("/blocklist")
def blocklist():
    try:
        with open("logs/blocked_macs.json","r") as f:
            data = json.load(f)
        return jsonify(data.get("blocked_macs",[]))
    except:
        return jsonify([])
    
if __name__ == "__main__":
    # (Don't run Flask by default here; run only if passed a flag!)
    pass
