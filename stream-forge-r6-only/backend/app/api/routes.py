from fastapi import APIRouter

from app.schemas.dashboard import MidReviewResponse, Week1Response, Week2Response
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api", tags=["dashboard"])
service = DashboardService()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/week1", response_model=Week1Response)
def get_week1() -> Week1Response:
    return service.get_week1_dashboard()


@router.get("/week2", response_model=Week2Response)
def get_week2() -> Week2Response:
    return service.get_week2_dashboard()


@router.get("/mid-review", response_model=MidReviewResponse)
def get_mid_review() -> MidReviewResponse:
    return service.get_mid_review_dashboard()
