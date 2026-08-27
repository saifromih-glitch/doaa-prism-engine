$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $root 'NVIDIA-610.88-Studio-Driver.exe'
$signature = Get-AuthenticodeSignature $installer
$result = [ordered]@{
    installer = $installer
    size_bytes = (Get-Item $installer).Length
    sha256 = (Get-FileHash -Algorithm SHA256 $installer).Hash.ToLowerInvariant()
    signature_status = $signature.Status.ToString()
    signer_subject = if ($signature.SignerCertificate) { $signature.SignerCertificate.Subject } else { $null }
    signer_issuer = if ($signature.SignerCertificate) { $signature.SignerCertificate.Issuer } else { $null }
    accepted = $signature.Status -eq 'Valid' -and $signature.SignerCertificate.Subject -match 'NVIDIA'
}
$result | ConvertTo-Json -Compress | Set-Content -Encoding UTF8 (Join-Path $root 'nvidia-driver-installer-verification.json')
if (-not $result.accepted) { throw 'NVIDIA installer signature verification rejected.' }
Write-Output (Join-Path $root 'nvidia-driver-installer-verification.json')
