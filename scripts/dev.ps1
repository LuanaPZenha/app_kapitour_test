# Sobe backend + instrucoes para Expo (modo LAN).
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "=== Kapitour Dev ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Subindo backend Docker..."
docker compose up -d redis auth content engagement commerce kapipass gateway

Start-Sleep -Seconds 3

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -match '^192\.168\.' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ip) { $ip = "127.0.0.1" }

$ok = $false
foreach ($porta in @(8000, 8080)) {
    try {
        $r = Invoke-WebRequest -Uri "http://${ip}:${porta}/api/health" -UseBasicParsing -TimeoutSec 4
        if ($r.StatusCode -eq 200) {
            Write-Host "API OK em http://${ip}:${porta}/api" -ForegroundColor Green
            $ok = $true
            break
        }
    } catch {}
}

if (-not $ok) {
    Write-Host "API nao respondeu. Verifique: docker compose ps" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/2] Em OUTRO terminal, inicie o app:" -ForegroundColor Cyan
Write-Host "  npm install" -ForegroundColor Green
Write-Host "  npm start" -ForegroundColor Green
Write-Host ""
Write-Host "Celular fisico (Expo Go): mesma Wi-Fi, modo LAN (nao Tunnel)."
Write-Host "O app detecta IP/porta do Metro sozinho — nao precisa editar IP no .env."
Write-Host "No log deve aparecer: API via Metro (porta 8081)"
Write-Host ""
Write-Host "Login teste: user@kapitour.com / user123"
Write-Host ""
Write-Host "Se o celular nao conectar, execute UMA VEZ como Admin:"
Write-Host "  scripts\abrir-firewall-api.bat" -ForegroundColor Yellow
