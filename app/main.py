from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .extraction import extract_sentences
from .compliance_engine import analyze_policy
from .models import AnalyzeRequest, AnalyzeResponse

app = FastAPI(
    title="PDPA Compliance Mapper API",
    description="Maps a privacy policy against Sri Lanka's PDPA (No. 9 of 2022) obligations.",
    version="1.0.0",
)

# Allow the Vite dev server (default port 5173) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "PDPA Compliance Mapper API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    sentences = extract_sentences(request.policy_text)
    section_results = analyze_policy(sentences)

    compliant_count = sum(1 for r in section_results if r["status"] == "compliant")
    gap_count = sum(1 for r in section_results if r["status"] == "gap")
    total = len(section_results)

    overall_percent = round((compliant_count / total) * 100, 1) if total else 0.0

    return AnalyzeResponse(
        overall_compliance_percent=overall_percent,
        total_sections=total,
        compliant_count=compliant_count,
        gap_count=gap_count,
        sections=section_results,
    )