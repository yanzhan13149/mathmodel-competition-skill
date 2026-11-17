#!/usr/bin/env python3
"""Tool-directory metadata contract.

Executable tools keep scripts; document adapters contain only original routing
instructions. Restricted upstream implementations must not enter this edition.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("figure", "paper_search", "docx", "xlsx", "pdf", "latex")
ADAPTERS = {"docx", "xlsx", "pdf"}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert m, "SKILL.md must start with YAML frontmatter"
    data = yaml.safe_load(m.group(1))
    assert isinstance(data, dict)
    return data


class ToolMetaTest(unittest.TestCase):
    def test_each_tool_has_skill_and_scripts(self) -> None:
        for tool in TOOLS:
            tool_dir = ROOT / "tools" / tool
            with self.subTest(tool=tool):
                skill = tool_dir / "SKILL.md"
                self.assertTrue(skill.is_file())
                meta = parse_frontmatter(skill.read_text(encoding="utf-8"))
                self.assertTrue(meta.get("name"))
                self.assertTrue(meta.get("description"))
                if tool not in ADAPTERS:
                    self.assertTrue((tool_dir / "scripts").is_dir())

    def test_document_adapters_do_not_bundle_upstream_implementation(self) -> None:
        for tool in ADAPTERS:
            with self.subTest(tool=tool):
                files = {p.name for p in (ROOT / "tools" / tool).iterdir()}
                self.assertEqual(files, {"SKILL.md"})


if __name__ == "__main__":
    unittest.main()
