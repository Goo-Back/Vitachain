# Story: Real-time Dashboard Visualization
**Story ID:** 3.3  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** ready-for-dev  
**Priority:** P0  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** view real-time dashboard with my IoT sensor data and alerts  
**So that** I can monitor my agricultural conditions, make informed decisions, and respond quickly to critical situations.

---

## Acceptance Criteria (BDD Format)

### AC1: Real-time Dashboard Data Loading
```gherkin
Scenario: Farmer loads KATARA dashboard with real-time data
  Given I am authenticated as a FARMER
  And I have registered ESP32 devices sending telemetry
  When I navigate to "/dashboard/katara"
  Then the dashboard loads within 3 seconds (NFR4)
  And I see my current telemetry data from all devices
  And I see device status indicators (online/offline)
  And I see summary statistics (avg temperature, humidity, NDVI)
  And I see unread alerts count
```

### AC2: Real-time Data Updates
```gherkin
Scenario: Dashboard updates automatically when new telemetry arrives
  Given I am viewing the KATARA dashboard
  And my ESP32 device sends new telemetry data
  Then the dashboard updates within 2 seconds (NFR5)
  And temperature/humidity/NDVI values refresh
  And device status indicators update if needed
  And new alerts appear immediately if thresholds exceeded
  And update animations are smooth and non-disruptive
```

### AC3: Multi-device Dashboard View
```gherkin
Scenario: Farmer views data from multiple devices
  Given I have 3 registered ESP32 devices
  And all devices are sending telemetry data
  When I view the KATARA dashboard
  Then I see data from all 3 devices
  And devices are organized by location/name
  And I can filter by specific device
  And I can compare readings across devices
  And each device shows last update timestamp
```

### AC4: Alert Integration
```gherkin
Scenario: Dashboard displays and manages alerts
  Given I have critical threshold alerts in katara_alerts table
  When I view the KATARA dashboard
  Then I see unread alerts prominently displayed
  And I can mark alerts as read from dashboard
  And alert severity is indicated by color coding
  And clicking alert shows details and recommended actions
  And alert count updates in real-time
```

### AC5: Historical Data Context
```gherkin
Scenario: Dashboard shows recent historical context
  Given I have telemetry data from the last 24 hours
  When I view the KATARA dashboard
  Then I see mini trend charts for temperature/humidity/NDVI
  And charts show last 24 hours of data points
  And current readings are highlighted on trends
  And I can hover to see specific values/timestamps
```

### AC6: Mobile Responsive Design
```gherkin
Scenario: Farmer views dashboard on mobile device
  Given I am using a mobile device (320px width)
  When I view the KATARA dashboard
  Then the layout is optimized for mobile viewing
  And all data is readable without horizontal scrolling
  And touch interactions work properly
  And loading times remain under 3 seconds on 3G
```

### AC7: Offline/Connection Error Handling
```gherkin
Scenario: Dashboard handles connection issues gracefully
  Given I am viewing the KATARA dashboard
  And my internet connection becomes unstable
  Then the dashboard shows last known data
  And I see a connection indicator showing status
  And data automatically resyncs when connection restores
  And error messages are clear and non-technical
```

---

## Technical Requirements

### Frontend Implementation
- **Framework:** Next.js 14 with TypeScript
- **Real-time:** Supabase Realtime WebSocket subscriptions
- **State Management:** React useState + useEffect patterns
- **Styling:** Tailwind CSS with responsive design
- **Performance:** Optimized for 3G connections, < 3s load time
- **Charts:** Lightweight charting library (Chart.js or similar)

### Backend Implementation
- **Endpoint:** `GET /api/katara/dashboard`
- **Authentication:** JWT Bearer token (FARMER role required)
- **Database:** Direct Supabase client with optimized queries
- **Real-time:** Supabase Realtime subscriptions for live updates
- **Performance:** < 200ms API response time (P95)

### Database Queries Required
```sql
-- Get farmer's devices with latest telemetry
SELECT d.*, t.temperature, t.humidity, t.ndvi, t.battery_level, t.timestamp
FROM iot_devices d
LEFT JOIN LATERAL (
  SELECT * FROM telemetry_readings 
  WHERE device_id = d.device_id 
  ORDER BY timestamp DESC LIMIT 1
) t ON true
WHERE d.farmer_id = $1;

-- Get unread alerts count
SELECT COUNT(*) as unread_count
FROM katara_alerts
WHERE farmer_id = $1 AND is_read = false;

-- Get 24-hour trend data
SELECT device_id, temperature, humidity, ndvi, timestamp
FROM telemetry_readings
WHERE farmer_id = $1 AND timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### API Contract
**Request:**
```
GET /api/katara/dashboard
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
  "devices": [
    {
      "id": "uuid-...",
      "device_id": "katara-550e8400-e29b-41d4-a716",
      "name": "Parcelle Nord",
      "location_lat": 33.5,
      "location_lng": -7.6,
      "status": "online",
      "last_seen": "2026-05-03T14:30:00Z",
      "current_telemetry": {
        "temperature": 36.8,
        "humidity": 55.2,
        "ndvi": 0.42,
        "battery_level": 78.5,
        "timestamp": "2026-05-03T14:30:00Z"
      }
    }
  ],
  "summary_stats": {
    "avg_temperature": 34.2,
    "avg_humidity": 62.1,
    "avg_ndvi": 0.38,
    "total_devices": 3,
    "online_devices": 2,
    "offline_devices": 1
  },
  "alerts": {
    "unread_count": 2,
    "recent_alerts": [
      {
        "id": "uuid-...",
        "type": "threshold_exceeded",
        "severity": "high",
        "message": "Temperature critical: 42°C",
        "created_at": "2026-05-03T14:25:00Z"
      }
    ]
  },
  "trend_data": {
    "last_24_hours": [
      {
        "device_id": "katara-550e8400-e29b-41d4-a716",
        "temperature": 36.8,
        "humidity": 55.2,
        "ndvi": 0.42,
        "timestamp": "2026-05-03T14:30:00Z"
      }
    ]
  }
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```typescript
// ✅ ALWAYS use Supabase Realtime for live updates
const subscription = supabase
  .channel('telemetry-updates')
  .on('postgres_changes', { 
    event: 'INSERT', 
    schema: 'public', 
    table: 'telemetry_readings',
    filter: `farmer_id=eq.${farmerId}`
  }, handleNewTelemetry)
  .subscribe()

// ✅ ALWAYS optimize for mobile/3G connections
const ChartComponent = lazy(() => import('./ChartComponent'))

// ✅ ALWAYS handle connection states gracefully
const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected')

// ❌ NEVER poll for updates (use WebSocket subscriptions)
// ❌ NEVER load all historical data (use 24-hour window)
// ❌ NEVER block UI during data loading
```

### File Structure Requirements
```
frontend/app/(dashboard)/katara/
  └── page.tsx                    # Main dashboard component (update existing)

frontend/components/katara/
  ├── DashboardStats.tsx          # Statistics cards component
  ├── DeviceList.tsx              # Device status list
  ├── TelemetryCharts.tsx         # Trend charts
  ├── AlertPanel.tsx              # Alert management
  ├── ConnectionStatus.tsx        # Connection indicator
  └── RealtimeProvider.tsx        # Supabase Realtime context

backend/app/api/routes/katara.py   # Add dashboard endpoint
backend/app/services/
  └── dashboard_service.py        # Dashboard data aggregation

backend/app/models/schemas.py      # Add DashboardResponse models

frontend/hooks/
  └── useKataraDashboard.ts        # Custom dashboard hook

backend/tests/
  └── test_dashboard_api.py        # Dashboard API tests
```

### Implementation Patterns
```typescript
// React Hook for Dashboard Data
function useKataraDashboard(farmerId: string) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Initial data load
    loadDashboardData()

    // Real-time subscription
    const subscription = supabase
      .channel(`dashboard-${farmerId}`)
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'telemetry_readings' },
        (payload) => handleRealtimeUpdate(payload)
      )
      .subscribe()

    return () => subscription.unsubscribe()
  }, [farmerId])

  return { data, loading, error }
}

// Backend Service
async def get_dashboard_data(farmer_id: UUID) -> DashboardResponse:
    # Get devices with latest telemetry
    devices = await get_farmer_devices_with_telemetry(farmer_id)
    
    # Calculate summary statistics
    stats = calculate_summary_stats(devices)
    
    # Get unread alerts
    alerts = await get_farmer_alerts(farmer_id)
    
    # Get 24-hour trend data
    trends = await get_trend_data(farmer_id, hours=24)
    
    return DashboardResponse(
        devices=devices,
        summary_stats=stats,
        alerts=alerts,
        trend_data=trends
    )
```

---

## Testing Requirements

### Frontend Tests
- Dashboard loading with authentication
- Real-time data updates simulation
- Mobile responsive layout testing
- Error handling for connection issues
- Component rendering with different data states
- Performance testing for 3G simulation

### Backend Tests
- Dashboard API endpoint with authentication
- Data aggregation accuracy
- Performance under load (multiple concurrent requests)
- Error handling for database failures
- Real-time subscription setup

### Integration Tests
- End-to-end dashboard flow
- Real-time telemetry update propagation
- Alert creation and dashboard display
- Mobile device compatibility
- Connection failure/recovery scenarios

### Test Coverage
```typescript
describe('Katara Dashboard', () => {
  test('loads dashboard data for authenticated farmer')
  test('displays real-time telemetry updates')
  test('shows alerts with proper severity indicators')
  test('handles connection errors gracefully')
  test('updates within 2 seconds performance requirement')
  test('responsive design on mobile devices')
})
```

---

## Performance Requirements

### Frontend Performance
- **Initial Load:** < 3 seconds on 4G connection (NFR4)
- **Real-time Updates:** < 2 seconds for data propagation (NFR5)
- **Mobile Optimization:** < 3 seconds on 3G connection
- **Bundle Size:** Dashboard components < 200KB gzipped
- **Animation Performance:** 60fps for chart updates

### Backend Performance
- **API Response:** < 200ms (P95) for dashboard data
- **Database Queries:** Optimized with proper indexes
- **Real-time Latency:** < 500ms for WebSocket message delivery
- **Concurrent Users:** Support 100+ simultaneous dashboard viewers

### Optimization Strategies
```typescript
// Code splitting for heavy components
const ChartsSection = lazy(() => import('./ChartsSection'))

// Memoization for expensive calculations
const memoizedStats = useMemo(() => calculateStats(data), [data])

// Virtualization for large device lists
const VirtualizedDeviceList = React.memo(({ devices }) => {
  return <FixedSizeList height={300} itemCount={devices.length} />
})
```

---

## Security Requirements

### Authentication & Authorization
- JWT token validation for dashboard access
- Farmer role requirement enforced
- Data isolation: farmers only see their own devices
- RLS policies enforced on all database queries

### Data Protection
- No sensitive data exposed in frontend
- Secure WebSocket connections (WSS)
- Rate limiting for dashboard API endpoints
- Input sanitization for all dynamic content

### Privacy Considerations
- Location data only shown to device owner
- Telemetry data isolated by farmer_id
- Alert information properly scoped
- No cross-farmer data leakage possible

---

## Dependencies & Integration

### Internal Dependencies
- Device registration data (story 3-1)
- Telemetry ingestion system (story 3-2)
- Alert system (future story 3-8)
- Authentication system (Epic 2)

### External Dependencies
- Supabase Realtime for WebSocket connections
- Chart.js or Recharts for data visualization
- Next.js for SSR and routing

### Successor Stories
- 3-4-telemetry-history-trend-analysis: Enhanced historical analysis
- 3-5-ai-agronomic-recommendations: AI insights integration
- 3-8-critical-condition-alert-system: Advanced alert management

---

## Project Context Reference

### Technology Stack
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with RLS
- **Real-time:** Supabase Realtime WebSocket
- **Charts:** Lightweight charting library
- **Authentication:** Supabase Auth JWT

### Code Conventions
- TypeScript strict mode throughout
- Async/await patterns for data fetching
- Component composition with React hooks
- Mobile-first responsive design
- Error boundaries for graceful degradation

### File Locations
- Dashboard: `frontend/app/(dashboard)/katara/page.tsx`
- Components: `frontend/components/katara/`
- API: `backend/app/api/routes/katara.py`
- Services: `backend/app/services/dashboard_service.py`
- Models: `backend/app/models/schemas.py`

---

## Implementation Notes

### Real-time Architecture
```typescript
// Supabase Realtime subscription setup
const setupRealtimeSubscription = (farmerId: string) => {
  return supabase
    .channel(`dashboard-${farmerId}`)
    .on('postgres_changes', 
      { event: 'INSERT', schema: 'public', table: 'telemetry_readings' },
      (payload) => {
        if (payload.new.farmer_id === farmerId) {
          updateDeviceTelemetry(payload.new)
        }
      }
    )
    .on('postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'katara_alerts' },
      (payload) => {
        if (payload.new.farmer_id === farmerId) {
          updateAlerts(payload.new)
        }
      }
    )
    .subscribe()
}
```

### Chart Implementation
```typescript
// Lightweight chart configuration
const TemperatureChart: React.FC<{ data: TelemetryPoint[] }> = ({ data }) => {
  return (
    <Line
      data={{
        labels: data.map(d => formatTime(d.timestamp)),
        datasets: [{
          label: 'Temperature (°C)',
          data: data.map(d => d.temperature),
          borderColor: 'rgb(255, 99, 132)',
          tension: 0.1
        }]
      }}
      options={{
        responsive: true,
        animation: { duration: 300 },
        scales: {
          y: { beginAtZero: false }
        }
      }}
    />
  )
}
```

### Mobile Optimization
```typescript
// Responsive grid system
const DashboardGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="col-span-1 md:col-span-2 lg:col-span-1">
        <StatsCard />
      </div>
      {/* Other components */}
    </div>
  )
}
```

---

## Completion Criteria

- [ ] Dashboard API endpoint implemented with optimized queries
- [ ] Real-time WebSocket subscriptions for live updates
- [ ] Responsive dashboard components with mobile optimization
- [ ] Chart visualization for 24-hour trends
- [ ] Alert integration with severity indicators
- [ ] Connection status handling and error recovery
- [ ] Performance requirements met (< 3s load, < 2s updates)
- [ ] Comprehensive unit and integration tests
- [ ] Mobile responsiveness verified
- [ ] Security requirements satisfied
- [ ] Accessibility compliance (WCAG 2.1 AA)

---

## Story Context

This story transforms the KATARA module from data collection to actionable insights. The real-time dashboard is the primary interface farmers will use daily to:

- Monitor current agricultural conditions
- Respond quickly to critical alerts
- Make data-driven farming decisions
- Track device health and status

The implementation must prioritize performance and mobile accessibility since farmers will primarily access this from fields with potentially poor connectivity. This dashboard serves as the foundation for future AI recommendations and advanced analytics features.

---

**Last Updated:** 2026-05-03T23:00:00Z  
**Previous Story:** 3-2-telemetry-data-ingestion (completed)  
**Next Story:** 3-4-telemetry-history-trend-analysis  
**Dependencies:** Stories 3-1 and 3-2 must be complete
