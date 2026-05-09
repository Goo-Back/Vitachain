import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const farmerId = searchParams.get('farmer_id')
    const status = searchParams.get('status') // online, offline, all
    const limit = searchParams.get('limit') || '50'
    
    // Mock devices data - in production this would come from backend
    const mockDevices = generateMockDevices(farmerId, status, parseInt(limit))
    
    return NextResponse.json({
      success: true,
      devices: mockDevices,
      total_count: mockDevices.length,
      filters: {
        farmer_id: farmerId,
        status: status || 'all',
        limit: parseInt(limit)
      }
    })
    
  } catch (error) {
    console.error('Devices List API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch devices',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate required fields
    const { device_id, name, location_lat, location_lng, farmer_id } = body
    
    if (!device_id || !farmer_id) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required fields',
          message: 'Device ID and Farmer ID are required'
        },
        { status: 400 }
      )
    }
    
    // Validate device ID format
    if (!device_id.startsWith('katara-')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid device ID format',
          message: 'Device ID must start with "katara-" followed by UUID'
        },
        { status: 400 }
      )
    }
    
    // Validate coordinates
    if (location_lat && (location_lat < -90 || location_lat > 90)) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid latitude',
          message: 'Latitude must be between -90 and 90 degrees'
        },
        { status: 400 }
      )
    }
    
    if (location_lng && (location_lng < -180 || location_lng > 180)) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid longitude',
          message: 'Longitude must be between -180 and 180 degrees'
        },
        { status: 400 }
      )
    }
    
    // Mock successful device registration
    const deviceData = {
      id: `device-${Date.now()}`,
      device_id: device_id,
      farmer_id: farmer_id,
      name: name || `Device ${device_id.split('-')[1]?.substring(0, 8)}`,
      location_lat: location_lat || null,
      location_lng: location_lng || null,
      status: 'offline',
      registered_at: new Date().toISOString(),
      firmware_version: '2.1.3',
      auto_analysis_enabled: true,
      analysis_frequency_hours: 6
    }
    
    return NextResponse.json({
      success: true,
      message: 'Device registered successfully',
      device: deviceData
    })
    
  } catch (error) {
    console.error('Device Registration API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to register device',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockDevices(farmerId?: string | null, status?: string | null, limit: number = 50) {
  const devices = []
  const deviceNames = ['Parcelle Nord', 'Parcelle Sud', 'Serre A', 'Serre B', 'Champ Est', 'Champ Ouest']
  
  const deviceCount = Math.min(limit, 10) // Generate up to 10 devices
  
  for (let i = 0; i < deviceCount; i++) {
    const deviceId = `katara-${generateUUID()}`
    const isOnline = Math.random() > 0.2 // 80% online
    const deviceStatus = status === 'all' ? (isOnline ? 'online' : 'offline') : status
    
    devices.push({
      id: `device-${i + 1}`,
      device_id: deviceId,
      farmer_id: farmerId || `farmer-${Math.floor(Math.random() * 1000) + 1}`,
      name: deviceNames[i % deviceNames.length],
      location_lat: 31.7917 + (Math.random() - 0.5) * 0.1,
      location_lng: -7.0926 + (Math.random() - 0.5) * 0.1,
      status: deviceStatus || (isOnline ? 'online' : 'offline'),
      battery_level: Math.floor(Math.random() * 60 + 40), // 40-100%
      last_seen: new Date(Date.now() - (isOnline ? 5 : 120) * 60 * 1000).toISOString(),
      firmware_version: '2.1.3',
      signal_strength: Math.floor(Math.random() * 30 + 70), // 70-100%
      uptime_percentage: Math.floor(Math.random() * 20 + 80), // 80-100%
      data_points_today: Math.floor(Math.random() * 100 + 50), // 50-150 readings
      last_maintenance: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
      auto_analysis_enabled: Math.random() > 0.1, // 90% enabled
      analysis_frequency_hours: Math.floor(Math.random() * 12 + 1) // 1-12 hours
    })
  }
  
  return devices
}

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}
