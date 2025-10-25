// Configuration
const API_BASE = 'http://localhost:5000';
let explorerUrl = '';
let logsCache = [];

// Helper: MAC validation
function isMac(mac) {
    return /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/.test(mac.trim());
}

// Fetch data from API
async function fetchData() {
    try {
        const logsRes = await fetch(`${API_BASE}/logs`);
        const logs = await logsRes.json();
        logsCache = logs;

        const blockchainRes = await fetch(`${API_BASE}/logs/blockchain`);
        const blockchain = await blockchainRes.json();

        const hybridRes = await fetch(`${API_BASE}/logs/hybrid`);
        const hybrid = await hybridRes.json();

        document.getElementById('localLogs').textContent = hybrid.local_logs ?? '--';
        document.getElementById('blockchainLogs').textContent = blockchain.total_blockchain_logs ?? '--';
        document.getElementById('appId').textContent = 'App ID: ' + (blockchain.app_id ?? 'N/A');
        explorerUrl = blockchain.explorer ?? '';
        updateTable(logs);
    } catch (error) {
        console.error('Fetch error:', error);
        document.getElementById('logsTable').innerHTML = '<tr><td colspan="6">Backend not running - Start api_server.py</td></tr>';
    }
}

// Determine signal strength class
function signalClass(signal) {
    const val = parseInt(signal);
    return (val > -50) ? 'sigStrong' : 'sigNormal';
}

// Update attacks table
function updateTable(logs) {
    const tbody = document.getElementById('logsTable');
    if (!logs.length) {
        tbody.innerHTML = '<tr><td colspan="6">No attacks detected yet</td></tr>';
        return;
    }
    tbody.innerHTML = logs.slice(0, 20).map((log) => {
        return `<tr>
            <td>${log.timestamp}</td>
            <td class="maccell">${log.mac}</td>
            <td class="${signalClass(log.signal)}">${log.signal}</td>
            <td>${log.channel}</td>
            <td>${log.message}</td>
            <td><button class="blockbtnmac" onclick="blockMAC('${log.mac}')">Block</button></td>
        </tr>`;
    }).join('');
}

// Fetch blocked MAC list
async function fetchBlockedList() {
    try {
        const response = await fetch(`${API_BASE}/blocklist`);
        const data = await response.json();
        const blockedMacs = data.blocked_macs || [];
        
        const content = document.getElementById('blockedContent');
        
        if (blockedMacs.length === 0) {
            content.innerHTML = '<div style="color: #64748b; padding: 20px; text-align: center;">No MACs blocked yet</div>';
            return;
        }
        
        content.innerHTML = `
            <div style="color: #94a3b8; font-size: 0.9em; margin-bottom: 10px;">
                Total: ${data.total} | Last Updated: ${data.last_updated}
            </div>
        ` + blockedMacs.map(mac => `
            <div class="blocked-item">
                <span class="blocked-mac">${mac}</span>
                <button class="unblock-btn" onclick="unblockMAC('${mac}')">Unblock</button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading blocked list:', error);
        document.getElementById('blockedContent').innerHTML = 
            '<div style="color: #ef4444; padding: 20px; text-align: center;">Error loading blocked MACs. Is api_server.py running?</div>';
    }
}

// Toggle blocked list visibility
function toggleBlockedList() {
    const list = document.getElementById('blockedList');
    if (list.classList.contains('show')) {
        list.classList.remove('show');
    } else {
        list.classList.add('show');
        fetchBlockedList();
    }
}

// Block MAC address
async function blockMAC(mac) {
    let toBlock = mac;
    if (!mac) {
        toBlock = document.getElementById('macInput').value.trim();
    }
    const result = document.getElementById('blockResult');
    result.textContent = "";
    
    if (!isMac(toBlock)) {
        result.textContent = "Invalid MAC address format!";
        result.className = "block-result fail";
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/block/${toBlock}`);
        const data = await response.json();
        
        if (response.ok) {
            result.textContent = "Blocked " + toBlock + " successfully.";
            result.className = "block-result success";
            
            // Refresh blocked list if visible
            if (document.getElementById('blockedList').classList.contains('show')) {
                fetchBlockedList();
            }
        } else {
            result.textContent = data.error || "Failed to block MAC!";
            result.className = "block-result fail";
        }
        
        document.getElementById('macInput').value = "";
        if (mac) setTimeout(() => { result.textContent = ""; }, 2200);
    } catch (error) {
        console.error('Block error:', error);
        result.textContent = "Failed to contact firewall backend.";
        result.className = "block-result fail";
    }
}

// Unblock MAC address
async function unblockMAC(mac) {
    try {
        const response = await fetch(`${API_BASE}/unblock/${mac}`);
        const data = await response.json();
        
        if (response.ok) {
            fetchBlockedList();
            
            const result = document.getElementById('blockResult');
            result.textContent = "Unblocked " + mac + " successfully.";
            result.className = "block-result success";
            setTimeout(() => { result.textContent = ""; }, 2200);
        } else {
            alert('Failed to unblock: ' + (data.error || data.message));
        }
    } catch (error) {
        console.error('Unblock error:', error);
        alert('Failed to unblock MAC. Is firewall server running?');
    }
}

// Open blockchain explorer
function openExplorer() {
    if (explorerUrl) {
        window.open(explorerUrl, '_blank');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('macInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') blockMAC();
    });

    // Initial fetch and auto-refresh
    fetchData();
    setInterval(fetchData, 5000);
});
