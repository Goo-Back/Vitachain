# Technical Architecture Decisions
# VitaChain v2.0 — Moroccan Agri-Food Platform

---

## Document Metadata

| Field | Value |
|---|---|
| **Project** | VitaChain v2.0 |
| **Author** | Winston (System Architect) |
| **Version** | 1.0 |
| **Date** | 2026-05-01 |
| **Status** | Approved for Implementation |
| **Review** | Aligns with PRD requirements |

---

## Executive Architecture Summary

VitaChain is a **microservices-based platform** optimized for Moroccan market constraints (3G connectivity, rural access) with four integrated modules:

- **KATARA** — Smart farming IoT with AI agronomic analysis
- **FARMARKET** — B2B agricultural marketplace  
- **BOTABA9A** — IoT marketing showcase for restaurants
- **SECONDSERVE** — Click & Collect surplus meal marketplace

The architecture follows **boring technology principles** with proven, stable components that prioritize developer productivity and operational reliability.

---

## 1. Core Architectural Decisions

### 1.1 Platform Architecture: Monolithic Frontend + Modular Backend

**Decision:** Single Next.js frontend with separate FastAPI microservices per business module.

**Rationale:**
- **Simplicity:** One frontend deployment, shared authentication state
- **Performance:** Optimized for 3G connections with single bundle
- **Maintainability:** Clear module boundaries while avoiding frontend complexity
- **Cost:** Single VPS deployment for MVP phase

**Trade-offs:**
- ❌ Frontend coupling across modules
- ✅ Reduced operational complexity
- ✅ Shared UI components and design system

### 1.2 Database Strategy: Supabase as Primary Data Store

**Decision:** Use Supabase (PostgreSQL + Auth + Realtime) as the single database solution.

**Rationale:**
- **Integrated Auth:** Built-in JWT authentication with RLS
- **Realtime:** WebSocket subscriptions for live updates
- **Security:** Row Level Security replaces custom authorization logic
- **Operations:** Managed backups, SSL, and maintenance
- **Cost:** Predictable pricing, no DBA overhead

**Trade-offs:**
- ❌ Vendor lock-in to Supabase
- ❌ Limited database-level customization
- ✅ Zero database maintenance overhead
- ✅ Built-in real-time capabilities

### 1.3 Container Strategy: Docker Compose on Single VPS

**Decision:** Deploy all services via Docker Compose on a single DigitalOcean VPS for MVP.

**Rationale:**
- **Simplicity:** No Kubernetes complexity for initial deployment
- **Cost:** Single VPS (~$110/month) fits budget constraints
- **Scalability Path:** Can extract services to separate VPS later
- **Development:** Parity between dev and prod environments

**Trade-offs:**
- ❌ Single point of failure
- ❌ Limited horizontal scaling
- ✅ Predictable costs and simple operations
- ✅ Fast deployment and rollback

---

## 2. Technology Stack Decisions

### 2.1 Frontend: Next.js 14 + TypeScript

**Decision:** Next.js 14 with TypeScript, Tailwind CSS, and shadcn/ui components.

**Rationale:**
- **Performance:** Automatic optimization and code splitting
- **SEO:** Built-in SSG support for marketing pages
- **Developer Experience:** TypeScript safety, hot reload
- **Ecosystem:** Large component library and community support
- **Mobile-First:** Responsive design optimized for 3G

**Alternatives Considered:**
- React SPA: ❌ No built-in routing/SSG
- Vue.js: ❌ Smaller ecosystem in Morocco
- Angular: ❌ Too complex for MVP timeline

### 2.2 Backend: FastAPI + Python 3.11

**Decision:** FastAPI with async/await patterns and Pydantic validation.

**Rationale:**
- **Performance:** Async I/O for IoT telemetry ingestion
- **Documentation:** Auto-generated OpenAPI specs
- **Validation:** Pydantic prevents runtime errors
- **Python Ecosystem:** Rich libraries for AI/ML integration
- **Type Safety:** Full TypeScript-like experience in Python

**Critical Implementation Rules:**
```python
# ✅ ALWAYS use async patterns
async def create_meal_reservation(meal_id: UUID, quantity: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(...)

# ❌ NEVER use sync patterns in FastAPI
def create_meal_reservation_sync(meal_id: UUID, quantity: int):
    response = requests.post(...)  # Blocks event loop
```

### 2.3 Database Access: Direct Supabase Client

**Decision:** Use `supabase-py` directly instead of SQLAlchemy ORM.

**Rationale:**
- **Simplicity:** No ORM abstraction layer to maintain
- **Performance:** Direct SQL execution
- **Realtime:** Built-in WebSocket support
- **Security:** RLS handles authorization at database level

**Critical Implementation Rules:**
```python
# ✅ Direct Supabase client
result = supabase.table('telemetry_readings').insert(data).execute()

# ❌ NEVER use SQLAlchemy
session.add(TelemetryReading(**data))
session.commit()
```

---

## 3. Security Architecture

### 3.1 Authentication: Supabase Auth + JWT

**Decision:** Delegate authentication entirely to Supabase Auth.

**Flow:**
1. User signs in via Supabase client
2. JWT returned with 24h expiry, 30d refresh token
3. JWT stored in httpOnly cookie via @supabase/ssr
4. Backend validates JWT on protected routes
5. RLS policies enforce data access

**Security Benefits:**
- ✅ No password storage in application code
- ✅ Automatic token refresh handling
- ✅ Built-in MFA support (future)
- ✅ GDPR compliance (user data deletion)

### 3.2 Authorization: Row Level Security (RLS)

**Decision:** Implement all authorization via PostgreSQL RLS policies.

**Rationale:**
- **Database-Level Security:** Policies enforced even if application bugs
- **Performance:** No application-level authorization checks
- **Simplicity:** Single source of truth for access rules
- **Audit:** All access logged in PostgreSQL

**Critical RLS Patterns:**
```sql
-- ✅ Owner-based access
CREATE POLICY "farmers_own_their_listings" ON farm_listings
FOR ALL USING (farmer_id = auth.uid());

-- ✅ Role-based access  
CREATE POLICY "admin_full_access" ON profiles
FOR ALL USING (auth.jwt()->>'role' = 'ADMIN');

-- ✅ Public read access
CREATE POLICY "public_read_listings" ON farm_listings
FOR SELECT USING (true);
```

### 3.3 API Security: NGINX Gateway + Rate Limiting

**Decision:** Use NGINX as reverse proxy with security headers and rate limiting.

**Configuration:**
```nginx
# Rate limiting per IP
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=telemetry:10m rate=100r/s;

# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

---

## 4. Data Architecture

### 4.1 Database Schema Design

**Decision:** Normalized schema with UUID primary keys and audit fields.

**Key Principles:**
- **UUIDs:** Prevent ID enumeration attacks
- **Audit Fields:** `created_at`, `updated_at` on all tables
- **Soft Deletes:** Status fields instead of DELETE operations
- **Foreign Keys:** Enforce data integrity

**Critical Tables:**
```sql
-- User profiles with role-based access
profiles (id UUID PK, role TEXT, full_name TEXT, phone TEXT)

-- IoT device registration
iot_devices (id UUID PK, device_id TEXT UNIQUE, farmer_id UUID FK)

-- Time-series telemetry data
telemetry_readings (id UUID PK, device_id TEXT, farmer_id UUID FK, 
                    temperature FLOAT, humidity FLOAT, ndvi FLOAT, 
                    timestamp TIMESTAMPTZ)

-- Marketplace listings
farm_listings (id UUID PK, farmer_id UUID FK, title TEXT, 
               product_type TEXT, quantity_kg FLOAT, price_per_kg FLOAT)
```

### 4.2 Real-time Data Strategy

**Decision:** Use Supabase Realtime for live dashboard updates.

**Implementation:**
```typescript
// Frontend subscription to sensor data
const subscription = supabase
  .channel('telemetry')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'telemetry_readings' },
    (payload) => updateDashboard(payload.new)
  )
  .subscribe();
```

**Use Cases:**
- ✅ Live telemetry updates in KATARA dashboard
- ✅ Real-time meal availability in SECONDSERVE
- ✅ New order notifications in FARMARKET
- ❌ Complex analytics (use batch processing)

---

## 5. Integration Architecture

### 5.1 AI Integration: Claude API via Async Client

**Decision:** Use Anthropic's Claude API for agronomic analysis.

**Architecture:**
```python
# Async AI service
class AIAnalysisService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_farm_data(self, telemetry_data: List[TelemetryReading]):
        prompt = self.build_agronomic_prompt(telemetry_data)
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

**Error Handling Strategy:**
- **Timeout:** 30-second limit with graceful degradation
- **Rate Limits:** Exponential backoff on 429 errors
- **Fallback:** Log error and continue without AI recommendation
- **Circuit Breaker:** Disable AI calls after repeated failures

### 5.2 Email Integration: Direct HTTP to Brevo

**Decision:** Use httpx for email sending instead of SDK.

**Rationale:**
- **Simplicity:** One less dependency to manage
- **Control:** Full control over retry logic
- **Performance:** Async HTTP client

**Implementation:**
```python
async def send_pickup_confirmation(email: str, pickup_code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": settings.BREVO_API_KEY},
            json={
                "to": [{"email": email}],
                "subject": "Votre code de retrait SecondServe",
                "htmlContent": f"Votre code: {pickup_code}"
            }
        )
    response.raise_for_status()
```

---

## 6. Performance Architecture

### 6.1 Caching Strategy

**Decision:** Multi-layer caching with Redis for frequently accessed data.

**Cache Layers:**
1. **Application Cache:** In-memory for session data
2. **Redis Cache:** Shared cache for API responses
3. **CDN Cache:** Static assets via NGINX
4. **Browser Cache:** Proper cache headers

**Redis Usage Patterns:**
```python
# Cache weather data for 15 minutes
@cache(expire=900)
async def get_weather_data(lat: float, lng: float):
    return await openweather_api.get_weather(lat, lng)

# Cache satellite imagery for 24 hours  
@cache(expire=86400)
async def get_ndvi_image(lat: float, lng: float):
    return await sentinel_hub.get_ndvi(lat, lng)
```

### 6.2 Database Optimization

**Decision:** Strategic indexing and query optimization for 3G performance.

**Index Strategy:**
```sql
-- Time-series queries (telemetry)
CREATE INDEX idx_telemetry_device_time 
ON telemetry_readings (device_id, timestamp DESC);

-- User-specific queries (alerts)
CREATE INDEX idx_alerts_farmer_unread 
ON katara_alerts (farmer_id, is_read, created_at DESC);

-- Geographic queries (marketplace)
CREATE INDEX idx_listings_location 
ON farm_listings USING GIST (point(location_lng, location_lat));
```

**Query Optimization Rules:**
- ✅ Use specific column selection instead of `SELECT *`
- ✅ Implement pagination with `LIMIT/OFFSET`
- ✅ Use `EXPLAIN ANALYZE` for slow queries
- ❌ Avoid N+1 queries with proper JOINs

---

## 7. Deployment Architecture

### 7.1 Container Strategy

**Decision:** Docker Compose with separate containers per service.

**Docker Compose Structure:**
```yaml
services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    
  frontend:
    build: ./frontend
    expose: ["3000"]
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      
  backend-katara:
    build: ./backend
    expose: ["8000"]
    environment:
      - DATABASE_URL=${SUPABASE_DB_URL}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      
  backend-farmarket:
    build: ./backend
    expose: ["8001"]
    command: ["uvicorn", "app.api.routes.farmarket:app", "--port", "8001"]
```

**Security Rules:**
- ✅ Only NGINX exposed to internet
- ✅ Internal services use Docker network
- ✅ Secrets via environment variables
- ❌ No volume mounts for production code

### 7.2 SSL and Security

**Decision:** Let's Encrypt for SSL with automatic renewal.

**Implementation:**
```bash
# Certbot with NGINX plugin
certbot --nginx -d vitachain.ma -d api.vitachain.ma
# Auto-renewal via cron
0 12 * * * /usr/bin/certbot renew --quiet
```

**Security Headers:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

---

## 8. Monitoring and Observability

### 8.1 Application Monitoring

**Decision:** Structured logging with health check endpoints.

**Logging Strategy:**
```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info("telemetry_received", 
           device_id=device_id, 
           temperature=temperature,
           processing_time_ms=processing_time)

# Error tracking
logger.error("ai_analysis_failed",
            error=str(e),
            device_id=device_id,
            fallback_used=True)
```

**Health Checks:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await check_database(),
            "ai_api": await check_claude_api(),
            "email_service": await check_brevo_api()
        }
    }
```

### 8.2 Performance Monitoring

**Decision:** Application metrics with alerting on critical failures.

**Key Metrics:**
- **API Response Time:** P95 < 200ms
- **Telemetry Ingestion:** < 50ms
- **Database Connection Pool:** < 80% utilization
- **Memory Usage:** < 80% container limit
- **Disk Space:** < 85% utilization

**Alert Thresholds:**
```yaml
alerts:
  - name: "API Latency High"
    condition: "api_p95_response_time > 500ms"
    action: "notify_dev_team"
    
  - name: "Telemetry Pipeline Down"
    condition: "telemetry_ingestion_failures > 10/min"
    action: "immediate_notification"
```

---

## 9. Scalability Path

### 9.1 Horizontal Scaling Strategy

**Phase 1 (MVP): Single VPS**
- All services on one DigitalOcean VPS
- Load handled via vertical scaling
- Cost: ~$110/month

**Phase 2 (Growth): Service Separation**
- Extract backend services to separate VPS
- Database remains on Supabase
- Add Redis cluster for caching
- Cost: ~$250/month

**Phase 3 (Scale): Microservices**
- Container orchestration (Kubernetes/ECS)
- Database read replicas
- CDN for static assets
- Cost: ~$800/month

### 9.2 Database Scaling

**Decision:** Stay with Supabase until specific scaling needs arise.

**Scaling Triggers:**
- > 1M telemetry readings per month
- > 10k concurrent users
- Complex analytics requirements
- Multi-region deployment needs

**Migration Path:**
1. Export data via Supabase pg_dump
2. Import to managed PostgreSQL
3. Update connection strings
4. Migrate authentication to custom solution

---

## 10. Risk Mitigation

### 10.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Supabase Downtime** | High | Implement health checks + graceful degradation |
| **Claude API Limits** | Medium | Fallback to rule-based recommendations |
| **VPS Failure** | High | Automated backups + quick redeployment |
| **3G Connectivity** | High | Optimized bundle sizes < 500KB |

### 10.2 Security Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data Breach** | Critical | RLS + encryption + audit logs |
| **IoT Device Compromise** | Medium | API key rotation + device whitelisting |
| **DDoS Attack** | Medium | NGINX rate limiting + Cloudflare |
| **JWT Token Theft** | High | httpOnly cookies + short expiry |

---

## 11. Implementation Guidelines

### 11.1 Development Rules

**Critical Architecture Rules:**
```python
# ✅ ALWAYS use async patterns in FastAPI
@app.post("/api/telemetry")
async def ingest_telemetry(data: TelemetryData):
    await telemetry_service.process_reading(data)

# ✅ ALWAYS extract user ID from JWT
farmer_id = get_current_user().id  # From JWT.sub

# ✅ ALWAYS use Supabase client directly
result = supabase.table("telemetry_readings").insert(data).execute()

# ❌ NEVER use sync HTTP clients
response = requests.get(url)  # Blocks event loop

# ❌ NEVER trust user input for ownership
farmer_id = request.body.farmer_id  # Security vulnerability
```

### 11.2 Code Organization

**Backend Structure:**
```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── telemetry.py      # M1 endpoints
│   │   │   ├── farmarket.py      # M2 endpoints
│   │   │   └── secondserve.py    # M4 endpoints
│   │   └── dependencies.py        # JWT validation
│   ├── services/
│   │   ├── telemetry_service.py  # Business logic
│   │   ├── ai_service.py         # Claude integration
│   │   └── notification_service.py
│   └── models/
│       └── schemas.py            # Pydantic models
```

**Frontend Structure:**
```
frontend/
├── app/
│   ├── (dashboard)/
│   │   ├── katara/               # M1 pages
│   │   ├── farmarket/            # M2 pages
│   │   └── secondserve/          # M4 pages
│   ├── (public)/
│   │   ├── farmarket/            # Public marketplace
│   │   └── botaba9a/             # Marketing pages
│   └── components/
│       └── ui/                   # Shared component library
```

---

## 12. Testing Strategy

### 12.1 Testing Architecture

**Decision:** Pyramid testing with comprehensive integration tests.

**Test Layers:**
1. **Unit Tests:** Individual functions and services
2. **Integration Tests:** API endpoints with test database
3. **E2E Tests:** Critical user journeys (Playwright)
4. **Performance Tests:** Load testing for telemetry ingestion

**Critical Test Coverage:**
- ✅ Authentication and authorization flows
- ✅ Telemetry ingestion pipeline
- ✅ Marketplace order creation
- ✅ Meal reservation atomicity
- ✅ AI service integration

---

## 13. Conclusion

This architecture prioritizes **simplicity, reliability, and maintainability** while meeting VitaChain's specific requirements for the Moroccan market. The decisions balance current MVP constraints with future scalability needs.

**Key Success Factors:**
1. **Boring Technology:** Proven, stable components
2. **Developer Productivity:** Clear patterns and conventions
3. **Operational Simplicity:** Minimal infrastructure complexity
4. **Security by Design:** RLS and JWT-first approach
5. **Performance First:** Optimized for 3G connectivity

The architecture provides a solid foundation for VitaChain's growth while maintaining the agility to pivot as market requirements evolve.

---

## Architecture Review Checklist

- [x] **Performance:** All response times meet PRD requirements
- [x] **Security:** Authentication, authorization, and data protection
- [x] **Scalability:** Clear path for growth phases
- [x] **Maintainability:** Clean code organization and patterns
- [x] **Reliability:** Error handling and graceful degradation
- [x] **Cost Efficiency:** Fits within OPEX budget constraints
- [x] **Market Fit:** Optimized for Moroccan 3G connectivity
- [x] **Developer Experience:** Clear guidelines and tooling

**Status:** ✅ Approved for Implementation
