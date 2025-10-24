from algosdk.v2client import algod
from algosdk import transaction, account, mnemonic
import base64
import os

# TestNet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

def deploy_contract():
    """Deploy WIDRS contract to Algorand TestNet"""
    
    print("="*70)
    print("🌐 WIDRS-X Web3 Deployment")
    print("="*70)
    
    # Initialize client
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    # Account setup
    print("\n1️⃣  Account Setup")
    print("-" * 70)
    
    if os.path.exists(".env.local"):
        print("Found existing .env.local file")
        use_existing = input("Use existing account? (y/n): ").lower()
        if use_existing == 'y':
            with open(".env.local", "r") as f:
                for line in f:
                    if line.startswith("ALGORAND_MNEMONIC="):
                        mnemonic_phrase = line.split("=", 1)[1].strip().strip('"')
                        private_key = mnemonic.to_private_key(mnemonic_phrase)
                        break
                else:
                    private_key = None
        else:
            private_key = None
    else:
        private_key = None
    
    if not private_key:
        create_new = input("Create new account? (y/n): ").lower()
        if create_new == 'y':
            private_key, address = account.generate_account()
            account_mnemonic = mnemonic.from_private_key(private_key)
            
            print("\n⚠️  IMPORTANT: Save this mnemonic phrase!")
            print("-" * 70)
            print(account_mnemonic)
            print("-" * 70)
            
            # Save to .env.local
            with open(".env.local", "w") as f:
                f.write(f'ALGORAND_MNEMONIC="{account_mnemonic}"\n')
                f.write(f'ALGORAND_ADDRESS="{address}"\n')
                f.write(f'ALGORAND_PRIVATE_KEY="{private_key}"\n')
            
            print("\n✅ Saved to .env.local")
            print(f"\n📍 Your TestNet Address: {address}")
            print(f"\n🪙  Get free TestNet ALGO:")
            print(f"   https://bank.testnet.algorand.network")
            print(f"\n   Paste your address: {address}")
            input("\n⏸️  Press ENTER after funding your account...")
        else:
            mnemonic_phrase = input("Enter your 25-word mnemonic: ")
            private_key = mnemonic.to_private_key(mnemonic_phrase)
    
    sender = account.address_from_private_key(private_key)
    
    # Check balance
    print("\n2️⃣  Checking Balance")
    print("-" * 70)
    try:
        account_info = algod_client.account_info(sender)
        balance = account_info['amount'] / 1_000_000
        print(f"✅ Balance: {balance:.2f} ALGO")
        
        if balance < 0.1:
            print("\n❌ Insufficient balance!")
            print(f"   Current: {balance:.2f} ALGO")
            print(f"   Required: 0.1 ALGO minimum")
            print(f"\n🪙  Get more from: https://bank.testnet.algorand.network")
            print(f"   Address: {sender}")
            return None
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return None
    
    # Compile TEAL
    print("\n3️⃣  Compiling Smart Contract")
    print("-" * 70)
    
    if not os.path.exists("widrs_approval.teal"):
        print("⚠️  TEAL files not found. Compiling now...")
        import subprocess
        result = subprocess.run(["python", "widrs_pyteal.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Compilation failed: {result.stderr}")
            return None
    
    try:
        with open("widrs_approval.teal", "r") as f:
            approval_teal = f.read()
        
        with open("widrs_clear.teal", "r") as f:
            clear_teal = f.read()
        
        print("✅ Loaded TEAL programs")
    except FileNotFoundError:
        print("❌ Run 'python widrs_pyteal.py' first!")
        return None
    
    # Compile to bytecode
    print("🔄 Compiling to bytecode...")
    approval_result = algod_client.compile(approval_teal)
    approval_program = base64.b64decode(approval_result['result'])
    
    clear_result = algod_client.compile(clear_teal)
    clear_program = base64.b64decode(clear_result['result'])
    print("✅ Bytecode compiled")
    
    # Deploy
    print("\n4️⃣  Deploying to Algorand TestNet")
    print("-" * 70)
    
    params = algod_client.suggested_params()
    
    txn = transaction.ApplicationCreateTxn(
        sender=sender,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(num_uints=2, num_byte_slices=2),
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0),
    )
    
    signed_txn = txn.sign(private_key)
    tx_id = algod_client.send_transaction(signed_txn)
    
    print(f"📡 Transaction sent: {tx_id}")
    print("⏳ Waiting for confirmation...")
    
    try:
        result = transaction.wait_for_confirmation(algod_client, tx_id, 4)
        app_id = result['application-index']
        
        print("\n" + "="*70)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"\n📦 App ID: {app_id}")
        print(f"\n🔗 View on Explorer:")
        print(f"   https://testnet.explorer.perawallet.app/application/{app_id}")
        print(f"\n📝 Add to your .env file:")
        print(f"   WIDRS_APP_ID={app_id}")
        print("="*70)
        
        # Update .env.local
        with open(".env.local", "a") as f:
            f.write(f"\nWIDRS_APP_ID={app_id}\n")
        
        print("\n✅ Configuration saved to .env.local")
        
        return app_id
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return None


if __name__ == "__main__":
    try:
        deploy_contract()
    except KeyboardInterrupt:
        print("\n\n⏹️  Deployment cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
