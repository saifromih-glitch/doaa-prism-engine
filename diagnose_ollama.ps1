$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
$service = Get-Service | Where-Object { $_.Name -match 'ollama' -or $_.DisplayName -match 'ollama' } | Select-Object Name,DisplayName,Status,StartType
$processes = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|llama-server' } | Select-Object ProcessId,Name,CommandLine
$port = Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
$nvidia = @(& nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits 2>&1)
$logCandidates = @(
    (Join-Path $env:LOCALAPPDATA 'Ollama\logs\server.log'),
    (Join-Path $env:LOCALAPPDATA 'Ollama\server.log'),
    (Join-Path $env:USERPROFILE '.ollama\logs\server.log')
) | Where-Object { Test-Path $_ }
$logSummary = @()
foreach ($path in $logCandidates) {
    $matches = @(Get-Content -Tail 400 $path | Where-Object { $_ -match '(?i)error|fail|panic|cuda|gpu|llama_server|timeout|unable|warn' } | Select-Object -Last 80)
    $logSummary += [pscustomobject]@{ path = $path; size_bytes = (Get-Item $path).Length; relevant_tail = @($matches) }
}
[pscustomobject]@{
    ollama_command = if ($ollamaCommand) { $ollamaCommand.Source } else { $null }
    ollama_version = @(& ollama --version 2>&1)
    services = @($service)
    processes = @($processes)
    port_11434 = @($port)
    nvidia_smi = @($nvidia)
    ollama_ps = @(& ollama ps 2>&1)
    logs = @($logSummary)
} | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-diagnosis.json')
Write-Output (Join-Path $root 'ollama-diagnosis.json')
