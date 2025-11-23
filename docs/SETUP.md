# FitFlow Pro - Setup Guide

## Prerequisites

### Backend Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- pip

### Web Dashboard Requirements
- Node.js 20+
- npm or yarn

### Mobile App Requirements
- Flutter 3.16+
- Dart 3.0+
- Android Studio (for Android)
- Xcode (for iOS, macOS only)

## Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Navigate to project root
cd fitflow-pro

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check if all services are running
docker-compose -f docker/docker-compose.yml ps

# Backend API: http://localhost:8000
# Web Dashboard: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Manual Setup

### 1. Backend API Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and configure your settings
nano .env

# Create database
# Make sure PostgreSQL is running, then:
createdb fitflow_db

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 2. Web Dashboard Setup

```bash
# Navigate to web dashboard directory
cd web-dashboard

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local and configure your settings
nano .env.local

# Start development server
npm run dev

# Dashboard will be available at http://localhost:3000
```

### 3. Mobile App Setup

#### Member App

```bash
# Navigate to mobile app directory
cd mobile-app

# Get Flutter dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Build APK for Android
flutter build apk

# Build for iOS (macOS only)
flutter build ios
```

#### Trainer App

```bash
# Navigate to trainer app directory
cd mobile-trainer-app

# Get Flutter dependencies
flutter pub get

# Run on connected device/emulator
flutter run
```

## Database Setup

### Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE fitflow_db;

-- Create user
CREATE USER fitflow WITH PASSWORD 'fitflow';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fitflow_db TO fitflow;
```

### Run Migrations

```bash
cd backend

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Downgrade (if needed)
alembic downgrade -1
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://fitflow:fitflow@localhost:5432/fitflow_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# API
API_V1_PREFIX=/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Payment Gateways
STRIPE_SECRET_KEY=sk_test_xxx
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=xxx

# Email
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@fitflowpro.com

# SMS
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890

# File Storage
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=fitflow-uploads
```

### Web Dashboard (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

NEXT_PUBLIC_APP_NAME=FitFlow Pro
```

## Creating Your First Organization

Once the backend is running, you can create your first organization:

```bash
# Use the API docs at http://localhost:8000/docs

# Or use curl:
curl -X POST "http://localhost:8000/api/v1/organizations/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Gym",
    "slug": "my-gym",
    "contact_email": "admin@mygym.com",
    "contact_phone": "+1234567890",
    "timezone": "America/New_York",
    "currency": "USD"
  }'
```

## Creating Admin User

```bash
# Register first user via API
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mygym.com",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "gym_owner",
    "organization_id": "your-org-id-here"
  }'
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Should respond with PONG

# Start Redis
redis-server
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Next Steps

1. Configure payment gateways (Stripe/Razorpay)
2. Set up email service (SendGrid)
3. Configure SMS service (Twilio)
4. Set up Firebase for push notifications
5. Configure AWS S3 or Cloudinary for file storage
6. Set up SSL certificates for production
7. Configure domain and subdomain routing
8. Set up monitoring and logging

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-repo/fitflow-pro/issues
- Documentation: https://docs.fitflowpro.com
- Email: support@fitflowpro.com
