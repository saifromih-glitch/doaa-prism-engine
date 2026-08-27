$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -like '*NVIDIA*' } | Select-Object Name,Status,ConfigManagerErrorCode,PNPDeviceID,DriverVersion,AdapterRAM
$pnp = Get-PnpDevice -Class Display | Select-Object Status,Class,FriendlyName,InstanceId,Problem,Present
$services = Get-Service | Where-Object { $_.Name -match 'nvidia|nv' -or $_.DisplayName -match 'nvidia' } | Select-Object Name,DisplayName,Status,StartType
[pscustomobject]@{
    gpu = @($gpu)
    display_devices = @($pnp)
    nvidia_services = @($services)
} | ConvertTo-Json -Depth 6 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-device-health.json')
Write-Output (Join-Path $root 'nvidia-device-health.json')
