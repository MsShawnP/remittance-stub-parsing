"""FastAPI application entry point.

Start with: uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.routes import demo, report, review, tour

APP_DIR = Path(__file__).parent

CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self'; "
    "img-src 'self'; "
    "connect-src 'self'; "
    "frame-src 'self'"
)


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = CSP
        return response


app = FastAPI(title="Remittance Stub Parser")
app.add_middleware(CSPMiddleware)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

app.include_router(demo.router)
app.include_router(tour.router)
app.include_router(review.router)
app.include_router(report.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
