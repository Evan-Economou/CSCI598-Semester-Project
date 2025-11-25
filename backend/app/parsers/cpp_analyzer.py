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
        Analyze a C++ file for style violations using rule-based checks and optionally LLM+RAG.

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
            print(f"\n{'='*60}")
            print(f"Starting analysis for: {file_name}")
            print(f"File size: {len(file_content)} characters")
            print(f"{'='*60}\n")

            # Built-in algorithmic checks (always run)
            print("Step 1: Running built-in algorithmic checks...")
            print("  - Consistent indentation (tabs/spaces)")
            print("  - Line length (<200 chars)")
            print("  - Consistent brace placement")
            print("  - Single-line if statements")
            print("  - File header comment")
            print("  - Comment frequency")
            print("  - No comments check (CRITICAL)")
            violations = self._run_basic_checks(file_content, style_guide)
            print(f"[OK] Found {len(violations)} formatting/documentation violations")

            # If RAG is enabled, use LLM for semantic analysis
            if use_rag:
                print("\nStep 2: LLM Semantic Analysis (using uploaded semantic style guide)...")
                print("  Searching for semantic issues:")
                print("  - Memory leaks")
                print("  - Naming conventions")
                print("  - Magic numbers")
                print("  - Code structure issues")
                print("  - Modern C++ best practices")

                # Get relevant context from RAG
                rag_context = self._get_rag_context(file_content, style_guide)
                if rag_context:
                    print(f"[OK] Retrieved RAG context ({len(rag_context)} characters)")
                else:
                    print("[WARN] No semantic style guide uploaded - upload semantic_style_guide.txt in RAG Management")

                print("\n  -> Calling Ollama/CodeLlama for semantic analysis...")
                print("  [WAIT] This may take 30-60 seconds depending on code complexity...")
                # Analyze with Ollama using RAG context
                llm_result = await self.ollama_service.analyze_code(
                    code=file_content,
                    style_guide=style_guide,
                    context=rag_context
                )

                # Merge LLM violations with rule-based violations
                if llm_result.get("status") == "success" and llm_result.get("violations"):
                    print(f"[OK] LLM semantic analysis complete")
                    llm_violations = self._convert_llm_violations(llm_result["violations"])
                    print(f"[OK] Found {len(llm_violations)} semantic violations from LLM")
                    violations.extend(llm_violations)
                elif llm_result.get("status") == "error":
                    print(f"[ERROR] LLM analysis failed: {llm_result.get('error', 'Unknown error')}")
                else:
                    print("[WARN] LLM returned no semantic violations")
            else:
                print("\nStep 2: RAG disabled, skipping semantic LLM analysis")

            # Remove duplicate violations (same line and type)
            print(f"\nStep 3: Deduplicating violations...")
            violations = self._deduplicate_violations(violations)
            print(f"[OK] Final violation count: {len(violations)}")
            print(f"{'='*60}\n")

            # Stats
            violations_by_severity = self._count_by_severity(violations)
            violations_by_type = self._count_by_type(violations)

            return AnalysisResult(
                file_name=file_name,
                file_path=file_path,
                timestamp=datetime.now(),
                violations=violations,
                total_violations=len(violations),
                violations_by_severity=violations_by_severity,
                violations_by_type=violations_by_type,
                status="success"
            )
        except Exception as e:
            print(f"Error during analysis: {e}")
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

    def _get_rag_context(self, code: str, style_guide: str) -> Optional[str]:
        """Retrieve relevant context from RAG system"""
        try:
            # Create a query combining code snippet and style guide info
            query = f"C++ code analysis style guide rules:\n{code[:500]}"

            # Search for relevant chunks
            relevant_chunks = self.rag_service.search_relevant_context(query, top_k=3)

            if relevant_chunks:
                context = "\n\n---\n\n".join(relevant_chunks)
                return f"Relevant style guide excerpts:\n\n{context}"

            return None

        except Exception as e:
            print(f"Error retrieving RAG context: {e}")
            return None

    def _convert_llm_violations(self, llm_violations: List[Dict]) -> List[Violation]:
        """Convert LLM violation dicts to Violation objects"""
        violations = []
        for v in llm_violations:
            try:
                violations.append(
                    Violation(
                        type=v.get("type", "style_violation"),
                        severity=ViolationSeverity[v.get("severity", "WARNING")],
                        line_number=v.get("line_number", 1),
                        description=v.get("description", "Style violation"),
                        rule_reference=v.get("rule_reference", ""),
                        code_snippet=""
                    )
                )
            except Exception as e:
                print(f"Error converting violation: {e}")
                continue
        return violations

    def _deduplicate_violations(self, violations: List[Violation]) -> List[Violation]:
        """Remove duplicate violations based on line number and type"""
        seen = set()
        unique = []
        for v in violations:
            key = (v.line_number, v.type)
            if key not in seen:
                seen.add(key)
                unique.append(v)
        return unique

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

    # --- Built-in algorithmic checks (always run) ---

    def _run_basic_checks(self, code: str, style_guide_text: str) -> List[Violation]:
        """
        Run built-in algorithmic formatting checks.
        These checks always run regardless of uploaded style guide.
        """
        violations: List[Violation] = []
        lines = code.split('\n')

        # 1. Check for consistent indentation
        violations.extend(self._check_consistent_indentation(lines))

        # 2. Check for extremely long lines (>200 chars)
        violations.extend(self._check_line_length(lines, 200))

        # 3. Check for consistent brace placement
        violations.extend(self._check_consistent_braces(lines))

        # 4. Check for single-line if statements without braces
        violations.extend(self._check_single_line_if_statements(lines))

        # 5. Check for file header comment
        violations.extend(self._check_file_header_comment(lines))

        # 6. Check comment frequency (every 20 lines)
        violations.extend(self._check_comment_frequency(lines))

        # 7. CRITICAL: Check if file has NO comments at all
        violations.extend(self._check_no_comments(lines))

        return violations

    def _check_consistent_indentation(self, lines: List[str]) -> List[Violation]:
        """Check for consistent indentation (tabs OR spaces, but consistent)"""
        violations = []
        uses_tabs = None
        uses_spaces = None

        for i, line in enumerate(lines, 1):
            if not line.strip():  # Skip empty lines
                continue

            # Get leading whitespace
            leading = len(line) - len(line.lstrip())
            if leading == 0:
                continue

            # Check what type of indentation is used
            if line[0] == '\t':
                uses_tabs = True
            elif line[0] == ' ':
                uses_spaces = True

            # If mixing tabs and spaces, that's a violation
            if uses_tabs and uses_spaces:
                violations.append(Violation(
                    type="inconsistent_indentation",
                    severity=ViolationSeverity.WARNING,
                    line_number=i,
                    description="File mixes tabs and spaces for indentation. Use one consistently.",
                    rule_reference="Consistent Indentation",
                    code_snippet=line.rstrip()
                ))
                break  # Only report once

        return violations

    def _check_line_length(self, lines: List[str], max_length: int) -> List[Violation]:
        """Check for extremely long lines (>200 chars)"""
        violations = []

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                violations.append(Violation(
                    type="line_too_long",
                    severity=ViolationSeverity.MINOR,
                    line_number=i,
                    description=f"Line is {len(line)} characters long (exceeds {max_length} character limit)",
                    rule_reference="Maximum Line Length",
                    code_snippet=line[:100] + "..." if len(line) > 100 else line
                ))

        return violations

    def _check_consistent_braces(self, lines: List[str]) -> List[Violation]:
        """Check that opening braces are placed consistently (same line OR next line, not mixed)"""
        violations = []
        same_line_count = 0
        next_line_count = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for function/control structure followed by brace on same line
            if re.search(r'(if|else|for|while|switch|class|struct)\s*\([^)]*\)\s*\{', stripped) or \
               re.search(r'(class|struct)\s+\w+\s*\{', stripped):
                same_line_count += 1

            # Check for standalone opening brace (next line style)
            if stripped == '{' and i > 1:
                prev_line = lines[i-2].strip()
                if re.search(r'(if|else|for|while|switch|class|struct)', prev_line):
                    next_line_count += 1

        # If mixing both styles significantly, report it
        if same_line_count > 0 and next_line_count > 0:
            violations.append(Violation(
                type="inconsistent_brace_placement",
                severity=ViolationSeverity.MINOR,
                line_number=1,
                description=f"File uses both same-line ({same_line_count}) and next-line ({next_line_count}) brace placement. Use one style consistently.",
                rule_reference="Consistent Brace Placement"
            ))

        return violations

    def _check_single_line_if_statements(self, lines: List[str]) -> List[Violation]:
        """Check for single-line if statements without braces"""
        violations = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Match if/for/while without braces on same line or next line
            if re.match(r'^\s*(if|for|while)\s*\([^)]+\)\s*[^{;]', line):
                # Check if next line has a brace
                if i < len(lines):
                    next_stripped = lines[i].strip()
                    if next_stripped and not next_stripped.startswith('{'):
                        violations.append(Violation(
                            type="missing_braces",
                            severity=ViolationSeverity.WARNING,
                            line_number=i,
                            description="Control structure should use braces even for single statements",
                            rule_reference="Always Use Braces",
                            code_snippet=stripped
                        ))

        return violations

    def _check_file_header_comment(self, lines: List[str]) -> List[Violation]:
        """Check for file header comment in first 10 lines"""
        violations = []
        has_header_comment = False

        for i in range(min(10, len(lines))):
            line = lines[i].strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                has_header_comment = True
                break

        if not has_header_comment:
            violations.append(Violation(
                type="missing_file_header",
                severity=ViolationSeverity.MINOR,
                line_number=1,
                description="File should have a header comment describing its purpose",
                rule_reference="File Header Comment"
            ))

        return violations

    def _check_comment_frequency(self, lines: List[str]) -> List[Violation]:
        """Check that there's at least one comment every 20 lines of code"""
        violations = []
        code_lines = 0
        last_comment_line = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Check if this is a comment
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                last_comment_line = i
                code_lines = 0  # Reset counter
            else:
                code_lines += 1

                # If we have 20 lines of code without a comment, flag it
                if code_lines >= 20:
                    violations.append(Violation(
                        type="insufficient_comments",
                        severity=ViolationSeverity.MINOR,
                        line_number=i,
                        description=f"No comments found in the last 20 lines of code (since line {last_comment_line})",
                        rule_reference="Comment Frequency"
                    ))
                    code_lines = 0  # Reset to avoid repeated violations

        return violations

    def _check_no_comments(self, lines: List[str]) -> List[Violation]:
        """CRITICAL: Check if file has NO comments at all"""
        violations = []
        has_any_comment = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                has_any_comment = True
                break

        if not has_any_comment:
            violations.append(Violation(
                type="no_comments",
                severity=ViolationSeverity.CRITICAL,
                line_number=1,
                description="File contains NO comments. Code must be documented for maintainability.",
                rule_reference="Code Documentation"
            ))

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
