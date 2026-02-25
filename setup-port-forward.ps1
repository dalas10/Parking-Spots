# Run this script as Administrator (right-click → Run with PowerShell as Admin)
# It forwards WSL2 ports so your phone can reach the app

$wslIP = "192.168.53.100"

Write-Host "Setting up port forwarding WSL2 -> Windows..." -ForegroundColor Cyan

# Remove old rules if any
netsh interface portproxy delete v4tov4 listenport=3000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=9999 listenaddress=0.0.0.0 2>$null

# Add forwarding rules
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3000 connectaddress=$wslIP connectport=3000
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8000 connectaddress=$wslIP connectport=8000
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9999 connectaddress=$wslIP connectport=9999

# Open firewall
netsh advfirewall firewall delete rule name="Urbee WSL2" 2>$null
netsh advfirewall firewall add rule name="Urbee WSL2" dir=in action=allow protocol=TCP localport=3000,8000,9999

Write-Host ""
Write-Host "Done! Active rules:" -ForegroundColor Green
netsh interface portproxy show v4tov4

Write-Host ""
Write-Host "Your phone can now reach:" -ForegroundColor Green
$winIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "172.*" -and $_.IPAddress -notlike "10.*" -and $_.PrefixOrigin -eq "Dhcp" } | Select-Object -First 1).IPAddress
Write-Host "  Web app:  http://$winIP`:3000" -ForegroundColor Yellow
Write-Host "  APK file: http://$winIP`:9999/urbee-android.apk" -ForegroundColor Yellow
Write-Host "  API:      http://$winIP`:8000" -ForegroundColor Yellow

Read-Host "`nPress Enter to close"
