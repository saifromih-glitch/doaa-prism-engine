$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$allowedNames = @('Kimi','Cici','Notion','LinkedIn','WhatsApp.Root','chrome')
$targets = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -in $allowedNames } | Select-Object ProcessName,Id)
$actions = @()
foreach ($target in $targets) {
    $output = @(& taskkill.exe /PID $target.Id /T /F 2>&1)
    $actions += [pscustomobject]@{ name = $target.ProcessName; id = $target.Id; taskkill_output = @($output) }
}
Start-Sleep -Seconds 3
$remaining = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -in $allowedNames } | Select-Object ProcessName,Id)
[pscustomobject]@{
    user_authorized_names = $allowedNames
    taskkill_actions = @($actions)
    remaining_allowed_processes = @($remaining)
    termination_verified = @($remaining).Count -eq 0
} | ConvertTo-Json -Depth 6 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'approved-app-termination-verification.json')
Write-Output (Join-Path $root 'approved-app-termination-verification.json')
