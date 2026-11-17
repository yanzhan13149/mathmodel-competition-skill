"""Check App exports, state preservation, and installed-resource completeness."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location("app_test_" + name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load_script("export_deepseek_app")
starter = load_script("start_contest")
installer = load_script("install_local")


class DeepSeekAppTests(unittest.TestCase):
    def test_generic_pack_and_zip_contain_only_expected_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            output, archive = exporter.export_pack(Path(temp) / "手机使用包", make_zip=True)
            expected = set(exporter.DOCUMENTS.values()) | {"来源与许可/LICENSE", "来源与许可/SOURCES.md"}
            self.assertEqual({p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}, expected)
            with zipfile.ZipFile(archive) as bundle:
                self.assertIsNone(bundle.testzip())
                self.assertEqual(set(bundle.namelist()), expected)
                for name in expected:
                    self.assertEqual(bundle.read(name).decode("utf-8"), (output / name).read_text(encoding="utf-8"))

    def test_each_competition_uses_its_own_rule_source(self):
        with tempfile.TemporaryDirectory() as temp:
            for comp in exporter.COMPETITIONS:
                output, _ = exporter.export_pack(Path(temp) / comp, competition=comp)
                rule_file = next(output.glob("历史规则基线-*.txt"))
                baseline = (ROOT / "competitions" / comp / "current_rules.md").read_text(encoding="utf-8")
                self.assertTrue(rule_file.read_text(encoding="utf-8").endswith(baseline))

    def test_snapshot_preserves_unknowns_and_does_not_copy_project_files(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = starter.create_workspace(Path(temp) / "contest", "mcm")
            (workspace / ".env").write_text("PRIVATE_SAMPLE=value", encoding="utf-8")
            (workspace / "results/private.csv").write_text("value\n1\n", encoding="utf-8")
            state_file = workspace / "state/decision_log.json"
            original = state_file.read_bytes()
            output, _ = exporter.export_pack(Path(temp) / "kit", workspace=workspace)
            text = (output / "比赛状态快照.txt").read_text(encoding="utf-8")
            snapshot = json.loads(text[text.index("{"):])
            self.assertIsNone(snapshot["problem_meta"]["deadline_iso"])
            self.assertIsNone(snapshot["compliance"]["ruleset"]["verified_at"])
            self.assertEqual(snapshot["compliance"]["ai_usage_summary"]["status"], "unknown")
            self.assertIsNone(snapshot["compliance"]["ai_usage_summary"]["entry_count"])
            self.assertIsNone(snapshot["stages"]["5"]["qi_count"])
            self.assertEqual(original, state_file.read_bytes())
            self.assertFalse((output / ".env").exists())
            self.assertFalse((output / "results").exists())

    def test_ai_usage_summary_distinguishes_empty_from_missing_and_recorded(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = starter.create_workspace(Path(temp) / "contest", "cumcm")
            state_file = workspace / "state/decision_log.json"
            state = json.loads(state_file.read_text(encoding="utf-8"))
            for usage, expected in ((None, "unknown"), ([], "source_declares_no_use"), ([{"purpose": "test"}], "recorded_in_source")):
                state["compliance"]["ai_usage"] = usage
                state_file.write_text(json.dumps(state), encoding="utf-8")
                _, text = exporter.read_snapshot(workspace)
                snapshot = json.loads(text[text.index("{"):])
                self.assertEqual(snapshot["compliance"]["ai_usage_summary"]["status"], expected)

    def test_conflicts_and_invalid_inputs_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            workspace = starter.create_workspace(base / "contest", "mcm")
            output = base / "kit"
            for options in ({"competition": "bad"}, {"workspace": base / "missing"}, {"workspace": workspace, "competition": "cumcm"}):
                with self.subTest(options=options), self.assertRaises((ValueError, OSError)):
                    exporter.export_pack(output, **options)
                self.assertFalse(output.exists())
            with self.assertRaises(ValueError):
                exporter.export_pack(ROOT / "kit")
            (base / "kit.zip").write_bytes(b"KEEP")
            with self.assertRaises(FileExistsError):
                exporter.export_pack(output, make_zip=True)
            self.assertFalse(output.exists())
            self.assertEqual((base / "kit.zip").read_bytes(), b"KEEP")
            output.mkdir()
            (output / "keep.txt").write_text("KEEP", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                exporter.export_pack(output)
            self.assertEqual((output / "keep.txt").read_text(encoding="utf-8"), "KEEP")

    def test_installed_skill_can_export_without_the_original_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            installed = installer.install(Path(temp) / "installed")
            output = Path(temp) / "kit"
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(installed / "scripts/export_deepseek_app.py"), str(output), "--zip"],
                cwd=temp, capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((output / "上传到DeepSeek.txt").is_file())
            self.assertTrue((Path(temp) / "kit.zip").is_file())


if __name__ == "__main__":
    unittest.main()
