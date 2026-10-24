"""Config and data-folder helpers shared by every script.

Config lookup: config/<name>.yaml holds the defaults. my-data/<name>.yaml holds your
changes. The two are MERGED (your file only needs the keys you changed), then checked.
Lists are replaced, not merged: if you set `brands:` you set the whole list.
"""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is missing. Run: python3 -m pip install --user pyyaml   (Windows: py -m pip install pyyaml)")

ROOT = Path(__file__).resolve().parents[1]

# Keys every merged config must have, used to catch typos and half-written files.
REQUIRED = {
    "scoring": ["weights", "bands", "caps"],
    "rules": ["rules", "route_priority"],
    "profile": ["candidate", "compensation", "roles", "domains", "locations"],
    "sources": ["sources"],
}

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (ValueError, OSError):
        pass


def data_dir(create: bool = True) -> Path:
    """Your private folder. Default my-data/. CAREEROS_DATA overrides it (used by the demo)."""
    raw = os.environ.get("CAREEROS_DATA", "").strip()
    d = Path(raw) if raw else ROOT / "my-data"
    if not d.is_absolute():
        d = (ROOT / d).resolve()
    if raw and _inside_repo_and_tracked(d):
        sys.exit(f"Refusing to use {d} as the data folder: it is inside the repo and not git-ignored. "
                 "Use my-data/ or a folder outside the repo.")
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def _inside_repo_and_tracked(d: Path) -> bool:
    try:
        d.relative_to(ROOT)
    except ValueError:
        return False
    if not (ROOT / ".git").exists():
        return False
    r = subprocess.run(["git", "check-ignore", "-q", str(d / "probe")], cwd=ROOT, capture_output=True)
    return r.returncode != 0


def _merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        out = copy.deepcopy(base)
        for k, v in over.items():
            out[k] = _merge(base.get(k), v) if k in base else copy.deepcopy(v)
        return out
    return copy.deepcopy(over) if over is not None else copy.deepcopy(base)


def _unknown_keys(default, mine, path=""):
    """Top-two-level keys in your file that the defaults don't know: probably typos."""
    out = []
    if isinstance(default, dict) and isinstance(mine, dict):
        for k, v in mine.items():
            if k not in default:
                out.append(f"{path}{k}")
            elif path.count(".") < 1 and isinstance(v, dict) and isinstance(default[k], dict) \
                    and k not in ("roles", "domains", "weights", "route_priority", "company_tiers", "resume_variants"):
                out += _unknown_keys(default[k], v, f"{path}{k}.")
    return out


def load(name: str) -> tuple[dict, Path]:
    default_path = ROOT / "config" / f"{name}.yaml"
    default = yaml.safe_load(default_path.read_text(encoding="utf-8")) or {}
    mine_path = data_dir(create=False) / f"{name}.yaml"
    used = default_path
    cfg = default
    if mine_path.exists():
        try:
            mine = yaml.safe_load(mine_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            sys.exit(f"{mine_path} is not valid YAML: {e}")
        for k in _unknown_keys(default, mine):
            print(f"warning: {mine_path.name} has a key the kit doesn't use: '{k}' (typo?)", file=sys.stderr)
        cfg = _merge(default, mine)
        used = mine_path
    missing = [k for k in REQUIRED.get(name, []) if k not in cfg]
    if missing:
        sys.exit(f"{name}.yaml is missing required keys: {missing}")
    return cfg, used


def slug(*parts: str) -> str:
    import re
    s = "-".join(p for p in parts if p)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80]
