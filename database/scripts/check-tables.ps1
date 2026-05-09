# VitaChain Quick Table Check
# Simple PowerShell script to verify tables exist in Supabase

Write-Host "=== VitaChain Database Table Check ===" -ForegroundColor Cyan

# Load environment variables from .env file
Get-Content "..\.env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$SUPABASE_URL = $env:SUPABASE_URL
$SERVICE_KEY = $env:SUPABASE_SERVICE_ROLE_KEY

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "- Supabase URL: $SUPABASE_URL" -ForegroundColor Gray
Write-Host "- Service Key: $($SERVICE_KEY.Substring(0, 10))..." -ForegroundColor Gray
Write-Host ""

# Tables to check
$tables = @(
    "users",
    "user_profiles", 
    "devices",
    "telemetry",
    "products",
    "orders",
    "meals",
    "reservations",
    "alerts",
    "notifications"
)

Write-Host "Checking table accessibility..." -ForegroundColor Yellow

$headers = @{
    "apikey" = $SERVICE_KEY
    "Authorization" = "Bearer $SERVICE_KEY"
    "Content-Type" = "application/json"
}

$successCount = 0
$totalCount = $tables.Count

foreach ($table in $tables) {
    try {
        $url = "$SUPABASE_URL/rest/v1/$table?select=count&limit=1"
        $response = Invoke-RestMethod -Uri $url -Method GET -Headers $headers -TimeoutSec 10
        Write-Host "✓ $table" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "✗ $table - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Results ===" -ForegroundColor Cyan
Write-Host "Tables accessible: $successCount/$totalCount" -ForegroundColor $(if ($successCount -eq $totalCount) { 'Green' } else { 'Yellow' })

if ($successCount -eq $totalCount) {
    Write-Host "🎉 All tables are accessible! Database setup successful!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tables are not accessible. Check the errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Note: Make sure to update SUPABASE_URL and SERVICE_KEY with your actual values" -ForegroundColor Gray
