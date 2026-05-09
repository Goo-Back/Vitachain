import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const limit = searchParams.get('limit') || '10'
    const severity = searchParams.get('severity')
    const unread = searchParams.get('unread') === 'true'
    
    // Mock data for alerts - in production this would come from backend
    const mockAlerts = generateMockAlerts(deviceId, parseInt(limit), severity, unread)
    
    return NextResponse.json({
      success: true,
      device_id: deviceId,
      alerts: mockAlerts,
      total_count: mockAlerts.length,
      unread_count: mockAlerts.filter(alert => alert.unread).length
    })
    
  } catch (error) {
    console.error('Device Alerts API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch device alerts',
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
    const { type, severity, message } = body
    
    if (!type || !severity || !message) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing required fields',
          message: 'Type, severity, and message are required'
        },
        { status: 400 }
      )
    }
    
    // Validate alert type
    const validTypes = ['threshold_exceeded', 'device_offline', 'low_battery', 'ai_recommendation', 'maintenance_required']
    if (!validTypes.includes(type)) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid alert type',
          message: 'Alert type must be one of: ' + validTypes.join(', ')
        },
        { status: 400 }
      )
    }
    
    // Validate severity
    const validSeverities = ['low', 'medium', 'high', 'critical']
    if (!validSeverities.includes(severity)) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid severity',
          message: 'Severity must be one of: ' + validSeverities.join(', ')
        },
        { status: 400 }
      )
    }
    
    // Mock successful alert creation
    const alertData = {
      id: `alert-${Date.now()}`,
      device_id: deviceId,
      type: type,
      severity: severity,
      message: message,
      created_at: new Date().toISOString(),
      unread: true,
      acknowledged: false,
      resolved: false,
      metadata: body.metadata || {}
    }
    
    return NextResponse.json({
      success: true,
      message: 'Alert created successfully',
      alert: alertData
    })
    
  } catch (error) {
    console.error('Alert POST API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to create alert',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockAlerts(deviceId: string, limit: number, severityFilter?: string, unreadOnly: boolean = false) {
  const alerts = []
  const now = new Date()
  const alertTypes = ['threshold_exceeded', 'device_offline', 'low_battery', 'ai_recommendation', 'maintenance_required']
  const severities = ['low', 'medium', 'high', 'critical']
  
  for (let i = 0; i < 20; i++) {
    const hoursAgo = Math.floor(Math.random() * 72) // Random time within last 3 days
    const timestamp = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000)
    
    const type = alertTypes[Math.floor(Math.random() * alertTypes.length)]
    const severity = severities[Math.floor(Math.random() * severities.length)]
    
    // Apply filters
    if (severityFilter && severity !== severityFilter) continue
    if (unreadOnly && Math.random() > 0.3) continue // 70% of alerts are unread
    
    let message = ''
    switch (type) {
      case 'threshold_exceeded':
        message = `Temperature threshold exceeded: ${Math.floor(Math.random() * 10 + 35)}°C`
        break
      case 'device_offline':
        message = 'Device went offline unexpectedly'
        break
      case 'low_battery':
        message = `Battery level low: ${Math.floor(Math.random() * 20 + 10)}%`
        break
      case 'ai_recommendation':
        message = 'AI recommends adjusting irrigation schedule based on current conditions'
        break
      case 'maintenance_required':
        message = 'Device maintenance required - sensor calibration needed'
        break
    }
    
    alerts.push({
      id: `alert-${deviceId}-${i}`,
      device_id: deviceId,
      type: type,
      severity: severity,
      message: message,
      created_at: timestamp.toISOString(),
      unread: Math.random() > 0.3, // 70% unread
      acknowledged: Math.random() > 0.8, // 20% acknowledged
      resolved: Math.random() > 0.9, // 10% resolved
      metadata: {
        temperature: Math.floor(Math.random() * 30 + 15),
        humidity: Math.floor(Math.random() * 40 + 30),
        ndvi: (Math.random() * 0.6 + 0.3).toFixed(3)
      }
    })
  }
  
  // Sort by creation date (newest first) and apply limit
  return alerts
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, limit)
}
