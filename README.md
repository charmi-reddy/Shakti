# Shakti
WIDRS-X supports end-to-end encrypted log storage to prevent tampering and unauthorized access. All attack events (Deauth, Evil Twin, Probe Floods, Handshake attempts, etc.) are stored in an encrypted format.
🛡️ WIDRS-X

Wi-Fi Intrusion Detection & Response System (Backend Engine + Rust Firewall)

WIDRS-X is a lightweight backend tool for detecting, analyzing, and blocking Wi-Fi attacks in real-time.
It combines a Python-based Wi-Fi IDS with a Rust-based firewall engine for active defense.

✨ Features

📡 Real-time Wi-Fi Threat Detection (Deauth, Evil Twin, Probe Floods, Handshake attempts)

🚫 Active Defense – Blocks attacker MAC addresses using system firewall (iptables/nftables)

🔐 Encrypted Logging – Secure storage of detected attacks, prevents tampering

⚡ REST API Integration – Flask-based API for external dashboard/frontend use

🖥️ Live Dashboard Support – Frontend "Shakti" visualizes logs & active threats

⚙️ Configurable – Manage interface, thresholds, and logging in config.yaml

📂 Project Structure
widrsx-backend/
│── firewall/          # Rust firewall engine (MAC blocking)
│── main.py            # Python Wi-Fi sniffer & detection engine
│── api_server.py      # Flask API server
│── config.yaml        # Configuration file
_----------------------------------------------------------------After Activate its Virtual Enviorment Only Run Bash Script And SEE Magic_----------------------------
│── logs/              # Encrypted log storage
│── run.sh             # Startup script (builds + runs backend)
