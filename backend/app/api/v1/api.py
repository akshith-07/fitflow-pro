from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    organizations,
    members,
    membership_plans,
    memberships,
    checkins,
    classes,
    trainers,
    payments,
    staff,
    leads,
    equipment,
    analytics,
    invoices,
    notifications,
    reports,
    websocket
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Organizations
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

# Members & Memberships
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(membership_plans.router, prefix="/membership-plans", tags=["membership-plans"])
api_router.include_router(memberships.router, prefix="/memberships", tags=["memberships"])

# Check-ins
api_router.include_router(checkins.router, prefix="/check-ins", tags=["check-ins"])

# Classes
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])

# Staff & Trainers
api_router.include_router(trainers.router, prefix="/trainers", tags=["trainers"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])

# Payments & Invoices
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])

# Leads
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])

# Equipment
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])

# Analytics & Reports
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

# WebSocket
api_router.include_router(websocket.router, tags=["websocket"])
