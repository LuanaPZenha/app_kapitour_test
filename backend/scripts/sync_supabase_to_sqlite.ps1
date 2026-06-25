param(
    [Parameter(Mandatory = $false)]
    [string]$DatabaseUrl = $env:SUPABASE_DATABASE_URL
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$dumpFile = Join-Path $root "database\supabase-live.sql"

if (-not $DatabaseUrl) {
    Write-Error "Defina SUPABASE_DATABASE_URL no .env. Exemplo: postgresql://postgres:SUA_SENHA@db.ansbowfekwzbljgrnidk.supabase.co:5432/postgres"
    exit 1
}

Write-Host "1/3 pg_dump do Supabase..."
& (Join-Path $PSScriptRoot "pg_dump_supabase.ps1") -DatabaseUrl $DatabaseUrl -OutputFile $dumpFile

Write-Host "2/3 Importando para SQLite..."
Push-Location (Join-Path $root "backend")
$env:DATABASE_URL = "sqlite:///../database/kapitour.db"
python (Join-Path $PSScriptRoot "import_supabase_backup.py") $dumpFile
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    exit $LASTEXITCODE
}
Pop-Location

Write-Host "3/3 Reiniciando Docker (se existir)..."
docker restart kapitour 2>$null

Write-Host "Sincronizacao concluida."
