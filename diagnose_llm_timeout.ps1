$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$os = Get-CimInstance Win32_OperatingSystem
$ollamaStatus = & ollama ps 2>&1 | Out-String
$topProcesses = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 8 -Property ProcessName,Id,@{Name='working_set_mib';Expression={[math]::Round($_.WorkingSet64 / 1MB,1)}}
[pscustomobject]@{
    observation = 'The first bounded smoke attempt exceeded its 120-second contract timeout before producing a recorded response; no DSL proposal was executed.'
    free_ram_gib = [math]::Round($os.FreePhysicalMemory / 1MB,2)
    total_ram_gib = [math]::Round($os.TotalVisibleMemorySize / 1MB,2)
    ollama_ps = $ollamaStatus.Trim()
    top_processes = @($topProcesses)
    recommendation = 'Do not retry under CONTRACT-LLM-0001. Require a new contract and explicit decision about available memory or a longer bounded startup allowance.'
} | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'llm-timeout-diagnosis.json')
Write-Output (Join-Path $root 'llm-timeout-diagnosis.json')
