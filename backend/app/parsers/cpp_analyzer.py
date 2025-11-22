"""
Main C++ code analyzer combining tree-sitter and LLM analysis
"""
import re
from typing import Callable, Dict, List, Optional, Tuple
from app.models.core import ViolationSeverity, Violation, AnalysisResult  # updated import
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
        Analyze a C++ file for style violations using both rule-based and LLM analysis.

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
            # 1. Run basic rule-based checks (fast, deterministic)
            basic_violations = self._run_basic_checks(file_content, style_guide)

            # 2. Get RAG context if enabled (for future enhancement)
            rag_context = None
            if use_rag:
                rag_context = self._get_rag_context(file_content)

            # 3. Run LLM analysis (semantic, context-aware)
            llm_violations = await self.ollama_service.analyze_code(
                code=file_content,
                style_guide=style_guide,
                context=rag_context
            )

            # 4. Merge violations from both sources (deduplicate similar ones)
            all_violations = self._merge_violations_smart(basic_violations, llm_violations)

            # 5. Calculate statistics
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
            print(f"Analysis error: {e}")
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
        """
        Retrieve relevant context from RAG system
        
        NOTE: This is a placeholder for future RAG integration.
        When implemented, this will:
        1. Extract key code patterns/constructs from the code
        2. Query RAG database for relevant style guide sections
        3. Return focused context to enhance LLM analysis
        """
        # TODO: Implement RAG context retrieval
        # Example future implementation:
        # - Extract function signatures, class definitions
        # - Query ChromaDB for similar examples
        # - Return relevant style guide excerpts
        return None

    def _merge_violations_smart(
        self,
        basic_violations: List[Violation],
        llm_violations: List[Violation]
    ) -> List[Violation]:
        """
        Intelligently merge violations from rule-based and LLM analysis.
        Deduplicates violations that refer to the same issue.
        """
        merged = list(basic_violations)  # Start with all basic violations
        
        # Track which lines already have violations
        existing_line_types = {}
        for v in basic_violations:
            key = (v.line_number, v.type)
            existing_line_types[key] = True
        
        # Add LLM violations if they're not duplicates
        for llm_v in llm_violations:
            key = (llm_v.line_number, llm_v.type)
            
            # Only add if this line+type combo doesn't exist
            # This prevents duplicate detections of the same issue
            if key not in existing_line_types:
                merged.append(llm_v)
                existing_line_types[key] = True
        
        # Sort by line number for easier reading
        merged.sort(key=lambda v: v.line_number)
        
        return merged

    # --- Basic checks (rule-driven) ---

    def _run_basic_checks(self, code: str, style_guide_text: str) -> List[Violation]:
        """
        Parse the uploaded style guide and run simple keyword-mapped checks.
        """
        rules = self._parse_style_guide_rules(style_guide_text)
        violations: List[Violation] = []

        for rule in rules:
            text = self._rule_text(rule)
            sev = self._rule_severity(rule)
            check = self._match_rule_to_check_text(text)

            if not check:
                continue

            for (line, col, msg, vtype) in check(code, text):
                snippet = self._line_snippet(code, line)
                violations.append(
                    Violation(
                        type=vtype,
                        severity=sev,
                        line_number=line,
                        column=col,
                        description=msg,
                        style_guide_reference=self._rule_reference(rule),
                        code_snippet=snippet
                    )
                )
        return violations

    def _parse_style_guide_rules(self, content: str):
        """
        Use StyleGuideProcessor; handle either StyleGuide object or list of rules.
        """
        sg = self.style_processor.parse_style_guide(content)
        # Supports both returns: StyleGuide with .rules or direct list
        rules = getattr(sg, "rules", sg)
        return rules or []

    def _rule_text(self, rule) -> str:
        # Prefer description + name when available
        name = getattr(rule, "rule_name", None) or getattr(rule, "name", None) or ""
        desc = getattr(rule, "description", None) or getattr(rule, "text", None) or ""
        return f"{name} {desc}".strip()

    def _rule_reference(self, rule) -> Optional[str]:
        # Use rule_name or a section/name-like attribute for reference
        return getattr(rule, "rule_name", None) or getattr(rule, "name", None)

    def _rule_severity(self, rule) -> ViolationSeverity:
        sev = getattr(rule, "severity", None)
        if isinstance(sev, ViolationSeverity):
            return sev
        if hasattr(sev, "name"):
            name = sev.name.upper()
        elif isinstance(sev, str):
            name = sev.upper()
        else:
            name = "WARNING"
        return {
            "CRITICAL": ViolationSeverity.CRITICAL,
            "WARNING": ViolationSeverity.WARNING,
            "MINOR": ViolationSeverity.MINOR,
        }.get(name, ViolationSeverity.WARNING)

    # --- Rule matching by text ---

    def _match_rule_to_check_text(self, text: str) -> Optional[Callable[[str, str], List[Tuple[int, Optional[int], str, str]]]]:
        low = text.lower()

        if "tab" in low and ("indent" in low or "tabs" in low or "no tab" in low):
            return self._check_no_tabs

        if "trailing whitespace" in low or "trailing spaces" in low:
            return self._check_trailing_whitespace

        if "line length" in low or "max line length" in low or "maximum line length" in low:
            return self._check_line_length

        if ("brace" in low or "braces" in low) and ("same line" in low or "k&r" in low or "opening brace" in low):
            return self._check_opening_brace_same_line

        if ("file header" in low or "header comment" in low or "file comment" in low):
            return self._check_file_header_comment

        return None

    # --- Checks (return tuples of (line, col, message, violation_type)) ---

    def _check_no_tabs(self, code: str, _rule_text: str):
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if "\t" in line:
                results.append((idx, line.find("\t") + 1, "Tabs found; use spaces for indentation", "indentation"))
        return results

    def _check_trailing_whitespace(self, code: str, _rule_text: str):
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if re.search(r"[ \t]+$", line):
                results.append((idx, None, "Trailing whitespace detected", "whitespace"))
        return results

    def _check_line_length(self, code: str, rule_text: str):
        limit = self._extract_first_int(rule_text) or 100
        results = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if len(line) > limit and "http" not in line:
                results.append((idx, limit + 1, f"Line exceeds maximum length of {limit} characters", "line_length"))
        return results

    def _check_opening_brace_same_line(self, code: str, _rule_text: str):
        results = []
        lines = code.splitlines()
        control_re = re.compile(r"^\s*(if|for|while|switch|class|struct|namespace|template|try|catch|do|else|enum)\b.*[^;]$")
        # fixed truncated regex
        func_decl_re = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_:<>~\s*&]+)\s+([A-Za-z_][A-Za-z0-9_:<>~]*)\s*\([^;]*\)\s*(const\s*)?(\w*\s*)?$")
        for i in range(len(lines) - 1):
            curr = lines[i]
            nxt = lines[i + 1]
            if curr.strip().startswith("//") or curr.strip().startswith("/*") or curr.strip().startswith("#"):
                continue
            is_header = bool(control_re.match(curr)) or bool(func_decl_re.match(curr))
            if is_header and "{" not in curr and re.match(r"^\s*{\s*$", nxt):
                results.append((i + 2, 1, "Opening brace should be on the same line as the declaration/statement", "brace_style"))
        return results

    def _check_file_header_comment(self, code: str, _rule_text: str):
        lines = code.splitlines()
        i = 0
        n = len(lines)
        while i < n and lines[i].strip() == "":
            i += 1
        if i < n and (lines[i].lstrip().startswith("//") or lines[i].lstrip().startswith("/*")):
            return []
        if i < n:
            return [(i + 1, 1, "Missing file header comment at top of file", "documentation")]
        return []

    # --- Helpers ---

    def _extract_first_int(self, text: str) -> Optional[int]:
        m = re.search(r"(\d+)", text)
        if not m:
            return None
        try:
            return int(m.group(1))
        except ValueError:
            return None

    def _line_snippet(self, code: str, line_no: int) -> Optional[str]:
        try:
            return code.splitlines()[line_no - 1]
        except Exception:
            return None

    # --- Keep existing summary helpers ---

    def _count_by_severity(self, violations: List[Violation]) -> dict:
        """Count violations by severity level"""
        counts = {
            "CRITICAL": 0,
            "WARNING": 0,
            "MINOR": 0
        }
        for v in violations:
            # v.severity is ViolationSeverity
            counts[v.severity.value if hasattr(v.severity, "value") else str(v.severity)] += 1
        return counts

    def _count_by_type(self, violations: List[Violation]) -> dict:
        """Count violations by type"""
        counts = {}
        for v in violations:
            counts[v.type] = counts.get(v.type, 0) + 1
        return counts

    # --- Remove conflicting sync analyze(req) path to avoid model mismatches ---
