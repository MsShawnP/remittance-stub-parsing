"""FastAPI application entry point.

Start with: uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import demo, report, review, tour

APP_DIR = Path(__file__).parent

app = FastAPI(title="Remittance Stub Parser")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

app.include_router(demo.router)
app.include_router(tour.router)
app.include_router(review.router)
app.include_router(report.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
