param(
    [Parameter(Mandatory = $false)]
    [string]$DatabaseUrl = $env:SUPABASE_DATABASE_URL,

    [Parameter(Mandatory = $false)]
    [string]$OutputFile = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..\database")).Path "supabase-live.sql")
)

if (-not $DatabaseUrl) {
    Write-Error "Defina SUPABASE_DATABASE_URL no .env ou passe -DatabaseUrl."
    exit 1
}

$uri = [Uri]$DatabaseUrl
$user = [Uri]::UnescapeDataString($uri.UserInfo.Split(":")[0])
$pass = [Uri]::UnescapeDataString($uri.UserInfo.Split(":")[1])
$hostName = $uri.Host
$port = if ($uri.Port -gt 0) { $uri.Port } else { 5432 }
$dbName = $uri.AbsolutePath.TrimStart("/")

$outputDir = Split-Path $OutputFile -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Gerando dump em: $OutputFile"

docker run --rm `
    -e PGPASSWORD=$pass `
    -e PGSSLMODE=require `
    -v "${outputDir}:/backup" `
    postgres:16 `
    pg_dump `
        -h $hostName `
        -p $port `
        -U $user `
        -d $dbName `
        --no-owner `
        --no-acl `
        -F p `
        -f "/backup/$(Split-Path $OutputFile -Leaf)"

if ($LASTEXITCODE -ne 0) {
    Write-Error "pg_dump falhou. Verifique senha, internet e se o projeto Supabase esta ativo."
    exit $LASTEXITCODE
}

Write-Host "Dump concluido: $OutputFile"
