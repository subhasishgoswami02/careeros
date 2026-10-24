"""Stop personal data from ever being committed.

Installed as a git pre-commit hook by scripts/install_guard.sh. It checks what is STAGED
(not what is on disk) and blocks the commit when:
  1. a staged file is inside my-data/ (any capitalisation)
  2. a staged file is a document, spreadsheet or image that could be a resume, payslip or screenshot,
     outside docs/images/ and examples/
  3. staged text contains a term from my-data/private-terms.txt
     (your name, emails, phone, employers, salary figures: /setup writes this file)

Run by hand any time:  python3 scripts/privacy_guard.py --all   (checks every tracked file)
Note: `git commit --no-verify` skips hooks. Don't.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS_FILE = ROOT / "my-data" / "private-terms.txt"
RISKY_EXT = {".pdf", ".doc", ".docx", ".odt", ".rtf", ".pages", ".txt.pdf",
             ".xls", ".xlsx", ".csv", ".numbers", ".ods", ".ppt", ".pptx", ".key",
             ".png", ".jpg", ".jpeg", ".heic", ".gif", ".webp", ".eml", ".msg"}
ALLOWED_DIRS = {("docs", "images"), ("examples",)}


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def staged_files(all_tracked: bool) -> list[str]:
    r = git("ls-files") if all_tracked else git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if r.returncode != 0:
        sys.exit("PRIVACY GUARD: this folder is not a git repository (or git failed), so nothing was checked.\n"
                 "If you never use git, your data can't be committed anyway. Otherwise run `git init` first.")
    return [f for f in r.stdout.decode("utf-8", "replace").splitlines() if f]


def staged_text(f: str, all_tracked: bool) -> str | None:
    r = git("show", f":{f}")  # the staged (index) version, not the file on disk
    if r.returncode != 0:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def terms() -> list[str]:
    if not TERMS_FILE.exists():
        return []
    return [t.strip().lower() for t in TERMS_FILE.read_text(encoding="utf-8").splitlines()
            if t.strip() and not t.lstrip().startswith("#") and len(t.strip()) >= 3]


def allowed_dir(parts: tuple[str, ...]) -> bool:
    return any(parts[:len(a)] == a for a in ALLOWED_DIRS)


def main() -> int:
    all_tracked = "--all" in sys.argv
    private, problems = terms(), []
    for f in staged_files(all_tracked):
        p = Path(f)
        parts = tuple(x.lower() for x in p.parts)
        if parts and parts[0] == "my-data":
            problems.append(f"{f}: inside my-data/ (personal data never gets committed)")
            continue
        if p.suffix.lower() in RISKY_EXT and not allowed_dir(parts):
            problems.append(f"{f}: a {p.suffix} file outside docs/images or examples (resume, payslip or screenshot?)")
            continue
        if private:
            text = staged_text(f, all_tracked)
            if text is None:
                continue
            hits = sorted({t for t in private if t in text.lower()})
            if hits:
                problems.append(f"{f}: contains private term(s) {hits}")
    if problems:
        print("PRIVACY GUARD: commit blocked\n  " + "\n  ".join(problems))
        print("\nFix: remove the private text, or unstage the file (git restore --staged <file>).")
        return 1
    print("privacy guard: ok" + ("" if private else
          "  (tip: list your name, email and employer in my-data/private-terms.txt so they get blocked too)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
