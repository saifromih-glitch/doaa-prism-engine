$ErrorActionPreference = 'Stop'
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$gpus = Get-CimInstance Win32_VideoController | ForEach-Object {
    [pscustomobject]@{
        name = $_.Name
        adapter_ram_gib = if ($_.AdapterRAM) { [math]::Round($_.AdapterRAM / 1GB, 2) } else { $null }
    }
}
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
$lms = Get-Command lms -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue
$ollamaModels = @()
if ($ollama) {
    try {
        $ollamaModels = @(ollama list 2>$null | Select-Object -Skip 1 | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    } catch {
        $ollamaModels = @('query_failed')
    }
}
[pscustomobject]@{
    os = $os.Caption
    version = $os.Version
    architecture = $os.OSArchitecture
    ram_gib = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    free_ram_gib = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    cpu = $cpu.Name
    logical_processors = $cpu.NumberOfLogicalProcessors
    gpus = @($gpus)
    ollama_installed = [bool]$ollama
    ollama_models = @($ollamaModels)
    lm_studio_cli_installed = [bool]$lms
    python_installed = [bool]$python
} | ConvertTo-Json -Depth 4 -Compress
