import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { lat: string; lng: string } }
) {
  try {
    const lat = parseFloat(params.lat)
    const lng = parseFloat(params.lng)
    
    // Validate coordinates
    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Invalid coordinates',
          message: 'Latitude must be between -90 and 90, longitude between -180 and 180'
        },
        { status: 400 }
      )
    }
    
    // Get query parameters
    const { searchParams } = new URL(request.url)
    const forecast = searchParams.get('forecast') || 'current'
    const days = searchParams.get('days') || '7'
    
    // Mock weather data - in production this would come from weather API
    const mockWeatherData = generateMockWeatherData(lat, lng, forecast, parseInt(days))
    
    return NextResponse.json({
      success: true,
      location: { lat, lng },
      weather: mockWeatherData,
      forecast_days: parseInt(days),
      data_source: 'mock_weather_api'
    })
    
  } catch (error) {
    console.error('Weather API Error:', error)
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch weather data',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

function generateMockWeatherData(lat: number, lng: number, forecast: string, days: number) {
  if (forecast === 'current') {
    return {
      current: {
        temperature: 22 + Math.random() * 8, // 22-30°C
        humidity: 45 + Math.random() * 25, // 45-70%
        pressure: 1010 + Math.random() * 20, // 1010-1030 hPa
        wind_speed: 5 + Math.random() * 10, // 5-15 km/h
        wind_direction: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.floor(Math.random() * 8)],
        visibility: 8 + Math.random() * 4, // 8-12 km
        uv_index: Math.floor(Math.random() * 11), // 0-10
        cloud_cover: Math.random() * 100, // 0-100%
        precipitation: Math.random() > 0.7 ? Math.random() * 5 : 0, // 0-5mm if raining
        timestamp: new Date().toISOString()
      },
      location_name: `Location ${lat.toFixed(2)}, ${lng.toFixed(2)}`,
      timezone: 'GMT+1'
    }
  } else {
    // Generate forecast data
    const forecastData = []
    const now = new Date()
    
    for (let i = 0; i < days; i++) {
      const date = new Date(now)
      date.setDate(date.getDate() + i)
      
      // Simulate weather patterns
      const baseTemp = 25 + Math.sin((date.getMonth() + i) * 0.5) * 5
      const tempVariation = (Math.random() - 0.5) * 10
      
      forecastData.push({
        date: date.toISOString().split('T')[0], // YYYY-MM-DD
        day_of_week: date.toLocaleDateString('en-US', { weekday: 'long' }),
        high_temp: baseTemp + tempVariation + Math.random() * 5,
        low_temp: baseTemp + tempVariation - Math.random() * 5,
        humidity: 50 + Math.random() * 30,
        precipitation_chance: Math.random() * 100,
        precipitation_amount: Math.random() > 0.6 ? Math.random() * 10 : 0,
        wind_speed: 5 + Math.random() * 15,
        wind_direction: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.floor(Math.random() * 8)],
        uv_index: Math.floor(Math.random() * 11),
        weather_condition: ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Heavy Rain'][Math.floor(Math.random() * 5)]
      })
    }
    
    return {
      forecast: forecastData,
      location_name: `Location ${lat.toFixed(2)}, ${lng.toFixed(2)}`,
      timezone: 'GMT+1',
      generated_at: new Date().toISOString()
    }
  }
}
