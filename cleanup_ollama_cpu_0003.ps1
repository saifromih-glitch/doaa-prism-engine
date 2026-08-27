$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$listeners = @(Get-NetTCPConnection -LocalPort 11437 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
$terminated = @()
foreach ($processId in $listeners) {
    $terminated += [pscustomobject]@{ pid = $processId; action = 'taskkill_tree' }
    & taskkill.exe /PID $processId /T /F | Out-Null
}
Start-Sleep -Seconds 3
$remaining = @(Get-NetTCPConnection -LocalPort 11437 -ErrorAction SilentlyContinue)
[pscustomobject]@{temporary_port=11437;terminated_listener_processes=@($terminated);port_closed=@($remaining).Count -eq 0;default_ollama_ps=@(& ollama.exe ps 2>&1);models_deleted=$false;doaa_source_modified=$false} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-cpu-0003-cleanup.json')
if (@($remaining).Count -ne 0) { throw 'Temporary CPU-0003 port remained open after cleanup.' }
Write-Output (Join-Path $root 'ollama-cpu-0003-cleanup.json')
