$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-OLLAMA-CPU-0002.json') | ConvertFrom-Json
$body = @{
    model = $contract.model
    prompt = $contract.request.prompt
    stream = $false
    think = $false
    keep_alive = '0s'
    options = $contract.request.options
} | ConvertTo-Json -Depth 5 -Compress
$rawPath = Join-Path $root 'ollama-cpu-0002-raw-response.json'
$receiptPath = Join-Path $root 'ollama-cpu-0002-receipt.json'
$started = Get-Date
$raw = $null
$parsed = $null
$errorText = $null
try {
    $http = Invoke-WebRequest -Uri 'http://127.0.0.1:11436/api/generate' -Method Post -ContentType 'application/json' -Body $body -TimeoutSec $contract.request.timeout_seconds -UseBasicParsing
    $raw = [string]$http.Content
    Set-Content -Encoding UTF8 -NoNewline $rawPath $raw
    $parsed = $raw | ConvertFrom-Json
} catch {
    $errorText = $_.Exception.Message
    if ($null -ne $raw) { Set-Content -Encoding UTF8 -NoNewline $rawPath $raw }
}
$responseText = if ($null -ne $parsed -and $null -ne $parsed.response) { [string]$parsed.response } else { $null }
$thinkingText = if ($null -ne $parsed -and $null -ne $parsed.thinking) { [string]$parsed.thinking } else { $null }
$accepted = ($null -ne $parsed) -and -not [string]::IsNullOrWhiteSpace($responseText) -and $responseText -match 'CPU_RAW_OK'
[pscustomobject]@{
    contract_id = $contract.contract_id
    elapsed_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
    raw_response_saved = Test-Path $rawPath
    raw_response_length = if ($null -ne $raw) { $raw.Length } else { 0 }
    response = $responseText
    thinking = $thinkingText
    error = $errorText
    accepted = $accepted
    dsl_execution = $false
    external_network_request = $false
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 $receiptPath
if (-not $accepted) { exit 1 }
Write-Output $receiptPath
