# Story: Alert Read/Unread Management
**Story ID:** 3.9  
**Epic:** 3 - Smart Farming with IoT (KATARA)  
**Status:** backlog  
**Priority:** P2  

---

## User Story

**As a** Farmer using VitaChain KATARA  
**I want to** manage my alert notifications by marking them as read or unread  
**So that** I can track which critical alerts I've already addressed and focus on new issues that require my attention, ensuring I don't miss important agricultural warnings.

---

## Acceptance Criteria (BDD Format)

### AC1: Alert List with Read/Unread Status
```gherkin
Scenario: Farmer views alerts with read/unread indicators
  Given I am authenticated as a FARMER
  And I have received threshold alerts for my devices
  When I navigate to "/dashboard/katara/alerts"
  Then I see a list of all my alerts
  And each alert shows read/unread status visually
  And unread alerts are highlighted or prominently displayed
  And the page loads within 3 seconds (NFR4)
```

### AC2: Mark Alert as Read
```gherkin
Scenario: Farmer marks an alert as read
  Given I am viewing my alerts list
  And I have unread alerts
  When I click "Mark as Read" on an unread alert
  Then the alert status changes to read
  And the visual highlighting is removed
  And the status persists across page refreshes
  And the change is reflected in real-time across devices
```

### AC3: Mark Alert as Unread
```gherkin
Scenario: Farmer marks an alert as unread
  Given I am viewing my alerts list
  And I have read alerts
  When I click "Mark as Unread" on a read alert
  Then the alert status changes to unread
  And the alert is highlighted as unread
  And the status persists across page refreshes
  And the change is reflected in real-time across devices
```

### AC4: Bulk Alert Management
```gherkin
Scenario: Farmer manages multiple alerts at once
  Given I have multiple unread alerts
  When I select multiple alerts
  Then I can "Mark All Selected as Read"
  And I can "Mark All Selected as Unread"
  And I can "Mark All as Read" for all alerts
  And the bulk operations complete within 2 seconds
```

### AC5: Alert Filtering by Status
```gherkin
Scenario: Farmer filters alerts by read/unread status
  Given I have both read and unread alerts
  When I apply "Unread Only" filter
  Then I see only unread alerts
  When I apply "Read Only" filter
  Then I see only read alerts
  When I apply "All Alerts" filter
  Then I see both read and unread alerts
  And filtering happens instantly without page reload
```

### AC6: Unread Alert Count Badge
```gherkin
Scenario: Farmer sees unread alert count
  Given I have unread alerts
  When I view the navigation menu
  Then I see a badge showing the count of unread alerts
  And the count updates in real-time when alerts are marked read/unread
  And the badge is hidden when there are no unread alerts
```

### AC7: Mobile Alert Management
```gherkin
Scenario: Farmer manages alerts on mobile device
  Given I am using a mobile device (320px width)
  When I view my alerts
  Then all read/unread controls are touch-friendly
  And swipe gestures work for marking alerts as read
  And the interface remains responsive and functional
  And loading times remain under 3 seconds on 3G
```

---

## Technical Requirements

### Frontend Implementation
- **Framework:** Next.js 14 with TypeScript
- **State Management:** React Query for server state, local state for UI updates
- **Real-time:** Supabase Realtime subscriptions for instant updates
- **UI Components:** Badge components for unread counts, toggle switches for status
- **Performance:** Optimistic updates for immediate UI feedback
- **Mobile:** Touch-friendly controls with swipe gestures

### Backend Implementation
- **Endpoint:** `PATCH /api/katara/alerts/{alert_id}/status`
- **Bulk Endpoint:** `PATCH /api/katara/alerts/bulk-status`
- **Authentication:** JWT Bearer token (FARMER role required)
- **Database:** Supabase with RLS policies for alert ownership
- **Real-time:** Supabase Realtime for status change broadcasts
- **Performance:** < 100ms response time for status updates

### Database Schema Required
```sql
-- Alerts table with read status
ALTER TABLE katara_alerts 
ADD COLUMN read_status BOOLEAN DEFAULT FALSE,
ADD COLUMN read_at TIMESTAMP WITH TIME ZONE;

-- Index for performance
CREATE INDEX idx_katara_alerts_read_status 
ON katara_alerts(farmer_id, read_status, created_at);

-- RLS Policy for read status updates
CREATE POLICY "Farmers can update their own alert read status"
ON katara_alerts
FOR UPDATE
USING (auth.uid() = farmer_id)
WITH CHECK (auth.uid() = farmer_id);
```

### API Contract
**Individual Alert Update:**
```
PATCH /api/katara/alerts/{alert_id}/status
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "read_status": true
}
```

**Response (200):**
```json
{
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "read_status": true,
  "read_at": "2026-05-03T23:48:00Z",
  "updated_at": "2026-05-03T23:48:00Z"
}
```

**Bulk Status Update:**
```
PATCH /api/katara/alerts/bulk-status
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "alert_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
  "read_status": false
}
```

**Response (200):**
```json
{
  "updated_count": 2,
  "failed_updates": [],
  "updated_alerts": [
    {
      "alert_id": "550e8400-e29b-41d4-a716-446655440000",
      "read_status": false,
      "read_at": null
    }
  ]
}
```

---

## Developer Context & Guardrails

### Critical Architecture Rules
```typescript
// ✅ ALWAYS use optimistic updates for immediate UI feedback
const markAsRead = async (alertId: string) => {
  // Optimistic update
  queryClient.setQueryData(['alerts'], (old: Alert[]) => 
    old?.map(alert => 
      alert.id === alertId ? { ...alert, read_status: true } : alert
    )
  )
  
  // Server update
  await updateAlertStatus(alertId, true)
}

// ✅ ALWAYS implement real-time subscriptions for multi-device sync
useEffect(() => {
  const subscription = supabase
    .channel('alert-status-changes')
    .on('postgres_changes', 
      { event: 'UPDATE', schema: 'public', table: 'katara_alerts' },
      (payload) => {
        queryClient.invalidateQueries(['alerts'])
      }
    )
    .subscribe()
    
  return () => subscription.unsubscribe()
}, [])

// ✅ ALWAYS validate alert ownership before status changes
const canUpdateAlert = (alert: Alert, userId: string) => {
  return alert.farmer_id === userId
}

// ❌ NEVER allow users to modify other farmers' alert status
// ❌ NEVER perform status updates without proper authentication
// ❌ NEVER rely solely on client-side state for read status
```

### File Structure Requirements
```
frontend/app/(dashboard)/katara/
  └── alerts/
      ├── page.tsx                    # Main alerts page (updated)
      ├── components/
      │   ├── AlertList.tsx            # Alert list with status indicators
      │   ├── AlertItem.tsx            # Individual alert component
      │   ├── StatusToggle.tsx         # Read/unread toggle component
      │   ├── BulkActions.tsx          # Bulk management controls
      │   ├── StatusFilter.tsx         # Filter by read status
      │   └── UnreadBadge.tsx          # Unread count badge
      └── hooks/
          ├── useAlertStatus.ts         # Alert status management hook
          └── useRealtimeAlerts.ts      # Real-time alert updates

frontend/components/
  └── common/
      ├── SwipeAction.tsx              # Mobile swipe gesture component
      └── OptimisticUpdate.tsx         # Reusable optimistic update pattern

backend/app/api/routes/katara.py       # Add alert status endpoints
backend/app/services/
  └── alert_service.py                 # Alert status management service

backend/app/models/schemas.py          # Add AlertStatusUpdate models
backend/tests/
  └── test_alert_status.py             # Alert status API tests
```

### Implementation Patterns
```typescript
// Custom Hook for Alert Status Management
function useAlertStatus() {
  const queryClient = useQueryClient()
  
  const updateStatus = useMutation({
    mutationFn: async ({ alertId, readStatus }: { alertId: string, readStatus: boolean }) => {
      const response = await fetch(`/api/katara/alerts/${alertId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ read_status: readStatus })
      })
      return response.json()
    },
    onMutate: async ({ alertId, readStatus }) => {
      // Optimistic update
      await queryClient.cancelQueries(['alerts'])
      const previousAlerts = queryClient.getQueryData(['alerts'])
      
      queryClient.setQueryData(['alerts'], (old: Alert[]) => 
        old?.map(alert => 
          alert.id === alertId ? { ...alert, read_status: readStatus } : alert
        )
      )
      
      return { previousAlerts }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['alerts'], context?.previousAlerts)
    },
    onSettled: () => {
      queryClient.invalidateQueries(['alerts'])
    }
  })
  
  return { updateStatus }
}

// Backend Service for Status Updates
async def update_alert_status(
  alert_id: UUID,
  farmer_id: UUID,
  read_status: bool
) -> AlertResponse:
  
  # Verify ownership
  alert = await get_alert_by_id(alert_id)
  if alert.farmer_id != farmer_id:
    raise HTTPException(403, "Cannot update other farmers' alerts")
  
  # Update status
  update_data = {
    "read_status": read_status,
    "read_at": datetime.utcnow() if read_status else None
  }
  
  updated_alert = await update_alert(alert_id, update_data)
  
  # Trigger real-time update
  await broadcast_alert_status_change(updated_alert)
  
  return AlertResponse(**updated_alert.dict())
```

---

## Testing Requirements

### Frontend Tests
- Alert list rendering with read/unread indicators
- Individual alert status toggle functionality
- Bulk status update operations
- Status filtering (all/read/unread)
- Unread count badge updates
- Mobile swipe gesture functionality
- Real-time status synchronization
- Optimistic update behavior
- Error handling for failed updates

### Backend Tests
- Alert status update API endpoint
- Bulk status update functionality
- Ownership validation and security
- Real-time broadcast triggers
- Database transaction integrity
- Error handling for invalid alert IDs
- Performance under concurrent updates
- RLS policy enforcement

### Integration Tests
- End-to-end alert management flow
- Multi-device real-time synchronization
- Mobile gesture integration
- Bulk operation validation
- Status persistence across sessions
- Real-time subscription behavior

### Test Coverage
```typescript
describe('Alert Read/Unread Management', () => {
  test('displays alerts with correct read/unread status')
  test('marks individual alert as read with optimistic update')
  test('marks individual alert as unread with optimistic update')
  test('performs bulk status updates efficiently')
  test('filters alerts by read/unread status')
  test('updates unread count badge in real-time')
  test('supports mobile swipe gestures for status changes')
  test('synchronizes status changes across multiple devices')
  test('prevents unauthorized status updates')
  test('handles network errors gracefully')
})
```

---

## Performance Requirements

### Frontend Performance
- **Status Toggle:** < 100ms visual feedback (optimistic update)
- **List Rendering:** < 2 seconds for 100+ alerts
- **Filter Operations:** < 500ms for instant filtering
- **Real-time Sync:** < 200ms for cross-device updates
- **Mobile Gestures:** 60fps swipe responsiveness

### Backend Performance
- **Status Update:** < 100ms API response time
- **Bulk Updates:** < 500ms for 50+ alerts
- **Real-time Broadcast:** < 50ms to subscribers
- **Database Queries:** Optimized with proper indexing
- **Concurrent Users:** Support 100+ simultaneous status updates

### Optimization Strategies
```typescript
// Virtual scrolling for large alert lists
const VirtualizedAlertList = ({ alerts }) => {
  return (
    <FixedSizeList
      height={600}
      itemCount={alerts.length}
      itemSize={80}
      itemData={alerts}
    >
      {AlertRow}
    </FixedSizeList>
  )
}

// Debounced filter updates
const debouncedFilter = useMemo(
  () => debounce((filter: string) => {
    setFilterQuery(filter)
  }, 300),
  []
)

// Efficient real-time subscriptions
const useAlertSubscription = (farmerId: string) => {
  useEffect(() => {
    const channel = supabase
      .channel(`alerts-${farmerId}`)
      .on('postgres_changes', 
        { 
          event: 'UPDATE', 
          schema: 'public', 
          table: 'katara_alerts',
          filter: `farmer_id=eq.${farmerId}`
        },
        handleAlertUpdate
      )
      .subscribe()
      
    return () => channel.unsubscribe()
  }, [farmerId])
}
```

---

## Security Requirements

### Authentication & Authorization
- JWT token validation for all status operations
- Farmer role requirement enforced
- Alert ownership verification before updates
- RLS policies preventing cross-farmer access

### Data Protection
- No sensitive data exposure in status updates
- Secure API endpoints with proper validation
- Rate limiting for bulk status operations
- Audit trail for status change operations

### Privacy Considerations
- Alert status only accessible to alert owner
- No cross-farmer data leakage possible
- Status changes logged for audit purposes
- Real-time updates scoped by farmer_id

---

## Dependencies & Integration

### Internal Dependencies
- Alert system (story 3-8) for alert creation and storage
- Real-time dashboard (story 3-3) for navigation integration
- Authentication system (Epic 2) for user identification
- Telemetry system (stories 3-1, 3-2) for alert generation

### External Dependencies
- Supabase Realtime for instant status synchronization
- React Query for optimistic updates and caching
- Touch gesture library for mobile swipe actions

### Successor Stories
- 3-10-alert-prioritization: Prioritize unread alerts by severity
- 3-11-alert-escalation: Auto-escalate unread critical alerts
- 9-2-email-alert-digests: Daily summaries of unread alerts

---

## Project Context Reference

### Technology Stack
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Backend:** FastAPI + Python 3.11 (async)
- **Database:** Supabase PostgreSQL with RLS policies
- **Real-time:** Supabase Realtime WebSocket subscriptions
- **State Management:** React Query with optimistic updates

### Code Conventions
- TypeScript strict mode throughout
- Async/await patterns for API calls
- Optimistic updates for immediate UI feedback
- Mobile-first responsive design
- Real-time synchronization across devices

### File Locations
- Alerts Page: `frontend/app/(dashboard)/katara/alerts/page.tsx`
- Components: `frontend/app/(dashboard)/katara/alerts/components/`
- API: `backend/app/api/routes/katara.py`
- Services: `backend/app/services/alert_service.py`
- Models: `backend/app/models/schemas.py`

---

## Implementation Notes

### Mobile Swipe Gestures
```typescript
// Mobile swipe to mark as read
const SwipeableAlert = ({ alert, onStatusChange }) => {
  return (
    <Swipeable
      onSwipeRight={() => onStatusChange(alert.id, true)}
      rightButtons={[
        <TouchableOpacity 
          style={styles.readButton}
          onPress={() => onStatusChange(alert.id, true)}
        >
          <Text>Mark as Read</Text>
        </TouchableOpacity>
      ]}
    >
      <AlertItem alert={alert} />
    </Swipeable>
  )
}
```

### Real-time Status Synchronization
```typescript
// Real-time alert status updates
const useRealtimeAlertSync = (farmerId: string) => {
  const queryClient = useQueryClient()
  
  useEffect(() => {
    const subscription = supabase
      .channel(`alert-status-${farmerId}`)
      .on('postgres_changes', 
        { 
          event: 'UPDATE', 
          schema: 'public', 
          table: 'katara_alerts',
          filter: `farmer_id=eq.${farmerId}`
        },
        (payload) => {
          // Update specific alert in cache
          queryClient.setQueryData(['alerts'], (old: Alert[]) => 
            old?.map(alert => 
              alert.id === payload.new.id ? payload.new : alert
            )
          )
        }
      )
      .subscribe()
      
    return () => subscription.unsubscribe()
  }, [farmerId, queryClient])
}
```

### Bulk Operations Optimization
```python
# Efficient bulk status updates
async def bulk_update_alert_status(
  alert_ids: List[UUID],
  farmer_id: UUID,
  read_status: bool
) -> BulkUpdateResponse:
  
  # Verify ownership for all alerts
  alerts = await get_alerts_by_ids(alert_ids)
  owned_alerts = [a for a in alerts if a.farmer_id == farmer_id]
  
  if len(owned_alerts) != len(alert_ids):
    raise HTTPException(403, "Some alerts not owned by farmer")
  
  # Bulk database update
  update_data = {
    "read_status": read_status,
    "read_at": datetime.utcnow() if read_status else None
  }
  
  updated_count = await bulk_update_alerts(alert_ids, update_data)
  
  # Broadcast changes
  for alert_id in alert_ids:
    await broadcast_alert_status_change(alert_id, read_status)
  
  return BulkUpdateResponse(
    updated_count=updated_count,
    failed_updates=[]
  )
```

---

### Review Findings

#### Decision Needed (resolved):
- [x] [Review][Decision] Real-time Error Handling Strategy — Real-time sync lacks offline fallback for connection failures (RESOLVED: Use connection status display)
- [x] [Review][Decision] Performance Monitoring Implementation — Missing 3-second load time and 2-second bulk operation monitoring (RESOLVED: Use client-side monitoring)
- [x] [Review][Decision] Mobile Swipe Gestures — Missing swipe gesture implementation for mobile devices (RESOLVED: Use react-swipeable library)

#### Patch (completed):
- [x] [Review][Patch] Database Migration Safety [database/migrations/13-alert-read-status.sql:12-16] - Fixed NULL handling with COALESCE
- [x] [Review][Patch] Input Validation Missing [backend/app/api/routes/katara.py:1374-1388] - Added array size validation (max 100)
- [x] [Review][Patch] UUID Format Validation [backend/app/api/routes/katara.py:1318-1325] - Improved error messages for invalid UUIDs
- [x] [Review][Patch] Timestamp Parsing Safety [backend/app/services/alert_service.py:352-353] - Added null check before timestamp parsing
- [x] [Review][Patch] Component Integration Missing [frontend components] - Updated AlertFeed to use read_status and integrated components

#### Deferred (checked):
- [x] [Review][Defer] Rate Limiting Missing [backend endpoints] — deferred, pre-existing security concern
- [x] [Review][Defer] Transaction Safety [backend/app/services/alert_service.py] — deferred, pre-existing pattern

---

## Completion Criteria

- [ ] Alert status update API endpoints
- [ ] Read/unread status indicators in alert list
- [ ] Individual alert status toggle functionality
- [ ] Bulk status update operations
- [ ] Status filtering (all/read/unread)
- [ ] Unread count badge with real-time updates
- [ ] Mobile swipe gesture support
- [ ] Real-time cross-device synchronization
- [ ] Optimistic updates for immediate feedback
- [ ] Comprehensive unit and integration tests
- [ ] Security requirements satisfied
- [ ] Performance requirements met
- [ ] Accessibility compliance (WCAG 2.1 AA)

---

## Tasks/Subtasks

### Backend Implementation
- [ ] Add read_status and read_at columns to katara_alerts table
- [ ] Create alert status update service functions
- [ ] Add individual and bulk status update API endpoints
- [ ] Implement real-time broadcast for status changes
- [ ] Add proper RLS policies for status updates
- [ ] Create comprehensive backend tests

### Frontend Implementation
- [ ] Update alert list component with status indicators
- [ ] Create status toggle component with optimistic updates
- [ ] Implement bulk actions component
- [ ] Add status filtering functionality
- [ ] Create unread count badge component
- [ ] Implement mobile swipe gestures
- [ ] Add real-time status synchronization

### Integration & Testing
- [ ] Create custom hooks for status management
- [ ] Implement real-time subscriptions
- [ ] Add performance optimizations
- [ ] Create comprehensive frontend tests
- [ ] Add integration tests
- [ ] Validate mobile functionality

---

## Dev Agent Record

### Implementation Plan
- Backend: Add status columns and API endpoints with proper security
- Frontend: Implement status indicators, toggles, and real-time sync
- Mobile: Add swipe gestures and touch-friendly controls
- Testing: Comprehensive coverage of all status management features

### Debug Log
- Story created in backlog status
- Awaiting implementation start

### Completion Notes
- Pending implementation

---

## File List
- backend/app/services/alert_service.py (to be updated)
- backend/app/api/routes/katara.py (to be updated)
- backend/app/models/schemas.py (to be updated)
- backend/tests/test_alert_status.py (new)
- frontend/app/(dashboard)/katara/alerts/page.tsx (to be updated)
- frontend/app/(dashboard)/katara/alerts/components/AlertList.tsx (to be updated)
- frontend/app/(dashboard)/katara/alerts/components/AlertItem.tsx (new)
- frontend/app/(dashboard)/katara/alerts/components/StatusToggle.tsx (new)
- frontend/app/(dashboard)/katara/alerts/components/BulkActions.tsx (new)
- frontend/app/(dashboard)/katara/alerts/components/StatusFilter.tsx (new)
- frontend/app/(dashboard)/katara/alerts/components/UnreadBadge.tsx (new)
- frontend/app/(dashboard)/katara/alerts/hooks/useAlertStatus.ts (new)
- frontend/app/(dashboard)/katara/alerts/hooks/useRealtimeAlerts.ts (new)
- frontend/components/common/SwipeAction.tsx (new)
- frontend/components/common/OptimisticUpdate.tsx (new)

---

## Change Log
- 2026-05-03: Story created for alert read/unread management functionality

---

## Story Context

This story enables farmers to effectively manage their alert notifications by providing read/unread status tracking. This is crucial for agricultural operations where farmers receive numerous threshold alerts and need to distinguish between new issues requiring attention and alerts they've already addressed.

The implementation focuses on:
- Clear visual indicators for alert status
- Efficient status management with optimistic updates
- Real-time synchronization across multiple devices
- Mobile-optimized interactions with swipe gestures
- Bulk operations for managing multiple alerts
- Proper security to prevent cross-farmer access

This functionality builds upon the alert system (story 3-8) and enhances the farmer's ability to stay on top of critical agricultural conditions without being overwhelmed by already-handled notifications.

---

**Last Updated:** 2026-05-03T23:48:00Z  
**Previous Story:** 3-8-threshold-based-alert-triggering  
**Next Story:** 3-10-alert-prioritization  
**Dependencies:** Story 3-8 must be complete
