@echo off
:: Clique direito > Executar como administrador
powershell -ExecutionPolicy Bypass -File "%~dp0abrir-firewall-api.ps1"
pause
