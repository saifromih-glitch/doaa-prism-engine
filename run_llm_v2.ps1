$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-LLM-0002-ollama-startup-smoke.json') | ConvertFrom-Json
$preflight = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'llm-v2-preflight.json') | ConvertFrom-Json
if (-not $preflight.accepted) { throw 'V2 requires accepted preflight.' }
if ($contract.model -ne 'qwen3.5:4b' -or $contract.dsl_execution_allowed -or $contract.network_allowed) { throw 'V2 contract boundary mismatch.' }
$requestPath = Join-Path $root 'llm-v2-request.txt'
$responsePath = Join-Path $root 'llm-v2-response.txt'
$receiptPath = Join-Path $root 'llm-v2-receipt.json'
[System.IO.File]::WriteAllText($requestPath, $contract.prompt, [System.Text.UTF8Encoding]::new($false))
$info = [System.Diagnostics.ProcessStartInfo]::new()
$info.FileName = 'ollama'
$info.Arguments = "run $($contract.model)"
$info.UseShellExecute = $false
$info.RedirectStandardInput = $true
$info.RedirectStandardOutput = $true
$info.RedirectStandardError = $true
$info.CreateNoWindow = $true
$process = [System.Diagnostics.Process]::new()
$process.StartInfo = $info
$timer = [System.Diagnostics.Stopwatch]::StartNew()
if (-not $process.Start()) { throw 'Could not start Ollama.' }
$process.StandardInput.Write($contract.prompt)
$process.StandardInput.Close()
$finished = $process.WaitForExit([int]$contract.startup_and_response_timeout_seconds * 1000)
if (-not $finished) {
    $process.Kill()
    $process.WaitForExit(10000) | Out-Null
}
$response = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()
$timer.Stop()
$exitCode = if ($finished) { $process.ExitCode } else { -1 }
[System.IO.File]::WriteAllText($responsePath, $response, [System.Text.UTF8Encoding]::new($false))
$receipt = [ordered]@{
    contract_id = $contract.contract_id
    model = $contract.model
    preflight_id = $preflight.preflight_id
    prompt_sha256 = (Get-FileHash -Algorithm SHA256 $requestPath).Hash.ToLowerInvariant()
    response_sha256 = (Get-FileHash -Algorithm SHA256 $responsePath).Hash.ToLowerInvariant()
    elapsed_ms = $timer.ElapsedMilliseconds
    timeout_seconds = $contract.startup_and_response_timeout_seconds
    timed_out = -not $finished
    exit_code = $exitCode
    response_nonempty = -not [string]::IsNullOrWhiteSpace($response)
    stderr_nonempty = -not [string]::IsNullOrWhiteSpace($stderr)
    dsl_executed = $false
    source_modified = $false
    network_used_by_runner = $false
}
$receipt | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 $receiptPath
if ($receipt.timed_out -or $exitCode -ne 0 -or -not $receipt.response_nonempty) { throw 'V2 local request did not produce a usable response.' }
Write-Output $receiptPath
