from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class Reference(BaseModel):
    title: str
    source_type: str
    url_or_path: str
    snippet: str


class ResearchReport(BaseModel):
    topic: str
    mode: str = "local_fallback"
    executive_summary: str
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)