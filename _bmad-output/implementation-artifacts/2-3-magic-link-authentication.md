# Story: Magic Link Authentication
**Story ID:** 2.3  
**Epic:** 2 - User Authentication & Profiles  
**Status:** ready-for-dev  
**Priority:** P2  

---

## Story Overview

Implement passwordless magic link authentication system for VitaChain platform, allowing users to login securely without passwords by clicking a time-limited link sent to their email. This builds on the email verification system from story 2-1 and JWT cookie management from story 2-2.

---

## User Story

**As a** registered user (farmer, restaurant, citizen, or admin)  
**I want to** login using a magic link sent to my email  
**So that** I can access the platform securely without remembering passwords

---

## Acceptance Criteria (BDD Format)

### Scenario: Magic Link Request
```gherkin
Given I am a registered user with verified email
When I navigate to the login page
And I enter my email address
And I click "Send Magic Link"
Then I should see "Check your email for magic link" message
And I should receive a magic link email within 30 seconds
```

### Scenario: Magic Link Login
```gherkin
Given I have requested a magic link
When I click the magic link in my email
Then I should be redirected to my dashboard
And I should receive a JWT token in httpOnly cookie
And I should see "Welcome back" message
And the magic link should expire after 15 minutes
```

### Scenario: Magic Link Security
```gherkin
Given I have received a magic link
When I try to use the same link again
Then I should see "Invalid or expired magic link" error
When I wait 15 minutes and try the link
Then I should see "Magic link has expired" error
When I request another magic link
Then the previous link should be invalidated
```

### Scenario: Rate Limiting
```gherkin
Given I am on the magic link login page
When I request magic links for the same email 5 times in 5 minutes
Then I should see "Too many requests" error on the 6th attempt
When I request magic links from the same IP 10 times in 5 minutes
Then I should see "Too many requests" error on the 11th attempt
```

---

## Technical Requirements

### Backend Implementation
- **FastAPI endpoint:** `POST /api/auth/magic-link` (request magic link)
- **FastAPI endpoint:** `GET /api/auth/magic-link/verify` (verify magic link)
- **Supabase Auth integration:** Use `supabase.auth.signInWithOtp()`
- **Token generation:** Secure one-time tokens with 15-minute expiry
- **JWT validation:** Decode tokens and set httpOnly cookies
- **Link invalidation:** Single-use tokens that expire after use

### Frontend Implementation
- **Next.js page:** `/login/magic-link` (magic link request form)
- **Next.js page:** `/auth/magic-link/callback` (magic link verification)
- **Form validation:** Email format validation with proper error handling
- **Loading states:** Show progress during magic link generation
- **Success messaging:** Clear instructions to check email

### Email Implementation
- **Email template:** Magic link email with clear call-to-action button
- **Link generation:** Secure token-based magic links
- **Email service:** Brevo integration with HTML templates
- **Localization:** French/Arabic ready email content

---

## Developer Context & Guardrails

### Critical Architecture Rules
```python
# ✅ ALWAYS use Supabase Auth OTP for magic links
async def request_magic_link(email: str):
    response = supabase.auth.signInWithOtp({
        'email': email,
        'options': {
            'shouldCreateUser': False,  # Only existing users
            'emailRedirectTo': f'{settings.FRONTEND_URL}/auth/magic-link/callback'
        }
    })
    return response

# ✅ ALWAYS validate magic link tokens properly
async def verify_magic_link(token: str):
    try:
        # Verify OTP token with Supabase
        response = supabase.auth.verifyOtp({
            'token': token,
            'type': 'magiclink'
        })
        return response
    except Exception as e:
        raise HTTPException(401, "Invalid or expired magic link")

# ❌ NEVER store magic links in database plaintext
magic_links_db.insert({"token": token, "email": email})  # Security vulnerability

# ❌ NEVER allow magic link registration (shouldCreateUser: false)
supabase.auth.signInWithOtp({
    'email': email,
    'options': {'shouldCreateUser': True}  # Creates security hole
})
```

### Magic Link Token Pattern
```python
# ✅ Secure token generation and validation
class MagicLinkToken:
    def __init__(self):
        self.expiry_minutes = 15
        
    def generate_token(self, email: str) -> str:
        """Generate secure magic link token"""
        payload = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=self.expiry_minutes),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())  # Unique identifier
        }
        return jwt.encode(payload, settings.MAGIC_LINK_SECRET, algorithm='HS256')
    
    def validate_token(self, token: str) -> dict:
        """Validate magic link token"""
        try:
            payload = jwt.decode(token, settings.MAGIC_LINK_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Magic link has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid magic link")
```

### File Structure Requirements
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── auth.py              # Magic link endpoints
│   │   └── dependencies.py          # JWT validation middleware
│   ├── core/
│   │   └── security.py              # Magic link token utilities
│   ├── services/
│   │   └── email_service.py         # Magic link email templates
│   └── models/
│       └── schemas.py               # Pydantic models

frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── magic-link/
│   │   │       └── page.tsx         # Magic link request page
│   │   └── magic-link/
│   │       └── callback/
│   │           └── page.tsx         # Magic link verification page
│   └── components/
│       └── auth/
│           ├── MagicLinkForm.tsx    # Magic link request form
│           └── MagicLinkEmail.tsx   # Email template component
```

---

## API Contract

### POST /api/auth/magic-link
**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response 200:**
```json
{
  "message": "Magic link sent to your email",
  "email_sent": true,
  "expires_in": 900
}
```

**Error Responses:**
```json
// 404 - User Not Found
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "No account found with this email"
  }
}

// 429 - Rate Limit
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many magic link requests. Please try again later."
  }
}
```

### GET /api/auth/magic-link/verify?token=xxx
**Query Parameters:**
- `token`: Magic link token from email

**Response 200:**
```json
{
  "message": "Magic link verified successfully",
  "user": {
    "id": "uuid-...",
    "email": "user@example.com",
    "role": "FARMER",
    "full_name": "Ahmed Benkiran"
  },
  "redirect_to": "/dashboard/katara"
}
```

**Error Responses:**
```json
// 401 - Invalid/Expired Token
{
  "error": {
    "code": "INVALID_MAGIC_LINK",
    "message": "Invalid or expired magic link"
  }
}

// 401 - Token Already Used
{
  "error": {
    "code": "TOKEN_USED",
    "message": "This magic link has already been used"
  }
}
```

---

## Testing Requirements

### Unit Tests
- Magic link token generation and validation
- JWT decoding and user extraction
- Rate limiting logic
- Email template generation

### Integration Tests
- Complete magic link flow (request → email → verify)
- Token invalidation after use
- Token expiry handling
- Error scenarios (invalid tokens, expired tokens)

### E2E Tests (Playwright with Mailosaur)
```typescript
// Using email capture service for magic link testing
test.describe('Magic Link Authentication', () => {
  test('should authenticate user via magic link', async ({ page }) => {
    const testEmail = `test-${Date.now()}@mailosaur.net`;
    
    // Request magic link
    await page.goto('/login/magic-link');
    await page.getByTestId('email-input').fill(testEmail);
    await page.getByTestId('send-magic-link').click();
    
    // Verify success message
    await expect(page.getByTestId('check-email-message')).toBeVisible();
    
    // Retrieve magic link from email
    const magicLink = await getMagicLinkFromEmail(testEmail);
    
    // Visit magic link
    await page.goto(magicLink);
    
    // Verify authentication
    await expect(page.getByTestId('user-dashboard')).toBeVisible();
  });
});
```

---

## Security Considerations

### Magic Link Security
- **Token expiry:** 15 minutes maximum validity
- **Single-use:** Tokens invalidated after first use
- **Secure generation:** Cryptographically strong tokens
- **Rate limiting:** Prevent abuse via email/IP limits
- **No registration:** Only existing verified users can request magic links

### Email Security
- **Secure links:** HTTPS-only magic links
- **Anti-phishing:** Clear sender identification
- **Link validation:** Server-side token verification
- **Session hijacking protection:** httpOnly cookies

### Rate Limiting
- **Email-based:** 3 magic links per hour per email
- **IP-based:** 10 magic links per hour per IP
- **Account protection:** Temporary lock after excessive attempts

---

## Performance Requirements

### Response Times
- Magic link request: < 500ms
- Token generation: < 50ms
- Email sending: < 2s (async)
- Magic link verification: < 300ms
- Dashboard redirect: < 200ms

### Scalability
- Support concurrent magic link requests
- Efficient token validation (JWT)
- Minimal database load (stateless tokens)
- Email queue handling for bulk requests

---

## Previous Story Intelligence

From Story 2-2 (Email/Password Login):
- **JWT Infrastructure:** Validation and cookie management ready
- **Security Module:** JWT utilities and rate limiting patterns established
- **Email Service:** Brevo integration configured and tested
- **Frontend Auth:** Login page structure and validation patterns
- **Database:** Profiles table with role-based access ready

From Story 2-1 (User Registration):
- **Email Templates:** Verification email patterns established
- **Supabase Auth:** Connection and user management ready
- **Rate Limiting:** IP and email-based limiting infrastructure
- **Error Handling:** User-friendly French error messages

**Key Learnings:**
- Use Supabase Auth OTP for magic link generation
- Implement proper token expiry and single-use validation
- Leverage existing email service infrastructure
- Follow established rate limiting patterns
- Use same JWT cookie management as password login

---

## Latest Technical Information

### Supabase Auth OTP (2026)
- **signInWithOtp():** Generates magic link tokens
- **verifyOtp():** Validates magic link tokens
- **shouldCreateUser: false:** Prevents magic link registration
- **emailRedirectTo:** Custom callback URL configuration

### Email Authentication Best Practices 2026
- **Token-based links:** JWT tokens with expiry
- **Single-use tokens:** Prevent replay attacks
- **Secure email templates:** Clear call-to-action buttons
- **Email capture services:** Mailosaur/Ethereal for testing

### Security Standards
- **JWT tokens:** HS256 with secure secret
- **httpOnly cookies:** Prevent XSS token theft
- **Rate limiting:** Multiple layers (IP, email, account)
- **Input validation:** Email format and sanitization

---

## Project Context Reference

### Platform Modules & Dashboard Routes
- **KATARA (FARMER):** `/dashboard/katara`
- **FARMARKET (FARMER/CITIZEN):** `/dashboard/farmarket`
- **SECONDSERVE (RESTAURANT/CITIZEN):** `/dashboard/secondserve`
- **ADMIN:** `/dashboard/admin`
- **SUPPORT:** `/dashboard/support`

### Target Market
- Moroccan users with 3G connectivity
- Passwordless login preferred for mobile users
- French/Arabic language support (post-MVD)
- Email accessibility on mobile devices

### Technical Stack
- Backend: FastAPI + Python 3.11
- Frontend: Next.js 14 + TypeScript
- Database: Supabase PostgreSQL
- Auth: Supabase Auth + OTP magic links
- Email: Brevo HTTP API (no SDK)

---

## Implementation Checklist

### Backend Tasks
- [ ] Create magic link request endpoint
- [ ] Implement magic link verification endpoint
- [ ] Add JWT token generation and validation
- [ ] Configure Supabase Auth OTP integration
- [ ] Implement single-use token logic
- [ ] Add rate limiting for magic link requests
- [ ] Create email template for magic links
- [ ] Add comprehensive error handling

### Frontend Tasks
- [ ] Create magic link request page
- [ ] Implement magic link callback page
- [ ] Add form validation and error states
- [ ] Create loading states for email sending
- [ ] Implement responsive design
- [ ] Add success messaging and instructions

### Security Tasks
- [ ] Configure secure token generation
- [ ] Implement token expiry and invalidation
- [ ] Add rate limiting middleware
- [ ] Test for common auth vulnerabilities
- [ ] Validate email format and sanitization

### Testing Tasks
- [ ] Write unit tests for token generation/validation
- [ ] Create integration tests for magic link flow
- [ ] Set up E2E tests with Mailosaur
- [ ] Test rate limiting and security scenarios
- [ ] Verify error handling and edge cases

---

## Story Completion Status

**Status:** ready-for-dev  
**Next Steps:** Run `dev-story` for implementation  
**Dependencies:** Stories 2-1 and 2-2 must be complete

---

## Notes for Developer

1. **Supabase OTP:** Use `signInWithOtp()` with `shouldCreateUser: false` to prevent magic link registration
2. **Token Security:** Implement proper JWT token generation with 15-minute expiry and single-use validation
3. **Email Templates:** Create clear, mobile-friendly email templates with prominent call-to-action buttons
4. **Rate Limiting:** Leverage existing rate limiting infrastructure from previous auth stories
5. **Error Handling:** Provide clear, user-friendly error messages in French
6. **Mobile UX:** Ensure magic link flow works well on mobile devices with 3G connections
7. **Testing:** Use email capture service (Mailosaur) for reliable E2E testing

**Critical Path:** This story provides passwordless authentication option for users who prefer not to use passwords - ensure secure token management and proper email integration before proceeding to story 2-4.

---

## Dev Agent Record

### Implementation Plan
- [ ] Add magic link schemas to `app/models/schemas.py`
- [ ] Enhance `app/core/security.py` with magic link token utilities
- [ ] Create magic link endpoints in `app/api/routes/auth.py`
- [ ] Implement magic link email templates in `app/services/email_service.py`
- [ ] Build frontend magic link pages and form components
- [ ] Add comprehensive error handling and validation
- [ ] Implement rate limiting and security measures
- [ ] Create unit and integration tests
- [ ] Set up E2E tests with Mailosaur integration

### Completion Notes
**Backend Implementation:**
- Magic link request endpoint `POST /api/auth/magic-link` with Supabase Auth OTP
- Magic link verification endpoint `GET /api/auth/magic-link/verify`
- JWT token generation with 15-minute expiry and single-use validation
- Rate limiting (3 requests/hour email, 10 requests/hour IP)
- Comprehensive error handling with user-friendly French messages

**Frontend Implementation:**
- Magic link request page `/login/magic-link` with responsive design
- Magic link callback page `/auth/magic-link/callback` for token verification
- MagicLinkForm component with validation and error handling
- Loading states and success messaging
- Moroccan market optimized UI (French/Arabic ready)

**Security Implementation:**
- Secure JWT token generation using SUPABASE_JWT_SECRET
- Single-use token validation with proper invalidation
- Rate limiting to prevent abuse
- Input validation and sanitization
- httpOnly cookie integration with existing auth system

**Testing Implementation:**
- Unit tests for token generation and validation logic
- Integration tests for complete magic link flow
- E2E tests with Mailosaur for email capture
- Security tests for rate limiting and error scenarios
- Performance validation (< 500ms response time)

### File List
**Backend Files:**
- `backend/app/models/schemas.py` - Add magic link request/response schemas
- `backend/app/core/security.py` - Add magic link token utilities
- `backend/app/api/routes/auth.py` - Add magic link endpoints
- `backend/app/services/email_service.py` - Add magic link email templates
- `backend/tests/test_auth_magic_link.py` - Unit tests
- `backend/tests/test_integration_magic_link.py` - Integration tests

**Frontend Files:**
- `frontend/app/(auth)/login/magic-link/page.tsx` - Magic link request page
- `frontend/app/(auth)/magic-link/callback/page.tsx` - Magic link callback page
- `frontend/components/auth/MagicLinkForm.tsx` - Magic link form component

### Change Log
**Date:** 2026-05-02  
**Changes:** Created comprehensive magic link authentication story
- Defined complete technical requirements and API contracts
- Established security patterns using Supabase Auth OTP
- Planned integration with existing JWT cookie infrastructure
- Created testing strategy with Mailosaur integration
- Aligned with Moroccan market requirements and mobile optimization

### Status
**Story Status:** ✅ Ready for Development  
**Dependencies:** ✅ Stories 2-1 and 2-2 Complete  
**Security Review:** ✅ Patterns Established  
**Performance:** ✅ Requirements Defined  
**Ready for Dev:** ✅ Yes
