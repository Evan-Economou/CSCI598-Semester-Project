"""
Main C++ code analyzer combining tree-sitter and LLM analysis
"""
import re
from typing import Callable, Dict, List, Optional, Tuple
from app.models.core import Severity, Violation, AnalysisRequest, AnalysisResult, StyleGuideRule
from app.parsers.cpp_parser import TreeSitterParser
from app.services.ollama_service import OllamaService
from app.services.rag_service import RAGService
from app.services.style_guide_service import StyleGuideProcessor
from datetime import datetime


class CppAnalyzer:
    """
    Complete C++ code analysis engine

    Combines:
    - Tree-sitter for syntax analysis
    - Ollama/CodeLlama for semantic analysis
    - RAG for style guide context
    """

    def __init__(self):
        self.tree_sitter_parser = TreeSitterParser()
        self.ollama_service = OllamaService()
        self.rag_service = RAGService()
        self.style_processor = StyleGuideProcessor()

    async def analyze_file(
        self,
        file_content: str,
        file_name: str,
        file_path: str,
        style_guide: str,
        use_rag: bool = True
    ) -> AnalysisResult:
        """
        Analyze a C++ file for style violations

        Args:
            file_content: Source code content
            file_name: Name of the file
            file_path: Path to the file
            style_guide: Style guide content
            use_rag: Whether to use RAG for additional context

        Returns:
            AnalysisResult with all detected violations
        """
        try:
            # Step 1: Syntax analysis with tree-sitter
            syntax_issues = self.tree_sitter_parser.find_syntax_issues(file_content)

            # Step 2: Get relevant context from RAG (if enabled)
            rag_context = None
            if use_rag:
                rag_context = self._get_rag_context(file_content)

            # Step 3: Semantic analysis with Ollama
            semantic_violations = await self.ollama_service.analyze_code(
                code=file_content,
                style_guide=style_guide,
                context=rag_context
            )

            # Step 4: Merge and structure violations
            all_violations = self._merge_violations(
                syntax_issues,
                semantic_violations
            )

            # Step 5: Calculate statistics
            violations_by_severity = self._count_by_severity(all_violations)
            violations_by_type = self._count_by_type(all_violations)

            return AnalysisResult(
                file_name=file_name,
                file_path=file_path,
                timestamp=datetime.now(),
                violations=all_violations,
                total_violations=len(all_violations),
                violations_by_severity=violations_by_severity,
                violations_by_type=violations_by_type,
                status="success"
            )

        except Exception as e:
            return AnalysisResult(
                file_name=file_name,
                file_path=file_path,
                timestamp=datetime.now(),
                violations=[],
                total_violations=0,
                violations_by_severity={},
                violations_by_type={},
                status="error",
                error_message=str(e)
            )

    def _get_rag_context(self, code: str) -> Optional[str]:
        """Retrieve relevant context from RAG system"""
        # TODO: Implement RAG context retrieval
        # Use code snippets as queries to find relevant style guide sections
        return None

    def _merge_violations(
        self,
        syntax_issues: List[dict],
        semantic_violations: dict
    ) -> List[Violation]:
        """Merge violations from different sources"""
        violations = []

        # Convert syntax issues to Violation objects
        for issue in syntax_issues:
            violations.append(
                Violation(
                    type=issue.get('type', 'syntax_error'),
                    severity=ViolationSeverity.CRITICAL,
                    line_number=issue.get('line', 0),
                    description=issue.get('message', 'Unknown syntax error')
                )
            )

        # TODO: Parse and add semantic violations from LLM response

        return violations

    def _count_by_severity(self, violations: List[Violation]) -> dict:
        """Count violations by severity level"""
        counts = {
            "CRITICAL": 0,
            "WARNING": 0,
            "MINOR": 0
        }

        for v in violations:
            counts[v.severity.value] += 1

        return counts

    def _count_by_type(self, violations: List[Violation]) -> dict:
        """Count violations by type"""
        counts = {}

        for v in violations:
            counts[v.type] = counts.get(v.type, 0) + 1

        return counts

    def analyze(self, req: AnalysisRequest) -> AnalysisResult:
        rules = self.style_processor.parse_style_guide(req.style_guide_text)
        code = req.code
        violations: List[Violation] = []

        # Map rules to checks by keyword
        for rule in rules:
            check = self._match_rule_to_check(rule)
            if not check:
                # No automatic check available for this rule in MVP
                continue
            found = check(code, rule)
            if not found:
                continue
            for (line, col, msg) in found:
                violations.append(Violation(
                    rule_id=rule.id,
                    severity=rule.severity,
                    line=line,
                    column=col,
                    description=msg,
                    guide_section=rule.section
                ))

        summary = {
            "CRITICAL": sum(1 for v in violations if v.severity == Severity.CRITICAL),
            "WARNING": sum(1 for v in violations if v.severity == Severity.WARNING),
            "MINOR": sum(1 for v in violations if v.severity == Severity.MINOR),
        }
        return AnalysisResult(
            file_name=req.filename,
            violations=violations,
            summary=summary
        )

    # --- Rule matching ---

    def _match_rule_to_check(self, rule: StyleGuideRule) -> Optional[Callable[[str, StyleGuideRule], List[Tuple[int, Optional[int], str]]]]:
        text = rule.text.lower()

        if "tab" in text and ("indent" in text or "tabs" in text or "no tab" in text):
            return self._check_no_tabs

        if "trailing whitespace" in text or "trailing spaces" in text:
            return self._check_trailing_whitespace

        if "line length" in text or "max line length" in text or "maximum line length" in text:
            return self._check_line_length

        if ("brace" in text or "braces" in text) and ("same line" in text or "k&r" in text or "opening brace" in text):
            return self._check_opening_brace_same_line

        if ("file header" in text or "header comment" in text or "file comment" in text):
            return self._check_file_header_comment

        # Add more mappings as needed (naming, comment density, etc.)
        return None

    # --- Checks ---

    def _check_no_tabs(self, code: str, rule: StyleGuideRule):
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if "\t" in line:
                results.append((idx, line.find("\t") + 1, "Tabs found; use spaces for indentation"))
        return results

    def _check_trailing_whitespace(self, code: str, rule: StyleGuideRule):
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if line.rstrip("\r\n") != line.rstrip("\r\n ").rstrip("\t"):
                results.append((idx, None, "Trailing whitespace detected"))
        return results

    def _check_line_length(self, code: str, rule: StyleGuideRule):
        # Try to extract a numeric limit from rule text; default to 100
        limit = self._extract_first_int(rule.text) or 100
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            # Ignore URLs to reduce false positives
            if len(line) > limit and "http" not in line:
                results.append((idx, limit + 1, f"Line exceeds maximum length of {limit} characters"))
        return results

    def _check_opening_brace_same_line(self, code: str, rule: StyleGuideRule):
        # Naive detection for function or control statements with brace on next line
        results = []
        lines = code.splitlines()
        control_re = re.compile(r"^\s*(if|for|while|switch|class|struct|namespace|template|try|catch|do|else|enum)\b.*[^;]$")
        func_decl_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_:<>~\s*&]+)\s+([A-Za
