from pyteal import *

def approval_program():
    """WIDRS Logger - PyTeal Version (Works on Windows!)"""
    
    # State variables
    log_count = Bytes("log_count")
    
    # Handle creation
    handle_creation = Seq([
        App.globalPut(log_count, Int(0)),
        Return(Int(1))
    ])
    
    # Handle log_attack call
    handle_log_attack = Seq([
        # Increment log counter
        App.globalPut(log_count, App.globalGet(log_count) + Int(1)),
        
        # Log the attack data
        # Args: [0]=method_name, [1]=mac, [2]=signal, [3]=channel, [4]=attack_type
        Log(Concat(
            Bytes("LOG:"),
            Itob(App.globalGet(log_count)),
            Bytes("|"),
            Txn.application_args[1],
            Bytes("|"),
            Txn.application_args[2],
            Bytes("|"),
            Txn.application_args[3],
            Bytes("|"),
            Txn.application_args[4],
            Bytes("|"),
            Itob(Global.latest_timestamp())
        )),
        
        Return(Int(1))
    ])
    
    # Handle get_total_logs call
    handle_get_total = Seq([
        Log(Itob(App.globalGet(log_count))),
        Return(Int(1))
    ])
    
    # Main program logic
    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.application_args[0] == Bytes("log_attack"), handle_log_attack],
        [Txn.application_args[0] == Bytes("get_total"), handle_get_total],
    )
    
    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    # Compile to TEAL
    print("🔨 Compiling WIDRS Smart Contract...")
    
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=10)
    clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=10)
    
    with open("widrs_approval.teal", "w") as f:
        f.write(approval_teal)
    
    with open("widrs_clear.teal", "w") as f:
        f.write(clear_teal)
    
    print("✅ Compilation successful!")
    print("   📄 widrs_approval.teal")
    print("   📄 widrs_clear.teal")
    print("\n🚀 Next step: python deploy_widrs.py")
