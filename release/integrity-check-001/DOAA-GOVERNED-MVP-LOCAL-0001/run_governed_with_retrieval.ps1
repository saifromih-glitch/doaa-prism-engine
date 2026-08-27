$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$registry = if($env:DOAA_ALGORITHM_REGISTRY){$env:DOAA_ALGORITHM_REGISTRY}else{Join-Path $root 'algorithm-registry.jsonl'}
$proposal = @{operation='remove_ascii_phone_separators';column='phone';worksheet=$null;dsl_version='1.4'}
$payload = @{registry_path=$registry;proposal=$proposal} | ConvertTo-Json -Depth 6 -Compress
$routerJson = $payload | py -3 (Join-Path $root 'doaa_premodel_router.py')
$router = $routerJson | ConvertFrom-Json
if($router.route -eq 'reuse_candidate'){
  $receipt = [pscustomobject]@{status='reuse_candidate';route='reuse_candidate';model_call=$false;automatic_execution=$false;execution_authority='none';registry_path=$registry;note='Exact registry match found. Continue through human review and safe execution; no model call.'}
  $receipt | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $root 'premodel-router-receipt.json')
  Write-Output (Join-Path $root 'premodel-router-receipt.json')
  exit 0
}
if($router.route -eq 'governed_model_stage'){
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'run_governed_proposal.ps1')
  exit $LASTEXITCODE
}
throw 'Pre-model router blocked the request.'
