"""
Core data models for Code Style Grader
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ViolationSeverity(str, Enum):
    """Severity levels for code violations"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    MINOR = "MINOR"


class Violation(BaseModel):
    """Represents a single code style violation"""
    type: str = Field(..., description="Type of violation")
    severity: ViolationSeverity = Field(..., description="Severity level")
    line_number: int = Field(..., description="Line number where violation occurs")
    column: Optional[int] = Field(None, description="Column position")
    description: str = Field(..., description="Description of the violation")
    style_guide_reference: Optional[str] = Field(None, description="Reference to style guide section")
    code_snippet: Optional[str] = Field(None, description="Code snippet showing the violation")


class AnalysisResult(BaseModel):
    """Analysis results for a single file"""
    file_name: str
    file_path: str
    timestamp: datetime = Field(default_factory=datetime.now)
    violations: List[Violation] = []
    total_violations: int = 0
    violations_by_severity: Dict[str, int] = {}
    violations_by_type: Dict[str, int] = {}
    status: str = "success"
    error_message: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: str
    file_name: str
    file_size: int
    status: str


class AnalysisRequest(BaseModel):
    """Request to analyze a file"""
    file_id: str
    style_guide_id: Optional[str] = None
    use_rag: bool = True


class StyleGuideRule(BaseModel):
    """Represents a single style guide rule"""
    severity: ViolationSeverity
    rule_name: str
    description: str
    examples: Optional[List[str]] = []


class StyleGuide(BaseModel):
    """Parsed style guide structure"""
    name: str
    rules: List[StyleGuideRule] = []
    raw_content: str
