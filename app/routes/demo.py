"""Demo routes: landing page, stub listing, and processing."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.extraction.pipeline import extract
from src.validation.reason_codes import validate_stub

router = APIRouter()

STUBS_DIR = Path(__file__).parent.parent.parent / "stubs"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _scan_stubs() -> list[dict]:
    """Scan the stubs/ directory and return metadata for each PDF."""
    if not STUBS_DIR.exists():
        return []

    stubs = []
    for pdf in sorted(STUBS_DIR.glob("*.pdf")):
        # Derive retailer from filename prefix
        name = pdf.stem
        if name.startswith("walmart"):
            retailer = "Walmart"
        elif name.startswith("costco"):
            retailer = "Costco"
        elif name.startswith("unfi"):
            retailer = "UNFI"
        elif name.startswith("keHE") or name.startswith("kehe"):
            retailer = "KeHE"
        else:
            retailer = "Unknown"

        is_broken = "broken" in name
        stubs.append({
            "filename": pdf.name,
            "name": name.replace("_", " ").title(),
            "retailer": retailer,
            "is_broken": is_broken,
            "size_kb": round(pdf.stat().st_size / 1024, 1),
        })

    return stubs


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Render the landing page."""
    return templates.TemplateResponse(request, "index.html")


@router.get("/stubs")
async def list_stubs():
    """Return JSON list of available stubs in the stubs/ directory."""
    return _scan_stubs()


@router.post("/process/{stub_filename}", response_class=HTMLResponse)
async def process_stub(stub_filename: str, request: Request):
    """Run extraction + validation on a stub, return HTMX partial.

    Extracts data from the PDF using the pipeline (pdfplumber,
    optionally LLM), validates arithmetic and reason codes, and
    returns a rendered stub_card partial for HTMX swap.
    """
    pdf_path = STUBS_DIR / stub_filename
    if not pdf_path.exists() or not pdf_path.suffix == ".pdf":
        raise HTTPException(status_code=404, detail=f"Stub not found: {stub_filename}")

    # Run extraction (skip LLM for demo speed)
    extraction_result = extract(pdf_path, skip_llm=True)
    stub = extraction_result.stub

    # Run validation
    validation = validate_stub(stub, stub_id=stub_filename)

    return templates.TemplateResponse(
        request,
        "partials/stub_card.html",
        context={
            "stub": stub,
            "validation": validation,
            "extraction_method": extraction_result.method,
            "filename": stub_filename,
        },
    )
