from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import BASE_PATH
from monitoring.metrics import start_metrics_server
from routers import auth, issues, stats, user
from db import Base, engine

# Create all tables (in production you'd use Alembic instead)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Issues & Insights Tracker", version="1.0.0", root_path=BASE_PATH)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (if stored locally)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])

# Start Prometheus server
start_metrics_server()


@asynccontextmanager
async def lifespan():
    # Code to run on startup
    start_metrics_server()
    print("Application startup complete.")
    yield
    # Code to run on shutdown (after the 'yield')
    print("Application shutdown complete.")


# Health check (optional)
@app.get("/")
def health_check():
    return {"status": "ok"}
