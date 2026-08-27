$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-LLM-0002-ollama-startup-smoke.json') | ConvertFrom-Json
$os = Get-CimInstance Win32_OperatingSystem
$freeRamGiB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$activeRows = @(& ollama ps 2>$null | Select-Object -Skip 1 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$installedRows = @(& ollama list 2>$null | Select-Object -Skip 1 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$modelInstalled = @($installedRows | Where-Object { $_ -match '^qwen3\.5:4b\s' }).Count -eq 1
$checks = [ordered]@{
    contract_identity = $contract.contract_id -eq 'CONTRACT-LLM-0002' -and $contract.model -eq 'qwen3.5:4b'
    free_ram = $freeRamGiB -ge [double]$contract.preflight.minimum_free_ram_gib
    no_active_model = $activeRows.Count -eq 0
    model_installed = $modelInstalled
    no_network = -not $contract.network_allowed
    no_dsl_execution = -not $contract.dsl_execution_allowed
}
$result = [ordered]@{
    preflight_id = 'LLM-V2-PREFLIGHT'
    free_ram_gib = $freeRamGiB
    active_ollama_rows = @($activeRows)
    checks = $checks
    accepted = -not ($checks.Values -contains $false)
}
$result | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'llm-v2-preflight.json')
if (-not $result.accepted) { throw 'LLM V2 preflight rejected.' }
Write-Output (Join-Path $root 'llm-v2-preflight.json')
