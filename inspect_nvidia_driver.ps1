$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Get-CimInstance Win32_PnPSignedDriver |
    Where-Object { $_.DeviceName -like '*NVIDIA*' } |
    Select-Object DeviceName,DriverVersion,DriverDate,InfName,Manufacturer |
    ConvertTo-Json -Compress |
    Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-driver-inspection.json')
Write-Output (Join-Path $root 'nvidia-driver-inspection.json')
