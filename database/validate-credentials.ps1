# Validate Supabase Credentials and Project Status

Write-Host "=== Supabase Credentials Validation ===" -ForegroundColor Cyan

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$url = $env:SUPABASE_URL
$anonKey = $env:SUPABASE_ANON_KEY
$serviceKey = $env:SUPABASE_SERVICE_ROLE_KEY

Write-Host "Project URL: $url"
Write-Host "Anon Key: $anonKey"
Write-Host "Service Key: $serviceKey"

if (-not $url -or -not $anonKey -or -not $serviceKey) {
    Write-Host "ERROR: Missing environment variables" -ForegroundColor Red
    exit 1
}

# Test 1: Check if project exists
Write-Host "`nTest 1: Project accessibility" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$url" -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS: Project URL is accessible" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Project URL not accessible - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Test anon key
Write-Host "`nTest 2: Anonymous key validation" -ForegroundColor Yellow
try {
    $headers = @{
        "apikey" = $anonKey
        "Authorization" = "Bearer $anonKey"
    }
    $response = Invoke-RestMethod -Uri "$url/rest/v1/" -Headers $headers -TimeoutSec 10
    Write-Host "SUCCESS: Anonymous key works" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Anonymous key invalid - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Test service key
Write-Host "`nTest 3: Service role key validation" -ForegroundColor Yellow
try {
    $headers = @{
        "apikey" = $serviceKey
        "Authorization" = "Bearer $serviceKey"
    }
    $response = Invoke-RestMethod -Uri "$url/rest/v1/" -Headers $headers -TimeoutSec 10
    Write-Host "SUCCESS: Service role key works" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Service role key invalid - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Check auth endpoint
Write-Host "`nTest 4: Auth service accessibility" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$url/auth/v1/settings" -Headers @{"apikey" = $anonKey} -TimeoutSec 10
    Write-Host "SUCCESS: Auth service accessible" -ForegroundColor Green
} catch {
    Write-Host "FAILED: Auth service not accessible - $($_.Exception.Message)" -ForegroundColor Red
}
