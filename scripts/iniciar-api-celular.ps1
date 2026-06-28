# Backend acessível no celular via porta 8000 (firewall Windows).
# Para a porta 8000, o container kapitour-communication-api precisa estar parado.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "Parando kapitour-communication-api (libera porta 8000)..."
docker stop kapitour-communication-api 2>$null

Write-Host "Subindo gateway na porta 8000..."
docker compose -f docker-compose.yml -f docker-compose.dev-mobile.yml up -d redis auth content engagement commerce kapipass gateway

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -match '^192\.168\.' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ip) { $ip = "192.168.1.7" }

$line = "EXPO_PUBLIC_API_URL=http://${ip}:8000/api"
if (Test-Path .env) {
    $envLines = Get-Content .env
    if ($envLines -match '^EXPO_PUBLIC_API_URL=') {
        ($envLines -replace '^EXPO_PUBLIC_API_URL=.*', $line) | Set-Content .env
    } else {
        Add-Content .env $line
    }
}

Write-Host ""
Write-Host "API no celular: http://${ip}:8000/api"
Write-Host ".env atualizado: $line"
Write-Host ""
Write-Host "Teste no navegador do celular:"
Write-Host "  http://${ip}:8000/api/health"
Write-Host ""
Write-Host "Depois reinicie o Expo: npx expo start -c"
Write-Host ""

try {
    $r = Invoke-WebRequest -Uri "http://${ip}:8000/api/health" -UseBasicParsing -TimeoutSec 8
    Write-Host "OK: $($r.Content)"
} catch {
    Write-Host "Aviso: teste local falhou - confira docker compose ps"
}
