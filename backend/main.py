import logging
from pathlib import Path
from typing import List, Optional, Set

from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.calendar_engine.generator import CalendarGenerator
from backend.fetchers.service import ContestService
from backend.models.contest import Contest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("contestpulse")

app = FastAPI(
    title="ContestPulse",
    description="Automated Coding Contest Calendar Agent with Native Phone Alarms",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

contest_service = ContestService(cache_ttl_seconds=600)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
FRONTEND_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/health")
async def health_check():
    """
    Ultra-lightweight health check endpoint.
    Used by external cron/ping services (like cron-job.org or UptimeRobot)
    to keep the free cloud server awake 24/7 without cold start delays.
    """
    return {"status": "ok", "app": "ContestPulse"}


@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serves the mobile-friendly web hub from frontend/."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ContestPulse is running! frontend/index.html not found.</h1>")


@app.get("/api/contests", response_model=List[Contest])
async def get_contests(
    platforms: Optional[str] = Query(None, description="Comma-separated platforms: codeforces,leetcode,codechef"),
    divisions: Optional[str] = Query(None, description="Comma-separated divisions/series"),
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data")
):
    """
    Returns upcoming contests as JSON for the interactive web UI and countdown timers.
    """
    if force_refresh:
        await contest_service.get_all_contests(force_refresh=True)

    platform_set = set(platforms.split(",")) if platforms else None
    division_set = set(divisions.split(",")) if divisions else None

    return await contest_service.filter_contests(
        platforms=platform_set,
        divisions=division_set
    )


@app.get("/calendar.ics")
async def get_calendar_feed(
    request: Request,
    platforms: Optional[str] = Query(None, description="Comma-separated platforms: codeforces,leetcode,codechef"),
    divisions: Optional[str] = Query(None, description="Comma-separated divisions/series"),
    alarm: int = Query(15, ge=1, le=1440, description="Alarm trigger offset in minutes before contest start"),
    alarm_name: str = Query("🚨 ContestPulse Alarm", description="Custom alarm name/label displayed on phone lock screen")
):
    """
    Dynamic RFC-5545 iCalendar (.ics) subscription endpoint.
    Users' phone calendars poll this endpoint to receive live updates and set native alarms.
    """
    platform_set = set(platforms.split(",")) if platforms else None
    division_set = set(divisions.split(",")) if divisions else None

    contests = await contest_service.filter_contests(
        platforms=platform_set,
        divisions=division_set
    )

    cal_name = "ContestPulse Contests"
    if platform_set and len(platform_set) == 1:
        cal_name = f"ContestPulse: {list(platform_set)[0].capitalize()}"

    ics_bytes = CalendarGenerator.generate_ics(
        contests=contests,
        calendar_name=cal_name,
        reminder_minutes=alarm,
        alarm_name=alarm_name
    )

    return Response(
        content=ics_bytes,
        media_type="text/calendar",
        headers={
            "Content-Disposition": 'inline; filename="contests.ics"',
            "Cache-Control": "max-age=3600, must-revalidate",
        }
    )
