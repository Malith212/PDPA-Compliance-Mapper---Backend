from typing import List, Optional
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    policy_text: str


class MatchedSentence(BaseModel):
    text: str
    semantic_score: float
    keyword_hit: bool
    matched_keyword: Optional[str] = None


class SectionResult(BaseModel):
    id: str
    section_number: str
    title: str
    description: str
    status: str  # "compliant" | "gap"
    final_score: float
    best_match: Optional[MatchedSentence] = None
    explanation: str


class AnalyzeResponse(BaseModel):
    overall_compliance_percent: float
    total_sections: int
    compliant_count: int
    gap_count: int
    sections: List[SectionResult]