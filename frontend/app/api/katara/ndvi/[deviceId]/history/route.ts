import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const days = searchParams.get('days') || '30'
    
    // Mock data for NDVI history - in production this would come from the backend
    const mockHistory = generateMockNDVIHistory(deviceId, parseInt(days))
    
    return NextResponse.json({
      success: true,
      history: mockHistory,
      device_id: deviceId,
      days_analyzed: parseInt(days),
      total_points: mockHistory.length
    })
    
  } catch (error) {
    console.error('NDVI History API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch NDVI history',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockNDVIHistory(deviceId: string, days: number) {
  const history = []
  const now = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    // Generate realistic NDVI values with some variation
    const baseNDVI = 0.65 + Math.sin(i * 0.1) * 0.15
    const ndviValue = Math.max(0, Math.min(1, baseNDVI + (Math.random() - 0.5) * 0.1))
    
    // Determine trend based on recent values
    let trend = 'stable'
    if (i > 0) {
      const prevValue = history[0]?.ndvi_value || ndviValue
      const diff = ndviValue - prevValue
      if (diff > 0.02) trend = 'improving'
      else if (diff < -0.02) trend = 'declining'
    }
    
    // Determine data quality based on cloud cover
    const cloudCover = Math.random() * 100
    let quality = 'excellent'
    if (cloudCover > 80) quality = 'poor'
    else if (cloudCover > 60) quality = 'fair'
    else if (cloudCover > 30) quality = 'good'
    
    history.push({
      id: `ndvi-${deviceId}-${i}`,
      date: date.toISOString(),
      ndvi_value: parseFloat(ndviValue.toFixed(3)),
      ndvi_trend: trend,
      data_quality: quality,
      cloud_cover: parseFloat(cloudCover.toFixed(1)),
      acquisition_date: date.toISOString(),
      imagery_url: `https://satellite-images.example.com/${deviceId}/${date.toISOString().split('T')[0]}.png`
    })
  }
  
  return history.reverse() // Return in chronological order
}
