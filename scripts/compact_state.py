#!/usr/bin/env python3
"""Capture and restore a compact list of SG1 paths without copying the tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe relative path: {value}")
    return path


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_archive(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-a", "--", str(source), str(destination)], check=True)


def capture(state: Path, root: Path, source_root: Path, paths: list[Path], once: bool) -> None:
    manifest_path = state / "manifest.json"
    if once and manifest_path.is_file():
        print(f"Preserving compact snapshot: {state}")
        return
    if state.exists():
        shutil.rmtree(state)
    (state / "files").mkdir(parents=True)
    items = []
    for relative in paths:
        source = source_root / relative
        present = source.exists() or source.is_symlink()
        items.append({"path": relative.as_posix(), "present": present})
        if present:
            copy_archive(source, state / "files" / relative)
    manifest = {
        "schema": 1,
        "root": str(root),
        "source_root": str(source_root),
        "items": items,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Compact snapshot created: {state} ({len(items)} paths)")


def restore(state: Path, root: Path) -> None:
    manifest_path = state / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"snapshot manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1:
        raise ValueError("unsupported compact snapshot schema")
    for item in manifest.get("items", []):
        relative = safe_relative(str(item["path"]))
        destination = root / relative
        if destination.exists() or destination.is_symlink():
            remove_path(destination)
        if item.get("present"):
            source = state / "files" / relative
            if not (source.exists() or source.is_symlink()):
                raise FileNotFoundError(f"snapshot payload missing: {source}")
            copy_archive(source, destination)
    print(f"Compact snapshot restored: {state}")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--state", required=True, type=Path)
    capture_parser.add_argument("--root", required=True, type=Path)
    capture_parser.add_argument("--source", type=Path)
    capture_parser.add_argument("--once", action="store_true")
    capture_parser.add_argument("paths", nargs="+")
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("--state", required=True, type=Path)
    restore_parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise ValueError(f"invalid SG1 root: {root}")
    if args.command == "capture":
        source_root = (args.source or root).resolve()
        if not source_root.is_dir():
            raise ValueError(f"invalid snapshot source: {source_root}")
        paths = [safe_relative(value) for value in args.paths]
        capture(args.state, root, source_root, paths, args.once)
    else:
        restore(args.state, root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

