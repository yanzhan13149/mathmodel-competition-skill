#!/usr/bin/env python3
"""Create an isolated contest workspace from the canonical state template."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPETITIONS = ("cumcm", "mcm", "diangong")
DIRECTORIES = (
    "state", "data/raw", "data/processed", "code", "results", "figures",
    "paper_workspace", "paper_output", "support_materials",
)


def parse_deadline(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("deadline must use ISO 8601, e.g. 2027-09-12T20:00:00+08:00") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("deadline requires a timezone, e.g. +08:00")
    return parsed.isoformat()


def create_workspace(
    destination: Path,
    competition: str,
    *,
    year: int | None = None,
    problem: str | None = None,
    deadline: str | None = None,
    team_size: int | None = None,
    pdf: Path | None = None,
    mode: str = "standard",
) -> Path:
    if competition not in COMPETITIONS:
        raise ValueError(f"unsupported competition: {competition}")
    if mode not in ("fast", "standard", "championship"):
        raise ValueError(f"unsupported mode: {mode}")
    if team_size is not None and team_size < 1:
        raise ValueError("team size must be positive")
    if year is not None and not 2000 <= year <= 2100:
        raise ValueError("year must be between 2000 and 2100")
    if deadline is not None:
        deadline = parse_deadline(deadline)
    if pdf is not None:
        pdf = pdf.expanduser().resolve(strict=True)
        if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
            raise ValueError("--pdf must refer to an existing PDF file")
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("create contest workspaces outside the skill repository")
    if destination.exists():
        raise FileExistsError(f"destination already exists; nothing overwritten: {destination}")
    state = json.loads((ROOT / "templates/shared/decision_log.json").read_text(encoding="utf-8"))
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    state.update(competition=competition, problem=problem, mode=mode, started_at=now)
    state["problem_meta"].update(
        year=year, letter=problem, deadline_iso=deadline, team_size=team_size,
    )
    state["paper_metadata"]["problem"] = problem
    state["compliance"]["ruleset"]["competition_year"] = year
    state["events"]["log"].append({
        "type": "workspace_initialized", "ts": now,
        "source": "scripts/start_contest.py", "pdf_path": str(pdf) if pdf else None,
        "note": "Scaffold only; rules, problem and AI use still require verification.",
    })
    destination.mkdir(parents=True, exist_ok=False)
    for directory in DIRECTORIES:
        (destination / directory).mkdir(parents=True, exist_ok=True)
    (destination / "state/decision_log.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    shutil.copy2(ROOT / "使用指南.md", destination / "使用指南.md")
    (destination / ".gitignore").write_text(
        ".venv/\n__pycache__/\n*.py[cod]\n.env\n.env.*\n!.env.example\n"
        "data/raw/\nstate/ai/\n*.aux\n*.log\n*.synctex.gz\n", encoding="utf-8",
    )
    (destination / "开始建模.md").write_text(
        f"# 比赛启动提示词\n\n在 Codex 中打开本目录，复制下面这段话：\n\n"
        f"使用 $mathmodel-skill 继续当前比赛项目。竞赛：{competition}；"
        f"届次：{year or '待确认'}；题号：{problem or '未选定'}；"
        f"截止时间：{deadline or '待确认'}。\n"
        "请先读取 state/decision_log.json，补齐缺少的启动信息并核验当届官方规则，"
        "从 Stage 0 开始，不猜测子问数量，不生成虚构数据或引用。\n\n"
        "尚未填写的队员特长和题目路径可以直接在聊天中补充。"
        "初始化文件不代表已完成环境检查、官方规则核验或 AI 使用披露。\n",
        encoding="utf-8",
    )
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new folder outside the skill repository")
    parser.add_argument("--competition", choices=COMPETITIONS, required=True)
    parser.add_argument("--year", type=int)
    parser.add_argument("--problem", help="selected problem label; omit when not yet known")
    parser.add_argument("--deadline", help="ISO 8601 with timezone; no assumed official deadline")
    parser.add_argument("--team-size", type=int)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--mode", choices=("fast", "standard", "championship"), default="standard")
    args = parser.parse_args(argv)
    try:
        output = create_workspace(**vars(args))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Created: {output}")
    print("Open this folder in Codex and read 开始建模.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
