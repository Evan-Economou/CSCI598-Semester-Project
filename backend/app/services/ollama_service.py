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

        base_prompt = f"""You are a C++ code style analyzer. Analyze the following code against the provided style guide.

Style Guide:
{style_guide}

"""
        if context:
            base_prompt += f"""Additional Context:
{context}

"""

        base_prompt += f"""Code to Analyze:
{code}

Please identify all style violations. For each violation, provide:
1. Type of violation
2. Severity (CRITICAL, WARNING, or MINOR)
3. Line number
4. Description
5. Reference to the style guide section

Format your response as a JSON array with this structure:
[
  {{
    "type": "violation_type",
    "severity": "CRITICAL|WARNING|MINOR",
    "line_number": 1,
    "description": "Description of the violation",
    "rule_reference": "Style guide section reference"
  }}
]

Only return the JSON, no other text."""

        return base_prompt
