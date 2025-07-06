from pydantic import BaseModel
from datetime import date


class DailyStatsOut(BaseModel):
    id: int
    status: str
    date: date
    count: int

    class Config:
        orm_mode = True
