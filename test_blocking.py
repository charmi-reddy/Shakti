from database import insert_log_hybrid
import socket
import logging
import time

logging.basicConfig(level=logging.INFO)

def auto_block_attacker(mac, signal):
    """Block attacker if signal is strong"""
    try:
        signal_strength = int(signal)
        
        if signal_strength > -50:
            logging.warning(f"🚨 STRONG SIGNAL: {mac} ({signal} dBm)")
            logging.info(f"🚫 Attempting to block...")
            
            with socket.create_connection(("127.0.0.1", 9000), timeout=3) as sock:
                sock.sendall((mac + "\n").encode())
                response = sock.recv(1024).decode().strip()
                
                if "Blocked" in response:
                    logging.info(f"✅ BLOCKED: {mac}")
                    return True
                else:
                    logging.error(f"❌ Failed: {response}")
                    return False
                    
    except ConnectionRefusedError:
        logging.error("❌ Firewall not running!")
    except Exception as e:
        logging.error(f"Error: {e}")
    
    return False

print("="*70)
print("🧪 Testing Auto-Blocking with Strong Signal Attack")
print("="*70)

# Test 1: Distant attacker (weak signal) - LOG ONLY
print("\n1️⃣ Test: Distant Attacker (Weak Signal)")
distant = {
    "mac": "11:22:33:44:55:66",
    "signal": "-75",  # Weak
    "channel": "6",
    "message": "DeAuth - Distant"
}
print(f"   MAC: {distant['mac']}, Signal: {distant['signal']} dBm")
insert_log_hybrid(distant['mac'], distant['signal'], distant['channel'], distant['message'])
blocked = auto_block_attacker(distant['mac'], distant['signal'])
print(f"   Result: {'🚫 BLOCKED' if blocked else '📝 LOGGED ONLY'}")
time.sleep(2)

# Test 2: Nearby attacker (strong signal) - BLOCK!
print("\n2️⃣ Test: Nearby Attacker (Strong Signal)")
nearby = {
    "mac": "DE:AD:BE:EF:00:01",
    "signal": "-35",  # Strong!
    "channel": "11",
    "message": "DeAuth - NEARBY THREAT"
}
print(f"   MAC: {nearby['mac']}, Signal: {nearby['signal']} dBm")
insert_log_hybrid(nearby['mac'], nearby['signal'], nearby['channel'], nearby['message'])
blocked = auto_block_attacker(nearby['mac'], nearby['signal'])
print(f"   Result: {'✅ BLOCKED AND LOGGED' if blocked else '⚠️ BLOCK FAILED'}")
time.sleep(2)

print("\n" + "="*70)
print("🎉 Test Complete!")
print("="*70)
print("\n📊 Check Results:")
print("   - Firewall Terminal: See block messages")
print("   - API: http://localhost:5000/logs")
print("   - Blockchain: http://localhost:5000/logs/blockchain")
