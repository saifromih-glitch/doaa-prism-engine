$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-OLLAMA-CPU-0003.json') | ConvertFrom-Json
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
if ($freeGiB -lt 5) { throw "Preflight rejected: free memory is $freeGiB GiB, below 5 GiB." }
if (Get-NetTCPConnection -LocalPort 11437 -ErrorAction SilentlyContinue) { throw 'Preflight rejected: port 11437 is already in use.' }
$ollama = (Get-Command ollama.exe -ErrorAction Stop).Source
$stdoutPath = Join-Path $root 'ollama-cpu-0003.stdout.log'
$stderrPath = Join-Path $root 'ollama-cpu-0003.stderr.log'
$command = 'set "CUDA_VISIBLE_DEVICES=-1"&& set "OLLAMA_LLM_LIBRARY=cpu_avx2"&& set "OLLAMA_KEEP_ALIVE=0s"&& set "OLLAMA_HOST=127.0.0.1:11437"&& "' + $ollama + '" serve'
$process = Start-Process -FilePath cmd.exe -ArgumentList @('/d','/c',$command) -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -WindowStyle Hidden -PassThru
$tags = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    Start-Sleep -Seconds 2
    try { $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11437/api/tags' -Method Get -TimeoutSec 3; if ($null -ne $tags) { break } } catch {}
}
if ($null -eq $tags) { & taskkill.exe /PID $process.Id /T /F | Out-Null; throw 'Temporary CPU-0003 server did not become ready within 60 seconds.' }
$listeners = @(Get-NetTCPConnection -LocalPort 11437 | Select-Object LocalAddress,LocalPort,State,OwningProcess)
if (@($listeners | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') }).Count -gt 0) { & taskkill.exe /PID $process.Id /T /F | Out-Null; throw 'CPU-0003 server listener was not local-only.' }
if (@($tags.models | Where-Object { $_.name -eq $contract.model }).Count -ne 1) { & taskkill.exe /PID $process.Id /T /F | Out-Null; throw 'CPU-0003 required model is not present.' }
[pscustomobject]@{contract_id=$contract.contract_id;ready=$true;temporary_server_pid=$process.Id;free_memory_gib_before=$freeGiB;listener=@($listeners);model_present=$true;dsl_execution=$false} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-cpu-0003-preflight.json')
Write-Output (Join-Path $root 'ollama-cpu-0003-preflight.json')
