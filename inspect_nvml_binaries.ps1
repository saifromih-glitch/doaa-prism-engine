$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$paths = @()
$paths += @(Get-Command nvidia-smi.exe -All -ErrorAction SilentlyContinue | ForEach-Object { $_.Source })
$paths += @('C:\Windows\System32\nvidia-smi.exe','C:\Windows\System32\nvml.dll','C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe','C:\Program Files\NVIDIA Corporation\NVSMI\nvml.dll') | Where-Object { Test-Path $_ }
$items = @($paths | Sort-Object -Unique | ForEach-Object {
    $item = Get-Item $_
    [pscustomobject]@{
        path = $_
        product_version = $item.VersionInfo.ProductVersion
        file_version = $item.VersionInfo.FileVersion
        sha256 = (Get-FileHash -Algorithm SHA256 $_).Hash.ToLowerInvariant()
    }
})
$envPathEntries = $env:PATH -split ';' | Where-Object { $_ -match 'NVIDIA|System32' }
[pscustomobject]@{
    files = $items
    path_entries_relevant = @($envPathEntries)
    nvidia_smi_raw = @(& nvidia-smi.exe 2>&1 | Select-Object -First 20)
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvml-binary-inspection.json')
Write-Output (Join-Path $root 'nvml-binary-inspection.json')
