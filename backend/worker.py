from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date

from db import SessionLocal
from models.issue import Issue
from models.daily_stats import DailyStats

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=1)
def aggregate_daily_stats():
    db: Session = SessionLocal()
    try:
        today = date.today()

        # Delete existing stats for today
        db.query(DailyStats).filter(DailyStats.date == today).delete()

        # Aggregate new stats
        results = (
            db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
        )

        for status, count in results:
            stat = DailyStats(status=status, count=count, date=today)
            db.add(stat)

        db.commit()
        print(f"[{datetime.now()}] Stats updated.")
    except Exception as e:
        print(f"Error in aggregation job: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()
