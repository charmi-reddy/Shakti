# Shakti-2.0 Complete Startup (Python Only - No Rust Needed!)

Write-Host "🔥 Starting Shakti-2.0 Web3 Security System" -ForegroundColor Green
Write-Host "=" * 70

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator!" -ForegroundColor Yellow
    Write-Host "   Firewall blocking may not work properly" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y") {
        exit
    }
}

# Start Python Firewall
Write-Host "1️⃣ Starting Python Firewall Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python firewall_server.py" -Verb RunAs
Start-Sleep -Seconds 3

# Start API Server
Write-Host "2️⃣ Starting Flask API Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python api_server.py"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Shakti-2.0 is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Services:" -ForegroundColor Yellow
Write-Host "   - Firewall Server: http://127.0.0.1:9000" -ForegroundColor White
Write-Host "   - API Server: http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Web Interfaces:" -ForegroundColor Yellow
Write-Host "   - Local Logs: http://localhost:5000/logs" -ForegroundColor White
Write-Host "   - Blockchain: http://localhost:5000/logs/blockchain" -ForegroundColor White
Write-Host "   - Block Attacker: http://localhost:5000/block/<MAC>" -ForegroundColor White
