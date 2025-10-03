"""
Style guide processing service
"""
from typing import List, Dict
from app.models.core import StyleGuide, StyleGuideRule, ViolationSeverity


class StyleGuideProcessor:
    """Process and parse style guide documents"""

    def parse_style_guide(self, content: str, name: str = "default") -> StyleGuide:
        """
        Parse a plain text style guide into structured format

        Expected format:
        CRITICAL
        - Rule 1
        - Rule 2

        WARNING
        - Rule 3

        MINOR
        - Rule 4
        """
        rules = []
        current_severity = None

        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # Check if this is a severity header
            if line in ["CRITICAL", "WARNING", "MINOR"]:
                current_severity = ViolationSeverity(line)
                continue

            # Parse rule (assuming bullet point format)
            if line.startswith('-') or line.startswith('*'):
                if current_severity:
                    rule_text = line[1:].strip()
                    if rule_text:  # Only add non-empty rules
                        rules.append(
                            StyleGuideRule(
                                severity=current_severity,
                                rule_name=rule_text[:50],  # First 50 chars as name
                                description=rule_text
                            )
                        )

        return StyleGuide(
            name=name,
            rules=rules,
            raw_content=content
        )

    def extract_sections(self, content: str) -> Dict[str, List[str]]:
        """Extract sections organized by severity"""
        sections = {
            "CRITICAL": [],
            "WARNING": [],
            "MINOR": []
        }

        current_section = None
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            if line in sections.keys():
                current_section = line
                continue

            if current_section and line:
                sections[current_section].append(line)

        return sections

    def get_rules_by_severity(
        self,
        style_guide: StyleGuide,
        severity: ViolationSeverity
    ) -> List[StyleGuideRule]:
        """Get all rules of a specific severity level"""
        return [rule for rule in style_guide.rules if rule.severity == severity]
