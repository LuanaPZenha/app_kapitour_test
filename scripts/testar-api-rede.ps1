# Testa se a API responde pelo IP da rede local (como o celular acessa).
$ip = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -match '^192\.168\.' -and $_.PrefixOrigin -ne 'WellKnown' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ip) {
    Write-Host "Nenhum IP 192.168.x.x encontrado. Rode ipconfig e ajuste o .env manualmente."
    exit 1
}

$url = "http://${ip}:8080/api/health"
Write-Host "Testando: $url"

try {
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
    Write-Host "OK ($($resp.StatusCode)): $($resp.Content)"
    Write-Host ""
    Write-Host "No .env use:"
    Write-Host "  EXPO_PUBLIC_API_URL=http://${ip}:8080/api"
} catch {
    Write-Host "FALHOU: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Se falhar aqui, o celular tambem nao vai conectar."
    Write-Host "Execute scripts/abrir-firewall-api.ps1 como Administrador."
    exit 1
}
