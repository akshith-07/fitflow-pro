from fastapi import APIRouter
from app.api.v1.endpoints import auth, organizations, members

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(members.router, prefix="/members", tags=["members"])

# Add more routers as needed:
# api_router.include_router(membership_plans.router, prefix="/membership-plans", tags=["membership-plans"])
# api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
# api_router.include_router(check_ins.router, prefix="/check-ins", tags=["check-ins"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
# etc...
