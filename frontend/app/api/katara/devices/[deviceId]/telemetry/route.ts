import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const hours = searchParams.get('hours') || '24'
    
    // Mock data for device telemetry - in production this would come from backend
    const mockTelemetry = generateMockTelemetry(deviceId, parseInt(hours))
    
    return NextResponse.json({
      success: true,
      device_id: deviceId,
      telemetry: mockTelemetry,
      hours_analyzed: parseInt(hours),
      total_readings: mockTelemetry.length
    })
    
  } catch (error) {
    console.error('Device Telemetry API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch device telemetry',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    const body = await request.json()
    
    // Validate required fields
    const { temperature, humidity, ndvi, battery_level } = body
    
    if (temperature === undefined || humidity === undefined) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required fields',
          message: 'Temperature and humidity are required'
        },
        { status: 400 }
      )
    }
    
    // Validate ranges
    if (temperature < -10 || temperature > 60) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid temperature range',
          message: 'Temperature must be between -10°C and 60°C'
        },
        { status: 400 }
      )
    }
    
    if (humidity < 0 || humidity > 100) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid humidity range',
          message: 'Humidity must be between 0% and 100%'
        },
        { status: 400 }
      )
    }
    
    if (ndvi !== undefined && (ndvi < -1 || ndvi > 1)) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid NDVI range',
          message: 'NDVI must be between -1 and 1'
        },
        { status: 400 }
      )
    }
    
    // Mock successful storage
    const telemetryData = {
      device_id: deviceId,
      temperature: parseFloat(temperature),
      humidity: parseFloat(humidity),
      ndvi: ndvi !== undefined ? parseFloat(ndvi) : null,
      battery_level: battery_level !== undefined ? parseFloat(battery_level) : null,
      timestamp: new Date().toISOString()
    }
    
    return NextResponse.json({
      success: true,
      message: 'Telemetry data received successfully',
      reading_id: `reading-${Date.now()}`,
      data: telemetryData
    })
    
  } catch (error) {
    console.error('Telemetry POST API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to process telemetry data',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockTelemetry(deviceId: string, hours: number) {
  const telemetry = []
  const now = new Date()
  
  for (let i = hours - 1; i >= 0; i--) {
    const timestamp = new Date(now)
    timestamp.setHours(timestamp.getHours() - i)
    
    // Generate realistic sensor data with daily patterns
    const hourOfDay = timestamp.getHours()
    let temperature = 20 + Math.sin((hourOfDay - 6) * Math.PI / 12) * 8
    temperature += (Math.random() - 0.5) * 2 // Add some variation
    
    let humidity = 60 + Math.sin((hourOfDay - 3) * Math.PI / 12) * 20
    humidity = Math.max(30, Math.min(90, humidity + (Math.random() - 0.5) * 10))
    
    // NDVI changes slowly over time
    const baseNDVI = 0.65 + Math.sin(i * 0.05) * 0.15
    const ndviValue = Math.max(0, Math.min(1, baseNDVI + (Math.random() - 0.5) * 0.05))
    
    // Battery decreases slowly
    const batteryLevel = Math.max(20, 95 - (hours - i) * 0.5 + (Math.random() - 0.5) * 5)
    
    telemetry.push({
      device_id: deviceId,
      temperature: parseFloat(temperature.toFixed(1)),
      humidity: parseFloat(humidity.toFixed(1)),
      ndvi: parseFloat(ndviValue.toFixed(3)),
      battery_level: parseFloat(batteryLevel.toFixed(1)),
      timestamp: timestamp.toISOString()
    })
  }
  
  return telemetry
}
