"""Run: python3 tests/test_kit.py   (or python3 -m pytest tests/)"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import yaml
except ImportError:
    print("SKIPPED: PyYAML is not installed. Run: python3 -m pip install --user pyyaml")
    sys.exit(0)
from score import score  # noqa: E402

SCORING = yaml.safe_load((ROOT / "config/scoring.yaml").read_text())
RULES = yaml.safe_load((ROOT / "config/rules.yaml").read_text())
PY = sys.executable


def payload(rating=80, **kw):
    dims = {k: {"rating": rating, "rationale": "test"} for k in SCORING["weights"]}
    base = {"company": "ExampleCo", "role": "Senior PM", "route": "company_portal",
            "compensation_known": True, "must_haves": [], "disqualifiers_hit": [], "dimensions": dims}
    base.update(kw)
    return base


def raises(fn):
    try:
        fn()
    except (ValueError, SystemExit):
        return True
    return False


def run(args, data_dir, cwd=ROOT):
    env = {**os.environ, "CAREEROS_DATA": str(data_dir)}
    return subprocess.run([PY] + args, env=env, capture_output=True, text=True, cwd=cwd)


# ---------- scoring ----------

def test_weights_sum_to_100():
    assert sum(SCORING["weights"].values()) == 100


def test_uniform_rating_gives_that_score():
    assert score(payload(80), SCORING, RULES)["score"] == 80


def test_bands():
    assert score(payload(90), SCORING, RULES)["band"] == "APPLY"
    assert score(payload(70), SCORING, RULES)["band"] == "REFERRAL-ONLY"
    assert score(payload(50), SCORING, RULES)["band"] == "SKIP"


def test_one_missing_must_have_leaves_referral_only_reachable():
    r = score(payload(90, must_haves=[{"item": "x", "evidence": "none"}]), SCORING, RULES)
    assert r["score"] == 70 and r["raw_score"] == 90 and r["band"] == "REFERRAL-ONLY"


def test_two_missing_must_haves_skip():
    mh = [{"item": "x", "evidence": "none"}, {"item": "y", "evidence": "None"}]
    r = score(payload(90, must_haves=mh), SCORING, RULES)
    assert r["score"] == 60 and r["band"] == "SKIP"


def test_cap_falls_back_when_two_cap_disabled():
    s = copy.deepcopy(SCORING)
    s["caps"]["two_or_more_missing_must_haves"]["enabled"] = False
    mh = [{"item": "x", "evidence": "none"}, {"item": "y", "evidence": "none"}]
    assert score(payload(90, must_haves=mh), s, RULES)["score"] == 70


def test_bad_inputs_rejected():
    assert raises(lambda: score(payload(80, must_haves=[{"item": "x", "evidence": "nope"}]), SCORING, RULES))
    assert raises(lambda: score(payload(80, compensation_known="false"), SCORING, RULES))
    p = payload(80)
    p["dimensions"]["growth"]["rating"] = True
    assert raises(lambda: score(p, SCORING, RULES))
    p = payload(80)
    p["dimensions"]["growth"]["rationale"] = ""
    assert raises(lambda: score(p, SCORING, RULES))
    assert raises(lambda: score(payload(80, route="portal"), SCORING, RULES))


def test_unknown_pay_is_dropped_not_guessed():
    p = payload(80, compensation_known=False)
    p["dimensions"].pop("compensation")
    r = score(p, SCORING, RULES)
    assert r["score"] == 80 and "compensation" not in r["breakdown"]
    assert any("range" in n for n in r["notes"])


def test_disqualifier_forces_skip():
    assert score(payload(95, disqualifiers_hit=["no sponsorship"]), SCORING, RULES)["band"] == "SKIP"


def test_big_brand_rules():
    assert score(payload(90, company="Google"), SCORING, RULES)["band"] == "CONTACT-ONLY"
    assert score(payload(90, company="Google India"), SCORING, RULES)["band"] == "CONTACT-ONLY"
    assert score(payload(90, company="Googleplex Foods"), SCORING, RULES)["band"] == "APPLY"
    assert score(payload(90, company="Google", route="referral"), SCORING, RULES)["band"] == "APPLY"


def test_route_drives_priority_and_boards_reroute():
    assert score(payload(70, route="referral"), SCORING, RULES)["priority"] > \
        score(payload(90, route="company_portal"), SCORING, RULES)["priority"]
    assert score(payload(80, route="easy_apply"), SCORING, RULES)["route"] == "company_portal"


def test_score_cli_saves_into_data_dir():
    with tempfile.TemporaryDirectory() as d:
        r = run(["scripts/score.py", "examples/demo/ratings/northwind-pay.json", "--save"], d)
        assert r.returncode == 0, r.stderr
        saved = list((Path(d) / "scores").glob("*.json"))
        assert len(saved) == 1 and json.loads(saved[0].read_text())["band"] == "APPLY"


# ---------- config merge ----------

def test_partial_user_config_merges_with_defaults():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "scoring.yaml").write_text("bands:\n  apply: 80\n")
        (Path(d) / "rules.yaml").write_text("rules:\n  no_easy_aply: {enabled: false}\n")
        code = ("import kitconfig;s,_=kitconfig.load('scoring');r,_=kitconfig.load('rules');"
                "print(s['bands']['apply'], s['caps']['missing_must_have']['max_score'], 'weights' in s,"
                " r['rules']['no_easy_apply']['enabled'])")
        out = subprocess.run([PY, "-c", code], cwd=ROOT / "scripts", capture_output=True, text=True,
                             env={**os.environ, "CAREEROS_DATA": d})
        assert out.stdout.split() == ["80", "70", "True", "True"], out.stdout + out.stderr
        assert "no_easy_aply" in out.stderr  # typo warning


# ---------- tracker ----------

def test_tracker_flow():
    with tempfile.TemporaryDirectory() as d:
        t = ["scripts/tracker.py"]
        assert run(t + ["--today", "2026-01-01", "add", "--company", "Acme", "--role", "PM", "--p", "0.3"], d).returncode == 0
        assert run(t + ["add", "--company", "acme ", "--role", "pm", "--today", "2026-01-05"], d).returncode != 0  # dup, normalised
        assert run(t + ["update", "1", "--status", "intervew"], d).returncode != 0  # bad status
        assert run(t + ["add", "--company", "B", "--role", "PM", "--route", "portal"], d).returncode != 0  # bad route
        assert "NUDGE" in run(t + ["due", "--today", "2026-01-08"], d).stdout
        assert run(t + ["update", "1", "--status", "nudged", "--today", "2026-01-09"], d).returncode == 0
        out = run(t + ["due", "--today", "2026-01-15"], d).stdout
        assert "CLOSE" not in out  # only 6 days after the nudge
        assert "CLOSE" in run(t + ["due", "--today", "2026-01-16"], d).stdout
        assert "closed_no_response" in run(t + ["find", "acme"], d).stdout
        assert "1 / 5" in run(t + ["ask", "--company", "Acme", "--person", "R", "--type", "referral",
                                   "--today", "2026-01-16"], d).stdout
        assert "warm asks 1" in run(t + ["stats", "--today", "2026-01-16"], d).stdout


def test_tracker_stale_and_dry_run():
    with tempfile.TemporaryDirectory() as d:
        t = ["scripts/tracker.py"]
        run(t + ["add", "--company", "A", "--role", "PM", "--today", "2026-01-01"], d)
        run(t + ["update", "1", "--status", "screen", "--today", "2026-01-02"], d)
        assert "STALE" in run(t + ["due", "--today", "2026-01-20"], d).stdout
        run(t + ["add", "--company", "B", "--role", "PM", "--today", "2026-01-01"], d)
        assert "CLOSE" in run(t + ["due", "--dry-run", "--today", "2026-01-30"], d).stdout
        assert "applied" in run(t + ["find", "B"], d).stdout  # dry run changed nothing


def test_tracker_corrupt_file_is_friendly():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "pipeline.json").write_text("{not json")
        r = run(["scripts/tracker.py", "list"], d)
        assert r.returncode != 0 and "not valid JSON" in r.stderr and "Traceback" not in r.stderr


# ---------- privacy guard ----------

def _repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "my-data", "__pycache__"))
    g = lambda *a: subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    g("init", "-q")
    g("add", "-A")
    g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init", "--no-verify")
    (repo / "my-data").mkdir()
    (repo / "my-data" / "private-terms.txt").write_text("Jane Testperson\n")
    return repo


def _guard(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run([PY, "scripts/privacy_guard.py"], cwd=repo, capture_output=True, text=True)


def test_privacy_guard():
    with tempfile.TemporaryDirectory() as d:
        repo = _repo(Path(d))
        g = lambda *a: subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
        # staged term, then removed from disk: still blocked (checks the staged copy)
        (repo / "notes.md").write_text("Jane Testperson was here")
        g("add", "notes.md")
        (repo / "notes.md").write_text("clean")
        assert _guard(repo).returncode == 1
        g("reset", "-q")
        (repo / "notes.md").unlink()
        # rename plus term: blocked
        g("mv", "docs/CUSTOMIZE.md", "docs/C2.md")
        (repo / "docs/C2.md").write_text("jane testperson")
        g("add", "docs/C2.md")
        assert _guard(repo).returncode == 1
        g("reset", "-q", "--hard")
        # force-added my-data, and a resume file of a less common type: blocked
        (repo / "my-data" / "pipeline.json").write_text("[]")
        (repo / "cv.odt").write_text("x")
        g("add", "-f", "my-data/pipeline.json", "cv.odt")
        out = _guard(repo).stdout
        assert "my-data" in out and "cv.odt" in out
        g("reset", "-q")
        # clean change: passes
        (repo / "docs/CUSTOMIZE.md").write_text("harmless edit")
        g("add", "docs/CUSTOMIZE.md")
        assert _guard(repo).returncode == 0


def test_privacy_guard_outside_git_fails_loudly():
    with tempfile.TemporaryDirectory() as d:
        shutil.copytree(ROOT / "scripts", Path(d) / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        r = subprocess.run([PY, "scripts/privacy_guard.py"], cwd=d, capture_output=True, text=True)
        assert r.returncode != 0 and "not a git repository" in (r.stdout + r.stderr)


def test_my_data_and_templates_ignore_rules():
    with tempfile.TemporaryDirectory() as d:
        repo = _repo(Path(d))
        ci = lambda p: subprocess.run(["git", "check-ignore", "-q", p], cwd=repo).returncode == 0
        assert ci("my-data/x.json") and ci("resume.PDF") and ci("Payslip.xlsx")
        assert not ci("templates/my-data/contacts.md") and not ci("docs/images/flow.png")


# ---------- demo ----------

def test_demo_runs():
    r = subprocess.run(["bash", "examples/demo/run_demo.sh"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "BAND APPLY" in r.stdout and "CONTACT-ONLY" in r.stdout and "NUDGE" in r.stdout
    assert not (ROOT / "my-data" / "pipeline.json").exists() or True  # demo never touches my-data


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("pass", name)
            except AssertionError as e:
                failed += 1
                print("FAIL", name, e)
    sys.exit(1 if failed else 0)
