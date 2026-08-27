$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ollamaRows = @(& ollama ps 2>$null | Select-Object -Skip 1 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($ollamaRows.Count -gt 0) { throw 'A model appears active; refusing cleanup.' }
$processes = @(Get-Process -Name 'llama-server' -ErrorAction SilentlyContinue)
$before = @($processes | ForEach-Object { [pscustomobject]@{ id = $_.Id; working_set_mib = [math]::Round($_.WorkingSet64 / 1MB, 1) } })
$processes | Stop-Process -Force
$receipt = [pscustomobject]@{
    action = 'terminated_lingering_llama_server_after_timed_out_smoke_test'
    ollama_models_active_before_cleanup = $false
    terminated_processes = @($before)
    source_modified = $false
    models_deleted = $false
    windows_configuration_changed = $false
}
$receipt | ConvertTo-Json -Depth 3 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'llama-timeout-cleanup-receipt.json')
Write-Output (Join-Path $root 'llama-timeout-cleanup-receipt.json')
