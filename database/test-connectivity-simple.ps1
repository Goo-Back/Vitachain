# Simple Supabase Connectivity Test
Write-Host "Testing Supabase connectivity..." -ForegroundColor Blue

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$url = $env:SUPABASE_URL
$key = $env:SUPABASE_ANON_KEY

Write-Host "URL: $url"
Write-Host "Key present: $(if ($key) { 'Yes' } else { 'No' })"

# Test basic connectivity
try {
    $headers = @{
        "apikey" = $key
        "Authorization" = "Bearer $key"
    }
    
    $response = Invoke-RestMethod -Uri "$url/rest/v1/" -Headers $headers
    Write-Host "✓ Basic connectivity successful" -ForegroundColor Green
} catch {
    Write-Host "✗ Connectivity failed: $($_.Exception.Message)" -ForegroundColor Red
}
