# Sentinel-UG Client Quick Deployment Script (Windows/PowerShell)
# Version: 1.0
# Deploys sentinel-client with automatic configuration

param(
    [string]$ClientID = "omega-client-$env:COMPUTERNAME",
    [string]$ProtectionLevel = "omega_full",
    [string]$NetworkMode = "bridge"
)

# Color output helper functions
function Write-ColorOutput([string]$message, [string]$color = "Green") {
    switch ($color) {
        "Green" { Write-Host "✓ $message" -ForegroundColor Green }
        "Blue" { Write-Host "→ $message" -ForegroundColor Cyan }
        "Yellow" { Write-Host "⚠ $message" -ForegroundColor Yellow }
        "Red" { Write-Host "✗ $message" -ForegroundColor Red }
        default { Write-Host $message }
    }
}

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SENTINEL-UG CLIENT DEPLOYMENT SCRIPT v1.0       ║" -ForegroundColor Cyan
Write-Host "║   Quantum-Safe Protection Agent Installation      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-ColorOutput "Configuration detected:" "Blue"
Write-Host "  Client ID: $ClientID"
Write-Host "  Protection Level: $ProtectionLevel"
Write-Host "  Network Mode: $NetworkMode"
Write-Host ""

# Check prerequisites
Write-ColorOutput "Checking prerequisites..." "Blue"

# Check Docker
$dockerInstalled = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
if (-not $dockerInstalled) {
    Write-ColorOutput "Docker is not installed" "Red"
    Write-Host "   Install from: https://www.docker.com/products/docker-desktop"
    exit 1
}
Write-ColorOutput "Docker installed" "Green"

# Check Docker Compose
$composeInstalled = $null -ne (Get-Command docker-compose -ErrorAction SilentlyContinue)
if (-not $composeInstalled) {
    Write-ColorOutput "Docker Compose is not installed" "Red"
    exit 1
}
Write-ColorOutput "Docker Compose installed" "Green"

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-ColorOutput "docker-compose.yml not found in current directory" "Red"
    Write-ColorOutput "Please run this script from the directory containing docker-compose.yml" "Yellow"
    exit 1
}
Write-ColorOutput "docker-compose.yml found" "Green"

Write-Host ""
Write-ColorOutput "Step 1: Generating client credentials..." "Blue"

# Check if .env exists and has CLIENT_TOKEN
$clientToken = $null
if (Test-Path ".env") {
    $envContent = Get-Content ".env" | Select-String "^CLIENT_TOKEN="
    if ($envContent) {
        $clientToken = $envContent -replace "CLIENT_TOKEN=", ""
        Write-ColorOutput "CLIENT_TOKEN already exists in .env" "Yellow"
        Write-Host "  Using existing token: $($clientToken.Substring(0, 20))..."
    }
}

# Generate new token if needed
if (-not $clientToken) {
    # Generate random token using .NET
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    $clientToken = [System.Convert]::ToBase64String($bytes)
    Write-ColorOutput "Generated new CLIENT_TOKEN ($($clientToken.Substring(0, 20))...)" "Green"
}

Write-Host ""
Write-ColorOutput "Step 2: Creating/updating .env configuration..." "Blue"

# Create or update .env file
$envFile = ".env"
$envContent = @()

if (Test-Path $envFile) {
    $envContent = Get-Content $envFile
}

# Update or add client settings
$settings = @{
    "CLIENT_ID" = $ClientID
    "CLIENT_TOKEN" = $clientToken
    "QUANTUM_ORCHESTRATOR_URL" = "wss://orchestrator.sentinel.ug/ws/client/$ClientID"
    "PROTECTION_LEVEL" = $ProtectionLevel
    "NETWORK_MODE" = $NetworkMode
}

foreach ($key in $settings.Keys) {
    $value = $settings[$key]
    $envContent = $envContent | Where-Object { -not $_.StartsWith("$key=") }
    $envContent += "$key=$value"
}

# Write back to .env
$envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force

Write-ColorOutput ".env configuration updated" "Green"

Write-Host ""
Write-ColorOutput "Step 3: Creating sentinel-client directories..." "Blue"

@('logs/sentinel-client', 'configs/threat-feeds', 'data/sentinel-client') | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

Write-ColorOutput "Directories created" "Green"

Write-Host ""
Write-ColorOutput "Step 4: Verifying existing services..." "Blue"

$services = try {
    & docker-compose ps --services --filter "status=running" 2>$null
} catch {
    $null
}

if (-not $services) {
    Write-ColorOutput "Main services not running" "Yellow"
    Write-ColorOutput "Starting Docker Compose stack..." "Blue"
    & docker-compose up -d | Out-Null
    Start-Sleep -Seconds 10
} else {
    Write-ColorOutput "Main services already running" "Green"
}

Write-Host ""
Write-ColorOutput "Step 5: Deploying sentinel-client..." "Blue"

# Verify sentinel-client service exists
$composeContent = Get-Content "docker-compose.yml" -Raw
if ($composeContent -match "sentinel-client:") {
    Write-ColorOutput "sentinel-client service found in docker-compose.yml" "Green"
} else {
    Write-ColorOutput "sentinel-client service not found in docker-compose.yml" "Red"
    Write-Host "   Please update docker-compose.yml to include sentinel-client service"
    exit 1
}

# Pull latest image
Write-ColorOutput "Pulling latest sentinel-client image..." "Blue"
& docker-compose pull sentinel-client 2>$null | Out-Null

# Start sentinel-client
Write-ColorOutput "Starting sentinel-client service..." "Blue"
& docker-compose up -d sentinel-client | Out-Null

Start-Sleep -Seconds 5

Write-Host ""
Write-ColorOutput "Step 6: Verifying deployment..." "Blue"

# Check if container is running
$running = & docker-compose ps sentinel-client | Select-String "Up"
if ($running) {
    Write-ColorOutput "sentinel-client is running" "Green"
} else {
    Write-ColorOutput "sentinel-client failed to start" "Red"
    & docker-compose logs sentinel-client
    exit 1
}

# Check health status
try {
    $health = & docker-compose exec sentinel-client curl -s http://localhost:9100/health 2>$null
    if ($health) {
        Write-ColorOutput "Health check passed" "Green"
    }
} catch {
    Write-ColorOutput "Health check endpoint not available yet (service initializing)" "Yellow"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    ✓ CLIENT DEPLOYMENT COMPLETE                   ║" -ForegroundColor Cyan
Write-Host "╠════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║                                                    ║ " -ForegroundColor Cyan
Write-Host "║  Client ID: $ClientID" -ForegroundColor Cyan
Write-Host "║  Status: RUNNING                                   ║" -ForegroundColor Cyan
Write-Host "║  Protection Level: $ProtectionLevel                ║" -ForegroundColor Cyan
Write-Host "║                                                    ║" -ForegroundColor Cyan
Write-Host "║  View logs:                                        ║" -ForegroundColor Cyan
Write-Host "║  > docker-compose logs -f sentinel-client          ║" -ForegroundColor Cyan
Write-Host "║                                                    ║" -ForegroundColor Cyan
Write-Host "║  Check status:                                     ║" -ForegroundColor Cyan
Write-Host "║  > docker-compose ps sentinel-client               ║" -ForegroundColor Cyan
Write-Host "║                                                    ║" -ForegroundColor Cyan
Write-Host "║  Verify health:                                    ║" -ForegroundColor Cyan
Write-Host "║  > docker-compose exec sentinel-client `                 ║" -ForegroundColor Cyan
Write-Host "║    curl http://localhost:9100/health               ║" -ForegroundColor Cyan
Write-Host "║                                                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-ColorOutput "Quick start commands:" "Blue"
Write-Host ""
Write-Host "  # View real-time logs"
Write-Host "  docker-compose logs -f sentinel-client"
Write-Host ""
Write-Host "  # Check client status"
Write-Host "  docker-compose exec sentinel-client curl http://localhost:9100/status"
Write-Host ""
Write-Host "  # Stop client"
Write-Host "  docker-compose stop sentinel-client"
Write-Host ""
Write-Host "  # Restart client"
Write-Host "  docker-compose restart sentinel-client"
Write-Host ""
Write-Host "  # Remove client"
Write-Host "  docker-compose down"
Write-Host ""

Write-ColorOutput "Setup complete! Your sentinel-client is now protecting your system." "Green"
Write-Host ""
Write-ColorOutput "Next steps:" "Blue"
Write-Host "  1. Monitor client logs: docker-compose logs -f sentinel-client"
Write-Host "  2. Access Omega dashboard: http://localhost:8080"
Write-Host "  3. View threat intelligence: http://localhost:8080/dashboard.html#threats"
Write-Host "  4. Configure threat feeds: Configure in configs/threat-feeds/"
Write-Host ""
Write-Host "📚 Documentation: See SENTINEL_CLIENT_DEPLOYMENT.md for detailed information"
