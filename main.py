from scapy.all import sniff, Dot11Deauth
import yaml
from database import insert_log_hybrid
import logging
import socket

try:
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    interface = config.get('interface')
    log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
except Exception as e:
    logging.basicConfig(level=logging.INFO)
    logging.error(f"Failed to load config.yaml: {e}")
    exit(1)

logging.basicConfig(level=log_level)

if not interface:
    logging.error("No interface specified in config.yaml.")
    exit(1)

def is_mac_blocked(mac):
    """Check if MAC is in the firewall blocklist (Windows-friendly)"""
    try:
        with socket.create_connection(("127.0.0.1", 9000), timeout=2) as sock:
            sock.sendall(f"CHECK {mac}\n".encode())
            response = sock.recv(1024).decode().strip()
            return "BLOCKED" in response
    except Exception as e:
        logging.warning(f"(Firewall check failed, assuming not blocked) {e}")
        return False

def auto_block_attacker(mac, signal):
    """Add attacker to the firewall blocklist if signal is strong (simulated block for Windows)"""
    try:
        signal_strength = int(signal)
        if signal_strength > -50:
            logging.warning(f"🚨 Strong signal ({signal_strength} dBm) detected for {mac}. Attempting to block.")
            try:
                with socket.create_connection(("127.0.0.1", 9000), timeout=2) as sock:
                    sock.sendall(f"{mac}\n".encode())
                    response = sock.recv(1024).decode().strip()
                    if "Blocked" in response:
                        logging.info(f"✅ BLOCKED: {mac}")
            except Exception as e:
                logging.error(f"❌ Failed to block {mac}: {e}")
    except Exception as e:
        logging.warning(f"(Signal parse failed: {signal}) {e}")

def handle_packet(pkt):
    if pkt.haslayer(Dot11Deauth):
        mac = getattr(pkt, 'addr2', "Unknown")
        signal = getattr(pkt, 'dBm_AntSignal', "?")

        # Extract channel
        channel_val = "Unknown"
        elt = pkt.getlayer('Dot11Elt')
        while elt is not None:
            if hasattr(elt, 'ID') and elt.ID == 3:
                try:
                    channel_val = str(elt.info[0])
                except Exception:
                    channel_val = "Unknown"
                break
            elt = elt.payload.getlayer('Dot11Elt')

        msg = "DeAuthentication"

        # Check if the MAC is already blocked
        if is_mac_blocked(mac):
            logging.info(f"⚠️  Ignoring packet from already-blocked MAC: {mac}")
            return

        # Hybrid log (SQLite + Blockchain)
        insert_log_hybrid(mac, signal, channel_val, msg)

        # Auto-block if strong signal
        auto_block_attacker(mac, signal)

        logging.info(f"🚨 DeAuth Detected: MAC={mac}, Signal={signal}, Channel={channel_val}")

logging.info(f"[*] Starting Wi-Fi sniffing on interface: {interface}")
try:
    sniff(prn=handle_packet, iface=interface, store=0)
except KeyboardInterrupt:
    logging.info("[*] Sniffing stopped by user.")
except Exception as e:
    logging.error(f"Error during sniffing: {e}")
