$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contractPath = Join-Path $root 'CONTRACT-LLM-0001-local-ollama-smoke.json'
$contract = Get-Content -Raw -Encoding UTF8 $contractPath | ConvertFrom-Json
if ($contract.runtime -ne 'ollama' -or $contract.model -ne 'qwen3.5:4b') { throw 'Contract runtime or model mismatch.' }
if ($contract.network_allowed -or $contract.installation_or_download_allowed -or $contract.source_modification_allowed) { throw 'Contract safety boundary mismatch.' }
$prompt = @"
You are proposing, not executing, a Prism DSL program. Return exactly one JSON object and nothing else.
Required object: {"dsl_version":"1.4","steps":[{"op":"remove_ascii_phone_separators","column":"phone"}]}
Task: Remove ASCII U+0020 spaces and ASCII U+002D hyphens only from the selected synthetic phone field. Preserve all other characters and fields. Do not use tools, commands, network, or explanations.
Synthetic rows:
[{"name":"Amina","phone":"+20 (10) 123-45-67","amount":125},{"name":"Basil","phone":"+20 NBSP 010- 456","amount":80}]
"@
$requestPath = Join-Path $root 'llm-smoke-request.txt'
$responsePath = Join-Path $root 'llm-smoke-response.txt'
$receiptPath = Join-Path $root 'llm-smoke-receipt.json'
[System.IO.File]::WriteAllText($requestPath, $prompt, [System.Text.UTF8Encoding]::new($false))
$processInfo = [System.Diagnostics.ProcessStartInfo]::new()
$processInfo.FileName = 'ollama'
$processInfo.Arguments = "run $($contract.model)"
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardInput = $true
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.CreateNoWindow = $true
$process = [System.Diagnostics.Process]::new()
$process.StartInfo = $processInfo
$watch = [System.Diagnostics.Stopwatch]::StartNew()
if (-not $process.Start()) { throw 'Unable to start local Ollama process.' }
$process.StandardInput.Write($prompt)
$process.StandardInput.Close()
$finished = $process.WaitForExit([int]$contract.timeout_seconds * 1000)
if (-not $finished) {
    $process.Kill($true)
    $process.WaitForExit()
}
$response = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()
$watch.Stop()
$exitCode = if ($finished) { $process.ExitCode } else { -1 }
[System.IO.File]::WriteAllText($responsePath, $response, [System.Text.UTF8Encoding]::new($false))
$receipt = [ordered]@{
    contract_id = $contract.contract_id
    model = $contract.model
    command = 'ollama run qwen3.5:4b <synthetic prompt>'
    request_sha256 = (Get-FileHash -Algorithm SHA256 $requestPath).Hash.ToLowerInvariant()
    response_sha256 = (Get-FileHash -Algorithm SHA256 $responsePath).Hash.ToLowerInvariant()
    response_nonempty = -not [string]::IsNullOrWhiteSpace($response)
    elapsed_ms = $watch.ElapsedMilliseconds
    timeout_seconds = $contract.timeout_seconds
    timed_out = -not $finished
    exit_code = $exitCode
    stderr_nonempty = -not [string]::IsNullOrWhiteSpace($stderr)
    dsl_executed = $false
    source_modified = $false
    network_used_by_runner = $false
}
$receipt | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 $receiptPath
if ($exitCode -ne 0 -or -not $receipt.response_nonempty) { throw 'Local model smoke request failed.' }
Write-Output $receiptPath
