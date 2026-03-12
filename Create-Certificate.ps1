# PowerShell Script to Create a Self-Signed Code Signing Certificate
# Usage: Run as Administrator

$certName = "Aleian Code Signing"
$password = "Aleian123" # Change this password!
$pfxFile = "MyCert.pfx"
$cerFile = "MyCert.cer"

Write-Host "Creating Self-Signed Certificate for '$certName'..." -ForegroundColor Cyan

# 1. Create Certificate in Current User Store
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$certName" -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(5)

if ($cert) {
    Write-Host "Certificate created successfully!" -ForegroundColor Green
    Write-Host "Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray

    # 2. Export to PFX (Private Key included)
    $securePassword = ConvertTo-SecureString -String $password -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $pfxFile -Password $securePassword
    Write-Host "Exported PFX to: $PWD\$pfxFile" -ForegroundColor Green
    Write-Host "Password: $password" -ForegroundColor Yellow

    # 3. Export to CER (Public Key only - for distribution)
    Export-Certificate -Cert $cert -FilePath $cerFile
    Write-Host "Exported CER to: $PWD\$cerFile" -ForegroundColor Green
    
    Write-Host "`nIMPORTANT:" -ForegroundColor Red
    Write-Host "1. Keep '$pfxFile' secure. It contains your private key."
    Write-Host "2. Distribute '$cerFile' to users. They must install it to 'Trusted Root Certification Authorities' to trust your app."
    Write-Host "3. Update 'build_installer.py' to use '$pfxFile' and password '$password'."
} else {
    Write-Host "Failed to create certificate." -ForegroundColor Red
}
