"""
Core data models for Code Style Grader
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Severity levels for code violations"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    MINOR = "MINOR"


class Violation(BaseModel):
    """Represents a single code style violation"""
    rule_id: Optional[str] = None
    severity: Severity
    line: int
    column: Optional[int] = None
    description: str
    guide_section: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request to analyze a file"""
    code: str
    filename: Optional[str] = None
    style_guide_text: str


class AnalysisResult(BaseModel):
    """Analysis results for a single file"""
    file_name: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    violations: List[Violation]
    summary: Dict[str, int]  # counts by severity, e.g., {"CRITICAL": 1, "WARNING": 3, "MINOR": 2}
