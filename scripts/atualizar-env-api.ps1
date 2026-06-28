Set-Location (Join-Path $PSScriptRoot "..")
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
} else {
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    Add-Content .env $line
}
Write-Host "Atualizado: $line"
