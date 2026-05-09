# VitaChain Database Verification Script

Write-Host "=== VitaChain Database Verification ===" -ForegroundColor Cyan

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$url = $env:SUPABASE_URL
$serviceKey = $env:SUPABASE_SERVICE_ROLE_KEY

Write-Host "URL: $url"
Write-Host "Service Key: $serviceKey"

if (-not $url -or -not $serviceKey) {
    Write-Host "ERROR: Missing environment variables"
    exit 1
}

$headers = @{
    "apikey" = $serviceKey
    "Authorization" = "Bearer $serviceKey"
    "Content-Type" = "application/json"
}

$tables = @("users", "user_profiles", "roles", "devices", "telemetry", "products", "orders", "meals", "reservations", "alerts", "audit_logs")

$successCount = 0
$totalCount = $tables.Count

Write-Host "Checking tables..." -ForegroundColor Yellow

foreach ($table in $tables) {
    try {
        $response = Invoke-RestMethod -Uri "$url/rest/v1/$table?select=count&limit=1" -Headers $headers -Method GET
        Write-Host "SUCCESS: $table"
        $successCount++
    } catch {
        Write-Host "FAILED: $table - $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Results: $successCount/$totalCount tables accessible"

if ($successCount -eq $totalCount) {
    Write-Host "All tables verified successfully!"
} else {
    Write-Host "Some tables are not accessible"
}
