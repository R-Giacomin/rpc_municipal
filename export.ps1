# Script de exportação WASM com patch automático de output_max_bytes
# Uso: .\export.ps1

Write-Host "Exportando dashboard para WASM..." -ForegroundColor Cyan
uv run marimo export html-wasm dashboard.py -o ./index.html --mode run --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "Aplicando patch de output_max_bytes (8MB -> 50MB)..." -ForegroundColor Yellow
    $content = Get-Content "index.html" -Raw
    $content = $content -replace '"output_max_bytes":\s*\d+', '"output_max_bytes": 50000000'

    Write-Host "Injetando meta tags de cache-control..." -ForegroundColor Yellow
    $cacheMeta = @"
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
"@
    $content = $content -replace '(<head[^>]*>)', "`$1`n$cacheMeta"

    Set-Content "index.html" -Value $content -NoNewline
    Write-Host "Exportação concluída com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Erro na exportação." -ForegroundColor Red
}
