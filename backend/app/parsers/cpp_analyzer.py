"""
Main C++ code analyzer combining tree-sitter and LLM analysis
"""
from typing import List, Optional
from app.models.core import Violation, AnalysisResult, ViolationSeverity
from app.parsers.cpp_parser import TreeSitterParser
from app.services.ollama_service import OllamaService
from app.services.rag_service import RAGService
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
