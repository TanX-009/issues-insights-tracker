from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from datetime import datetime, date
import time
from sqlalchemy.exc import OperationalError

from db import SessionLocal
from models.issue import Issue
from models.daily_stats import DailyStats

scheduler = BlockingScheduler()


def get_db_with_retries(retries=5, delay=3) -> Session:
    for i in range(retries):
        try:
            db = SessionLocal()
            # Test connection
            db.execute(text("SELECT 1"))
            return db
        except OperationalError as e:
            print(f"[Retry {i+1}/{retries}] Database not ready: {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to the database after multiple retries.")


@scheduler.scheduled_job("interval", minutes=30)
def aggregate_daily_stats():
    db: Session = get_db_with_retries()
    try:
        today = date.today()

        db.query(DailyStats).filter(DailyStats.date == today).delete()

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
