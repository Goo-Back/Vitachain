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
    
    // Generate mock data with plain serializable objects
    const history = generateSerializableHistory(deviceId, parseInt(days))
    
    // Create a plain object that Next.js can serialize
    const response = {
      success: true,
      history: history,
      device_id: deviceId,
      days_analyzed: parseInt(days),
      total_points: history.length
    }
    
    return NextResponse.json(response)
    
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

function generateSerializableHistory(deviceId: string, days: number) {
  const history = []
  const now = Date.now()
  
  for (let i = 0; i < days; i++) {
    const timestamp = now - (days - 1 - i) * 86400000 // days ago in milliseconds
    
    // Generate realistic NDVI values
    const baseNDVI = 0.65 + Math.sin(i * 0.1) * 0.15
    const ndviValue = Math.max(0, Math.min(1, baseNDVI + (Math.random() - 0.5) * 0.1))
    
    // Determine trend based on previous value
    let trend = 'stable'
    if (i > 0) {
      const prevValue = history[i - 1]?.ndvi_value || ndviValue
      const diff = ndviValue - prevValue
      if (diff > 0.02) trend = 'improving'
      else if (diff < -0.02) trend = 'declining'
    }
    
    // Determine data quality
    const cloudCover = Math.random() * 100
    let quality = 'excellent'
    if (cloudCover > 80) quality = 'poor'
    else if (cloudCover > 60) quality = 'fair'
    else if (cloudCover > 30) quality = 'good'
    
    // Create date string to avoid Date object serialization issues
    const dateStr = new Date(timestamp).toISOString()
    const dateOnly = dateStr.split('T')[0]
    
    // Create plain object with only serializable properties
    const historyItem = {
      id: 'ndvi-' + deviceId + '-' + i,
      date: dateStr,
      ndvi_value: Math.round(ndviValue * 1000) / 1000, // Avoid floating precision issues
      ndvi_trend: trend,
      data_quality: quality,
      cloud_cover: Math.round(cloudCover * 10) / 10,
      acquisition_date: dateStr,
      imagery_url: 'https://satellite-images.example.com/' + deviceId + '/' + dateOnly + '.png'
    }
    
    history.push(historyItem)
  }
  
  return history
}