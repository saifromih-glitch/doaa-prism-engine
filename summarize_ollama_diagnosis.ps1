$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$processes = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|llama-server' } | ForEach-Object { [pscustomobject]@{ process_id = $_.ProcessId; name = $_.Name; command_line_prefix = if ($_.CommandLine) { $_.CommandLine.Substring(0, [math]::Min(300, $_.CommandLine.Length)) } else { $null } } }
$nvidia = @(& nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits 2>&1 | Select-Object -First 5)
$logPaths = @((Join-Path $env:LOCALAPPDATA 'Ollama\logs\server.log'), (Join-Path $env:LOCALAPPDATA 'Ollama\server.log'), (Join-Path $env:USERPROFILE '.ollama\logs\server.log')) | Where-Object { Test-Path $_ }
$errors = @()
foreach ($logPath in $logPaths) {
    $errors += @(Get-Content -Tail 300 $logPath | Where-Object { $_ -match '(?i)error|fail|panic|cuda|gpu|timeout|unable' } | Select-Object -Last 15 | ForEach-Object { $_.Substring(0, [math]::Min(500, $_.Length)) })
}
[pscustomobject]@{
    ollama_version = @(& ollama --version 2>&1 | Select-Object -First 3)
    ollama_ps = @(& ollama ps 2>&1 | Select-Object -First 5)
    processes = @($processes)
    gpu = @($nvidia)
    relevant_log_lines = @($errors | Select-Object -Last 30)
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-diagnosis-summary.json')
Write-Output (Join-Path $root 'ollama-diagnosis-summary.json')
