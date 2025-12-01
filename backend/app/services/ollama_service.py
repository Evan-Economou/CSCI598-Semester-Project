"""
Ollama LLM integration service
"""
import os
import json
from typing import Optional, Dict, Any, List
import ollama


class OllamaService:
    """Service for interacting with Ollama and CodeLlama"""

    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "codellama:7b")
        self.client = ollama.Client(host=self.host)

    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            self.client.list()
            return True
        except Exception as e:
            print(f"Ollama connection error: {e}")
            return False

    async def check_model(self) -> bool:
        """Check if CodeLlama model is available"""
        try:
            models = self.client.list()
            return any(self.model in m['name'] for m in models['models'])
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False

    async def analyze_code(
        self,
        code: str,
        style_guide: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code for style violations using CodeLlama

        Args:
            code: C++ source code to analyze
            style_guide: Style guide rules
            context: Additional context from RAG system

        Returns:
            Dictionary containing detected violations
        """
        try:
            import time
            start_time = time.time()

            print(f"  -> Building analysis prompt...")
            print(f"    Code length: {len(code)} chars")
            print(f"    Style guide length: {len(style_guide)} chars")
            if context:
                print(f"    RAG context length: {len(context)} chars")

            prompt = self._build_analysis_prompt(code, style_guide, context)
            print(f"    Total prompt length: {len(prompt)} chars")

            # Call Ollama with the prompt
            print(f"  -> Sending request to Ollama ({self.model})...")
            print(f"    Host: {self.host}")

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,  # Low temperature for consistent analysis
                    'num_predict': 2000  # Allow enough tokens for detailed analysis
                }
            )

            elapsed = time.time() - start_time
            print(f"  -> Received response from Ollama ({elapsed:.1f}s)")

            # Extract the response content
            response_text = response['message']['content']
            print(f"    Response length: {len(response_text)} chars")

            # Parse the JSON response
            print(f"  -> Parsing LLM response...")
            violations = self._parse_llm_response(response_text)
            print(f"    Parsed {len(violations)} violations")

            return {
                "violations": violations,
                "status": "success",
                "raw_response": response_text
            }

        except Exception as e:
            print(f"[ERROR] Error during code analysis: {e}")
            import traceback
            traceback.print_exc()
            return {
                "violations": [],
                "status": "error",
                "error": str(e)
            }

    def _parse_llm_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the LLM response and extract violations"""
        try:
            # Try to find JSON in the response
            # LLMs sometimes wrap JSON in markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()

            # Parse JSON
            data = json.loads(json_text)

            # Handle different JSON structures
            if isinstance(data, list):
                violations = data
            elif isinstance(data, dict):
                violations = data.get('violations', [data])
            else:
                violations = []

            # Normalize violation structure
            normalized = []
            for v in violations:
                normalized.append({
                    "type": v.get("type", "style_violation"),
                    "severity": v.get("severity", "WARNING").upper(),
                    "line_number": int(v.get("line_number", v.get("line", 1))),
                    "description": v.get("description", "Style violation detected"),
                    "rule_reference": v.get("rule_reference", v.get("reference", ""))
                })

            return normalized

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response text: {response_text[:500]}")  # Log first 500 chars
            return []

    def _build_analysis_prompt(
        self,
        code: str,
        style_guide: str,
        context: Optional[str] = None
    ) -> str:
        """Construct the prompt for code analysis"""

        # Add line numbers to code for better accuracy
        numbered_lines = []
        for i, line in enumerate(code.split('\n'), 1):
            numbered_lines.append(f"{i:4d} | {line}")
        numbered_code = '\n'.join(numbered_lines)

        base_prompt = f"""You are a C++ semantic code analyzer. Analyze ONLY the user's code shown below.

TASK: Find semantic and logic issues in the CODE TO ANALYZE section.

RULES TO CHECK (reference only - NOT code to analyze):
{style_guide}

"""
        if context:
            base_prompt += f"""ADDITIONAL CONTEXT:
{context}

"""

        base_prompt += f"""
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
CODE TO ANALYZE (with line numbers):
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
{numbered_code}
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
END OF CODE - Analyze the code above ONLY
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

WHAT TO LOOK FOR:
- Memory leaks: new/malloc without delete/free
- Wrong delete: delete[] vs delete mismatch
- Naming: camelCase for functions, PascalCase for classes
- Magic numbers: hardcoded values like 18, 500, 1.15
- NULL vs nullptr
- Missing switch default
- Variable shadowing
- Deep nesting (>3 levels)
- Long functions (>50 lines)
- Uninitialized variables

DO NOT REPORT:
- Formatting (tabs/spaces/braces/line length)
- Missing comments (handled separately)

CRITICAL: Before reporting a violation, verify:
1. The violation exists in the CODE TO ANALYZE section (NOT the rules section)
2. The line number is correct (use numbers before the | symbol)
3. The code on that line actually has the issue you're reporting

OUTPUT FORMAT (JSON array only, no other text):
[
  {{
    "type": "memory_leak",
    "severity": "CRITICAL",
    "line_number": 5,
    "description": "new int[100] without delete[]",
    "rule_reference": "Memory Management"
  }}
]

If NO violations found, return: []

Only return valid JSON. No explanations, no markdown, just the JSON array."""

        return base_prompt

    async def check_comment_quality(self, code: str) -> Dict[str, Any]:
        """
        Simple LLM task: Check if comments are descriptive and useful.
        This is a basic task the LLM can reliably handle.

        Args:
            code: C++ source code to analyze

        Returns:
            Dictionary containing comment quality issues
        """
        try:
            # Add line numbers to code
            numbered_lines = []
            for i, line in enumerate(code.split('\n'), 1):
                numbered_lines.append(f"{i:4d} | {line}")
            numbered_code = '\n'.join(numbered_lines)

            prompt = f"""You are checking comment quality in C++ code. This is a SIMPLE task.

CODE WITH LINE NUMBERS:
{numbered_code}

TASK: Find comments that are NOT descriptive or useful.

ONLY report comments that are:
1. Too vague (e.g., "// x" or "// temp")
2. Completely unhelpful (e.g., "// code" or "// function")
3. Obvious/redundant (e.g., "// increment i" for i++)

DO NOT report:
- Missing comments (handled separately)
- Code issues (only check comments)

If ALL comments are adequately descriptive, return: []

OUTPUT FORMAT (JSON array only, no other text):
[
  {{
    "type": "poor_comment_quality",
    "severity": "MINOR",
    "line_number": 5,
    "description": "Comment is too vague",
    "rule_reference": "Code Documentation"
  }}
]

Only return valid JSON. If no issues, return: []"""

            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1, 'num_predict': 500}
            )

            response_text = response['message']['content']
            violations = self._parse_llm_response(response_text)

            return {
                "violations": violations,
                "status": "success"
            }

        except Exception as e:
            print(f"[ERROR] Error during comment quality check: {e}")
            return {
                "violations": [],
                "status": "error",
                "error": str(e)
            }
