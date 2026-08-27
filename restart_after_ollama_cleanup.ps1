$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stopped = @()
foreach ($name in @('ollama app', 'ollama', 'llama-server')) {
    $items = @(Get-Process -Name $name -ErrorAction SilentlyContinue)
    foreach ($item in $items) {
        $stopped += [pscustomobject]@{ name = $item.ProcessName; id = $item.Id }
        Stop-Process -Id $item.Id -Force
    }
}
$receipt = [pscustomobject]@{
    action = 'restart_after_ollama_gpu_diagnosis'
    stopped_ollama_processes = @($stopped)
    models_deleted = $false
    source_modified = $false
    windows_driver_modified = $false
    restart_scheduled_seconds = 30
}
$receipt | ConvertTo-Json -Depth 3 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-restart-receipt.json')
Start-Process -FilePath shutdown.exe -ArgumentList @('/r', '/t', '30', '/c', 'Restart approved for Ollama GPU recovery')
Write-Output (Join-Path $root 'ollama-restart-receipt.json')
