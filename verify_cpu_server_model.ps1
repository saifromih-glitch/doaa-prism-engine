$ErrorActionPreference = 'Stop'
$response = Invoke-RestMethod -Uri 'http://127.0.0.1:11435/api/tags' -Method Get -TimeoutSec 10
$result = [pscustomobject]@{
    model_names = @($response.models | ForEach-Object { $_.name })
    qwen_4b_present = @($response.models | Where-Object { $_.name -eq 'qwen3.5:4b' }).Count -eq 1
}
$result | ConvertTo-Json -Compress
