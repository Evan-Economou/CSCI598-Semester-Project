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


# Alias for compatibility
ViolationSeverity = Severity


class StyleGuideRule(BaseModel):
    """Individual style guide rule"""
    id: str
    text: str
    severity: Severity
    section: str


class StyleGuide(BaseModel):
    """Parsed style guide document"""
    name: str
    rules: List[StyleGuideRule]
    raw_content: str


class Violation(BaseModel):
    """Represents a single code style violation"""
    type: str = "general"
    severity: Severity
    line_number: int
    column: Optional[int] = None
    description: str
    style_guide_reference: Optional[str] = None
    code_snippet: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request to analyze a file"""
    file_id: str
    style_guide_id: Optional[str] = None
    use_rag: bool = False


class AnalysisResult(BaseModel):
    """Analysis results for a single file"""
    file_name: str
    file_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    violations: List[Violation]
    total_violations: int
    violations_by_severity: Dict[str, int]
    violations_by_type: Dict[str, int]
    status: str = "success"
    error_message: Optional[str] = None
