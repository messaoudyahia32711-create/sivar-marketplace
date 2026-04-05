$ErrorActionPreference = "SilentlyContinue"
$ports = 8000, 5173, 5174, 5175, 5176, 5177
Write-Host "Killing old servers on ports: $($ports -join ', ')"

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen
    if ($connections) {
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force
            Write-Host "Killed process $($conn.OwningProcess) on port $port"
        }
    }
}

Start-Sleep -Seconds 2
Write-Host "Starting Django Backend..."
Start-Process -WindowStyle Hidden -FilePath "venv\Scripts\python.exe" -ArgumentList "manage.py runserver 0.0.0.0:8000" -WorkingDirectory $(Get-Location)

Write-Host "Starting Vendor Dashboard..."
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$(Get-Location)\vendor-dashboard"

Write-Host "Starting Customer Dashboard..."
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$(Get-Location)\customer-dashboard"

Write-Host "Starting Institution Dashboard..."
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$(Get-Location)\institution-dashboard"

Write-Host "Starting Incubator Dashboard..."
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$(Get-Location)\incubator-dashboard"

Write-Host "All servers started!"
