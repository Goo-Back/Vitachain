# Story: 2-9 Temporary Account Blocking

**Epic**: 2 - User Authentication & Profiles  
**Story ID**: 2.9  
**Status**: ready-for-dev  
**Priority**: P2 (Post-MVD)  
**Estimated Effort**: 2-3 days  

## User Story

**As a** platform administrator  
**I want** to temporarily block user accounts for security reasons  
**So that** I can protect the platform from malicious activity while maintaining the ability to restore legitimate user access  

## Acceptance Criteria (BDD Format)

```gherkin
Feature: Temporary Account Blocking
  As a platform administrator
  I want to temporarily block user accounts for security reasons
  So that I can protect the platform from malicious activity

  Scenario: Block user account for suspicious activity
    Given an administrator identifies a user account with suspicious activity
    When the administrator blocks the account with a reason and duration
    Then the user account should be immediately blocked from all platform access
    And the user should receive an email notification about the block
    And the block should automatically expire after the specified duration
    And an audit log entry should be created

  Scenario: Block user account from admin dashboard
    Given an administrator is viewing a user's profile in the admin dashboard
    When they click "Block Account" and provide blocking details
    Then the account should be blocked immediately
    And they should see a confirmation message with block details
    And the user's status should update to "blocked" in all views

  Scenario: Automatic block for security violations
    Given the security system detects severe policy violations
    When the violation threshold is exceeded
    Then the user account should be automatically blocked for 24 hours
    And an admin alert should be generated
    And the user should receive a security notification

  Scenario: Unblock user account
    Given a user account is currently blocked
    When an administrator chooses to unblock the account
    Then the account should be immediately restored to full access
    And the user should receive an email notification about unblocking
    And an audit log entry should be created for the unblock action

  Scenario: View blocked accounts dashboard
    Given an administrator accesses the account management dashboard
    When viewing the blocked accounts section
    Then they should see all currently blocked accounts
    And each should show block reason, duration, and time remaining
    And they should have options to unblock or extend blocks

  Scenario: User attempts login while blocked
    Given a user account is blocked
    When the user attempts to log in
    Then they should see a clear message indicating their account is blocked
    And the message should include block reason and duration
    And they should not be able to access any platform features

  Scenario: Block expires automatically
    Given a user account was blocked with a specific duration
    When the block duration expires
    Then the account should be automatically unblocked
    And the user should receive an email notification about account restoration
    And the system should log the automatic unblock event
```

## Technical Requirements

### Core Functionality
- **Account Blocking Service**: Extend existing user management with temporary blocking capabilities
- **Admin Interface**: Integrate blocking controls into existing admin dashboard
- **Notification System**: Email notifications for block/unblock events
- **Audit Logging**: Complete audit trail for all blocking actions
- **Automatic Expiration**: Time-based block expiration with background processing
- **Security Integration**: Link with suspicious login detection from story 2-8

### Database Schema Extensions

```sql
-- Add blocking status to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) 
  DEFAULT 'active' CHECK (account_status IN ('active', 'blocked', 'suspended'));

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS block_reason TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS blocked_at TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS blocked_until TIMESTAMPTZ;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS blocked_by UUID REFERENCES profiles(id);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS auto_block BOOLEAN DEFAULT FALSE;

-- Create account_blocks table for detailed tracking
CREATE TABLE IF NOT EXISTS account_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    blocked_by UUID REFERENCES profiles(id),
    block_reason TEXT NOT NULL,
    block_duration_hours INTEGER NOT NULL,
    blocked_at TIMESTAMPTZ DEFAULT NOW(),
    blocked_until TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    auto_block BOOLEAN DEFAULT FALSE,
    security_event_id UUID REFERENCES security_events(id),
    unblocked_at TIMESTAMPTZ,
    unblocked_by UUID REFERENCES profiles(id),
    unblock_reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_account_status ON profiles(account_status);
CREATE INDEX IF NOT EXISTS idx_profiles_blocked_until ON profiles(blocked_until) WHERE blocked_until IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_account_blocks_user_id ON account_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_account_blocks_is_active ON account_blocks(is_active);
CREATE INDEX IF NOT EXISTS idx_account_blocks_blocked_until ON account_blocks(blocked_until);

-- RLS Policies for account_blocks
CREATE POLICY "admin_reads_all_blocks" ON account_blocks FOR SELECT
  USING (auth.jwt()->>'role' = 'ADMIN');

CREATE POLICY "admin_manages_blocks" ON account_blocks FOR ALL
  USING (auth.jwt()->>'role' = 'ADMIN');
```

### API Endpoints

```python
# Add to existing auth.py or create admin.py router

@router.post("/admin/users/{user_id}/block")
async def block_user_account(
    user_id: str,
    block_request: AccountBlockRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Block a user account temporarily
    Requires ADMIN role
    """

@router.post("/admin/users/{user_id}/unblock")
async def unblock_user_account(
    user_id: str,
    unblock_request: AccountUnblockRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Unblock a user account
    Requires ADMIN role
    """

@router.get("/admin/users/blocked")
async def get_blocked_users(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get list of all currently blocked users
    Requires ADMIN role
    """

@router.post("/admin/users/{user_id}/block/extend")
async def extend_user_block(
    user_id: str,
    extend_request: BlockExtensionRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Extend an existing block duration
    Requires ADMIN role
    """

# Background task for automatic block expiration
@router.post("/internal/blocks/cleanup")
async def cleanup_expired_blocks(
    supabase: Client = Depends(get_supabase_client)
):
    """
    Internal endpoint to process expired blocks
    Called by background scheduler
    """
```

## Architecture Compliance

### Integration with Existing Systems
- **Extend Admin Dashboard**: Add blocking controls to existing user management interface from story 2-7
- **Security Integration**: Link with suspicious login detection from story 2-8 for automatic blocks
- **Notification Service**: Use existing email service infrastructure from previous stories
- **Authentication Flow**: Integrate with existing auth middleware to check block status
- **Audit Logging**: Leverage existing audit patterns from admin stories

### Code Structure Requirements
```
backend/app/core/
├── account_blocking.py (new)
└── auth_middleware.py (extend existing)

backend/app/api/routes/
├── auth.py (extend existing)
└── admin.py (extend existing)

backend/app/services/
├── account_service.py (extend existing)
├── notification_service.py (extend existing)
└── block_service.py (new)

backend/app/models/
├── account_models.py (extend existing)
└── admin_models.py (extend existing)

backend/app/tasks/
└── block_cleanup.py (new - background tasks)
```

### Security Requirements
- **Performance**: Block status check must complete within 50ms during auth
- **Privacy**: Store only necessary blocking data, comply with GDPR
- **Audit Trail**: Complete audit log for all blocking actions
- **Data Integrity**: Ensure blocks cannot be bypassed through any means
- **Notification Reliability**: Ensure block/unblock notifications are delivered

## Implementation Tasks

### Phase 1: Core Blocking Service (1 day)
1. **Database Migration**
   - Add blocking columns to profiles table
   - Create account_blocks table
   - Add RLS policies and indexes
   - Update existing admin views

2. **Account Blocking Service**
   - Implement block/unblock logic
   - Add automatic expiration handling
   - Create audit logging functionality
   - Integrate with existing user service

### Phase 2: API Integration (1 day)
1. **Admin API Endpoints**
   - Block/unblock user endpoints
   - Blocked users listing
   - Block extension functionality
   - Integration with existing admin auth

2. **Authentication Middleware Update**
   - Add block status check to auth middleware
   - Handle blocked user login attempts
   - Return appropriate error messages

### Phase 3: Dashboard & Notifications (0.5-1 day)
1. **Admin Dashboard Integration**
   - Add block controls to user management
   - Create blocked accounts view
   - Add block history and analytics
   - Integrate with existing admin interface

2. **Notification System**
   - Block notification emails
   - Unblock notification emails
   - Admin alerts for automatic blocks
   - Integration with existing email service

### Phase 4: Background Processing (0.5 day)
1. **Automatic Expiration**
   - Background task for block cleanup
   - Scheduled job configuration
   - Automatic unblock notifications
   - Cleanup of expired block records

## Testing Requirements

### Unit Tests
- Test all blocking/unblocking operations
- Test database schema and RLS policies
- Test API endpoints with different user roles
- Test automatic expiration logic
- Test notification sending

### Integration Tests
- Test integration with existing auth flow
- Test admin dashboard blocking controls
- Test end-to-end block/unblock workflow
- Test email notification delivery
- Test background task processing

### Security Tests
- Test that blocked users cannot bypass blocks
- Test audit trail completeness
- Test role-based access control
- Test data privacy compliance
- Test notification security

## Previous Story Intelligence

### From Story 2-8 (Suspicious Login Detection)
- **Security Integration**: Link automatic blocks with suspicious login detection
- **Security Events**: Use existing security_events table for block triggers
- **Admin Alerts**: Leverage existing security alert infrastructure
- **IP Blocking**: Coordinate with IP blocking for comprehensive security

### From Story 2-7 (Admin User Management Dashboard)
- **Admin Interface**: Extend existing user management dashboard
- **User Views**: Add blocking controls to existing user profile views
- **Admin Auth**: Use existing admin authentication and authorization
- **Audit Patterns**: Follow established audit logging patterns

### From Story 2-6 (Role-Based Access Control)
- **Authorization**: Use existing role validation for admin-only features
- **Permission Checks**: Follow established admin permission patterns
- **JWT Integration**: Use existing JWT role extraction for authorization

## Latest Technical Information (2024 Best Practices)

### Account Blocking Patterns
Based on 2024 security best practices, implement these blocking patterns:

1. **Progressive Blocking**
   - Warning notifications before blocks
   - Increasing block durations for repeat offenses
   - Manual review requirements for extended blocks

2. **Context-Aware Blocking**
   - Different block types for different violations
   - Temporary vs permanent blocking options
   - Appeal mechanisms for blocked users

3. **Automated Security Response**
   - Integration with threat detection systems
   - Automatic blocks for high-confidence threats
   - Manual review for ambiguous cases

4. **User Experience Considerations**
   - Clear communication about block reasons
   - Transparent block duration information
   - Easy appeal process for legitimate users

### Modern Security Approaches
- **Zero Trust**: Verify all access attempts, even from known users
- **Behavioral Analysis**: Consider user behavior patterns in blocking decisions
- **Privacy-First**: Minimize data collection while maintaining security
- **Transparency**: Clear communication about security actions

## Project Context Reference

### Technology Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: Supabase PostgreSQL with RLS
- **Authentication**: Supabase Auth with JWT
- **Admin Dashboard**: Existing Next.js admin interface
- **Email Service**: Existing Brevo email integration
- **Background Tasks**: Celery or similar for scheduled tasks

### Key Dependencies
- `supabase-py`: For database operations
- `python-jose`: For JWT validation
- `fastapi`: For API endpoints
- `structlog`: For audit logging
- `httpx`: For email service integration

### Environment Variables Required
```bash
# Existing variables (reuse)
SUPABASE_URL
SUPABASE_SERVICE_KEY
SUPABASE_JWT_SECRET
BREVO_API_KEY

# Variables for this story (may reuse existing)
ADMIN_EMAIL_TEMPLATE_ID  # For block notifications
USER_EMAIL_TEMPLATE_ID   # For user notifications
SECURITY_WEBHOOK_URL     # For security alerts
```

## Success Criteria

### Functional Success
- [ ] Admin can block/unblock user accounts successfully
- [ ] Blocked users cannot access any platform features
- [ ] Automatic block expiration works correctly
- [ ] Email notifications are sent for all block/unblock events
- [ ] Complete audit trail is maintained for all actions

### Performance Success
- [ ] Block status check completes within 50ms during login
- [ ] Admin dashboard loads blocked accounts within 2 seconds
- [ ] Background block cleanup processes efficiently
- [ ] Email notifications are sent promptly

### Security Success
- [ ] Blocked accounts cannot bypass restrictions
- [ ] All blocking actions are properly audited
- [ ] Only admins can manage account blocks
- [ ] Sensitive blocking data is protected by RLS

### User Experience Success
- [ ] Clear error messages for blocked users
- [ ] Admin interface is intuitive and efficient
- [ ] Block reasons are communicated clearly
- [ ] Unblock process is straightforward for admins

## Risk Mitigation

### Technical Risks
- **Performance Impact**: Minimize by efficient database queries and caching
- **False Positives**: Implement manual review and appeal processes
- **Notification Failures**: Implement retry mechanisms and fallback notifications
- **Database Locks**: Use proper transaction management

### Operational Risks
- **Admin Errors**: Implement confirmation dialogs and audit trails
- **User Dissatisfaction**: Clear communication and appeal mechanisms
- **System Abuse**: Rate limiting and monitoring of block operations
- **Data Privacy**: GDPR-compliant data handling and retention policies

## Completion Status

**Status**: ready-for-dev  
**Completion Note**: Ultimate context engine analysis completed - comprehensive developer guide created with existing infrastructure integration, latest security best practices, and detailed implementation roadmap for temporary account blocking functionality.
