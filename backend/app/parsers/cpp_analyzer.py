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

            # Step 1: Formatting checks
            print("Step 1: Running formatting checks...")
            print("  - Proper indentation (nesting levels)")
            print("  - Line length (<200 chars)")
            print("  - Single-line if statements (missing braces)")
            print("  - File header comment")
            print("  - No comments check - CRITICAL (excluding header)")
            violations = self._run_basic_checks(file_content, style_guide)
            print(f"[OK] Found {len(violations)} formatting violations")

            # Step 2: Algorithmic semantic checks
            print("\nStep 2: Running algorithmic semantic checks...")
            print("  - Memory leaks (new/delete matching)")
            print("  - Naming conventions (camelCase/PascalCase)")

            # Check if style guide mentions magic numbers
            check_magic_numbers = False
            if style_guide:
                style_guide_lower = style_guide.lower()
                if 'magic number' in style_guide_lower or 'const' in style_guide_lower or 'named constant' in style_guide_lower:
                    check_magic_numbers = True
                    print("  - Magic numbers (hardcoded literals)")

            print("  - NULL vs nullptr")
            semantic_violations = self._run_semantic_checks(file_content, check_magic_numbers)
            print(f"[OK] Found {len(semantic_violations)} semantic violations")
            violations.extend(semantic_violations)

            # Step 3: LLM comment quality check (simple task)
            if use_rag:
                print("\nStep 3: LLM comment quality analysis...")
                print("  [WAIT] Checking if comments are descriptive...")
                llm_result = await self.ollama_service.check_comment_quality(
                    code=file_content
                )

                if llm_result.get("status") == "success" and llm_result.get("violations"):
                    llm_violations = self._convert_llm_violations(llm_result["violations"])
                    print(f"[OK] Found {len(llm_violations)} comment quality issues")
                    violations.extend(llm_violations)
                else:
                    print("[OK] Comments are adequately descriptive")
            else:
                print("\nStep 3: LLM disabled, skipping comment quality check")

            # Remove duplicate violations (same line and type)
            print(f"\nStep 4: Deduplicating violations...")
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

        try:
            # 1. Check for proper indentation (nesting levels)
            violations.extend(self._check_proper_indentation(lines))
        except Exception as e:
            print(f"[ERROR] in _check_proper_indentation: {e}")

        try:
            # 2. Check for extremely long lines (>200 chars)
            violations.extend(self._check_line_length(lines, 200))
        except Exception as e:
            print(f"[ERROR] in _check_line_length: {e}")

        try:
            # 3. Check for single-line if statements without braces
            violations.extend(self._check_single_line_if_statements(lines))
        except Exception as e:
            print(f"[ERROR] in _check_single_line_if_statements: {e}")

        try:
            # 4. Check for file header comment
            violations.extend(self._check_file_header_comment(lines))
        except Exception as e:
            print(f"[ERROR] in _check_file_header_comment: {e}")

        try:
            # 5. CRITICAL: Check if file has NO comments (excluding header)
            violations.extend(self._check_no_comments(lines))
        except Exception as e:
            print(f"[ERROR] in _check_no_comments: {e}")

        return violations

    def _check_proper_indentation(self, lines: List[str]) -> List[Violation]:
        """Check for proper indentation based on brace nesting levels"""
        violations = []
        uses_tabs = None
        uses_spaces = None
        indent_size = None

        # First pass: determine if file uses tabs or spaces and indentation size
        for line in lines:
            if not line.strip() or len(line) == len(line.lstrip()):
                continue

            # Check what type of indentation is used
            if line[0] == '\t':
                if uses_spaces:
                    # Mixing tabs and spaces
                    violations.append(Violation(
                        type="mixed_indentation",
                        severity=ViolationSeverity.WARNING,
                        line_number=1,
                        description="File mixes tabs and spaces for indentation. Use one consistently.",
                        rule_reference="Consistent Indentation"
                    ))
                    return violations
                uses_tabs = True
                indent_size = 1
            elif line[0] == ' ':
                if uses_tabs:
                    # Mixing tabs and spaces
                    violations.append(Violation(
                        type="mixed_indentation",
                        severity=ViolationSeverity.WARNING,
                        line_number=1,
                        description="File mixes tabs and spaces for indentation. Use one consistently.",
                        rule_reference="Consistent Indentation"
                    ))
                    return violations
                uses_spaces = True
                if indent_size is None:
                    # Use standard: 4 spaces = 1 tab = 1 level
                    indent_size = 4

        if uses_tabs is None and uses_spaces is None:
            # No indented lines found
            return violations

        # Second pass: check that indentation levels match brace nesting
        expected_level = 0
        in_switch = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines and preprocessor directives
            if not stripped or stripped.startswith('#'):
                continue

            # Calculate current indentation level
            if uses_tabs:
                current_indent = len(line) - len(line.lstrip('\t'))
            else:
                leading_spaces = len(line) - len(line.lstrip(' '))
                current_indent = leading_spaces // indent_size if indent_size > 0 else 0

            # Track if we're in a switch statement
            if 'switch' in stripped and '{' in stripped:
                in_switch = True

            # Check for closing braces (decrease expected level before checking)
            if stripped.startswith('}'):
                expected_level = max(0, expected_level - 1)
                if in_switch:
                    in_switch = False

            # Check if indentation matches expected level
            if current_indent != expected_level and not stripped.startswith('}'):
                # Allow flexibility for:
                # - Labels (anything ending with :)
                # - Access specifiers
                # - Case statements and their contents (allow expected_level OR expected_level + 1)
                is_label = stripped.endswith(':') or stripped in ['public:', 'private:', 'protected:']
                is_case_related = stripped.startswith('case ') or stripped.startswith('default')
                is_inside_switch = in_switch and (current_indent == expected_level + 1 or is_case_related)

                if not (is_label or is_inside_switch):
                    violations.append(Violation(
                        type="improper_indentation",
                        severity=ViolationSeverity.WARNING,
                        line_number=i,
                        description=f"Indentation level {current_indent} does not match expected nesting level {expected_level}",
                        rule_reference="Proper Indentation",
                        code_snippet=line.rstrip()
                    ))

            # Check for opening braces (increase expected level after this line)
            if '{' in stripped and not stripped.startswith('}'):
                expected_level += stripped.count('{') - stripped.count('}')

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

            # Match if/for/while at the start
            keyword_match = re.match(r'^\s*(if|else\s+if|for|while)\s*\(', line)
            if keyword_match:
                # Find the matching closing parenthesis by counting parens
                paren_count = 0
                paren_start = keyword_match.end() - 1  # Position of opening '('
                paren_end = -1

                for pos in range(paren_start, len(line)):
                    if line[pos] == '(':
                        paren_count += 1
                    elif line[pos] == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            paren_end = pos
                            break

                if paren_end == -1:
                    # Couldn't find matching paren, skip
                    continue

                # Check what comes after the closing paren
                remainder = line[paren_end + 1:].strip()

                # If there's a brace on same line, it's OK
                if remainder.startswith('{'):
                    continue

                # If there's code on the same line (one-liner), it's a violation
                if remainder and not remainder.startswith('//'):
                    violations.append(Violation(
                        type="missing_braces",
                        severity=ViolationSeverity.WARNING,
                        line_number=i,
                        description="Control structure should use braces even for single statements",
                        rule_reference="Always Use Braces",
                        code_snippet=stripped
                    ))
                    continue

                # If next line doesn't start with '{', it's a violation
                if i < len(lines):
                    next_stripped = lines[i].strip()
                    if next_stripped and not next_stripped.startswith('{') and not next_stripped.startswith('//'):
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
        """CRITICAL: Check if file has NO comments (excluding header comments)"""
        violations = []
        has_non_header_comment = False

        # Skip first 10 lines (header comment area)
        for i, line in enumerate(lines):
            if i >= 10:  # Only check lines after the header
                stripped = line.strip()
                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    has_non_header_comment = True
                    break

        if not has_non_header_comment:
            violations.append(Violation(
                type="no_comments",
                severity=ViolationSeverity.CRITICAL,
                line_number=11,
                description="File contains NO comments beyond the header. Code must be documented for maintainability.",
                rule_reference="Code Documentation"
            ))

        return violations

    # --- Algorithmic semantic checks (always run) ---

    def _run_semantic_checks(self, code: str, check_magic_numbers: bool = False) -> List[Violation]:
        """
        Run algorithmic semantic checks for memory leaks, naming, magic numbers, etc.
        These are deterministic and don't rely on LLM.

        Args:
            code: Source code to analyze
            check_magic_numbers: Whether to check for magic numbers (based on style guide)
        """
        violations: List[Violation] = []
        lines = code.split('\n')

        try:
            violations.extend(self._check_memory_leaks(lines))
        except Exception as e:
            print(f"[ERROR] in _check_memory_leaks: {e}")

        try:
            violations.extend(self._check_naming_conventions(lines))
        except Exception as e:
            print(f"[ERROR] in _check_naming_conventions: {e}")

        # Only check magic numbers if style guide mentions it
        if check_magic_numbers:
            try:
                violations.extend(self._check_magic_numbers(lines))
            except Exception as e:
                print(f"[ERROR] in _check_magic_numbers: {e}")

        try:
            violations.extend(self._check_null_vs_nullptr(lines))
        except Exception as e:
            print(f"[ERROR] in _check_null_vs_nullptr: {e}")

        return violations

    def _check_memory_leaks(self, lines: List[str]) -> List[Violation]:
        """Detect simple memory leaks - new without corresponding delete"""
        violations = []

        # Track all new allocations and deletes in the code
        new_patterns = []
        delete_patterns = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # Find new allocations
            if 'new ' in stripped or 'new[' in stripped:
                # Extract variable name if possible
                match = re.search(r'(\w+)\s*=\s*new\s+', stripped)
                if match:
                    var_name = match.group(1)
                    is_array = 'new[]' in stripped or re.search(r'new\s+\w+\[', stripped)
                    new_patterns.append({
                        'line': i,
                        'var': var_name,
                        'is_array': is_array,
                        'matched': False
                    })

            # Find delete statements
            if 'delete ' in stripped or 'delete[]' in stripped:
                match = re.search(r'delete\s*\[\s*\]?\s*(\w+)', stripped)
                if not match:
                    match = re.search(r'delete\s+(\w+)', stripped)
                if match:
                    var_name = match.group(1)
                    is_array_delete = 'delete[]' in stripped or 'delete [' in stripped
                    delete_patterns.append({
                        'var': var_name,
                        'is_array': is_array_delete
                    })

        # Match news with deletes
        for new in new_patterns:
            for delete in delete_patterns:
                if new['var'] == delete['var']:
                    new['matched'] = True
                    # Check for delete/delete[] mismatch
                    if new['is_array'] and not delete['is_array']:
                        violations.append(Violation(
                            type="wrong_delete_type",
                            severity=ViolationSeverity.CRITICAL,
                            line_number=new['line'],
                            description=f"Array allocated with 'new[]' but deleted with 'delete' (should use 'delete[]')",
                            rule_reference="Memory Management"
                        ))
                    elif not new['is_array'] and delete['is_array']:
                        violations.append(Violation(
                            type="wrong_delete_type",
                            severity=ViolationSeverity.CRITICAL,
                            line_number=new['line'],
                            description=f"Single object allocated with 'new' but deleted with 'delete[]' (should use 'delete')",
                            rule_reference="Memory Management"
                        ))
                    break

        # Report unmatched news as memory leaks
        for new in new_patterns:
            if not new['matched']:
                delete_type = "delete[]" if new['is_array'] else "delete"
                violations.append(Violation(
                    type="memory_leak",
                    severity=ViolationSeverity.CRITICAL,
                    line_number=new['line'],
                    description=f"Memory allocated with 'new' but no corresponding '{delete_type}' found for variable '{new['var']}'",
                    rule_reference="Memory Management"
                ))

        return violations

    def _check_naming_conventions(self, lines: List[str]) -> List[Violation]:
        """Check for camelCase functions and PascalCase classes"""
        violations = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments and preprocessor directives
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('#'):
                continue

            # Check class names (should be PascalCase)
            class_match = re.search(r'\bclass\s+([a-zA-Z_]\w*)', stripped)
            if class_match:
                class_name = class_match.group(1)
                # PascalCase: starts with uppercase, no underscores
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    violations.append(Violation(
                        type="naming_convention",
                        severity=ViolationSeverity.WARNING,
                        line_number=i,
                        description=f"Class '{class_name}' should use PascalCase (e.g., 'MyClass')",
                        rule_reference="Naming Conventions",
                        code_snippet=stripped
                    ))

            # Check function names (should be camelCase)
            # Match: return_type function_name(
            func_match = re.search(r'\b([a-z_]\w*)\s*\([^)]*\)\s*[{;]', stripped)
            if func_match and 'if' not in stripped and 'for' not in stripped and 'while' not in stripped and 'switch' not in stripped:
                func_name = func_match.group(1)
                # Exclude constructors, main, common keywords
                if func_name not in ['main', 'if', 'for', 'while', 'switch', 'return']:
                    # camelCase: starts with lowercase, no underscores (except single letter at start)
                    if '_' in func_name:
                        violations.append(Violation(
                            type="naming_convention",
                            severity=ViolationSeverity.WARNING,
                            line_number=i,
                            description=f"Function '{func_name}' should use camelCase, not snake_case (e.g., 'myFunction')",
                            rule_reference="Naming Conventions",
                            code_snippet=stripped
                        ))

        return violations

    def _check_magic_numbers(self, lines: List[str]) -> List[Violation]:
        """Detect hardcoded numeric literals (magic numbers)"""
        violations = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments, preprocessor, and includes
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('#'):
                continue

            # Find numeric literals that aren't 0, 1, -1
            # Exclude: loop counters (i = 0, i < 10), array indices
            numbers = re.findall(r'\b(\d+\.?\d*)\b', stripped)

            for num in numbers:
                # Allow 0, 1, and single-digit numbers in certain contexts
                if num in ['0', '1']:
                    continue

                # Skip if in loop context
                if re.search(r'(for|while)\s*\([^)]*' + num, stripped):
                    continue

                # Skip if it looks like array size or index
                if re.search(r'\[' + num + r'\]', stripped):
                    continue

                # Flag as magic number
                violations.append(Violation(
                    type="magic_number",
                    severity=ViolationSeverity.WARNING,
                    line_number=i,
                    description=f"Magic number '{num}' should be a named constant (e.g., 'const int MAX_SIZE = {num}')",
                    rule_reference="Magic Numbers",
                    code_snippet=stripped
                ))
                break  # Only report once per line

        return violations

    def _check_null_vs_nullptr(self, lines: List[str]) -> List[Violation]:
        """Check for NULL usage instead of nullptr"""
        violations = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # Check for NULL (but not in #define NULL or comments)
            if re.search(r'\bNULL\b', stripped) and not stripped.startswith('#'):
                violations.append(Violation(
                    type="use_nullptr",
                    severity=ViolationSeverity.WARNING,
                    line_number=i,
                    description="Use 'nullptr' instead of 'NULL' in modern C++",
                    rule_reference="Modern C++ Practices",
                    code_snippet=stripped
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
