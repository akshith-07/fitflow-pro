# FitFlow Pro - Architecture Overview

## System Architecture

FitFlow Pro is built as a modern, scalable SaaS platform using a microservices-inspired architecture.

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Mobile Apps    │     │  Web Dashboard  │     │  Admin Panel    │
│  (Flutter)      │     │  (Next.js)      │     │  (Next.js)      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   API Gateway / Load    │
                    │   Balancer (Optional)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   FastAPI Backend       │
                    │   - REST API            │
                    │   - WebSocket           │
                    │   - Authentication      │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌────────▼────────┐   ┌─────────▼─────────┐   ┌────────▼────────┐
│  PostgreSQL     │   │     Redis         │   │   Celery        │
│  (Primary DB)   │   │  (Cache/Queue)    │   │  (Background)   │
└─────────────────┘   └───────────────────┘   └─────────────────┘
         │
         │
┌────────▼────────────────────────────────────────────────────┐
│  External Services                                           │
│  - Stripe/Razorpay (Payments)                               │
│  - SendGrid (Email)                                         │
│  - Twilio (SMS/WhatsApp)                                    │
│  - Firebase (Push Notifications)                            │
│  - AWS S3 / Cloudinary (File Storage)                       │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic
- **Background Tasks**: Celery
- **Task Queue**: Redis

### Frontend (Web Dashboard)
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Language**: TypeScript
- **Styling**: TailwindCSS + Shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: React Query
- **Authentication**: NextAuth.js
- **Charts**: Recharts

### Mobile Apps (Flutter)
- **Framework**: Flutter 3.16+
- **Language**: Dart 3.0+
- **State Management**: Provider / Riverpod
- **HTTP Client**: Dio
- **Local Storage**: Hive
- **Push Notifications**: Firebase Cloud Messaging

### Database
- **Primary**: PostgreSQL 15+
- **Cache**: Redis 7+

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (Dev), Kubernetes (Prod)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Multi-Tenant Architecture

### Tenant Isolation
Each gym/organization is a separate tenant with isolated data:

```python
# All database models include organization_id
class Member(Base):
    id = UUID
    organization_id = UUID  # Tenant isolation
    user_id = UUID
    ...

# Middleware ensures users only access their organization's data
def get_current_organization(current_user: User) -> Organization:
    return db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
```

### Row-Level Security
- Every query is scoped to the current organization
- Middleware validates organization access
- Database indexes on `(organization_id, created_at)`

### Subdomain Routing
- Each gym gets a custom subdomain: `gym-name.fitflowpro.com`
- Subdomain resolves to organization via slug
- Tenant context set at middleware level

## Authentication & Authorization

### JWT-Based Authentication
```
1. User logs in with email/password
2. Backend validates credentials
3. Generate JWT access token (30 min expiry)
4. Generate refresh token (7 days expiry)
5. Client stores tokens securely
6. Access token sent in Authorization header
7. Refresh token used to get new access token
```

### Role-Based Access Control (RBAC)

Roles (in order of permissions):
1. **Super Admin** - Platform owner, full access
2. **Gym Owner** - Full access to their gym
3. **Admin** - Manage members, staff, operations
4. **Trainer** - Manage assigned clients only
5. **Receptionist** - Check-ins, basic operations
6. **Member** - Personal data access only

```python
# Endpoint protection example
@router.get("/members/")
def list_members(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.GYM_OWNER]))
):
    # Only admins and gym owners can list all members
    ...
```

## Data Flow

### Member Check-In Flow
```
1. Member opens mobile app
2. Display QR code from local storage
3. Scan QR code at gym kiosk/turnstile
4. POST /api/v1/check-ins with QR code
5. Backend validates:
   - QR code is valid
   - Membership is active
   - Payment is current
   - Access hours allow entry
6. Grant or deny access
7. WebSocket broadcasts check-in to dashboard
8. Update occupancy count in real-time
```

### Recurring Payment Flow
```
1. Celery scheduled task runs daily
2. Query memberships expiring today
3. Attempt payment via Stripe/Razorpay
4. On success:
   - Create payment record
   - Generate invoice
   - Extend membership
   - Send confirmation email/SMS
5. On failure:
   - Retry with exponential backoff (3 attempts)
   - Send payment failed notification
   - After grace period: freeze membership
```

### Real-Time Updates (WebSocket)
```
Client                    Server                    Database
  │                         │                          │
  │─── Connect WS ─────────▶│                          │
  │◀── Connected ───────────│                          │
  │                         │                          │
  │                         │◀─ Check-in event ────────│
  │◀── Check-in data ───────│                          │
  │                         │                          │
  │─── Disconnect ─────────▶│                          │
```

## Database Schema

### Core Tables
- `organizations` - Gym/tenant data
- `users` - All user accounts
- `members` - Member profiles
- `membership_plans` - Subscription plans
- `memberships` - Active subscriptions
- `check_ins` - Attendance records
- `classes` - Class templates
- `class_schedules` - Scheduled class instances
- `class_bookings` - Member bookings
- `trainers` - Trainer profiles
- `payments` - Payment transactions
- `invoices` - Generated invoices
- `notifications` - Notification log

### Indexes
```sql
-- Multi-tenant queries
CREATE INDEX idx_members_org_created
ON members (organization_id, created_at DESC);

-- Check-in lookup
CREATE INDEX idx_checkins_member_time
ON check_ins (member_id, check_in_time DESC);

-- Active memberships
CREATE INDEX idx_memberships_status
ON memberships (organization_id, status, end_date);
```

## API Design

### RESTful Endpoints
```
# Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

# Organizations
GET    /api/v1/organizations/
POST   /api/v1/organizations/
GET    /api/v1/organizations/{id}
PUT    /api/v1/organizations/{id}
DELETE /api/v1/organizations/{id}

# Members
GET    /api/v1/members/
POST   /api/v1/members/
GET    /api/v1/members/{id}
PUT    /api/v1/members/{id}
DELETE /api/v1/members/{id}

# Similar patterns for:
# - Membership Plans
# - Classes
# - Check-ins
# - Payments
# - Analytics
# - Reports
```

### WebSocket Endpoints
```
WS /ws/check-ins          # Real-time check-in updates
WS /ws/bookings           # Class booking updates
WS /ws/notifications      # Push notifications
WS /ws/occupancy          # Current gym occupancy
```

## Caching Strategy

### Redis Cache Layers
1. **User Session Cache** (TTL: 30 min)
   - JWT token validation
   - User permissions

2. **Data Cache** (TTL: varies)
   - Organization settings: 1 hour
   - Membership plans: 1 hour
   - Class schedules: 15 min
   - Member profiles: 5 min

3. **Rate Limiting** (TTL: 1 min)
   - API rate limits per user/IP
   - Failed login attempts

4. **Task Queue**
   - Celery task queue
   - Background job processing

## Scalability Considerations

### Horizontal Scaling
- Stateless API design allows multiple instances
- Load balancer distributes traffic
- Redis for shared session state
- WebSocket connections via Redis Pub/Sub

### Database Scaling
- Read replicas for analytics queries
- Connection pooling (10-20 connections)
- Pagination on all list endpoints
- Efficient indexes for tenant isolation

### File Storage
- Offload to AWS S3 / Cloudinary
- CDN for static assets
- Async file uploads via Celery

## Security

### API Security
- HTTPS only in production
- JWT tokens with short expiry
- Rate limiting (60 req/min per user)
- CORS configuration
- SQL injection prevention (ORM)
- XSS protection
- CSRF tokens

### Data Security
- Password hashing (bcrypt)
- Sensitive data encryption
- PII protection
- Payment data tokenization (PCI compliance)
- Audit logs for sensitive operations

### Mobile App Security
- Certificate pinning
- Secure local storage (Hive encrypted)
- Biometric authentication
- No sensitive data in logs

## Monitoring & Observability

### Metrics
- Request latency (p50, p95, p99)
- Error rates
- Database query performance
- Cache hit rates
- Background job success/failure

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking (Sentry)
- Audit logs for compliance

### Alerts
- API downtime
- Database connection issues
- Failed payment processing
- High error rates
- Disk space warnings

## Deployment Architecture

### Development
- Docker Compose
- Local PostgreSQL
- Local Redis
- Hot reload enabled

### Staging
- Kubernetes cluster
- Managed PostgreSQL (RDS)
- Managed Redis (ElastiCache)
- CI/CD via GitHub Actions

### Production
- Multi-region Kubernetes
- PostgreSQL with replication
- Redis cluster
- CDN (CloudFlare)
- Auto-scaling enabled
- Blue-green deployments
- Monitoring & alerting
- Automated backups

## Future Enhancements

1. **Microservices Split**
   - Payment service
   - Notification service
   - Analytics service

2. **Advanced Features**
   - AI-powered churn prediction
   - Personalized workout recommendations
   - Computer vision form checking
   - Voice-activated check-ins

3. **Performance**
   - GraphQL API option
   - Edge computing for global latency
   - Serverless functions for background tasks

4. **Integrations**
   - Wearable device sync (Fitbit, Apple Health)
   - Accounting software (QuickBooks, Xero)
   - CRM integration (Salesforce)
   - Marketing automation (HubSpot)
