import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { deviceId: string } }
) {
  try {
    const deviceId = params.deviceId
    
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const days = searchParams.get('days') || '7'
    
    // Mock data for AI recommendations - in production this would come from backend AI service
    const mockRecommendations = generateMockRecommendations(deviceId, parseInt(days))
    
    return NextResponse.json({
      success: true,
      device_id: deviceId,
      recommendations: mockRecommendations,
      analysis_period_days: parseInt(days),
      generated_at: new Date().toISOString(),
      confidence_score: 0.85
    })
    
  } catch (error) {
    console.error('Device Recommendations API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch AI recommendations',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockRecommendations(deviceId: string, days: number) {
  // Generate realistic AI recommendations based on simulated conditions
  const currentConditions = generateCurrentConditions()
  const recommendations = []
  
  // Irrigation recommendations
  if (currentConditions.humidity < 40) {
    recommendations.push({
      category: 'irrigation',
      priority: 'high',
      action: 'Increase irrigation frequency',
      details: 'Soil moisture is critically low. Increase irrigation by 30% for the next 3 days.',
      estimated_impact: 'Prevent crop stress, improve yield by 15%',
      urgency: 'immediate'
    })
  } else if (currentConditions.humidity < 60) {
    recommendations.push({
      category: 'irrigation',
      priority: 'medium',
      action: 'Optimize irrigation schedule',
      details: 'Soil moisture is below optimal. Adjust irrigation timing to early morning for better absorption.',
      estimated_impact: 'Improve water efficiency by 20%',
      urgency: 'next_24h'
    })
  }
  
  // Temperature-based recommendations
  if (currentConditions.temperature > 35) {
    recommendations.push({
      category: 'temperature',
      priority: 'high',
      action: 'Implement cooling measures',
      details: 'High temperature stress detected. Consider shade nets or increased ventilation.',
      estimated_impact: 'Reduce heat stress, maintain crop quality',
      urgency: 'immediate'
    })
  }
  
  // NDVI-based recommendations
  if (currentConditions.ndvi < 0.3) {
    recommendations.push({
      category: 'crop_health',
      priority: 'critical',
      action: 'Investigate crop health issues',
      details: 'Low NDVI indicates potential disease or nutrient deficiency. Conduct soil and plant health assessment.',
      estimated_impact: 'Prevent yield loss, identify issues early',
      urgency: 'immediate'
    })
  } else if (currentConditions.ndvi < 0.5) {
    recommendations.push({
      category: 'crop_health',
      priority: 'medium',
      action: 'Monitor crop development',
      details: 'Moderate NDVI suggests slower growth. Monitor for nutrient deficiencies.',
      estimated_impact: 'Optimize fertilization, improve growth rate',
      urgency: 'next_48h'
    })
  }
  
  // Soil recommendations
  if (currentConditions.ph < 6.0) {
    recommendations.push({
      category: 'soil',
      priority: 'medium',
      action: 'Adjust soil pH',
      details: 'Soil pH is acidic. Consider adding lime or other pH adjusters.',
      estimated_impact: 'Improve nutrient availability, boost yield',
      urgency: 'next_week'
    })
  }
  
  // Predictive recommendations
  if (currentConditions.battery_level < 30) {
    recommendations.push({
      category: 'maintenance',
      priority: 'high',
      action: 'Replace device battery',
      details: 'Device battery is low. Replace battery to ensure continuous monitoring.',
      estimated_impact: 'Maintain data collection, prevent monitoring gaps',
      urgency: 'next_24h'
    })
  }
  
  // General optimization recommendations
  recommendations.push({
    category: 'optimization',
    priority: 'low',
    action: 'Schedule regular maintenance',
    details: 'Implement preventive maintenance schedule for sensors and irrigation systems.',
    estimated_impact: 'Reduce equipment failures, improve reliability',
    urgency: 'next_month'
  })
  
  return recommendations
}

function generateCurrentConditions() {
  return {
    temperature: 28 + Math.random() * 10, // 28-38°C
    humidity: 45 + Math.random() * 30, // 45-75%
    ndvi: 0.4 + Math.random() * 0.3, // 0.4-0.7
    ph: 5.8 + Math.random() * 1.2, // 5.8-7.0
    battery_level: 60 + Math.random() * 30, // 60-90%
    last_rainfall: Math.random() * 20, // 0-20mm
    growth_stage: ['vegetative', 'flowering', 'fruiting'][Math.floor(Math.random() * 3)]
  }
}
