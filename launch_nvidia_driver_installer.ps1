$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $root 'NVIDIA-610.88-Studio-Driver.exe'
$verification = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'nvidia-driver-installer-verification.json') | ConvertFrom-Json
if (-not $verification.accepted) { throw 'Unsigned or unapproved NVIDIA installer.' }
Get-Process -Name 'ollama app','ollama','llama-server' -ErrorAction SilentlyContinue | Stop-Process -Force
$process = Start-Process -FilePath $installer -PassThru
[pscustomobject]@{
    action = 'launched_official_nvidia_studio_driver_installer'
    installer_sha256 = $verification.sha256
    signer_subject = $verification.signer_subject
    process_id = $process.Id
    started_utc = (Get-Date).ToUniversalTime().ToString('o')
    ollama_processes_stopped = $true
    models_deleted = $false
    doaa_source_modified = $false
} | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-driver-installer-launch.json')
Write-Output (Join-Path $root 'nvidia-driver-installer-launch.json')
