from fastapi import APIRouter

from app.api.routes import analysis, company, copilot, health, rules, upload

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
