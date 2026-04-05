$ErrorActionPreference = "SilentlyContinue"

Write-Host "Killing old servers on 5174, 5175, 5176"
$ports = 5174, 5175, 5176
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen
    foreach ($c in $conns) {
        Stop-Process -Id $c.OwningProcess -Force
    }
}

Write-Host "Starting Vite Servers..."

Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$PWD\vendor-dashboard"
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$PWD\customer-dashboard"
Start-Process -WindowStyle Hidden -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "$PWD\institution-dashboard"

Write-Host "Done!"
