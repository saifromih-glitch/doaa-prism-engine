$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$contract = Get-Content -Raw -Encoding UTF8 (Join-Path $root 'CONTRACT-OLLAMA-CPU-0001.json') | ConvertFrom-Json
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
if ($freeGiB -lt 5) { throw "Preflight rejected: free memory is $freeGiB GiB, below 5 GiB." }
if (Get-NetTCPConnection -LocalPort 11435 -ErrorAction SilentlyContinue) { throw 'Preflight rejected: port 11435 is already in use.' }
$ollama = (Get-Command ollama.exe -ErrorAction Stop).Source
$logPath = Join-Path $root 'ollama-cpu-isolation-server.stdout.log'
$errorPath = Join-Path $root 'ollama-cpu-isolation-server.stderr.log'
$command = 'set "CUDA_VISIBLE_DEVICES=-1"&& set "OLLAMA_LLM_LIBRARY=cpu_avx2"&& set "OLLAMA_KEEP_ALIVE=0s"&& set "OLLAMA_HOST=127.0.0.1:11435"&& "' + $ollama + '" serve'
$process = Start-Process -FilePath cmd.exe -ArgumentList @('/d','/c',$command) -RedirectStandardOutput $logPath -RedirectStandardError $errorPath -WindowStyle Hidden -PassThru
$ready = $false
for ($attempt = 1; $attempt -le 30; $attempt++) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-RestMethod -Uri 'http://127.0.0.1:11435/api/tags' -Method Get -TimeoutSec 3
        if ($null -ne $response) { $ready = $true; break }
    } catch {}
}
if (-not $ready) {
    & taskkill.exe /PID $process.Id /T /F | Out-Null
    throw 'Temporary CPU-only Ollama server did not become ready within 60 seconds.'
}
$listeners = Get-NetTCPConnection -LocalPort 11435 | Select-Object LocalAddress,LocalPort,State,OwningProcess
if (@($listeners | Where-Object { $_.LocalAddress -notin @('127.0.0.1','::1') }).Count -gt 0) {
    & taskkill.exe /PID $process.Id /T /F | Out-Null
    throw 'Temporary CPU-only server listener was not local-only.'
}
[pscustomobject]@{
    contract_id = $contract.contract_id
    ready = $ready
    temporary_server_pid = $process.Id
    free_memory_gib_before = $freeGiB
    listener = @($listeners)
    log_path = $logPath
    model_present = @($response.models | Where-Object { $_.name -eq $contract.model }).Count -eq 1
    dsl_execution = $false
} | ConvertTo-Json -Depth 5 -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'ollama-cpu-isolation-preflight.json')
Write-Output (Join-Path $root 'ollama-cpu-isolation-preflight.json')
