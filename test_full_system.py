from database import insert_log_hybrid
import logging
import time

logging.basicConfig(level=logging.INFO)

print("=" * 70)
print("🚨 SHAKTI-2.0 WEB3 FULL SYSTEM TEST")
print("=" * 70)

# Simulate 3 real attacks
attacks = [
    {
        "mac": "DE:AD:BE:EF:CA:FE",
        "signal": "-42",
        "channel": "6",
        "message": "DeAuthentication Attack - Strong Signal!"
    },
    {
        "mac": "BA:DC:0F:FE:E0:0D",
        "signal": "-68",
        "channel": "11",
        "message": "Evil Twin AP Detected"
    },
    {
        "mac": "13:37:HA:CK:ER:01",
        "signal": "-55",
        "channel": "1",
        "message": "Probe Request Flood"
    }
]

for i, attack in enumerate(attacks, 1):
    print(f"\n{'='*70}")
    print(f"🎯 Attack #{i}: {attack['message']}")
    print(f"   MAC: {attack['mac']} | Signal: {attack['signal']} | Channel: {attack['channel']}")
    print(f"{'='*70}")
    
    # Log to both SQLite and Blockchain
    insert_log_hybrid(
        mac=attack['mac'],
        signal=attack['signal'],
        channel=attack['channel'],
        message=attack['message']
    )
    
    print(f"✅ Logged to SQLite")
    print(f"🔗 Blockchain transaction initiated...")
    
    # Wait for blockchain confirmation
    print(f"⏳ Waiting 8 seconds for blockchain confirmation...")
    time.sleep(8)

print("\n" + "=" * 70)
print("🎉 ALL ATTACKS LOGGED SUCCESSFULLY!")
print("=" * 70)
print("\n📊 View Results:")
print(f"   Local DB: Check logs/wifi_attack_logs.db")
print(f"   Blockchain: https://testnet.explorer.perawallet.app/application/748319582")
print("\n💻 API Endpoints (start api_server.py first):")
print(f"   http://localhost:5000/logs - Local logs")
print(f"   http://localhost:5000/logs/blockchain - Blockchain stats")
print(f"   http://localhost:5000/logs/hybrid - Combined view")
