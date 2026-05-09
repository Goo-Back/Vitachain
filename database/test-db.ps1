# Test Supabase Database Connectivity

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

$url = $env:SUPABASE_URL
$key = $env:SUPABASE_ANON_KEY

Write-Host "Testing connectivity to Supabase..."
Write-Host "URL: $url"

if (-not $url -or -not $key) {
    Write-Host "ERROR: Missing environment variables"
    exit 1
}

try {
    $headers = @{
        "apikey" = $key
        "Authorization" = "Bearer $key"
    }
    
    $response = Invoke-RestMethod -Uri "$url/rest/v1/" -Headers $headers
    Write-Host "SUCCESS: Database is accessible"
} catch {
    Write-Host "ERROR: Database connection failed"
    Write-Host $_.Exception.Message
}
