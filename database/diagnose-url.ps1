# Diagnose Supabase URL Format Issues

Write-Host "=== Supabase URL Diagnosis ===" -ForegroundColor Cyan

# Load service key (the only one that worked)
$serviceKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnZHRxdnBjaGZucnNjdXB5eWFhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzY2MDIxNSwiZXhwIjoyMDkzMjM2MjE1fQ.ooEwiNP2PN4sVvL681UAxUdJBu89aX44rOLqCn55s9vo"

$headers = @{
    "apikey" = $serviceKey
    "Authorization" = "Bearer $serviceKey"
    "Content-Type" = "application/json"
}

# Test different URL formats
$urlFormats = @(
    "https://bgdtqvpchfnrscupyyaa.supabase.co",
    "https://bgdtqvpchfnrscupyyaa.supabase.co/rest/v1",
    "https://api.supabase.io/v1/projects/bgdtqvpchfnrscupyyaa",
    "https://bgdtqvpchfnrscupyyaa.ghost.io",
    "https://supabase.com/dashboard/project/bgdtqvpchfnrscupyyaa"
)

Write-Host "Testing different URL formats..." -ForegroundColor Yellow

foreach ($url in $urlFormats) {
    Write-Host "`nTesting: $url" -ForegroundColor White
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Write-Host "SUCCESS: HTTP $($response.StatusCode)" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "FAILED: HTTP $statusCode" -ForegroundColor Red
    }
}

# Test REST API endpoints specifically
Write-Host "`n=== Testing REST API Endpoints ===" -ForegroundColor Yellow

$restUrls = @(
    "https://bgdtqvpchfnrscupyyaa.supabase.co/rest/v1/",
    "https://bgdtqvpchfnrscupyyaa.supabase.co/rest/v1/users",
    "https://bgdtqvpchfnrscupyyaa.supabase.co/auth/v1/settings"
)

foreach ($url in $restUrls) {
    Write-Host "`nTesting REST: $url" -ForegroundColor White
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5
        Write-Host "SUCCESS: API endpoint accessible" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "FAILED: HTTP $statusCode" -ForegroundColor Red
    }
}
