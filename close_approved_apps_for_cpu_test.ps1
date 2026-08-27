$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$allowedNames = @('Kimi','Cici','Notion','LinkedIn','WhatsApp.Root','chrome')
$initial = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -in $allowedNames })
$receipt = @()
foreach ($process in $initial) {
    $receipt += [pscustomobject]@{ name = $process.ProcessName; id = $process.Id; action = 'close_requested' }
    if ($process.MainWindowHandle -ne 0) { [void]$process.CloseMainWindow() }
}
Start-Sleep -Seconds 5
foreach ($process in $initial) {
    try {
        $stillRunning = Get-Process -Id $process.Id -ErrorAction Stop
        Stop-Process -Id $stillRunning.Id -Force
        $receipt | Where-Object { $_.id -eq $stillRunning.Id } | ForEach-Object { $_.action = 'force_closed_after_grace_period' }
    } catch {}
}
[pscustomobject]@{
    allowed_process_names = $allowedNames
    closed_processes = @($receipt)
    protected_processes = @('Manus','explorer','ollama','nvidia-smi','system processes')
    timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'approved-app-closure-receipt.json')
Write-Output (Join-Path $root 'approved-app-closure-receipt.json')
