from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date
from uuid import UUID


# Dashboard Analytics
class DashboardMetrics(BaseModel):
    current_occupancy: int
    checkins_today: int
    checkins_yesterday: int
    revenue_today: float
    revenue_yesterday: float
    active_memberships: int
    new_members_today: int
    expiring_memberships_this_week: int
    overdue_payments: int
    class_bookings_today: int


# Member Analytics
class MemberAnalytics(BaseModel):
    total_members: int
    total_active: int
    total_frozen: int
    total_expired: int
    total_cancelled: int
    member_growth: List[Dict[str, Any]]
    gender_distribution: List[Dict[str, Any]]


# Revenue Analytics
class RevenueAnalytics(BaseModel):
    total_revenue: float
    mrr: float
    arr: float
    revenue_by_payment_method: List[Dict[str, Any]]
    daily_revenue: List[Dict[str, Any]]
    start_date: Any
    end_date: Any


# Financial Analytics
class FinancialAnalytics(BaseModel):
    monthly_recurring_revenue: float
    annual_recurring_revenue: float
    revenue_by_plan: List[Dict[str, Any]]
    revenue_by_period: List[Dict[str, Any]]
    payment_method_breakdown: Dict[str, float]
    refunds_total: float
    profit_margin: float


# Attendance Analytics
class AttendanceAnalytics(BaseModel):
    total_checkins: int
    daily_checkins: List[Dict[str, Any]]
    peak_hours: List[Dict[str, Any]]
    average_session_duration_minutes: float
    start_date: Any
    end_date: Any


# Class Analytics
class ClassAnalytics(BaseModel):
    popular_classes: List[Dict[str, Any]]
    average_attendance: List[Dict[str, Any]]
    total_bookings: int
    no_shows: int
    no_show_rate: float
    start_date: Any
    end_date: Any


# Trainer Performance
class TrainerPerformance(BaseModel):
    trainer_id: UUID
    trainer_name: str
    total_sessions: int
    total_classes: int
    average_rating: float
    revenue_generated: float
    commission_earned: float
    client_retention_rate: float
    member_satisfaction: float


# Churn Prediction
class ChurnPrediction(BaseModel):
    member_id: UUID
    member_name: str
    churn_risk_score: float  # 0-1, higher = more likely to churn
    last_visit_days_ago: int
    membership_expires_in_days: int
    attendance_trend: str  # increasing, stable, declining
    recommended_actions: List[str]


# Revenue Forecast
class RevenueForecast(BaseModel):
    month: str
    predicted_revenue: float
    confidence_interval_low: float
    confidence_interval_high: float


# Custom Report Request
class ReportRequest(BaseModel):
    report_type: str  # membership, financial, attendance, class, trainer
    start_date: date
    end_date: date
    filters: Optional[Dict[str, Any]] = None
    group_by: Optional[str] = None
    format: str = "pdf"  # pdf, excel, csv


# Report Response
class ReportResponse(BaseModel):
    id: UUID
    report_type: str
    status: str  # pending, processing, completed, failed
    file_url: Optional[str] = None
    created_at: date
    completed_at: Optional[date] = None
