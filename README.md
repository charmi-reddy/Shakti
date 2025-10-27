#Shakti
A secure web platform with blockchain-enabled logging and firewall protection


🌟 Overview
Shakti is a modular security-focused platform that integrates multiple cutting-edge technologies to provide a robust, transparent, and secure web application environment. Written primarily in Python and JavaScript, with supporting components in Rust and PowerShell, Shakti combines:

Backend Logic — Core Python-based application handling business logic

Firewall Protection — Advanced firewall subsystem for request filtering and security

Blockchain Audit Trail — Immutable logging infrastructure for transparency and accountability

Modern Frontend — Responsive web interface built with JavaScript, HTML, and CSS

Shakti is designed for developers, security engineers, and teams who need a comprehensive demonstration platform that showcases how modern security technologies can work together seamlessly.

✨ Key Features
🔒 Multi-Layer Security: Integrated firewall protection with customizable rule sets

⛓️ Blockchain-Enabled Logging: Immutable audit trails for all critical operations

🎨 Modern UI: Clean, responsive frontend with intuitive user experience

🔧 Modular Architecture: Each component can be extended, modified, or replaced independently

🚀 Easy Deployment: Simple batch script setup for Windows environments

🧪 Comprehensive Testing: Automated test suite for reliability

📦 Lightweight Dependencies: Minimal external dependencies for easy maintenance

🔄 Real-time Monitoring: Live monitoring of system activities and security events

🏗️ Architecture
Shakti follows a modular, layered architecture:

text
┌─────────────────────────────────────┐
│         Frontend (UI Layer)         │
│    JavaScript / HTML / CSS          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│       Core Backend (Logic)          │
│         Python Module               │
└─────────┬───────────┬───────────────┘
          │           │
          ▼           ▼
┌─────────────┐  ┌──────────────────┐
│  Firewall   │  │   Blockchain     │
│   Module    │  │  Audit System    │
└─────────────┘  └──────────────────┘
Technology Stack
Component	Technologies
Backend	Python 3.8+
Frontend	JavaScript (ES6+), HTML5, CSS3
Blockchain	Custom blockchain implementation
Firewall	Python-based firewall engine
Utilities	Rust, PowerShell, Batch scripts
Package Management	pip (Python), npm (Node.js)
📦 Prerequisites
Before installing Shakti, ensure you have the following installed on your system:

Required Software
Python 3.8 or higher - Download Python

Node.js and npm - Download Node.js

Git - Download Git

Modern Web Browser - Chrome, Firefox, Edge, or Safari

Operating System
Windows 10/11 (for batch script support)

Linux/macOS (you may need to create equivalent shell scripts)

Optional
Rust (if modifying Rust components)

Visual Studio Code or preferred code editor

🚀 Installation
Follow these steps to get Shakti up and running on your local machine.

Step 1: Clone the Repository
bash
git clone https://github.com/charmi-reddy/Shakti.git
cd Shakti
Step 2: Install Python Dependencies
Open your terminal or VSCode integrated terminal and run:

bash
pip install -r requirements.txt
This will install all required Python packages listed in requirements.txt.

Step 3: Install Node.js Dependencies (if applicable)
If your frontend has Node.js dependencies:

bash
npm install
Step 4: Verify Installation
Ensure all dependencies are installed correctly:

bash
python --version  # Should show Python 3.8+
node --version    # Should show Node.js version
npm --version     # Should show npm version
⚡ Quick Start
Windows Users
Run the included batch script to start Shakti:

bash
.\start_shakti.bat
This script will:

Open two terminal windows for the backend and frontend servers

Start the Python backend server

Start the frontend development server

Automatically open your default web browser to the application

Linux/macOS Users
Create and run a shell script equivalent:

bash
# Start backend
python core/main.py &

# Start frontend (if applicable)
cd frontend && npm start &

# Open browser
open http://localhost:3000  # macOS
# or
xdg-open http://localhost:3000  # Linux
Accessing the Application
Once started, navigate to:

text
http://localhost:3000


📁 Project Structure
Shakti/
|-- main.py                  # System controller
|-- api_server.py            # HTTP API, logging, block/unblock
|-- database.py              # Data storage for MACs/channels/signal
|-- database_blockchain.py   # Pushes data to Algorand blockchain
|-- firewall_server.py       # Handles MAC blocklist and network policies
|-- smart_contract/          # PyTeal contract(s) for Algorand
|-- frontend/                # React.js client dashboard
|-- requirements.txt         # Python deps
|-- package.json             # Node.js deps
|-- scripts/                 # Utility/setup scripts
|-- tests/                   # Automated tests
|-- start_shakti.bat         # Batch launcher script


🧩 Core Modules
main.py
System controller for detection, logging, firewall actions; coordinates workflow, backend communication, packet analysis, event alerts.

api_server.py
Audit logging and real-time network protection API server; manages HTTP requests to block/unblock MACs, interfaces with dashboard.

database.py
Backend storage for MAC events, signal data, channels, and messages; efficient lookups for network analytics.

database_blockchain.py
Pushes events to Algorand, guaranteeing immutability and audit compliance; syncs backend events with blockchain state.

firewall_server.py
Handles blocklist operations and network access; enforces security policies using detection module outputs.

smart_contract (PyTeal)
Algorand contract recording wireless attacks with full detail and count; enables compliance-ready audit trails.

⚙️ Configuration
requirements.txt, package.json – dependencies

.env – credentials, backend/frontend config

Firewall rules, API endpoints customizable in code or config files

Algorand parameters set in smart contract source

💻 Usage
Starting Individual Components
Backend Only:

bash
python core/main.py
Frontend Only:

bash
cd frontend
npm start
Run Tests:

bash
python -m pytest tests/
API Endpoints (Example)
text
GET  /api/status          - System health check
POST /api/logs            - Add audit log entry
GET  /api/blockchain      - View blockchain
GET  /api/firewall/rules  - View firewall rules
POST /api/firewall/rules  - Add firewall rule
🔧 Troubleshooting
Common Issues
Issue: Port Already in Use

text
Error: Address already in use
Solution: Change the port in your configuration or kill the process using the port:

bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:5000 | xargs kill -9
Issue: Module Not Found

text
ModuleNotFoundError: No module named 'xyz'
Solution: Reinstall dependencies:

bash
pip install -r requirements.txt --force-reinstall
Issue: Frontend Not Loading

Solution:

Check if both servers are running

Verify the API_BASE_URL in the frontend configuration

Check the browser console for errors


🐛 Troubleshooting
Port conflicts: ensure no server is already running (lsof -i :5000)

Node or Python modules not found: reinstall dependencies

Smart contract errors: check Algorand node/sandbox status

UI not loading: verify backend API and check logs


🤝 Contributing
Fork the repo, create a feature branch (git checkout -b feat/xyz)

Run tests on your branch (pytest)

Ensure code/doc updates pass lint/format checks

Open a PR with details and rationale


Getting Help
📝 GitHub Issues

📧 Contact the maintainer

💬 Community discussions

🤝 Contributing
We welcome contributions to Shakti! Here's how you can help:

How to Contribute
Fork the repository

Create a feature branch

bash
git checkout -b feature/amazing-feature
Make your changes

Commit your changes

bash
git commit -m "Add amazing feature"
Push to the branch

bash
git push origin feature/amazing-feature
Open a Pull Request

Code Style Guidelines
Follow PEP 8 for Python code

Use meaningful variable and function names

Add comments for complex logic

Write tests for new features

Update documentation as needed

Version History
v1.0.0 (Current) - Initial release with core features

v0.9.0 - Beta release with basic functionality


🚦 Roadmap
iOS/Android mobile companion app

Advanced analytics (anomaly detection)

Distributed firewall mode (multiple nodes)

On-chain alert escalation

Integration with enterprise SIEM/SOAR tools

Rust-based firewall engine full migration


🙏 Acknowledgments
Inspiration - Various open-source security and blockchain projects

Libraries - Python, Node.js, and the open-source community

Tools - Git, GitHub, VSCode

Community - Thank you to everyone who has tested and provided feedback

📞 Support
If you encounter any issues or have questions:

🐛 Report Bugs: GitHub Issues

💡 Feature Requests: GitHub Discussions

<div align="center">
Made with ❤️ by the Shakti Team

⭐ Star this repository if you find it helpful!

Report Bug · Request Feature · Documentation

</div>
