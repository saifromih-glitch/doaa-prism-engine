$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$items = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match 'nvidia|setup|installer' -or $_.CommandLine -match 'NVIDIA-610\.88' } |
    Select-Object ProcessId,Name,CommandLine
[pscustomobject]@{
    matching_processes = @($items)
    installer_exists = Test-Path (Join-Path $root 'NVIDIA-610.88-Studio-Driver.exe')
    launch_receipt_exists = Test-Path (Join-Path $root 'nvidia-driver-installer-launch.json')
} | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-installer-process-inspection.json')
Write-Output (Join-Path $root 'nvidia-installer-process-inspection.json')
