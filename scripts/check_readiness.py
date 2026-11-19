#!/usr/bin/env python3
"""Probe public HTTP entrypoints; leave browser, transfer and Word checks unverified."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
READ_LIMIT = 64 * 1024
LITERATURE_SITES = (
    ("MDPI", "https://www.mdpi.com"),
    ("Springer", "https://link.springer.com"),
    ("Elsevier ScienceDirect", "https://www.sciencedirect.com"),
    ("IEEE Xplore", "https://ieeexplore.ieee.org"),
)
RESTRICTED_CODES = {401, 403, 407, 418, 429}
CHALLENGE_MARKERS = (b"verify you are human", b"cf-chl-", b"<title>just a moment", b"<title>access denied")


def validate_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or any(character.isspace() for character in url)):
        raise ValueError("official URL must be a public HTTP(S) address without credentials or spaces")
    return url


def validate_timeout(value: float) -> float:
    if not math.isfinite(value) or not 0.1 <= value <= 15:
        raise ValueError("timeout must be between 0.1 and 15 seconds")
    return value


def pending(reason: str) -> dict:
    return {"status": "pending_manual", "reason": reason}


def probe_url(name: str, url: str, timeout: float = 5) -> dict:
    """A successful GET proves HTTP reachability only, not browser usability."""
    validate_url(url)
    validate_timeout(timeout)
    result = {"name": name, "url": url, "status": "unreachable", "http_status": None,
              "final_url": None, "bytes_read": 0, "reason": ""}
    request = urllib.request.Request(url, headers={"User-Agent": "MathModel-Readiness/1.0"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(READ_LIMIT)
            status = response.status
            result.update(http_status=status, final_url=response.geturl(), bytes_read=len(body))
            if any(marker in body.lower() for marker in CHALLENGE_MARKERS):
                result.update(status="restricted", reason="HTTP response contains an access challenge; browser confirmation required")
            elif 200 <= status < 300:
                result.update(status="http_reachable", reason="Read-only HTTP GET succeeded; browser and authenticated access remain unverified")
            else:
                result.update(status="http_error", reason=f"HTTP {status}")
    except urllib.error.HTTPError as error:
        result.update(status="restricted" if error.code in RESTRICTED_CODES else "http_error",
                      http_status=error.code, final_url=error.geturl(), reason=f"HTTP {error.code}: {error.reason}")
        error.close()
    except (urllib.error.URLError, OSError, TimeoutError) as error:
        result["reason"] = str(getattr(error, "reason", error))
    return result


def report_directory(workspace: Path) -> Path:
    workspace = workspace.expanduser().resolve()
    if workspace == ROOT or ROOT in workspace.parents or workspace in ROOT.parents:
        raise ValueError("workspace must be outside the skill repository and its ancestors")
    directory = workspace / "state" / "readiness"
    if not directory.resolve().is_relative_to(workspace):
        raise ValueError("readiness output must stay inside the workspace")
    return directory


def build_report(*, official_url: str | None = None, timeout: float = 5, skip_network: bool = False) -> dict:
    validate_timeout(timeout)
    if official_url is not None:
        validate_url(official_url)
    targets = list(LITERATURE_SITES)
    if official_url is not None:
        targets.insert(0, ("Contest official website", official_url))
    if skip_network:
        results = [{"name": name, "url": url, "status": "skipped", "http_status": None,
                    "final_url": None, "bytes_read": 0, "reason": "Network checks explicitly skipped"}
                   for name, url in targets]
    else:
        with ThreadPoolExecutor(max_workers=min(5, len(targets))) as executor:
            results = list(executor.map(lambda target: probe_url(*target, timeout=timeout), targets))
    official = results.pop(0) if official_url is not None else {
        "name": "Contest official website", "url": None,
        **pending("Provide the actual current contest website before checking it"),
    }
    return {
        "schema_version": "1.0",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "network": {"official_website": official, "literature_sites": results},
        "browser": pending("Open the contest and literature sites in the actual browser; HTTP GET is not browser evidence"),
        "file_transfer": {
            "download": pending("Download and open a permitted sample file using the actual browser"),
            "upload": pending("Use an explicitly provided test upload area or record the team's test evidence; no submission was performed"),
        },
        "word": pending("Open, edit, save and reopen a test DOCX in the actual Word application"),
        "overall_status": "needs_attention",
    }


def check_readiness(workspace: Path, **options) -> tuple[Path, dict]:
    directory = report_directory(workspace)
    report = build_report(**options)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "latest.json"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".readiness-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, epilog="Exit 0 means the diagnostic report was written, not that all readiness checks passed.")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--official-url", help="actual current contest website supplied by the user or verified rules")
    parser.add_argument("--timeout", type=float, default=5, help="per-request socket timeout in seconds (0.1-15)")
    parser.add_argument("--skip-network", action="store_true", help="write an offline report; network status remains skipped")
    args = parser.parse_args(argv)
    try:
        path, report = check_readiness(args.workspace, official_url=args.official_url,
                                       timeout=args.timeout, skip_network=args.skip_network)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"report": str(path), "checked_at": report["checked_at"],
                      "overall_status": report["overall_status"]}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
