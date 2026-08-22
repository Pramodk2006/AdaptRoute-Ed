"""
Routing router — API endpoints for multi-LLM router telemetry and policy management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.routing_service import RoutingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/routing", tags=["Routing Telemetry"])


class PolicyConfigRequest(BaseModel):
    policy: str  # heuristic | bandit


@router.get("/telemetry")
def get_router_telemetry(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve telemetry metrics for the adaptive routing engine."""
    service = RoutingService(db)
    return service.get_telemetry(user_id=current_user.id)


@router.put("/config")
def update_router_policy(
    body: PolicyConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update active routing policy ('heuristic' or 'bandit')."""
    try:
        service = RoutingService(db)
        return service.set_policy(body.policy)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
