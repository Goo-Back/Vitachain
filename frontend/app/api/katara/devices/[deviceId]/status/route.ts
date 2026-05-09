import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    
    // Mock device status data - in production this would come from backend
    const mockDeviceStatus = generateMockDeviceStatus(deviceId)
    
    return NextResponse.json({
      success: true,
      device_id: deviceId,
      status: mockDeviceStatus,
      last_updated: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Device Status API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch device status',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockDeviceStatus(deviceId: string) {
  // Simulate different device states based on device ID patterns
  const deviceHash = deviceId.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
  const isOnline = deviceHash % 3 !== 0 // ~67% online
  
  const baseStatus: any = {
    device_id: deviceId,
    name: `Device ${deviceId.split('-')[1]?.substring(0, 8) || 'Unknown'}`,
    location_lat: 31.7917 + (Math.random() - 0.5) * 0.1,
    location_lng: -7.0926 + (Math.random() - 0.5) * 0.1,
    status: isOnline ? 'online' : 'offline',
    battery_level: Math.floor(Math.random() * 60 + 40), // 40-100%
    last_seen: new Date(Date.now() - (isOnline ? 5 : 120) * 60 * 1000).toISOString(),
    firmware_version: '2.1.3',
    signal_strength: Math.floor(Math.random() * 30 + 70), // 70-100%
    uptime_percentage: Math.floor(Math.random() * 20 + 80), // 80-100%
    data_points_today: Math.floor(Math.random() * 100 + 50), // 50-150 readings
    last_maintenance: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }
  
  // Add current telemetry if online
  if (isOnline) {
    baseStatus.current_telemetry = {
      temperature: 22 + Math.random() * 8, // 22-30°C
      humidity: 55 + Math.random() * 20, // 55-75%
      ndvi: 0.5 + Math.random() * 0.3, // 0.5-0.8
      timestamp: new Date().toISOString()
    }
  }
  
  // Add active alerts if any
  const hasAlerts = Math.random() > 0.7 // 30% chance of active alerts
  if (hasAlerts) {
    baseStatus.active_alerts = [
      {
        id: `alert-${Date.now()}`,
        type: Math.random() > 0.5 ? 'threshold_exceeded' : 'low_battery',
        severity: Math.random() > 0.6 ? 'high' : 'medium',
        message: Math.random() > 0.5 ? 'Temperature above optimal range' : 'Battery level below 30%',
        created_at: new Date(Date.now() - Math.floor(Math.random() * 6) * 60 * 60 * 1000).toISOString()
      }
    ]
  }
  
  return baseStatus
}
