# Libera portas 8000 e 8080 (gateway Kapitour) no firewall do Windows.
# Execute como Administrador: clique direito > Executar como administrador

$ErrorActionPreference = "Stop"

function Add-PortRule($nome, $porta) {
    $existente = Get-NetFirewallRule -DisplayName $nome -ErrorAction SilentlyContinue
    if ($existente) {
        Enable-NetFirewallRule -DisplayName $nome
        Write-Host "Regra '$nome' ja existe - habilitada."
    } else {
        New-NetFirewallRule `
            -DisplayName $nome `
            -Direction Inbound `
            -Action Allow `
            -Protocol TCP `
            -LocalPort $porta `
            -Profile Any
        Write-Host "Regra '$nome' criada (porta $porta)."
    }
}

Add-PortRule "Kapitour API 8000" 8000
Add-PortRule "Kapitour API 8080" 8080

$ip = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -match '^192\.168\.' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

Write-Host ""
Write-Host "Firewall configurado."
Write-Host "Teste no celular (mesma Wi-Fi):"
Write-Host "  http://${ip}:8000/api/health"
Write-Host "  http://${ip}:8080/api/health"
Write-Host ""
Write-Host "Suba o backend:"
Write-Host "  docker compose up -d redis auth content engagement commerce kapipass gateway"
Write-Host ""
Write-Host "Inicie o Expo em modo LAN (nao Tunnel):"
Write-Host "  npx expo start --lan"
