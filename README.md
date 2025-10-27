# Shakti

## What is Shakti?  
“Shakti” is a project that combines multiple components (core logic, firewall, blockchain, frontend, scripts, tests) into a unified system. Written primarily in Python, JavaScript/HTML/CSS (frontend), plus some Rust and PowerShell scripts, it aims to provide [insert brief high-level purpose here: e.g., “a secure web platform with blockchain-enabled logging and firewall protection”].  
  
### Key modules  
- `core/` — the main backend logic in Python  
- `firewall/` — subsystem handling firewall rules and protections  
- `blockchain/` — blockchain-enabled audit/log infrastructure  
- `frontend/` — client UI built with JavaScript/HTML/CSS  
- `scripts/` — supporting scripts (batch, PowerShell) for setup or utilities  
- `tests/` — automated tests for verifying functionality  
- `requirements.txt` & `package.json` — dependencies for Python and Node side respectively  
- `start_shakti.bat` — simple Windows batch script to launch the system  

## Why this project?  
- Combines multiple security-relevant technologies (firewall, blockchain) into one offering.  
- Modular architecture allows each component to be extended or replaced.  
- The frontend + backend separation makes it easier to build UI features while the backend focuses on logic and security.  
- Aimed at developers, security engineers and integrators who want an end-to-end demonstration platform.

## Who is it for?  
- Developers wanting to explore how to integrate blockchain with logging or audit systems.  
- Security researchers or engineers who want a sandbox for firewall + backend + UI.  
- Teams wanting a prototype or blueprint for a larger project with similar architecture.

---

## Installation  

Follow the steps below to get Shakti up and running on your local machine.

### Prerequisites  
- Python (e.g., Python 3.8+) installed  
- Node.js and npm (for the frontend)  
- Git (to clone the repo)  
- On Windows: batch script support (for `start_shakti.bat`)  
- (Optionally) If you are on Linux/macOS, you may adapt the batch script or create a shell equivalent.

### Step-by-step  

1. Clone the repository:  
   ```bash
   git clone https://github.com/charmi-reddy/Shakti.git
   cd Shakti
2. Run this in your vscode terminal:
   ```bash
   pip install -r requirements.txt
3. Run the start_shakti.bat file:
   ```bash
   .\start_shakti.bat
4. Upon starting, 2 terminals will open to start the servers and then the frontend will opein your default broswer!

