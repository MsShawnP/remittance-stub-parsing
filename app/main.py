"""FastAPI application entry point.

Start with: uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import demo, report, review, tour

APP_DIR = Path(__file__).parent

CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "font-src 'self'; "
    "img-src 'self'; "
    "connect-src 'self'; "
    "frame-src 'self'"
)


class CSPMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_csp(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"content-security-policy", CSP.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_csp)


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
