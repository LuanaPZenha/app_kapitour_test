# Libera a porta 8080 (gateway Kapitour) no firewall do Windows.
# Execute como Administrador: clique direito > "Executar com PowerShell" como admin
# ou: Start-Process powershell -Verb RunAs -ArgumentList '-File scripts/abrir-firewall-api.ps1'

$ruleName = "Kapitour API 8080"
$existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existing) {
    Write-Host "Regra '$ruleName' ja existe. Habilitando..."
    Enable-NetFirewallRule -DisplayName $ruleName
} else {
    New-NetFirewallRule `
        -DisplayName $ruleName `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort 8080 `
        -Profile Any
    Write-Host "Regra '$ruleName' criada com sucesso."
}

Write-Host ""
Write-Host "Teste no celular (mesma Wi-Fi):"
Write-Host "  http://192.168.1.7:8080/api/health"
Write-Host ""
