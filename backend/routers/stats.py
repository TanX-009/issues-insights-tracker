from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from db import get_db
from dependencies import require_role
from models.daily_stats import DailyStats
from schemas.stats import DailyStatsOut  # You'll need to define this schema

router = APIRouter()


@router.get("/daily", response_model=List[DailyStatsOut])
def get_daily_stats(
    status: Optional[str] = Query(None),
    stat_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    _=Depends(require_role(["ADMIN"])),
):
    """
    Fetch daily stats. Supports optional filtering by status and/or date.
    Logs query parameters and result count.
    """
    logger.info(
        {
            "event": "get_daily_stats_request",
            "filters": {"status": status, "date": stat_date},
        }
    )

    query = db.query(DailyStats)

    if status:
        query = query.filter(DailyStats.status == status)
    if stat_date:
        query = query.filter(DailyStats.date == stat_date)

    stats = query.order_by(DailyStats.date.desc()).all()

    logger.info(
        {
            "event": "get_daily_stats_success",
            "count": len(stats),
            "filters": {"status": status, "date": stat_date},
        }
    )

    return stats
