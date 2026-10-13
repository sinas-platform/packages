#!/usr/bin/env python3
"""Install every package in index.json on a running Sinas and check it holds up.

For each package: preview it (filling every required variable with a dummy
value of the right type), install it, and install it again, which must
change nothing (an idempotent upgrade). Package-specific checks then read
back what was installed through the API.

    SINAS_URL=http://localhost:8000 SINAS_EMAIL=... SINAS_PASSWORD=... \\
        python scripts/check_packages.py [package ...]

Standard library only. Exits 1 on the first package that fails, with the
reason.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("SINAS_URL", "http://localhost:8000").rstrip("/")

# Tried in order for a text variable with a pattern; the first that matches wins.
TEXT_CANDIDATES = ["ci", "ci-test", "https://example.com", "ci@example.com", "1", "C0123456789", "example.com"]


class CheckFailed(Exception):
    pass


def call(method: str, path: str, body=None, token=None):
    req = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise CheckFailed(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')[:2000]}") from None


def login() -> str:
    email, password = os.environ.get("SINAS_EMAIL"), os.environ.get("SINAS_PASSWORD")
    if not email or not password:
        raise CheckFailed("SINAS_EMAIL and SINAS_PASSWORD must be set")
    return call("POST", "/auth/login", {"email": email, "password": password})["access_token"]


def dummy(decl: dict):
    kind = decl.get("type", "text")
    if kind == "enum":
        return (decl.get("choices") or [None])[0]
    if kind == "boolean":
        return False
    if kind in ("number", "integer"):
        return 1
    if kind == "secret":
        return "ci-dummy-secret"
    pattern = decl.get("pattern")
    for candidate in TEXT_CANDIDATES:
        if not pattern or re.match(pattern, candidate):
            return candidate
    raise CheckFailed(f"no dummy value matches the pattern of variable '{decl['name']}': {pattern}")


def variables_for(declarations: list[dict]) -> dict:
    return {
        d["name"]: dummy(d)
        for d in declarations or []
        if d.get("required", True) and d.get("default") is None
    }


def counts(apply: dict) -> dict:
    summary = apply.get("summary") or {}
    return {action: sum((summary.get(action) or {}).values()) for action in ("created", "updated", "deleted")}


def check_package(entry: dict, token: str) -> None:
    source = (ROOT / entry["path"]).read_text()
    first = call("POST", "/api/v1/packages/preview", {"source": source}, token)
    values = variables_for(first.get("variables"))
    preview = call("POST", "/api/v1/packages/preview", {"source": source, "variables": values}, token)
    if not preview.get("success"):
        raise CheckFailed(f"preview failed: {preview.get('errors')}")

    body = {"source": source, "variables": values, "allowBroadRolePermissions": True}
    installed = call("POST", "/api/v1/packages/install", body, token)
    if not installed["apply"].get("success"):
        raise CheckFailed(f"install failed: {installed['apply'].get('errors')}")
    if installed["package"]["version"] != entry["version"]:
        raise CheckFailed(f"installed version {installed['package']['version']} != index {entry['version']}")

    again = call("POST", "/api/v1/packages/install", body, token)
    changed = counts(again["apply"])
    if not again["apply"].get("success") or any(changed.values()):
        raise CheckFailed(f"reinstall was not a no-op: {changed} {again['apply'].get('errors')}")

    extra = EXTRA_CHECKS.get(entry["name"])
    if extra:
        extra(token)


def check_way_of_working(token: str) -> None:
    """The exemplar agent has the loop switched on, the skill preloaded, and
    approval rules that let reads run and make publishing ask."""
    agent = call("GET", "/api/v1/agents/way-of-working/assistant", token=token)
    tools = set(agent.get("system_tools") or [])
    missing = {"workbench", "codeExecution", "askUser", "artifacts", "background"} - tools
    if missing:
        raise CheckFailed(f"assistant is missing system tools: {sorted(missing)}")
    skills = agent.get("enabled_skills") or []
    if not any(s.get("skill") == "way-of-working/workbench-loop" and s.get("preload") for s in skills):
        raise CheckFailed("assistant does not preload way-of-working/workbench-loop")
    approvals = agent.get("tool_approvals") or {}
    rules = {r.get("match"): r.get("action") for r in approvals.get("rules") or []}
    if approvals.get("default") != "auto" or rules.get("workbench_promote") != "ask":
        raise CheckFailed(f"unexpected tool approvals: {approvals}")
    skill = call("GET", "/api/v1/skills/way-of-working/workbench-loop", token=token)
    if "workbench" not in (skill.get("content") or ""):
        raise CheckFailed("the workbench-loop skill has no content")


EXTRA_CHECKS = {"way-of-working": check_way_of_working}


def main() -> int:
    index = json.loads((ROOT / "index.json").read_text())
    wanted = set(sys.argv[1:])
    entries = [p for p in index["packages"] if not wanted or p["name"] in wanted]
    try:
        token = login()
        for entry in entries:
            check_package(entry, token)
            print(f"ok   {entry['name']} {entry['version']}")
    except CheckFailed as e:
        print(f"FAIL {entry['name'] if 'entry' in locals() else '-'}: {e}", file=sys.stderr)
        return 1
    print(f"{len(entries)} packages install cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
