"""Client-mode tests for remittance-stub-parsing.

Adversarial fixtures per checklist §6 for a PDF + config intake: clean run
(parity with the demo golden), an unrecognized PDF (blocked), no PDFs (blocked),
a missing reference ledger (proceeds with a warning), a new-format config drop-in,
and the --final watermark.

Skipped if lailara_engagement isn't installed.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

pytest.importorskip("lailara_engagement")

import client_mode  # noqa: E402
from src.stub_generator import generate_all_stubs  # noqa: E402

REPO = Path(__file__).resolve().parent

_DEMO_CONFIG = f"""
client: {{name: "Cinderhaven Provisions (demo)"}}
engagement: {{id: CINDERHAVEN-DEMO}}
as_of_date: "2026-07-30"
demo: true
basis: {{dispute_window_days: 90, window_label: "90-day dispute window"}}
reference_ledger: "{(REPO / 'data' / 'cinderhaven_reference.json').as_posix()}"
"""

_MERIDIAN_CONFIG = """
client: {name: Meridian Farms}
engagement: {id: MER-2026-08}
as_of_date: "2026-07-30"
demo: true
basis: {dispute_window_days: 90}
reference_ledger: "does-not-exist.json"
"""


def _cfg(tmp_path, text):
    p = tmp_path / "engagement.yml"
    p.write_text(text, encoding="utf-8")
    return str(p)


def _simple_pdf(path: Path, text: str):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(str(path))


@pytest.fixture(scope="module")
def demo_stub_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("stubs")
    generate_all_stubs(d)
    return d


def test_clean_run_parity_with_golden(demo_stub_dir, tmp_path):
    cfg = _cfg(tmp_path, _DEMO_CONFIG)
    out = str(tmp_path / "client-output")
    result = client_mode.run(cfg, str(demo_stub_dir), out)
    assert result["status"] == "ok"
    assert result["stub_count"] == 15
    assert Decimal(result["recoverable"]) == Decimal("207338.44")   # == demo golden

    s = json.load(open(result["summary_json"], encoding="utf-8"))
    assert s["within_window"] == "26173.80"
    assert s["past_window"] == "181164.64"
    assert s["format_count"] == 4

    html = open(result["report"], encoding="utf-8").read()
    assert "Cinderhaven Provisions (demo)" in html
    assert "#f5f3ee" in html and "SHA-256" in html and "DRAFT" in html
    assert "90 days" in html                          # dispute window printed
    assert "2026-07-30" in html                       # as_of printed


def test_unrecognized_pdf_blocks(tmp_path):
    d = tmp_path / "stubs"
    d.mkdir()
    _simple_pdf(d / "not_a_remittance.pdf", "Just some random document, no retailer header here.")
    cfg = _cfg(tmp_path, _DEMO_CONFIG)
    result = client_mode.run(cfg, str(d), str(tmp_path / "out"))
    assert result["status"] == "blocked"
    rr = open(result["readiness_report"], encoding="utf-8").read()
    assert "not_a_remittance.pdf" in rr
    assert "format plugin" in rr.lower()


def test_no_pdfs_blocks(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    cfg = _cfg(tmp_path, _DEMO_CONFIG)
    result = client_mode.run(cfg, str(d), str(tmp_path / "out"))
    assert result["status"] == "blocked"
    assert "no remittance pdfs" in open(result["readiness_report"], encoding="utf-8").read().lower()


def test_missing_ledger_proceeds_with_warning(demo_stub_dir, tmp_path):
    # Missing reference ledger -> warning (not a block); recoverable still computed
    # (all deductions unmatched), and provenance stamps "proceeded with warnings".
    cfg = _cfg(tmp_path, _MERIDIAN_CONFIG)
    result = client_mode.run(cfg, str(demo_stub_dir), str(tmp_path / "out"))
    assert result["status"] == "ok"
    html = open(result["report"], encoding="utf-8").read()
    assert "proceeded with warnings" in html


def test_final_drops_watermark(demo_stub_dir, tmp_path):
    cfg = _cfg(tmp_path, _DEMO_CONFIG)
    result = client_mode.run(cfg, str(demo_stub_dir), str(tmp_path / "out"), final=True)
    assert "ll-draft" not in open(result["report"], encoding="utf-8").read()
