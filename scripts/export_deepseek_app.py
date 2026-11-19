#!/usr/bin/env python3
"""Export an uploadable DeepSeek App kit; optionally add a read-only state snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapters/deepseek-app"
COMPETITIONS = ("cumcm", "mcm", "diangong")
DOCUMENTS = {
    "README.md": "00-使用说明.txt",
    "上传到DeepSeek.txt": "上传到DeepSeek.txt",
    "开场提示词.txt": "开场提示词.txt",
    "接力记录模板.txt": "接力记录模板.txt",
    "代码运行指南.txt": "代码运行指南.txt",
    "阶段卡/建模与选题.txt": "阶段卡/建模与选题.txt",
    "阶段卡/求解与稳健性.txt": "阶段卡/求解与稳健性.txt",
    "阶段卡/论文与终审.txt": "阶段卡/论文与终审.txt",
}


def without_docs(value):
    if isinstance(value, dict):
        return {key: without_docs(item) for key, item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [without_docs(item) for item in value]
    return value


def read_snapshot(workspace: Path) -> tuple[str, str]:
    state_path = workspace.expanduser().resolve(strict=True) / "state/decision_log.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("_schema_version") not in ("3.1", "3.2"):
        raise ValueError("workspace state must use a supported schema (3.1 or 3.2)")
    competition = state.get("competition")
    stage = state.get("current_stage")
    if competition not in COMPETITIONS:
        raise ValueError("workspace state has an unsupported competition")
    if not isinstance(stage, int) or isinstance(stage, bool) or not 0 <= stage <= 9:
        raise ValueError("workspace state has an invalid stage")
    compliance = state.get("compliance")
    if not isinstance(compliance, dict) or not isinstance(compliance.get("ruleset"), dict):
        raise ValueError("workspace state has no valid compliance record")
    usage = compliance.get("ai_usage")
    if usage is not None and not isinstance(usage, list):
        raise ValueError("ai_usage must be null or a list")
    if usage is None:
        usage_status = "unknown"
    elif usage:
        usage_status = "recorded_in_source"
    else:
        usage_status = "source_declares_no_use"
    snapshot = {key: state.get(key) for key in (
        "_schema_version", "competition", "problem", "problem_meta", "current_stage",
        "mode", "started_at", "paper_metadata",
    )}
    startup_checks = state.get("startup_checks")
    if startup_checks is not None and not isinstance(startup_checks, dict):
        raise ValueError("startup_checks must be null or an object")
    snapshot["startup_checks"] = without_docs(startup_checks)
    snapshot["compliance"] = {
        "ruleset": without_docs(compliance["ruleset"]),
        "ai_usage_summary": {
            "status": usage_status,
            "entry_count": len(usage) if usage is not None else None,
            "note": "仅概括源文件的历史记录；本次 DeepSeek App 使用需追加实际记录。",
        },
    }
    snapshot["stages"] = without_docs(state.get("stages", {}))
    text = (
        "比赛状态快照：来自队伍已有 state/decision_log.json 的选定字段。\n"
        "导出没有执行代码、核验来源或重新验收；源文件中的完成状态仍需实际证据。\n"
        "本包不自动附带题目、数据、代码、结果、图片或完整 AI 对话，请按当前任务另行提供。\n\n"
        + json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    )
    return competition, text


def export_pack(
    destination: Path,
    *,
    competition: str | None = None,
    workspace: Path | None = None,
    make_zip: bool = False,
) -> tuple[Path, Path | None]:
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents or destination in ROOT.parents:
        raise ValueError("export the App kit outside the skill repository")
    if competition is not None and competition not in COMPETITIONS:
        raise ValueError("unsupported competition")
    archive = destination.parent / (destination.name + ".zip") if make_zip else None
    if destination.exists() or (archive is not None and archive.exists()):
        raise FileExistsError("destination or archive already exists; nothing overwritten")
    # Read and validate everything before creating any output.
    content = {target: (ADAPTER / source).read_text(encoding="utf-8") for source, target in DOCUMENTS.items()}
    if workspace is not None:
        source_competition, snapshot = read_snapshot(workspace)
        if competition is not None and competition != source_competition:
            raise ValueError("--competition does not match the workspace state")
        competition = source_competition
        content["比赛状态快照.txt"] = snapshot
    if competition is not None:
        baseline = (ROOT / "competitions" / competition / "current_rules.md").read_text(encoding="utf-8")
        content[f"历史规则基线-{competition}-仍需当届核验.txt"] = (
            "这是仓库保存的历史核对基线，不代表本次比赛或导出时已实时核验。\n"
            "请核对文档适用届次并实际打开官方来源；核验完成前规则状态保持待核验。\n\n"
            + baseline
        )
    for name in ("LICENSE", "SOURCES.md"):
        content["来源与许可/" + name] = (ROOT / name).read_text(encoding="utf-8")
    destination.mkdir(parents=True, exist_ok=False)
    for relative, text in content.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(text.encode("utf-8"))
    if archive is not None:
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for relative in content:
                bundle.write(destination / relative, arcname=relative)
    return destination, archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--competition", choices=COMPETITIONS)
    parser.add_argument("--workspace", type=Path, help="existing contest workspace; exports a read-only snapshot")
    parser.add_argument("--zip", action="store_true", dest="make_zip")
    args = parser.parse_args(argv)
    try:
        output, archive = export_pack(**vars(args))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Created App kit: {output}")
    if archive is not None:
        print(f"Archive: {archive}")
    print("Upload 上传到DeepSeek.txt and the contest attachments in the DeepSeek App.")
    print("No account was connected and no files were uploaded by this command.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
