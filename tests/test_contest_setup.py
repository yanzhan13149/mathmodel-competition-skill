"""Check that contest setup preserves unknown facts and existing work."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


starter = load_script("start_contest")
installer = load_script("install_local")


class ContestSetupTests(unittest.TestCase):
    def test_all_contests_keep_unknown_rules_and_ai_use(self):
        with tempfile.TemporaryDirectory() as temp:
            for comp in starter.COMPETITIONS:
                output = starter.create_workspace(Path(temp) / comp, comp)
                state = json.loads((output / "state/decision_log.json").read_text(encoding="utf-8"))
                self.assertEqual(state["competition"], comp)
                self.assertIsNone(state["compliance"]["ai_usage"])
                self.assertIsNone(state["compliance"]["ruleset"]["verified_at"])
                self.assertIsNone(state["problem_meta"]["deadline_iso"])
                self.assertIsNone(state["stages"]["5"]["qi_count"])
                self.assertFalse(state["stages"]["0"]["checklist_completed"])
                self.assertTrue((output / "data/raw").is_dir())
                self.assertIn("$mathmodel-skill", (output / "开始建模.md").read_text(encoding="utf-8"))

    def test_supplied_inputs_and_timezone_survive(self):
        with tempfile.TemporaryDirectory() as temp:
            pdf = Path(temp) / "题目.pdf"
            pdf.write_bytes(b"%PDF-1.4\n")
            output = starter.create_workspace(
                Path(temp) / "contest", "mcm", year=2027, problem="B", team_size=3,
                deadline="2027-02-01T21:00:00-05:00", pdf=pdf,
            )
            state = json.loads((output / "state/decision_log.json").read_text(encoding="utf-8"))
            self.assertEqual(state["problem_meta"]["deadline_iso"], "2027-02-01T21:00:00-05:00")
            self.assertEqual(state["problem_meta"]["year"], 2027)
            self.assertEqual(state["paper_metadata"]["problem"], "B")
            self.assertEqual(state["events"]["log"][-1]["pdf_path"], str(pdf.resolve()))

    def test_existing_workspace_is_not_modified(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "比赛"
            starter.create_workspace(output, "cumcm")
            state_file = output / "state/decision_log.json"
            before = state_file.read_bytes()
            with self.assertRaises(FileExistsError):
                starter.create_workspace(output, "mcm")
            self.assertEqual(state_file.read_bytes(), before)

    def test_bad_inputs_leave_no_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "contest"
            for options in ({"team_size": 0}, {"deadline": "2027-01-01T00:00:00"}, {"pdf": Path(temp) / "missing.pdf"}):
                with self.subTest(options=options), self.assertRaises((ValueError, OSError)):
                    starter.create_workspace(output, "cumcm", **options)
                self.assertFalse(output.exists())
            with self.assertRaises(ValueError):
                starter.create_workspace(ROOT / "my-contest", "cumcm")

    def test_installed_skill_is_self_contained_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = installer.install(Path(temp) / "skill")
            self.assertTrue((output / "templates/shared/decision_log.json").is_file())
            self.assertTrue((output / "references/stage_00_kickoff.md").is_file())
            self.assertFalse((output / ".git").exists())
            self.assertFalse((output / "tools/docx/scripts").exists())
            proc = subprocess.run(
                [sys.executable, str(output / "scripts/start_contest.py"), str(Path(temp) / "new contest"), "--competition", "mcm"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            with self.assertRaises(FileExistsError):
                installer.install(output)


if __name__ == "__main__":
    unittest.main()
