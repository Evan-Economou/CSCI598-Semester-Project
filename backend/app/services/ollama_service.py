"""
Ollama LLM integration service for C++ code analysis
"""
import os
import json
import re
from typing import Optional, Dict, Any, List
import ollama
from app.models.core import Violation, ViolationSeverity


class OllamaService:
    """Service for interacting with Ollama and CodeLlama"""

    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "codellama:7b")
        self.client = ollama.Client(host=self.host)
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
        # Lower temperature for more consistent, focused analysis

    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            self.client.list()
            return True
        except Exception as e:
            print(f"Ollama connection check failed: {e}")
            return False

    async def check_model(self) -> bool:
        """Check if CodeLlama model is available"""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            return any(self.model in name for name in model_names)
        except Exception as e:
            print(f"Model availability check failed: {e}")
            return False

    async def analyze_code(
        self,
        code: str,
        style_guide: str,
        context: Optional[str] = None
    ) -> List[Violation]:
        """
        Analyze code for style violations using CodeLlama

        Args:
            code: C++ source code to analyze
            style_guide: Style guide rules
            context: Additional context from RAG system (for future use)

        Returns:
            List of Violation objects
        """
        try:
            prompt = self._build_analysis_prompt(code, style_guide, context)
            
            # Call Ollama with the analysis prompt
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": self.temperature,
                    "num_predict": 2048,  # Limit response length
                }
            )
            
            response_text = response.get('response', '')
            
            # Parse violations from response
            violations = self._parse_violations(response_text, code)
            
            return violations
            
        except Exception as e:
            print(f"Code analysis failed: {e}")
            # Return empty list on error rather than failing
            return []

    def _build_analysis_prompt(
        self,
        code: str,
        style_guide: str,
        context: Optional[str] = None
    ) -> str:
        """Construct the prompt for code analysis"""

        # Extract key rules from style guide for focused analysis
        style_summary = self._extract_style_summary(style_guide)

        base_prompt = f"""You are a C++ code style analyzer. Analyze the provided code against the style guide rules.

STYLE GUIDE RULES:
{style_summary}
"""
        
        # RAG context integration point (for future)
        if context:
            base_prompt += f"""
ADDITIONAL CONTEXT:
{context}
"""

        base_prompt += f"""
CODE TO ANALYZE:
```cpp
{code}
```

INSTRUCTIONS:
1. Identify ALL style violations in the code
2. For each violation, provide EXACTLY ONE SENTENCE describing what's wrong
3. Reference the specific line number where the violation occurs
4. Classify severity as CRITICAL, WARNING, or MINOR
5. Keep descriptions concise and actionable

OUTPUT FORMAT (one violation per line):
LINE <number> | <SEVERITY> | <type> | <one-sentence description>

Example:
LINE 5 | CRITICAL | indentation | Tabs used instead of spaces for indentation
LINE 12 | WARNING | naming | Function name uses snake_case instead of camelCase
LINE 20 | MINOR | whitespace | Missing blank line between logical sections

Begin analysis:"""

        return base_prompt

    def _extract_style_summary(self, style_guide: str) -> str:
        """Extract key rules from style guide for efficient prompting"""
        lines = style_guide.split('\n')
        summary_lines = []
        current_severity = None
        
        for line in lines:
            # Detect severity headers
            if line.strip() in ['CRITICAL', 'WARNING', 'MINOR']:
                current_severity = line.strip()
                summary_lines.append(f"\n{current_severity}:")
                continue
            
            # Include rule lines (starting with -)
            if line.strip().startswith('-') and current_severity:
                summary_lines.append(line.strip())
        
        # If no structured summary found, use first 1000 chars
        if not summary_lines:
            return style_guide[:1000]
        
        return '\n'.join(summary_lines)

    def _parse_violations(self, response_text: str, original_code: str) -> List[Violation]:
        """
        Parse violations from LLM response
        
        Expected format: LINE <number> | <SEVERITY> | <type> | <description>
        """
        violations = []
        code_lines = original_code.split('\n')
        
        # Pattern to match violation lines
        pattern = r'LINE\s+(\d+)\s*\|\s*(CRITICAL|WARNING|MINOR)\s*\|\s*([^|]+)\s*\|\s*(.+)'
        
        for line in response_text.split('\n'):
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                line_num = int(match.group(1))
                severity_str = match.group(2).upper()
                violation_type = match.group(3).strip()
                description = match.group(4).strip()
                
                # Map severity string to enum
                severity_map = {
                    'CRITICAL': ViolationSeverity.CRITICAL,
                    'WARNING': ViolationSeverity.WARNING,
                    'MINOR': ViolationSeverity.MINOR
                }
                severity = severity_map.get(severity_str, ViolationSeverity.WARNING)
                
                # Get code snippet
                code_snippet = None
                if 0 < line_num <= len(code_lines):
                    code_snippet = code_lines[line_num - 1]
                
                violations.append(
                    Violation(
                        type=violation_type,
                        severity=severity,
                        line_number=line_num,
                        description=description,
                        code_snippet=code_snippet,
                        style_guide_reference=f"{severity_str} rules"
                    )
                )
        
        return violations
