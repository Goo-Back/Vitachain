# Check Actual Database State Using Service Key

Write-Host "=== Database State Check ===" -ForegroundColor Cyan

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$url = $env:SUPABASE_URL
$serviceKey = $env:SUPABASE_SERVICE_ROLE_KEY

Write-Host "Using URL: $url"

$headers = @{
    "apikey" = $serviceKey
    "Authorization" = "Bearer $serviceKey"
    "Content-Type" = "application/json"
    "Prefer" = "resolution=merge-duplicates"
}

# Test 1: List all tables
Write-Host "`nTest 1: Listing all tables" -ForegroundColor Yellow
try {
    $query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    $response = Invoke-RestMethod -Uri "$url/rest/v1/rpc/get_tables" -Headers $headers -Method POST -Body (@{"query" = $query} | ConvertTo-Json) -TimeoutSec 10
    Write-Host "Tables found: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Failed to list tables: $($_.Exception.Message)" -ForegroundColor Red
    
    # Alternative: Try to query information_schema directly
    try {
        $response = Invoke-RestMethod -Uri "$url/rest/v1/information_schema.tables?select=table_name&table_schema=eq.public" -Headers $headers -TimeoutSec 10
        Write-Host "Tables via direct query: $($response | ConvertTo-Json)" -ForegroundColor Green
    } catch {
        Write-Host "Direct query also failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 2: Check specific tables
Write-Host "`nTest 2: Checking specific tables" -ForegroundColor Yellow
$tables = @("users", "user_profiles", "roles", "devices", "telemetry", "products", "orders", "meals", "reservations", "alerts", "audit_logs")

foreach ($table in $tables) {
    try {
        $response = Invoke-RestMethod -Uri "$url/rest/v1/$table?select=count&limit=1" -Headers $headers -Method GET -TimeoutSec 5
        Write-Host "SUCCESS: $table" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "FAILED: $table - HTTP $statusCode" -ForegroundColor Red
    }
}

# Test 3: Try to create a simple table to test permissions
Write-Host "`nTest 3: Testing write permissions" -ForegroundColor Yellow
try {
    $createTableQuery = @"
    CREATE TABLE IF NOT EXISTS test_connection (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP DEFAULT NOW()
    );
"@
    
    $body = @{
        "query" = $createTableQuery
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$url/rest/v1/rpc/execute_sql" -Headers $headers -Method POST -Body $body -TimeoutSec 10
    Write-Host "SUCCESS: Write permissions working" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Write permissions - $($_.Exception.Message)" -ForegroundColor Red
}
