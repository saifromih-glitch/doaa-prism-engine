$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 11438
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB, 2)
if ($freeGiB -lt 5) { throw "Preflight rejected: free memory is $freeGiB GiB." }
$ollama = (Get-Command ollama.exe -ErrorAction Stop).Source
$stdoutPath = Join-Path $root 'proposal-ollama.stdout.log'
$stderrPath = Join-Path $root 'proposal-ollama.stderr.log'
$rawPath = Join-Path $root 'governed-proposal-raw-response.json'
$inputPath = Join-Path $root 'governed-proposal-gate-input.json'
$gatePath = Join-Path $root 'doaa_proposal_gate.py'
$repairPath = Join-Path $root 'doaa_proposal_repair.py'
$auditPath = Join-Path $root 'doaa_audit_log.py'
$auditLogPath = Join-Path $root 'governed-proposal-audit.jsonl'
$receiptPath = Join-Path $root 'governed-proposal-receipt.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$command = 'set CUDA_VISIBLE_DEVICES=-1&& set OLLAMA_LLM_LIBRARY=cpu_avx2&& set OLLAMA_KEEP_ALIVE=0s&& set OLLAMA_HOST=127.0.0.1:' + $port + '&& "' + $ollama + '" serve'
$server = Start-Process cmd.exe -ArgumentList @('/d','/c',$command) -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 8
$tags = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $port + '/api/tags') -Method Get -TimeoutSec 10
if (@($tags.models | Where-Object { $_.name -eq 'qwen3.5:4b' }).Count -ne 1) { taskkill.exe /PID $server.Id /T /F | Out-Null; throw 'Current model is not present.' }
$request = @{goal='Remove ASCII spaces and hyphens from phone column only; preserve name and amount.';table_schema=@(@{name='name';type='text'},@{name='phone';type='text'},@{name='amount';type='number'});dsl_version='1.4'}
$instruction = 'Return one JSON object only and no markdown. Use exactly this schema and no other keys: {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"A short explanation"}. Replace only the rationale text. Do not use proposed_action. Propose only remove_ascii_phone_separators for this request. Never execute anything.'
$body = @{model='qwen3.5:4b';prompt=($instruction + "`nRequest JSON:`n" + ($request | ConvertTo-Json -Depth 5 -Compress));stream=$false;think=$false;format='json';keep_alive='0s';options=@{num_ctx=2048;num_predict=128;temperature=0}} | ConvertTo-Json -Depth 8 -Compress
$http = Invoke-WebRequest -Uri ('http://127.0.0.1:' + $port + '/api/generate') -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 600 -UseBasicParsing
$raw = [string]$http.Content
[System.IO.File]::WriteAllText($rawPath,$raw,$utf8)
$api = $raw | ConvertFrom-Json
$rawModelText = [string]$api.response
$repairInput = @{request=$request;raw_model_text=$rawModelText} | ConvertTo-Json -Depth 8 -Compress
[System.IO.File]::WriteAllText($inputPath,$repairInput,$utf8)
$gateResult = Get-Content -Raw -Encoding UTF8 $inputPath | py -3 $repairPath
[System.IO.File]::WriteAllText((Join-Path $root 'governed-proposal-gate-result.json'),$gateResult,$utf8)
$gateObj = $gateResult | ConvertFrom-Json
$auditInput = @{audit_path=$auditLogPath;request=$request;raw_model_text=$rawModelText;repaired_model_text=$gateObj.repaired_model_text;gate_result=$gateObj;repair_id=$gateObj.repair_id} | ConvertTo-Json -Depth 10 -Compress
$auditRecord = $auditInput | py -3 $auditPath
[pscustomobject]@{contract_id='CONTRACT-LLM-0003-BOUNDED-PROPOSAL-REPAIR';model='qwen3.5:4b';free_memory_gib_before=$freeGiB;raw_saved=$true;audit_record=($auditRecord | ConvertFrom-Json);gate_result=$gateObj;dsl_execution=$false;external_network_request=$false} | ConvertTo-Json -Depth 10 -Compress | Set-Content -Encoding UTF8 $receiptPath
taskkill.exe /PID $server.Id /T /F | Out-Null
Write-Output $receiptPath
