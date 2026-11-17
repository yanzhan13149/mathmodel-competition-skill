#!/usr/bin/env python3
"""Install the complete skill resources, not only the plugin discovery shim."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ("agents", "assets", "competitions", "config", "references", "scripts", "templates", "tools", "adapters")
FILES = ("SKILL.md", "使用指南.md", "LICENSE", "SOURCES.md", "THIRD_PARTY_NOTICES.md", "latexmkrc", "requirements-contest.txt", "比赛快速上手.md")


def default_destination(client: str) -> Path:
    if client == "claude":
        return Path.home() / ".claude/skills/mathmodel-skill"
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills/mathmodel-skill"


def install(destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents or destination in ROOT.parents:
        raise ValueError("installation destination must be separate from the source repository")
    if destination.exists():
        raise FileExistsError(f"destination already exists; nothing overwritten: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    for directory in RESOURCES:
        shutil.copytree(
            ROOT / directory, destination / directory,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
        )
    for name in FILES:
        shutil.copy2(ROOT / name, destination / name)
    # doctor validates plugin packaging as well as runtime resources.
    shutil.copytree(ROOT / ".codex-plugin", destination / ".codex-plugin")
    shutil.copytree(ROOT / "skills", destination / "skills")
    shutil.copy2(ROOT / "README.md", destination / "README.md")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=("codex", "claude"), default="codex")
    parser.add_argument("--dest", type=Path, help="exact destination skill folder; refuses overwrite")
    args = parser.parse_args(argv)
    try:
        output = install(args.dest if args.dest is not None else default_destination(args.client))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Installed: {output}")
    print("The skill will be available on your next turn. Invoke $mathmodel-skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
