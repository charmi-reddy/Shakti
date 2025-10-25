from algosdk.v2client import algod
from algosdk import transaction, mnemonic
from algosdk.account import address_from_private_key
import base64
import os
import logging
import time

# Configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
APP_ID = 748319582

def load_private_key():
    """Load and properly decode Algorand private key"""
    try:
        with open(".env.local", "r") as f:
            for line in f:
                if line.startswith("ALGORAND_PRIVATE_KEY="):
                    key = line.split("=", 1)[1].strip()
                    # Private key is base64 encoded, decode it
                    return base64.b64decode(key)
                elif line.startswith("ALGORAND_MNEMONIC="):
                    # Alternative: use mnemonic
                    mnemonic_phrase = line.split("=", 1)[1].strip().strip('"')
                    return mnemonic.to_private_key(mnemonic_phrase)
        return None
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        return None

PRIVATE_KEY = load_private_key()
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def insert_log_blockchain(mac, signal, channel, message, retries=3):
    """
    Write attack log to Algorand blockchain with retry logic
    
    Args:
        mac: MAC address
        signal: Signal strength
        channel: Wi-Fi channel
        message: Attack type
        retries: Number of retry attempts
        
    Returns:
        tx_id: Transaction ID or None
    """
    for attempt in range(retries):
        try:
            if not PRIVATE_KEY:
                logging.warning("Blockchain credentials not configured")
                return None
            
            sender = address_from_private_key(PRIVATE_KEY)
            
            # Get transaction parameters
            params = algod_client.suggested_params()
            params.flat_fee = True
            params.fee = 1000
            
            # Prepare application arguments
            app_args = [
                b"log_attack",
                mac.encode('utf-8'),
                str(signal).encode('utf-8'),
                str(channel).encode('utf-8'),
                message.encode('utf-8')
            ]
            
            # Create transaction
            txn = transaction.ApplicationCallTxn(
                sender=sender,
                sp=params,
                index=APP_ID,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args
            )
            
            # Sign and send
            signed_txn = txn.sign(PRIVATE_KEY)
            tx_id = algod_client.send_transaction(signed_txn)
            
            logging.info(f"📡 Transaction sent: {tx_id[:10]}...")
            
            # Wait for confirmation with longer timeout
            result = transaction.wait_for_confirmation(algod_client, tx_id, 10)
            
            logging.info(f"✅ Attack logged on blockchain: Tx {tx_id[:8]}...")
            return tx_id
            
        except Exception as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                logging.warning(f"⚠️  Attempt {attempt + 1}/{retries} failed: {str(e)[:50]}... Retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                logging.error(f"❌ Blockchain logging failed after {retries} attempts: {e}")
                return None
    
    return None


def get_total_logs_blockchain():
    """Query total number of logs from blockchain"""
    try:
        if not PRIVATE_KEY:
            return 0
        
        sender = address_from_private_key(PRIVATE_KEY)
        
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = 1000
        
        app_args = [b"get_total"]
        
        txn = transaction.ApplicationCallTxn(
            sender=sender,
            sp=params,
            index=APP_ID,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=app_args
        )
        
        signed_txn = txn.sign(PRIVATE_KEY)
        tx_id = algod_client.send_transaction(signed_txn)
        
        result = transaction.wait_for_confirmation(algod_client, tx_id, 10)
        
        if 'logs' in result and len(result['logs']) > 0:
            # Decode log count
            import struct
            log_bytes = base64.b64decode(result['logs'][0])
            log_count = struct.unpack('>Q', log_bytes)[0]
            return log_count
        
        return 0
        
    except Exception as e:
        logging.error(f"Failed to query blockchain logs: {e}")
        return 0


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing blockchain integration...")
    print(f"📦 App ID: {APP_ID}")
    print(f"🌐 Network: Algorand TestNet")
    
    if not PRIVATE_KEY:
        print("\n❌ No private key found in .env.local!")
        print("Make sure ALGORAND_PRIVATE_KEY or ALGORAND_MNEMONIC is set")
        exit(1)
    
    sender = address_from_private_key(PRIVATE_KEY)
    print(f"👤 Sender: {sender}")
    
    # Check balance
    try:
        account_info = algod_client.account_info(sender)
        balance = account_info['amount'] / 1_000_000
        print(f"💰 Balance: {balance:.2f} ALGO")
        
        if balance < 0.01:
            print("\n⚠️  Warning: Low balance! Get more from:")
            print("   https://bank.testnet.algorand.network")
    except Exception as e:
        print(f"⚠️  Could not check balance: {e}")
    
    # Test logging
    print("\n1️⃣ Testing log_attack...")
    tx_id = insert_log_blockchain(
        mac="AA:BB:CC:DD:EE:FF",
        signal="-65",
        channel="6",
        message="DeAuth Test"
    )
    
    if tx_id:
        print(f"✅ Test log successful!")
        print(f"   Transaction: https://testnet.explorer.perawallet.app/tx/{tx_id}")
    else:
        print("❌ Test log failed")
    
    # Test query
    print("\n2️⃣ Testing get_total_logs...")
    total = get_total_logs_blockchain()
    print(f"✅ Total logs on blockchain: {total}")
    
    print("\n🎉 Integration test complete!")
    print(f"\n🔗 View your app:")
    print(f"   https://testnet.explorer.perawallet.app/application/{APP_ID}")
