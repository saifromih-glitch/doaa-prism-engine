$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$os = Get-CimInstance Win32_OperatingSystem
$processes = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 25 @{Name='name';Expression={$_.ProcessName}},Id,@{Name='working_set_mib';Expression={[math]::Round($_.WorkingSet64/1MB,1)}},@{Name='private_memory_mib';Expression={[math]::Round($_.PrivateMemorySize64/1MB,1)}}
[pscustomobject]@{
    free_memory_gib = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
    total_memory_gib = [math]::Round(($os.TotalVisibleMemorySize * 1KB) / 1GB, 2)
    top_processes = @($processes)
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'memory-pressure-inspection.json')
Write-Output (Join-Path $root 'memory-pressure-inspection.json')
