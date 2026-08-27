$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
[pscustomobject]@{
    action = 'restart_after_nvidia_610_88_install'
    approved_by_user = $true
    expected_post_restart_check = 'nvidia-smi then Ollama status only'
    timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-post-install-restart-receipt.json')
Restart-Computer -Force
