#!/usr/bin/env bash
# Installs the privacy guard as a git pre-commit hook. Run once on every computer you clone to.
# Only needed if you use git with this folder. If you downloaded the ZIP and never commit,
# your data can't end up on GitHub anyway.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "This folder isn't a git repository, so there is nothing to protect yet."
  echo "If you plan to use git, run 'git init' first, then run this script again."
  exit 1
fi
HOOKS="$(git rev-parse --git-path hooks)"   # respects core.hooksPath
mkdir -p "$HOOKS"
cat > "$HOOKS/pre-commit" <<'HOOK'
#!/usr/bin/env bash
cd "$(git rev-parse --show-toplevel)"
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
exec "$PY" scripts/privacy_guard.py
HOOK
chmod +x "$HOOKS/pre-commit"
echo "Privacy guard installed at $HOOKS/pre-commit. Every commit is now checked for personal data."
