@echo off
echo Killing any existing node processes on ports 5174, 5175, 5176...
for /f "tokens=5" %%a in ('netstat -aon ^| find "5174"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "5175"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find "5176"') do taskkill /f /pid %%a >nul 2>&1

echo Starting Vendor Dashboard on port 5175...
start "Vendor Dashboard" cmd /k "cd vendor-dashboard && npm run dev -- --port 5175"

echo Starting Institution Dashboard on port 5174...
start "Institution Dashboard" cmd /k "cd institution-dashboard && npm run dev -- --port 5174"

echo Starting Customer Dashboard on port 5176...
start "Customer Dashboard" cmd /k "cd customer-dashboard && npm run dev -- --port 5176"

echo All dashboards started! You can close this window.
exit
