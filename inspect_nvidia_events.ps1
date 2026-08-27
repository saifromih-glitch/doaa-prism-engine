$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$events = Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=(Get-Date).AddDays(-2)} |
    Where-Object { $_.ProviderName -match 'nvidia|nvlddmkm|display' -or $_.Message -match '(?i)nvidia|nvml|nvlddmkm' } |
    Select-Object -First 40 TimeCreated,Id,LevelDisplayName,ProviderName,@{Name='message_prefix';Expression={($_.Message -replace '\s+',' ').Substring(0,[math]::Min(500,($_.Message -replace '\s+',' ').Length))}}
[pscustomobject]@{ events = @($events) } | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-system-events.json')
Write-Output (Join-Path $root 'nvidia-system-events.json')
