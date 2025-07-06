from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from .base import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    count = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("status", "date", name="uix_status_date"),)
