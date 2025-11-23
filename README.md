# FitFlow Pro - Enterprise Gym Management SaaS Platform

A complete multi-tenant gym & fitness studio management SaaS platform with Flutter mobile apps, Next.js admin dashboard, FastAPI backend, automated recurring billing, class scheduling, QR check-ins, trainer management, analytics dashboards, and AI-powered member engagement features.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Flutter 3.16+](https://img.shields.io/badge/Flutter-3.16+-blue)](https://flutter.dev/)

## 🌟 Features

### 🏢 Multi-Tenant Architecture
- Complete tenant isolation with organization-based data segregation
- Custom subdomain for each gym (e.g., `gym-name.fitflowpro.com`)
- Row-level security and efficient multi-tenant queries
- Scalable architecture supporting unlimited gyms

### 👥 Member Management
- Complete member profiles with photos, medical history, and fitness goals
- Advanced search, filtering, and segmentation
- Member status tracking (active, frozen, expired, cancelled)
- Bulk import/export functionality
- Custom tags and notes
- Document uploads (ID, medical certificates)

### 💳 Automated Billing & Payments
- Recurring payment processing with smart retry logic
- Multiple payment gateways (Stripe, Razorpay)
- Automatic invoice generation and delivery
- Prorated billing and refund processing
- Grace periods and late fee calculation
- Payment method management
- Failed payment dunning sequences

### 🎯 Class Scheduling & Booking
- Drag-and-drop class schedule management
- Real-time availability and waitlist management
- Member booking via mobile app
- Automatic notifications and reminders
- No-show and late cancellation tracking
- Class analytics and performance metrics

### 📱 QR Code Check-Ins
- Multiple check-in methods (QR code, NFC, biometric, manual)
- Real-time occupancy tracking
- Attendance analytics and streak tracking
- Access control integration
- Gamification with badges and achievements

### 🏋️ Trainer Management
- Trainer profiles with specializations and certifications
- Session scheduling and management
- Client assignment and tracking
- Performance analytics
- Commission calculation
- Rating and review system

### 📊 Analytics & Reports
- Real-time dashboard with key metrics
- Revenue tracking (MRR, ARR, LTV)
- Member retention and churn analysis
- Attendance patterns and peak hours
- Class popularity and performance
- Custom report builder
- Automated report delivery

### 📲 Mobile Apps
- **Member App** (Flutter)
  - Profile and membership management
  - QR code check-ins
  - Class browsing and booking
  - Workout tracking
  - Progress photos and measurements
  - Social features and challenges

- **Trainer App** (Flutter)
  - Client management
  - Workout plan creation
  - Session tracking
  - Progress monitoring
  - Earnings dashboard

### 🌐 Web Admin Dashboard
- Modern, responsive design (Next.js + TailwindCSS)
- Role-based access control
- Real-time updates via WebSocket
- Dark mode support
- Comprehensive member management
- Financial reporting
- Staff management
- Equipment inventory
- Lead management

### 🔔 Notifications
- Multi-channel notifications (Email, SMS, Push, WhatsApp)
- Automated triggers for key events
- Customizable templates
- Scheduled campaigns
- Delivery tracking and analytics

### 🤖 AI Features
- Churn prediction and retention campaigns
- Personalized workout recommendations
- Smart class suggestions
- AI chatbot assistant

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Cache/Queue**: Redis 7+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Background Tasks**: Celery
- **Authentication**: JWT
- **API Docs**: OpenAPI/Swagger

### Web Dashboard
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: React 18 + TailwindCSS + Shadcn/ui
- **State**: Zustand
- **Data Fetching**: React Query
- **Auth**: NextAuth.js
- **Charts**: Recharts

### Mobile Apps
- **Framework**: Flutter 3.16+
- **Language**: Dart 3.0+
- **State**: Provider/Riverpod
- **HTTP**: Dio
- **Local DB**: Hive
- **Notifications**: Firebase Cloud Messaging

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose, Kubernetes
- **File Storage**: AWS S3 / Cloudinary
- **Payments**: Stripe, Razorpay
- **Email**: SendGrid
- **SMS**: Twilio
- **Push**: Firebase

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Flutter 3.16+ (for mobile apps)
- Docker & Docker Compose (optional)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/fitflow-pro.git
cd fitflow-pro

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Access the services:
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Web Dashboard: http://localhost:3000
```

### Manual Setup

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Setup database
createdb fitflow_db
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### 2. Web Dashboard Setup

```bash
cd web-dashboard

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### 3. Mobile App Setup

```bash
cd mobile-app

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run
```

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [API Documentation](docs/API.md) - Complete API reference

## 🏗️ Project Structure

```
fitflow-pro/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
│
├── web-dashboard/          # Next.js admin dashboard
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── mobile-app/            # Flutter member app
│   ├── lib/
│   │   ├── models/
│   │   ├── screens/
│   │   ├── services/
│   │   └── widgets/
│   └── pubspec.yaml
│
├── mobile-trainer-app/    # Flutter trainer app
│   ├── lib/
│   └── pubspec.yaml
│
├── docker/                # Docker configurations
│   └── docker-compose.yml
│
└── docs/                  # Documentation
    ├── SETUP.md
    ├── ARCHITECTURE.md
    └── API.md
```

## 🔐 Security

- JWT-based authentication with token rotation
- Role-based access control (RBAC)
- Password hashing with bcrypt
- SQL injection prevention via ORM
- XSS and CSRF protection
- Rate limiting on API endpoints
- HTTPS/TLS in production
- PCI compliance for payments
- GDPR-ready (data export/deletion)
- Audit logging for sensitive operations

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- **Email**: support@fitflowpro.com
- **Documentation**: https://docs.fitflowpro.com
- **Issues**: [GitHub Issues](https://github.com/your-repo/fitflow-pro/issues)

---

**Built with ❤️ for the fitness industry**
