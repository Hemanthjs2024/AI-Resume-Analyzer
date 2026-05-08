import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from services.roadmap_engine import generate_weekly_plan

logger = logging.getLogger("resume-agent.roadmap")
router = APIRouter()


class RoadmapRequest(BaseModel):
    committed_projects: list[dict[str, Any]]
    skill_gaps: list[dict[str, Any]] = []
    user_level: str = "fresher"


@router.post("/roadmap")
async def get_roadmap(req: RoadmapRequest):
    try:
        committed = [p for p in req.committed_projects if p.get("committed")]
        return generate_weekly_plan(committed, req.skill_gaps, req.user_level)
    except Exception as e:
        logger.exception("Roadmap generation failed")
        raise HTTPException(status_code=500, detail=str(e))
