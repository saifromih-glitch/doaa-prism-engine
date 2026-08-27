$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-LLM-0002-ollama-startup-smoke.json') | ConvertFrom-Json
$preflight = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'llm-v2-preflight.json') | ConvertFrom-Json
$receipt = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'llm-v2-receipt.json') | ConvertFrom-Json
$responsePath = Join-Path $root 'llm-v2-response.txt'
$responseLength = if (Test-Path $responsePath) { (Get-Item $responsePath).Length } else { -1 }
$checks = [ordered]@{
    contract_identity = $contract.contract_id -eq 'CONTRACT-LLM-0002' -and $contract.model -eq 'qwen3.5:4b'
    preflight_accepted = $preflight.accepted -eq $true
    timed_out = $receipt.timed_out -eq $true -and $receipt.elapsed_ms -ge 300000
    no_response = $receipt.response_nonempty -eq $false -and $responseLength -eq 0
    no_dsl_execution = $receipt.dsl_executed -eq $false
    no_source_modification = $receipt.source_modified -eq $false
    no_runner_network = $receipt.network_used_by_runner -eq $false
}
$result = [ordered]@{
    verification_id = 'LLM-V2-INDEPENDENT-VERIFY'
    decision = 'reject_integration_no_retry_under_this_contract'
    checks = $checks
    accepted_as_failure_evidence = -not ($checks.Values -contains $false)
    claim_boundary = 'This proves only that the V2 request timed out under the recorded local conditions; it does not prove the model is defective.'
}
$result | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'llm-v2-independent-verification.json')
if (-not $result.accepted_as_failure_evidence) { throw 'V2 independent verification rejected.' }
Write-Output (Join-Path $root 'llm-v2-independent-verification.json')
