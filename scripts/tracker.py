"""Your pipeline: applications (my-data/pipeline.json) and warm asks (my-data/asks.json).

Applications
  add      python3 scripts/tracker.py add --company Acme --role "Senior PM" --route company_portal \
               --score-file my-data/scores/acme-senior-pm-2026-10-26.json --contact "Asha R, Group PM" \
               --p 0.3 --prediction "named HM, strong match, but cold"
  list     python3 scripts/tracker.py list            (active only; --all for everything)
  find     python3 scripts/tracker.py find acme       (look up an id)
  check    python3 scripts/tracker.py check --company Acme --role "Senior PM"   (before applying)
  update   python3 scripts/tracker.py update 3 --status screen --note "recruiter call booked"
  due      python3 scripts/tracker.py due             (nudges, stale interviews, auto-close; --dry-run to only show)
  stats    python3 scripts/tracker.py stats           (funnel by route, this week vs targets, predictions)

Warm asks (referral asks, notes to named hiring managers or recruiters)
  ask      python3 scripts/tracker.py ask --company Acme --person "Ravi S" --type referral [--app 3]

Add --today YYYY-MM-DD anywhere to pretend it is another day (for testing).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitconfig  # noqa: E402

STATUSES = ["applied", "nudged", "replied", "screen", "interview", "offer", "accepted", "declined",
            "rejected", "rejected_auto", "withdrawn", "closed_no_response"]
WAITING = {"applied", "nudged"}
IN_PROCESS = {"replied", "screen", "interview", "offer"}
CLOSED = {"accepted", "declined", "rejected", "rejected_auto", "withdrawn", "closed_no_response"}
HUMAN_REPLY = {"replied", "screen", "interview", "offer", "accepted", "declined", "rejected"}  # not rejected_auto
INTERVIEWED = {"interview", "offer", "accepted", "declined"}
COLD_ROUTES = {"company_portal", "job_board", "easy_apply", "agency"}
ASK_TYPES = ["referral", "hiring_manager", "recruiter", "follow_up", "connection"]


# ---------- storage (atomic writes + a simple lock) ----------

def _path(name: str) -> Path:
    return kitconfig.data_dir() / name


def _read(name: str) -> list[dict]:
    p = _path(name)
    if not p.exists() or not p.read_text(encoding="utf-8").strip():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{p} is not valid JSON ({e}). Fix it by hand or restore {p.name}.bak")
    if not isinstance(data, list):
        sys.exit(f"{p} should contain a list of records")
    return data


def _write(name: str, rows: list[dict]) -> None:
    p = _path(name)
    if p.exists():
        p.with_suffix(p.suffix + ".bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=p.name, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    os.replace(tmp, p)


@contextlib.contextmanager
def locked():
    lock = kitconfig.data_dir() / ".tracker.lock"
    for _ in range(100):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - lock.stat().st_mtime > 30:  # stale lock from a crashed run
                lock.unlink(missing_ok=True)
            time.sleep(0.1)
    else:
        sys.exit("The tracker is busy (another run is writing). Try again in a moment.")
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


# ---------- helpers ----------

def today(a) -> date:
    if not a.today:
        return date.today()
    try:
        return datetime.strptime(a.today, "%Y-%m-%d").date()
    except ValueError:
        sys.exit(f"--today must look like 2026-10-26, got '{a.today}'")


def norm(s: str) -> str:
    return " ".join(str(s or "").lower().replace(",", " ").split())


def rules_cfg() -> dict:
    return kitconfig.load("rules")[0]


def age(row: dict, d: date) -> int:
    return (d - date.fromisoformat(row["date_applied"])).days


def last_change(row: dict) -> date:
    dates = [row["date_applied"]] + [h["date"] for h in row.get("history", [])]
    return date.fromisoformat(max(dates))


def line(r: dict, d: date) -> str:
    who = f"  -> {r['contact']}" if r.get("contact") else ""
    rnd = f" ({r['round']})" if r.get("round") else ""
    return f"#{r['id']:<3} {r['status']:<18} day {age(r, d):<3} {r['company']} / {r['role']}{rnd}{who}"


# ---------- commands ----------

def cmd_add(a) -> None:
    routes = rules_cfg()["route_priority"]
    sc = {}
    if a.score_file:
        p = Path(a.score_file)
        if not p.exists():
            sys.exit(f"Score file not found: {p}")
        try:
            sc = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"{p} is not valid JSON ({e}). Re-run score.py --save to recreate it.")
    route = a.route or sc.get("route") or "company_portal"
    if route not in routes:
        sys.exit(f"Unknown route '{route}'. Use one of: {', '.join(routes)}")
    if a.p is not None and not 0 <= a.p <= 1:
        sys.exit("--p is a probability between 0 and 1, e.g. 0.3")
    with locked():
        rows = _read("pipeline.json")
        for r in rows:
            if norm(r["company"]) == norm(a.company) and norm(r["role"]) == norm(a.role) \
                    and (today(a) - date.fromisoformat(r["date_applied"])).days < 30:
                sys.exit(f"Already applied: #{r['id']} {r['company']} / {r['role']} on {r['date_applied']}")
        row = {"id": max([r["id"] for r in rows], default=0) + 1, "company": a.company.strip(), "role": a.role.strip(),
               "route": route, "score": a.score if a.score is not None else sc.get("score"), "band": sc.get("band"),
               "score_file": a.score_file or "", "url": a.url or sc.get("url") or "", "jd_file": sc.get("jd_file") or "",
               "contact": a.contact, "p_reply": a.p, "prediction": a.prediction,
               "date_applied": today(a).isoformat(), "status": "applied", "round": "", "history": []}
        rows.append(row)
        _write("pipeline.json", rows)
    print(f"Added #{row['id']} {row['company']} / {row['role']}  (route {route})")
    if sc.get("band") == "REFERRAL-ONLY" and route in COLD_ROUTES and not a.contact:
        print("  warning: this role scored REFERRAL-ONLY but is logged as a cold application with no contact")
    if not a.prediction:
        print("  tip: add --prediction next time; /retro grades it later")


def cmd_update(a) -> None:
    with locked():
        rows = _read("pipeline.json")
        row = next((r for r in rows if r["id"] == a.id), None)
        if not row:
            sys.exit(f"No application #{a.id}. Run: python3 scripts/tracker.py find <company>")
        row.setdefault("history", []).append({"date": today(a).isoformat(), "from": row["status"], "to": a.status,
                                              "note": a.note})
        row["status"] = a.status
        if a.round:
            row["round"] = a.round
        if a.contact:
            row["contact"] = a.contact
        _write("pipeline.json", rows)
    print(f"#{a.id} {row['company']} -> {a.status}" + (f" ({a.round})" if a.round else ""))


def cmd_list(a) -> None:
    rows = _read("pipeline.json")
    d = today(a)
    shown = rows if a.all else [r for r in rows if r["status"] not in CLOSED]
    if not shown:
        print("Nothing here yet." if not rows else "No active applications. Use --all to see closed ones.")
    for r in sorted(shown, key=lambda r: (r["status"] in WAITING, r["date_applied"])):
        print(line(r, d))


def cmd_find(a) -> None:
    q = norm(a.text)
    d = today(a)
    hits = [r for r in _read("pipeline.json") if q in norm(r["company"]) or q in norm(r["role"])]
    print("\n".join(line(r, d) for r in hits) if hits else f"No match for '{a.text}'.")


def cmd_check(a) -> None:
    rows, d, cfg = _read("pipeline.json"), today(a), rules_cfg()
    co = [r for r in rows if norm(r["company"]) == norm(a.company)]
    dup = [r for r in co if a.role and norm(r["role"]) == norm(a.role) and age(r, d) < 30]
    silent = [r for r in co if r["status"] in {"closed_no_response", "applied", "nudged", "rejected_auto"}]
    limit = cfg["rules"].get("company_history_check", {}).get("silent_applications_before_contact_only", 3)
    open_ = [r for r in co if r["status"] not in CLOSED]
    print(f"{a.company}: {len(co)} past application(s), {len(open_)} open, {len(silent)} with no human reply")
    for r in co:
        print("   " + line(r, d))
    if dup:
        print("BLOCK: you already applied to this role in the last 30 days.")
    elif cfg["rules"].get("company_history_check", {}).get("enabled") and len(silent) >= limit:
        print(f"CONTACT-ONLY: {len(silent)} silent applications here. Find a person instead of applying cold again.")
    else:
        print("OK to proceed.")
    asks = [x for x in _read("asks.json") if norm(x["company"]) == norm(a.company)
            and (d - date.fromisoformat(x["date"])).days < 7]
    cap = cfg["rules"].get("warm_asks_over_volume", {}).get("max_contacts_per_company_per_week", 2)
    if len(asks) >= cap:
        print(f"HOLD outreach: {len(asks)} people contacted at {a.company} this week (limit {cap}).")


def cmd_ask(a) -> None:
    with locked():
        rows = _read("asks.json")
        rows.append({"date": today(a).isoformat(), "company": a.company.strip(), "person": a.person.strip(),
                     "type": a.type, "app_id": a.app, "note": a.note})
        _write("asks.json", rows)
    wk = [x for x in rows if (today(a) - date.fromisoformat(x["date"])).days < 7 and x["type"] != "connection"]
    floor = rules_cfg()["rules"].get("warm_asks_over_volume", {}).get("warm_asks_per_week_floor", 5)
    print(f"Logged {a.type} ask to {a.person} at {a.company}. Warm asks in the last 7 days: {len(wk)} / {floor}")


def cmd_due(a) -> None:
    fu = rules_cfg()["rules"].get("follow_up_then_close", {})
    if not fu.get("enabled", True):
        print("Follow-ups are switched off in rules.yaml (follow_up_then_close).")
        return
    nudge, close, after = fu.get("nudge_on_day", 7), fu.get("close_on_day", 14), fu.get("close_days_after_nudge", 7)
    stale = fu.get("stale_in_process_days", 10)
    d, out = today(a), []
    with locked():
        rows, changed = _read("pipeline.json"), False
        for r in rows:
            n = age(r, d)
            if r["status"] in WAITING:
                nudged_on = next((h["date"] for h in reversed(r.get("history", [])) if h["to"] == "nudged"), None)
                since_nudge = (d - date.fromisoformat(nudged_on)).days if nudged_on else None
                ready = n >= close and (since_nudge is None or since_nudge >= after)
                if ready:
                    out.append(f"  CLOSE   {line(r, d)}  (no human reply)")
                    if not a.dry_run:
                        r.setdefault("history", []).append({"date": d.isoformat(), "from": r["status"],
                                                            "to": "closed_no_response", "note": f"auto-closed at day {n}"})
                        r["status"], changed = "closed_no_response", True
                elif r["status"] == "applied" and n >= nudge:
                    out.append(f"  NUDGE   {line(r, d)}  -> one short note to "
                               f"{r.get('contact') or 'a named person (find one first)'}, then mark it: "
                               f"update {r['id']} --status nudged")
            elif r["status"] in IN_PROCESS and (d - last_change(r)).days >= stale:
                out.append(f"  STALE   {line(r, d)}  (no update for {(d - last_change(r)).days} days: check in)")
        if changed:
            _write("pipeline.json", rows)
    print(f"Follow-ups for {d}" + (" (dry run, nothing changed)" if a.dry_run else ""))
    print("\n".join(out) if out else "  Nothing due.")


def cmd_stats(a) -> None:
    rows, asks, d, cfg = _read("pipeline.json"), _read("asks.json"), today(a), rules_cfg()
    since = d - timedelta(days=a.days) if a.days else None
    sel = [r for r in rows if not since or date.fromisoformat(r["date_applied"]) >= since]
    if not rows:
        print("No applications yet.")
        return
    st = Counter(r["status"] for r in sel)
    window = f"last {a.days} days" if a.days else "all time"
    print(f"{window}: {len(sel)} applications | waiting {sum(st[s] for s in WAITING)} | in process "
          f"{sum(st[s] for s in IN_PROCESS)} | " + " | ".join(f"{k} {v}" for k, v in st.most_common() if k in CLOSED))
    by = defaultdict(lambda: [0, 0, 0])
    for r in sel:
        b = by[r["route"]]
        reached = {h["to"] for h in r.get("history", [])} | {r["status"]}
        b[0] += 1
        b[1] += bool(reached & HUMAN_REPLY)
        b[2] += bool(reached & INTERVIEWED)
    print(f"\n{'route':<26}{'sent':>6}{'reply%':>8}{'interview%':>12}")
    for route, (n, rep, inter) in sorted(by.items(), key=lambda x: -x[1][0]):
        print(f"{route:<26}{n:>6}{100 * rep / n:>7.0f}%{100 * inter / n:>11.0f}%")
    wk = d - timedelta(days=7)
    warm = [x for x in asks if date.fromisoformat(x["date"]) > wk and x["type"] != "connection"]
    cold = [r for r in rows if date.fromisoformat(r["date_applied"]) > wk and r["route"] in COLD_ROUTES and not r.get("contact")]
    w = cfg["rules"].get("warm_asks_over_volume", {})
    print(f"\nLast 7 days: warm asks {len(warm)} / {w.get('warm_asks_per_week_floor', 5)} (floor)   "
          f"cold applications {len(cold)} / {w.get('cold_applications_per_week_cap', 10)} (cap)")
    graded = [r for r in sel if r["status"] not in WAITING and r.get("p_reply") is not None]
    if graded:
        print("\nPredictions vs what happened:")
        for r in graded:
            got = bool(({h['to'] for h in r.get('history', [])} | {r['status']}) & HUMAN_REPLY)
            print(f"  #{r['id']:<3} said {r['p_reply']:.0%} reply -> {'replied' if got else 'no reply'}   "
                  f"{r['company']}: {r.get('prediction', '')}")


def main() -> None:
    top = argparse.ArgumentParser(add_help=False)
    top.add_argument("--today", help="YYYY-MM-DD, pretend it's another day")
    common = argparse.ArgumentParser(add_help=False)  # same flag after the command, without clobbering
    common.add_argument("--today", default=argparse.SUPPRESS, help="YYYY-MM-DD, pretend it's another day")
    ap = argparse.ArgumentParser(description="Pipeline tracker", parents=[top])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add", parents=[common])
    p.add_argument("--company", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--route", help="defaults to the route in --score-file, else company_portal")
    p.add_argument("--score-file", help="the file /score saved; fills score, band, route and link")
    p.add_argument("--score", type=int)
    p.add_argument("--url", help="link to the posting")
    p.add_argument("--contact", default="", help="the named person, e.g. 'Asha R, Group PM'")
    p.add_argument("--p", type=float, help="your chance of a human reply, 0-1, written BEFORE sending")
    p.add_argument("--prediction", default="", help="one line: what you expect and why")
    p = sub.add_parser("update", parents=[common])
    p.add_argument("id", type=int)
    p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--round", default="", help="e.g. 'recruiter screen', 'HM round', 'case', 'final'")
    p.add_argument("--contact", default="")
    p.add_argument("--note", default="")
    p = sub.add_parser("list", parents=[common])
    p.add_argument("--all", action="store_true")
    p = sub.add_parser("find", parents=[common])
    p.add_argument("text")
    p = sub.add_parser("check", parents=[common])
    p.add_argument("--company", required=True)
    p.add_argument("--role", default="")
    p = sub.add_parser("ask", parents=[common])
    p.add_argument("--company", required=True)
    p.add_argument("--person", required=True)
    p.add_argument("--type", required=True, choices=ASK_TYPES)
    p.add_argument("--app", type=int, help="application id, if this ask is about one")
    p.add_argument("--note", default="")
    p = sub.add_parser("due", parents=[common])
    p.add_argument("--dry-run", action="store_true", help="show what is due without changing anything")
    p = sub.add_parser("stats", parents=[common])
    p.add_argument("--days", type=int, help="only applications from the last N days")
    a = ap.parse_args()
    {"add": cmd_add, "update": cmd_update, "list": cmd_list, "find": cmd_find, "check": cmd_check,
     "ask": cmd_ask, "due": cmd_due, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
