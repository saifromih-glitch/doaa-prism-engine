$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-OLLAMA-CPU-0003.json') | ConvertFrom-Json
$body = @{model=$contract.model;prompt=$contract.request.prompt;stream=$false;think=$false;keep_alive='0s';options=$contract.request.options} | ConvertTo-Json -Depth 5 -Compress
$rawPath = Join-Path $root 'ollama-cpu-0003-raw-response.json'
$receiptPath = Join-Path $root 'ollama-cpu-0003-receipt.json'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$started = Get-Date
$raw = $null
$parsed = $null
$errorText = $null
try {
    $http = Invoke-WebRequest -Uri 'http://127.0.0.1:11437/api/generate' -Method Post -ContentType 'application/json' -Body $body -TimeoutSec $contract.request.timeout_seconds -UseBasicParsing
    $raw = [string]$http.Content
    [System.IO.File]::WriteAllText($rawPath, $raw, $utf8NoBom)
    $parsed = $raw | ConvertFrom-Json
} catch {
    $errorText = $_.Exception.Message
    if ($null -ne $raw) { [System.IO.File]::WriteAllText($rawPath, $raw, $utf8NoBom) }
}
$responseText = if ($null -ne $parsed -and $null -ne $parsed.response) { [string]$parsed.response } else { $null }
$thinkingText = if ($null -ne $parsed -and $null -ne $parsed.thinking) { [string]$parsed.thinking } else { $null }
$accepted = ($null -ne $parsed) -and -not [string]::IsNullOrWhiteSpace($responseText) -and $responseText -match 'CPU_PERSIST_OK'
[pscustomobject]@{contract_id=$contract.contract_id;elapsed_seconds=[math]::Round(((Get-Date)-$started).TotalSeconds,2);raw_response_saved=(Test-Path $rawPath);raw_response_length=if($null -ne $raw){$raw.Length}else{0};response=$responseText;thinking=$thinkingText;error=$errorText;accepted=$accepted;dsl_execution=$false;external_network_request=$false} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 $receiptPath
if (-not $accepted) { exit 1 }
Write-Output $receiptPath
