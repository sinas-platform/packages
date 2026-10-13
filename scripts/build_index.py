#!/usr/bin/env python3
"""Build index.json: the list of packages a Sinas package repository serves.

Sinas reads a repository through this one file (one request per refresh, on
any static host). Each entry names a package, its version and where its
package.yaml lives relative to the repository root, with a checksum so Sinas
can tell the file it downloads is the one the index describes.

    python scripts/build_index.py           # write index.json
    python scripts/build_index.py --check   # fail if index.json is out of date

The output is deterministic (sorted, no timestamps), so --check in CI catches
a package changed without regenerating the index.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.json"
SCHEMA = "sinas.package-index/v1"
REPOSITORY = {
    "name": "sinas-official",
    "title": "Sinas official packages",
    "url": "https://github.com/sinas-platform/packages",
}


def entry(path: Path) -> dict:
    raw = path.read_bytes()
    doc = yaml.safe_load(raw)
    if not isinstance(doc, dict) or doc.get("kind") != "SinasPackage":
        raise ValueError(f"{path}: not a SinasPackage document")
    meta = doc.get("package") or {}
    name, version = meta.get("name"), meta.get("version")
    if not name or not version:
        raise ValueError(f"{path}: package.name and package.version are required")
    folder = path.parent
    if folder.name != name:
        raise ValueError(f"{path}: folder '{folder.name}' must match package name '{name}'")
    out = {
        "name": name,
        "version": str(version),
        "description": " ".join(str(meta.get("description") or "").split()),
        "author": meta.get("author"),
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size": len(raw),
    }
    if meta.get("multiInstance") is True:
        # Sinas offers "install another" for these straight from the catalog.
        out["multiInstance"] = True
    readme = folder / "README.md"
    if readme.exists():
        out["readme"] = readme.relative_to(ROOT).as_posix()
    return out


def build() -> dict:
    packages = [entry(p) for p in sorted((ROOT / "packages").glob("*/package.yaml"))]
    names = [p["name"] for p in packages]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"duplicate package names: {', '.join(duplicates)}")
    return {"schema": SCHEMA, "repository": REPOSITORY, "packages": packages}


def render(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if index.json is not up to date")
    args = parser.parse_args()
    try:
        text = render(build())
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.check:
        current = INDEX.read_text() if INDEX.exists() else ""
        if current != text:
            print("index.json is out of date: run python scripts/build_index.py", file=sys.stderr)
            return 1
        print(f"index.json is up to date ({len(json.loads(text)['packages'])} packages)")
        return 0
    INDEX.write_text(text)
    print(f"wrote index.json ({len(json.loads(text)['packages'])} packages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
