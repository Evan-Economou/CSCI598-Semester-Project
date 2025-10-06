"""
Style guide processing service
"""
import re
import hashlib
from typing import List, Tuple, Dict
from app.models.core import StyleGuide, StyleGuideRule, ViolationSeverity, Severity


SECTION_HEADER_RE = re.compile(r"^\s*([A-Z][A-Z0-9 _-]{2,})\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")


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
        sections = self._split_into_sections(content)
        rules: List[StyleGuideRule] = []
        for section_name, lines in sections:
            severity = self._severity_from_section(section_name)
            for line in lines:
                m = BULLET_RE.match(line)
                if not m:
                    continue
                text = m.group(1).strip()
                rid = self._rule_id(section_name, text)
                rules.append(StyleGuideRule(
                    id=rid,
                    text=text,
                    severity=severity,
                    section=section_name.strip()
                ))

        return StyleGuide(
            name=name,
            rules=rules,
            raw_content=content
        )

    def _split_into_sections(self, content: str) -> List[Tuple[str, List[str]]]:
        lines = content.splitlines()
        sections: List[Tuple[str, List[str]]] = []
        current_name = "GENERAL"
        current_lines: List[str] = []
        for line in lines:
            if SECTION_HEADER_RE.match(line):
                # push previous
                if current_lines:
                    sections.append((current_name, current_lines))
                current_name = line.strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_name, current_lines))
        return sections

    def _severity_from_section(self, name: str) -> Severity:
        name_up = name.upper()
        if "CRITICAL" in name_up:
            return Severity.CRITICAL
        if "WARNING" in name_up:
            return Severity.WARNING
        if "MINOR" in name_up:
            return Severity.MINOR
        # Default fallback if unspecified
        return Severity.WARNING

    def _rule_id(self, section: str, text: str) -> str:
        # Stable short id derived from section+text
        base = f"{section}::{text}"
        digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
        return f"rule_{digest}"

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
