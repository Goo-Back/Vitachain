# VitaChain Supabase Connectivity Test Script
# Tests database connectivity and basic operations

Write-Host "Starting Supabase connectivity test..." -ForegroundColor Blue

# Load environment variables from .env file
$envFile = ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment variables from $envFile..." -ForegroundColor Green
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    exit 1
}

# Get environment variables
$supabaseUrl = $env:SUPABASE_URL
$supabaseAnonKey = $env:SUPABASE_ANON_KEY
$supabaseServiceKey = $env:SUPABASE_SERVICE_ROLE_KEY

if (-not $supabaseUrl -or -not $supabaseAnonKey) {
    Write-Host "Error: Missing required environment variables!" -ForegroundColor Red
    Write-Host "SUPABASE_URL and SUPABASE_ANON_KEY must be set" -ForegroundColor Red
    exit 1
}

Write-Host "Testing connectivity to: $supabaseUrl" -ForegroundColor Green

# Test 1: Basic API connectivity
Write-Host "`nTest 1: Basic API connectivity..." -ForegroundColor Yellow
try {
    $headers = @{
        "apikey" = $supabaseAnonKey
        "Authorization" = "Bearer $supabaseAnonKey"
    }
    
    $response = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/" -Headers $headers -Method GET
    Write-Host "✓ API connectivity successful" -ForegroundColor Green
} catch {
    Write-Host "✗ API connectivity failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Table access test
Write-Host "`nTest 2: Table access test..." -ForegroundColor Yellow
$tables = @("users", "user_profiles", "roles", "devices", "telemetry", "products", "orders", "meals", "reservations", "alerts", "audit_logs")

foreach ($table in $tables) {
    try {
        $response = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/$table?select=count&limit=1" -Headers $headers -Method HEAD
        Write-Host "✓ Table '$table' accessible" -ForegroundColor Green
    } catch {
        Write-Host "✗ Table '$table' not accessible: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: Auth service test
Write-Host "`nTest 3: Auth service test..." -ForegroundColor Yellow
try {
    $authHeaders = @{
        "apikey" = $supabaseAnonKey
        "Content-Type" = "application/json"
    }
    
    $authResponse = Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/settings" -Headers $authHeaders -Method GET
    Write-Host "✓ Auth service accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Auth service failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nConnectivity test completed!" -ForegroundColor Green
