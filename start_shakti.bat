@echo off
title Shakti-2.0 Launcher
echo ========================================
echo   Starting SHAKTI-2.0 System
echo ========================================
echo.

echo [1/3] Starting Firewall Server...
start "Shakti Firewall" cmd /k "cd /d %~dp0 && python firewall/firewall_server.py"
timeout /t 2 /nobreak > nul

echo [2/3] Starting API Server...
start "Shakti API" cmd /k "cd /d %~dp0 && python core/api_server.py"
timeout /t 3 /nobreak > nul

echo [3/3] Opening Dashboard...
start "" "%~dp0frontend\index.html"

echo.
echo ========================================
echo   All services started successfully!
echo ========================================
echo.
echo Dashboard: http://localhost:3000
echo API: http://localhost:5000
echo Firewall: Port 9000
echo.
echo Press any key to exit this window...
pause > nul