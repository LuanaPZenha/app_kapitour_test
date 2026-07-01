Set-Location (Join-Path $PSScriptRoot "..")

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -match '^192\.168\.' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ip) { $ip = "192.168.1.12" }

$porta = $null
foreach ($p in @(8000, 8080)) {
    try {
        $r = Invoke-WebRequest -Uri "http://${ip}:${p}/api/health" -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) {
            $porta = $p
            break
        }
    } catch {}
}

if (-not $porta) {
    Write-Host "API nao respondeu em 8080 nem 8000. Suba o backend:"
    Write-Host "  docker compose up -d redis auth content engagement commerce kapipass gateway"
    exit 1
}

$line = "EXPO_PUBLIC_API_URL=http://${ip}:${porta}/api"
if (Test-Path .env) {
    $envLines = Get-Content .env
    if ($envLines -match '^EXPO_PUBLIC_API_URL=') {
        ($envLines -replace '^EXPO_PUBLIC_API_URL=.*', $line) | Set-Content .env
    } else {
        Add-Content .env $line
    }
} else {
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    if (Test-Path .env) {
        (Get-Content .env) -replace '^EXPO_PUBLIC_API_URL=.*', $line | Set-Content .env
    } else {
        Set-Content .env $line
    }
}

Write-Host "IP Wi-Fi: $ip"
Write-Host "Porta ativa: $porta"
Write-Host "Atualizado: $line"
Write-Host ""
Write-Host "Teste no celular: http://${ip}:${porta}/api/health"
Write-Host "Reinicie o Expo: npx expo start -c"
