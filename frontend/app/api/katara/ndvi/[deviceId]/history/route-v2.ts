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
    
    // Simple mock data generation - avoid complex objects
    const mockData = {
      success: true,
      history: [
        {
          id: `ndvi-${deviceId}-1`,
          date: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          ndvi_value: 0.72,
          ndvi_trend: 'stable',
          data_quality: 'good',
          cloud_cover: 85.2,
          acquisition_date: new Date(Date.now() - 86400000).toISOString(),
          imagery_url: `https://satellite-images.example.com/${deviceId}/2024-05-09.png`
        },
        {
          id: `ndvi-${deviceId}-2`,
          date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
          ndvi_value: 0.68,
          ndvi_trend: 'declining',
          data_quality: 'fair',
          cloud_cover: 92.1,
          acquisition_date: new Date(Date.now() - 172800000).toISOString(),
          imagery_url: `https://satellite-images.example.com/${deviceId}/2024-05-08.png`
        }
      ],
      device_id: deviceId,
      days_analyzed: parseInt(days),
      total_points: 2
    }
    
    return NextResponse.json(mockData)
    
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
