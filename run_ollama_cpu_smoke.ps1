$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-OLLAMA-CPU-0001.json') | ConvertFrom-Json
$body = @{
    model = $contract.model
    prompt = $contract.request.prompt
    stream = $false
    keep_alive = '0s'
    options = $contract.request.options
} | ConvertTo-Json -Depth 5 -Compress
$started = Get-Date
$accepted = $false
$responseText = $null
$errorText = $null
try {
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:11435/api/generate' -Method Post -ContentType 'application/json' -Body $body -TimeoutSec $contract.request.timeout_seconds
    $responseText = [string]$response.response
    $accepted = -not [string]::IsNullOrWhiteSpace($responseText) -and $responseText -match 'CPU_SMOKE_OK'
} catch {
    $errorText = $_.Exception.Message
}
$elapsed = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
[pscustomobject]@{
    contract_id = $contract.contract_id
    synthetic_prompt = $contract.request.prompt
    elapsed_seconds = $elapsed
    response = $responseText
    error = $errorText
    accepted = $accepted
    dsl_execution = $false
    external_network_request = $false
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-cpu-smoke-receipt.json')
if (-not $accepted) { exit 1 }
Write-Output (Join-Path $root 'ollama-cpu-smoke-receipt.json')
