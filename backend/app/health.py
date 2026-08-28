from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class HealthStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ok"]


@router.get("/health")
def get_health() -> HealthStatus:
    return HealthStatus(status="ok")
