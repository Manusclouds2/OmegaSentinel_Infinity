param(
    [string]$target = "x86_64-pc-windows-msvc",
    [string]$usbDrive = "",
    [string]$SignCertPath = "",
    [string]$SignCertPassword = "",
    [string]$SignKey = "",
    [string]$SignCert = "",
    [switch]$CreateUEFIImage = $false,
    [string]$EmbedPassword = ""
)

# Prepare environment variables for signing/UEFI options
if ($SignCertPath) { $env:SIGN_PFX = $SignCertPath }
if ($SignCertPassword) { $env:SIGN_PFX_PASS = $SignCertPassword }
if ($SignKey) { $env:SIGN_KEY = $SignKey }
if ($SignCert) { $env:SIGN_CERT = $SignCert }
if ($CreateUEFIImage) { $env:CREATE_UEFI_IMAGE = "1" }
if ($EmbedPassword) { $env:EMBED_PASSWORD = $EmbedPassword }

# Run the Rust deployer to build and package the requested target
Write-Host "[+] Building and packaging target: $target"
& cargo run --bin deployer -- deploy $target
if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployer failed. Aborting."
    exit 1
}

$distPath = Join-Path -Path (Resolve-Path -LiteralPath "dist") -ChildPath $target
if (-not (Test-Path $distPath)) {
    Write-Error "Dist path not found: $distPath"
    exit 1
}

# If usbDrive not provided, attempt to find the first removable drive
if (-not $usbDrive) {
    $removables = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 }
    if ($removables.Count -eq 0) {
        Write-Error "No removable drives detected. Please insert a USB drive or specify -usbDrive." 
        exit 1
    }
    $usbDrive = $removables[0].DeviceID
    Write-Host "Detected removable drive: $usbDrive"
}

# Determine what to copy: if UEFI image requested, prefer ISO; otherwise copy dist folder
try {
    if ($CreateUEFIImage) {
        $iso = Get-ChildItem -Path $distPath -Filter "*-uefi.iso" -Recurse | Select-Object -First 1
        if ($iso) {
            Copy-Item -Path $iso.FullName -Destination $usbDrive -Force
            Write-Host "[+] UEFI ISO copied to $usbDrive"
        } else {
            Write-Warning "No UEFI ISO found. Copying packaged directory instead."
            $dest = Join-Path -Path $usbDrive -ChildPath (Split-Path -Path $distPath -Leaf)
            if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
            Copy-Item -Path $distPath -Destination $usbDrive -Recurse -Force
            Write-Host "[+] Packaged artifacts copied to $usbDrive"
        }
    } else {
        $dest = Join-Path -Path $usbDrive -ChildPath (Split-Path -Path $distPath -Leaf)
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Path $distPath -Destination $usbDrive -Recurse -Force
        Write-Host "[+] Packaged artifacts copied to $usbDrive"
    }
} catch {
    Write-Error "Failed to copy to USB drive: $_"
    exit 1
}

Write-Host "[+] Deployment to USB complete."
