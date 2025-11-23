# FitFlow Pro Backend API

Complete backend implementation for the FitFlow Pro Enterprise Gym Management SaaS Platform.

## 🏗️ Architecture

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+ ORM
- **Caching**: Redis 7+
- **Background Tasks**: Celery with Redis broker
- **Authentication**: JWT-based authentication
- **API Documentation**: Auto-generated OpenAPI/Swagger

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # Main API router
│   │       └── endpoints/          # API endpoints
│   │           ├── auth.py
│   │           ├── organizations.py
│   │           ├── members.py
│   │           ├── membership_plans.py
│   │           ├── memberships.py
│   │           ├── checkins.py
│   │           ├── classes.py
│   │           ├── trainers.py
│   │           ├── payments.py
│   │           ├── staff.py
│   │           ├── leads.py
│   │           └── equipment.py
│   ├── core/
│   │   ├── config.py               # Settings configuration
│   │   ├── deps.py                 # Dependencies
│   │   └── security.py             # Security utilities
│   ├── db/
│   │   ├── base.py                 # Base model
│   │   └── session.py              # Database session
│   ├── models/                     # SQLAlchemy models
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── member.py
│   │   ├── membership.py
│   │   ├── checkin.py
│   │   ├── class_model.py
│   │   ├── trainer.py
│   │   ├── payment.py
│   │   ├── staff.py
│   │   ├── lead.py
│   │   ├── equipment.py
│   │   └── notification.py
│   ├── schemas/                    # Pydantic schemas
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── member.py
│   │   ├── membership.py
│   │   ├── checkin.py
│   │   ├── class_schema.py
│   │   ├── trainer.py
│   │   ├── payment.py
│   │   ├── staff.py
│   │   ├── lead.py
│   │   ├── equipment.py
│   │   └── analytics.py
│   ├── services/                   # Business logic services
│   │   ├── payment_gateway.py      # Stripe/Razorpay integration
│   │   ├── notification.py         # Email/SMS/Push/WhatsApp
│   │   └── storage.py              # S3/Cloudinary file storage
│   ├── tasks/                      # Celery background tasks
│   │   ├── payments.py
│   │   ├── notifications.py
│   │   ├── memberships.py
│   │   └── analytics.py
│   ├── celery_app.py               # Celery configuration
│   └── main.py                     # FastAPI application
├── alembic/                        # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## ✨ Features Implemented

### 1. **Authentication & Authorization**
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- User roles: Super Admin, Gym Owner, Admin, Trainer, Receptionist, Member
- Multi-tenant architecture with organization-level data isolation

### 2. **Core API Endpoints**

#### Organizations (`/api/v1/organizations`)
- Create and manage gym organizations
- Organization settings and branding
- Multi-location support

#### Members (`/api/v1/members`)
- Complete member management (CRUD)
- Member profiles with photos and medical history
- Advanced search and filtering
- Member segmentation

#### Membership Plans (`/api/v1/membership-plans`)
- Create custom pricing plans
- Plan features and access hours
- Dynamic pricing support

#### Memberships (`/api/v1/memberships`)
- Assign memberships to members
- Freeze/unfreeze memberships
- Cancel memberships
- Automatic renewal
- Prorated billing

#### Check-ins (`/api/v1/check-ins`)
- QR code check-in
- Manual check-in by staff
- Real-time occupancy tracking
- Check-in statistics and analytics
- Member attendance history

#### Classes (`/api/v1/classes`)
- Class management (create, update, delete)
- Class scheduling with recurring support
- Member booking system
- Waitlist management
- Class attendance tracking
- Capacity management

#### Trainers (`/api/v1/trainers`)
- Trainer profiles with specializations
- Commission tracking
- Performance ratings
- Session management

#### Payments (`/api/v1/payments`)
- Payment processing
- Invoice generation
- Payment history
- Failed payment retry logic
- Refund processing

#### Staff (`/api/v1/staff`)
- Staff member management
- Role assignment
- Salary tracking

#### Leads (`/api/v1/leads`)
- Lead capture and management
- Lead status tracking
- Lead-to-member conversion
- Assignment to sales staff

#### Equipment (`/api/v1/equipment`)
- Equipment inventory
- Maintenance scheduling
- Status tracking

### 3. **Payment Gateway Integration**
- **Stripe Integration**:
  - Customer management
  - Payment intents
  - Subscriptions
  - Refunds
  - Webhooks support

- **Razorpay Integration**:
  - Indian payment methods (UPI, Cards, etc.)
  - Payment links
  - Recurring payments
  - Refunds

- **Abstraction Layer**: Easily switch between payment gateways

### 4. **Notification Services**
- **Email** (SendGrid):
  - Transactional emails
  - Template support
  - Bulk emails

- **SMS** (Twilio):
  - SMS notifications
  - Payment reminders
  - Class reminders

- **Push Notifications** (Firebase Cloud Messaging):
  - Mobile push notifications
  - Multicast support
  - Custom data payloads

- **WhatsApp** (Twilio Business API):
  - WhatsApp messages
  - Rich media support

### 5. **File Storage Services**
- **AWS S3**:
  - Secure file uploads
  - Public and private files
  - Presigned URLs

- **Cloudinary**:
  - Image uploads
  - Image transformations
  - Video support

### 6. **Background Tasks (Celery)**

#### Payment Tasks:
- Process recurring payments
- Retry failed payments
- Generate invoice PDFs

#### Notification Tasks:
- Send payment reminders
- Send class reminders (30 min before)
- Send welcome emails to new members
- Send birthday wishes

#### Membership Tasks:
- Check expiring memberships (7-day warning)
- Automatically expire memberships
- Check inactive members (14+ days)
- Send re-engagement emails
- Unfreeze memberships automatically

#### Analytics Tasks:
- Calculate weekly analytics
- Calculate monthly churn rate
- Predict churn risk (ML-based)

### 7. **Scheduled Jobs**
All background tasks run on schedules:
- Recurring payments: Daily at 2 AM
- Payment reminders: Daily at 9 AM
- Expiring memberships check: Daily at 8 AM
- Class reminders: Every hour
- Weekly analytics: Sundays at 1 AM
- Inactive members check: Mondays at 10 AM

## 🚀 Setup Instructions

### 1. Prerequisites
```bash
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fitflow_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Payment Gateways
STRIPE_SECRET_KEY=sk_test_xxx
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=xxx

# Notifications
SENDGRID_API_KEY=SG.xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# File Storage
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=fitflow-uploads

# Or use Cloudinary
CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
```

### 4. Database Setup
```bash
# Create database
createdb fitflow_db

# Run migrations
alembic upgrade head
```

### 5. Run Development Server
```bash
# Start FastAPI server
uvicorn app.main:app --reload

# API will be available at: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 6. Start Celery Workers
```bash
# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.celery_app beat --loglevel=info
```

## 📊 Database Models

### Core Models:
- **Organization**: Multi-tenant gym organizations
- **User**: Authentication and user management
- **Member**: Gym member profiles
- **MembershipPlan**: Pricing plans
- **Membership**: Member subscriptions
- **CheckIn**: Attendance tracking
- **Class**: Class definitions
- **ClassSchedule**: Class time slots
- **ClassBooking**: Member class bookings
- **Trainer**: Trainer profiles
- **Payment**: Payment records
- **Invoice**: Invoice generation
- **Staff**: Staff members
- **Lead**: Sales leads
- **Equipment**: Equipment inventory
- **Notification**: Notification logs

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Refresh token rotation
- Role-based access control (RBAC)
- Organization-level data isolation
- API rate limiting
- HTTPS enforcement
- SQL injection prevention (ORM)
- XSS protection
- CSRF tokens

## 📈 Analytics & Reporting

- Real-time dashboard metrics
- Member analytics (growth, retention, churn)
- Financial analytics (MRR, ARR, revenue trends)
- Attendance analytics (peak hours, occupancy)
- Class analytics (popularity, attendance rates)
- Trainer performance metrics
- Churn prediction (ML-based)
- Custom report generation

## 🧪 API Testing

### Swagger UI
Visit `http://localhost:8000/docs` for interactive API documentation

### Example API Calls

#### Authentication
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

#### Create Member
```bash
curl -X POST "http://localhost:8000/api/v1/members" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "member@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'
```

#### Check-in Member
```bash
curl -X POST "http://localhost:8000/api/v1/check-ins" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "uuid-here",
    "check_in_time": "2025-01-15T10:00:00",
    "method": "qr"
  }'
```

## 🔄 API Versioning

All APIs are versioned under `/api/v1/`. Future versions will be available at `/api/v2/`, etc.

## 📝 Development Workflow

1. **Create new feature branch**
2. **Implement models** in `app/models/`
3. **Create schemas** in `app/schemas/`
4. **Build API endpoints** in `app/api/v1/endpoints/`
5. **Add to router** in `app/api/v1/api.py`
6. **Create migration**: `alembic revision --autogenerate -m "description"`
7. **Run migration**: `alembic upgrade head`
8. **Test endpoints** using Swagger UI
9. **Commit and push**

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `psql -l`

### Redis Connection Issues
- Verify Redis is running: `redis-cli ping`
- Check REDIS_URL in `.env`

### Celery Tasks Not Running
- Ensure Redis is running
- Check Celery worker logs
- Verify task names match in `celery_app.py`

## 📚 Additional Documentation

- **API Reference**: Available at `/docs` and `/redoc`
- **Database Schema**: See `app/models/`
- **Business Logic**: See `app/services/`
- **Background Tasks**: See `app/tasks/`

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for all classes and functions
4. Create comprehensive tests
5. Update API documentation

## 📧 Support

For issues or questions, please contact the development team.

---

**Built with ❤️ for FitFlow Pro**
