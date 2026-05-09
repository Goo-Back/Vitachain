# VitaChain Docker Validation Script (PowerShell)
# Tests all Docker services and configurations

param(
    [switch]$SkipBuildTests,
    [switch]$SkipConnectivityTests
)

# Test counters
$script:TestsTotal = 0
$script:TestsPassed = 0
$script:TestsFailed = 0

# Helper functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
    $script:TestsPassed++
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    $script:TestsFailed++
}

function Test-Command {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    $script:TestsTotal++
    Write-Info "Running: $Name"
    
    try {
        if (& $Test) {
            Write-Success $Name
            return $true
        }
    }
    catch {
        # Fall through to failure
    }
    
    Write-Fail $Name
    return $false
}

# Print header
Write-Host "=========================================="
Write-Host "VitaChain Docker Validation Suite"
Write-Host "=========================================="
Write-Host ""

# Check if Docker is running
Write-Info "Checking Docker daemon..."
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker daemon is running"
    } else {
        Write-Fail "Docker daemon is not running"
        exit 1
    }
}
catch {
    Write-Fail "Docker daemon is not running"
    exit 1
}

# Check if Docker Compose is available
Write-Info "Checking Docker Compose..."
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose is available"
    } else {
        Write-Fail "Docker Compose is not installed"
        exit 1
    }
}
catch {
    Write-Fail "Docker Compose is not installed"
    exit 1
}

# Validate Docker Compose configuration
Write-Info "Validating Docker Compose configuration..."
try {
    $configResult = docker-compose config 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose configuration is valid"
    } else {
        Write-Fail "Docker Compose configuration has errors"
        docker-compose config
        exit 1
    }
}
catch {
    Write-Fail "Docker Compose configuration has errors"
    docker-compose config
    exit 1
}

# Check required files
Write-Info "Checking required files..."
$requiredFiles = @(
    "docker-compose.yml",
    ".env.example",
    "nginx\nginx.conf",
    "nginx\conf.d\vitachain.conf",
    "frontend\Dockerfile",
    "backend\Dockerfile"
)

foreach ($file in $requiredFiles) {
    $script:TestsTotal++
    if (Test-Path $file) {
        Write-Success "Required file exists: $file"
    } else {
        Write-Fail "Required file missing: $file"
    }
}

# Check environment file
Write-Info "Checking environment configuration..."
if (Test-Path ".env") {
    # Check for required environment variables
    $requiredVars = @(
        "SUPABASE_URL",
        "SUPABASE_DB_URL", 
        "SUPABASE_JWT_SECRET",
        "NODE_ENV"
    )
    
    foreach ($var in $requiredVars) {
        $script:TestsTotal++
        $envContent = Get-Content ".env"
        if ($envContent -match "^$var=") {
            Write-Success "Environment variable set: $var"
        } else {
            Write-Fail "Environment variable missing: $var"
        }
    }
} else {
    Write-Info "No .env file found (expected for first-time setup)"
}

# Check SSL certificates
Write-Info "Checking SSL certificates..."
if ((Test-Path "ssl\vitachain.ma.crt") -and (Test-Path "ssl\vitachain.ma.key")) {
    Write-Success "SSL certificate files exist"
    
    # Validate certificate format
    try {
        $certResult = openssl x509 -in "ssl\vitachain.ma.crt" -noout -text 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "SSL certificate is valid"
            $script:TestsPassed++
        } else {
            Write-Fail "SSL certificate is invalid"
            $script:TestsFailed++
        }
    }
    catch {
        Write-Fail "SSL certificate is invalid"
        $script:TestsFailed++
    }
    $script:TestsTotal++
    
    # Check certificate permissions
    try {
        $fileInfo = Get-Item "ssl\vitachain.ma.key" -ErrorAction Stop
        if ($fileInfo.Mode -match "^-rw.*") {  # Basic check for read/write permissions
            Write-Success "SSL key has appropriate permissions"
            $script:TestsPassed++
        } else {
            Write-Fail "SSL key permissions are too open"
            $script:TestsFailed++
        }
    }
    catch {
        Write-Fail "Cannot check SSL key permissions"
        $script:TestsFailed++
    }
    $script:TestsTotal++
} else {
    Write-Info "SSL certificates not found (run setup-ssl.sh)"
}

# Check directory structure
Write-Info "Checking directory structure..."
$requiredDirs = @(
    "logs\nginx",
    "ssl",
    "backups\supabase",
    "nginx\conf.d"
)

foreach ($dir in $requiredDirs) {
    $script:TestsTotal++
    if (Test-Path $dir -PathType Container) {
        Write-Success "Directory exists: $dir"
    } else {
        Write-Fail "Directory missing: $dir"
    }
}

# Test Docker image builds (if containers are not running)
$containersRunning = docker-compose ps | Select-String "Up" -Quiet
if (-not $containersRunning -and -not $SkipBuildTests) {
    Write-Info "Testing Docker image builds..."
    
    # Test frontend build
    Write-Info "Building frontend image..."
    try {
        docker-compose build frontend 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend image builds successfully"
        } else {
            Write-Fail "Frontend image build failed"
        }
    }
    catch {
        Write-Fail "Frontend image build failed"
    }
    $script:TestsTotal++
    
    # Test backend build
    Write-Info "Building backend image..."
    try {
        docker-compose build backend-katara 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backend image builds successfully"
        } else {
            Write-Fail "Backend image build failed"
        }
    }
    catch {
        Write-Fail "Backend image build failed"
    }
    $script:TestsTotal++
}

# Test service connectivity (if containers are running)
if ($containersRunning -and -not $SkipConnectivityTests) {
    Write-Info "Testing service connectivity..."
    
    # Test NGINX health
    Test-Command "NGINX health check" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    # Test frontend health
    Test-Command "Frontend health check" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    # Test backend health checks
    Test-Command "KATARA backend health" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    Test-Command "FARMARKET backend health" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    Test-Command "SECONDSERVE backend health" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    # Test API routing through NGINX
    Test-Command "API routing (KATARA)" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost/api/katara/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    Test-Command "API routing (FARMARKET)" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost/api/farmarket/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    Test-Command "API routing (SECONDSERVE)" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost/api/secondserve/health" -UseBasicParsing -TimeoutSec 5 2>$null
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    # Test SSL (if certificates are present)
    if (Test-Path "ssl\vitachain.ma.crt") {
        Test-Command "HTTPS health check" {
            try {
                $response = Invoke-WebRequest -Uri "https://localhost:8443/health" -UseBasicParsing -TimeoutSec 5 -SkipCertificateCheck 2>$null
                return $response.StatusCode -eq 200
            }
            catch {
                return $false
            }
        }
    }
} else {
    Write-Info "Containers are not running - skipping connectivity tests"
}

# Test Docker network
Write-Info "Testing Docker network..."
try {
    $networks = docker network ls | Select-String "vitachain_vitachain_network"
    if ($networks) {
        Write-Success "Docker network exists"
        
        # Test network configuration
        try {
            $networkInfo = docker network inspect vitachain_vitachain_network 2>$null | ConvertFrom-Json
            if ($networkInfo.IPAM.Config.Count -gt 0) {
                $subnet = $networkInfo.IPAM.Config[0].Subnet
                Write-Success "Network subnet configured: $subnet"
                $script:TestsPassed++
            } else {
                Write-Fail "Network subnet not configured"
                $script:TestsFailed++
            }
        }
        catch {
            Write-Fail "Network subnet not configured"
            $script:TestsFailed++
        }
        $script:TestsTotal++
    } else {
        Write-Info "Docker network not created (run docker-compose up)"
    }
}
catch {
    Write-Info "Docker network not created (run docker-compose up)"
}

# Test resource limits
Write-Info "Testing resource limits configuration..."
$composeContent = Get-Content "docker-compose.yml" -Raw
if ($composeContent -match "deploy:") {
    Write-Success "Resource limits are configured"
    $script:TestsPassed++
} else {
    Write-Fail "Resource limits not found in configuration"
    $script:TestsFailed++
}
$script:TestsTotal++

# Check for security configurations
Write-Info "Checking security configurations..."

# Test non-root user configuration
if ($composeContent -match "user:") {
    Write-Success "Non-root user configuration found"
    $script:TestsPassed++
} else {
    Write-Info "Non-root user configuration not explicitly set"
}
$script:TestsTotal++

# Test health check configuration
$healthCheckCount = ([regex]::Matches($composeContent, "healthcheck:")).Count
if ($healthCheckCount -gt 0) {
    Write-Success "Health checks configured ($healthCheckCount services)"
    $script:TestsPassed++
} else {
    Write-Fail "No health checks configured"
    $script:TestsFailed++
}
$script:TestsTotal++

# Print summary
Write-Host ""
Write-Host "=========================================="
Write-Host "Validation Summary"
Write-Host "=========================================="
Write-Host "Total Tests: $script:TestsTotal"
Write-Host "Passed: $script:TestsPassed" -ForegroundColor Green
Write-Host "Failed: $script:TestsFailed" -ForegroundColor Red

if ($script:TestsFailed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
}
