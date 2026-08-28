#!/usr/bin/env python3
"""Conservative pre-release scanner for SUP-MIMIC.

This is not a legal review. It catches common mistakes before pushing a public
repository: secrets, local paths, build caches, large data files, and likely
patient-level exports.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(authorization|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)\bapi[_-]?key\b\s*[:=]\s*['\"]?(?!replace|your|env|SUP_)[A-Za-z0-9_\-]{16,}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Z]:\\"),
    re.compile(r"/mnt/"),
    re.compile(r"/home/[^/\s]+/"),
]
SENSITIVE_EXTENSIONS = {
    ".parquet",
    ".feather",
    ".db",
    ".sqlite",
    ".pkl",
    ".pickle",
    ".xlsx",
    ".xls",
    ".pyc",
}
GENERATED_NAMES = {"__pycache__", ".pytest_cache", "outputs", "raw", "restricted", "private", "data"}


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit repository before public release.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--max-bytes", type=int, default=20_000_000)
    return parser.parse_args()


def should_read(path: Path) -> bool:
    return path.suffix.lower() in {
        ".py",
        ".md",
        ".sql",
        ".yaml",
        ".yml",
        ".toml",
        ".tex",
        ".bib",
        ".json",
        ".jsonl",
        ".csv",
        ".txt",
    }


def main() -> None:
    args = build_args()
    issues: list[str] = []
    for path in args.root.rglob("*"):
        rel = path.relative_to(args.root)
        parts_lower = {p.lower() for p in rel.parts}
        if path.is_dir():
            continue
        if path.suffix.lower() in SENSITIVE_EXTENSIONS:
            issues.append(f"sensitive file extension: {rel}")
        if path.stat().st_size > args.max_bytes:
            issues.append(f"large file requires manual review: {rel} ({path.stat().st_size} bytes)")
        if any(p in parts_lower for p in {"outputs", "raw", "restricted", "private"}):
            issues.append(f"file under private/generated directory: {rel}")
        if not should_read(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.name == "qa_release_audit.py":
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(f"secret-like string: {rel}")
                break
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(text) and "qa_release_audit.py" not in str(rel):
                issues.append(f"local absolute path: {rel}")
                break

    if issues:
        print("Release audit failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Release audit passed.")


if __name__ == "__main__":
    main()
