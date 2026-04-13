@echo off
REM LOPUTH JOSEEPH OMEGA - Windows Deployment Script
REM Professional Cybersecurity Firewall Platform

setlocal enabledelayedexpansion
cls

echo.
echo =========================================================================
echo   LOPUTH JOSEEPH OMEGA - Professional Cybersecurity Firewall
echo   Windows Deployment Script
echo =========================================================================
echo.

REM Check if Docker is installed
echo [*] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker Desktop is not installed or not in PATH
    echo [!] Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [+] Docker found: 
docker --version
echo.

REM Check if Docker is running
echo [*] Checking if Docker daemon is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker daemon is not running
    echo [!] Please start Docker Desktop
    pause
    exit /b 1
)
echo [+] Docker is running
echo.

REM Create directories
echo [*] Creating configuration directories...
if not exist configs mkdir configs
if not exist configs\quantum-keys mkdir configs\quantum-keys
if not exist logs mkdir logs
if not exist data mkdir data
if not exist scan mkdir scan
echo [+] Directories created
echo.

REM Generate keys (using openssl from Git Bash or WSL)
echo [*] Generating security keys...
openssl genrsa -out configs\quantum-keys\master.key 4096 >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] OpenSSL not found. Skipping key generation.
    echo [!] Install Git for Windows or use WSL for full functionality
) else (
    echo [+] Security keys generated
)
echo.

REM Create .env file if it doesn't exist
echo [*] Creating environment configuration...
if not exist .env (
    copy .env.example .env >nul
    echo [+] .env file created from template
    echo [!] IMPORTANT: Edit .env with your API keys and passwords
) else (
    echo [+] .env file already exists
)
echo.

REM Build Docker images
echo [*] Building Docker images...
echo [This may take 5-10 minutes on first run]
docker-compose build
if %errorlevel% neq 0 (
    echo [!] Docker build failed
    pause
    exit /b 1
)
echo [+] Docker images built successfully
echo.

REM Start services
echo [*] Starting OMEGA services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [!] Failed to start services
    docker-compose logs
    pause
    exit /b 1
)
echo [+] Services started
echo.

REM Wait for services to be ready
echo [*] Waiting for services to initialize (30 seconds)...
timeout /t 30 /nobreak
echo.

REM Check service health
echo [*] Checking service health...
docker-compose ps
echo.

REM Display access information
echo.
echo =========================================================================
echo   DEPLOYMENT COMPLETE!
echo =========================================================================
echo.
echo [+] Your OMEGA system is running on:
echo.
echo     Web Dashboard:  http://localhost:8080
echo     Grafana:        http://localhost:3000
echo     Prometheus:     http://localhost:9090
echo     API Docs:       http://localhost:8080/docs
echo.
echo [+] Default Credentials:
echo     Username: admin
echo     Password: letmein
echo.
echo [!] IMPORTANT: Change your password immediately!
echo.
echo [+] Useful Commands:
echo.
echo     View logs:
echo     docker-compose logs -f app
echo.
echo     Stop services:
echo     docker-compose down
echo.
echo     Restart services:
echo     docker-compose restart
echo.
echo     View running containers:
echo     docker-compose ps
echo.
echo =========================================================================
echo.

REM Open browser
choice /C YN /M "Open dashboard in browser now?"
if %errorlevel% equ 1 (
    start http://localhost:8080/login.html
)

echo.
echo [+] Deployment completed successfully!
echo [+] For detailed documentation, see DEPLOYMENT.md
echo.
pause
