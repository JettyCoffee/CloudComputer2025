from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class ClassifyRequest(BaseModel):
    concept: str = Field(..., min_length=1)
    max_disciplines: int = Field(5, ge=1, le=12)
    min_relevance: float = Field(0.3, ge=0.0, le=1.0)


class Discipline(BaseModel):
    id: str
    name: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    search_keywords: list[str] = Field(default_factory=list)
    is_primary: bool = False


class SuggestedAddition(BaseModel):
    name: str
    reason: str


class ClassifyResult(BaseModel):
    concept: str
    primary_discipline: str
    disciplines: list[Discipline]
    suggested_additions: list[SuggestedAddition] = Field(default_factory=list)


class DisciplineInput(BaseModel):
    name: str
    search_keywords: list[str] = Field(default_factory=list)


class SearchConfig(BaseModel):
    depth: Literal["shallow", "medium", "deep"] = "medium"
    max_results_per_discipline: int = Field(10, ge=1, le=50)
    enable_validation: bool = True


class SearchStartRequest(BaseModel):
    concept: str = Field(..., min_length=1)
    disciplines: list[DisciplineInput]
    search_config: SearchConfig = Field(default_factory=SearchConfig)


class SearchStartResult(BaseModel):
    task_id: str
    status: Literal["pending", "processing", "completed", "failed", "cancelled"]
    created_at: datetime
    estimated_duration_seconds: int = 30


class SourceInfo(BaseModel):
    url: str
    title: Optional[str] = None
    published_date: Optional[str] = None


class ValidationInfo(BaseModel):
    is_validated: bool = False
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    notes: Optional[str] = None


class Chunk(BaseModel):
    id: str
    content: str
    discipline: str
    source: SourceInfo
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    academic_value: float = Field(0.0, ge=0.0, le=1.0)
    validation: ValidationInfo = Field(default_factory=ValidationInfo)
    extracted_entities: list[str] = Field(default_factory=list)


class SearchSummary(BaseModel):
    total_chunks: int
    disciplines_covered: int
    average_relevance: float = 0.0


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class SearchResultsResponseData(BaseModel):
    task_id: str
    concept: str
    summary: SearchSummary
    chunks: list[Chunk]
    pagination: Pagination


class SearchProgress(BaseModel):
    overall: int = 0
    current_stage: str = "pending"
    stages: dict[str, str] = Field(default_factory=dict)


class StatusPartialResults(BaseModel):
    total_chunks_found: int = 0
    validated_chunks: int = 0
    by_discipline: dict[str, int] = Field(default_factory=dict)


class SearchStatusData(BaseModel):
    task_id: str
    status: Literal["pending", "processing", "completed", "failed", "cancelled"]
    progress: SearchProgress
    partial_results: StatusPartialResults
    started_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class CancelTaskResult(BaseModel):
    task_id: str
    status: Literal["cancelled"] = "cancelled"

class PlanRequest(BaseModel):
    concept: str = Field(..., min_length=1)
    max_disciplines: int = Field(8, ge=1, le=12)
    min_relevance: float = Field(0.3, ge=0.0, le=1.0)
    default_selected: int = Field(3, ge=1, le=12)

class PlanDiscipline(Discipline):
    is_default_selected: bool = False


class PlanResult(BaseModel):
    concept: str
    primary_discipline: str
    defaults: list[str] = Field(default_factory=list)  # discipline ids
    disciplines: list[PlanDiscipline]
    suggested_additions: list[SuggestedAddition] = Field(default_factory=list)