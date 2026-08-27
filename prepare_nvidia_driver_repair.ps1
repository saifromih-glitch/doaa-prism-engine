$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$computer = Get-CimInstance Win32_ComputerSystem
$gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -like '*NVIDIA*' } | Select-Object Name,DriverVersion,VideoProcessor
[pscustomobject]@{
    manufacturer = $computer.Manufacturer
    model = $computer.Model
    gpu = @($gpu)
    os = (Get-CimInstance Win32_OperatingSystem).Caption
    architecture = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
    repair_scope = 'official NVIDIA driver installer only; no model deletion and no Doaa source modification'
} | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-repair-preparation.json')
Write-Output (Join-Path $root 'nvidia-repair-preparation.json')
