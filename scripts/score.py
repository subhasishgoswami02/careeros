"""Turn per-dimension ratings into a transparent score, band and next action.

Claude (the /score skill) does the judgment: it reads the JD and writes a 0-100 rating plus a
reason for each dimension. This script does the arithmetic, applies the caps and rules, and
picks the band, so the total always follows scoring.yaml and rules.yaml.

    python3 scripts/score.py ratings.json            # print the score card
    python3 scripts/score.py ratings.json --save     # also save the result to my-data/scores/
    python3 scripts/score.py ratings.json --json     # machine-readable

The ratings file shape is examples/demo/ratings/northwind-pay.json. Fields:
  company, role, location           text
  jd_file, url                      where the JD text and posting live (optional but recommended)
  route                             a key of rules.yaml route_priority
  priority_keyword_title            true / false
  compensation_known                true / false (false = pay not posted; omit the compensation dimension)
  disqualifiers_hit                 list of text, [] if none
  must_haves                        [{"item": "...", "evidence": "strong" | "partial" | "none"}]
  nice_to_haves                     same shape, optional, shown but not scored
  dimensions                        {"<dimension>": {"rating": 0-100, "rationale": "..."}}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitconfig  # noqa: E402

EVIDENCE = {"strong", "partial", "none"}
BANDS_ORDER = ["APPLY", "REFERRAL-ONLY", "CONTACT-ONLY", "SKIP"]


def _bool(payload: dict, key: str, default: bool) -> bool:
    v = payload.get(key, default)
    if not isinstance(v, bool):
        raise ValueError(f"'{key}' must be true or false (no quotes), got {v!r}")
    return v


def _evidence(items, label):
    out = []
    for m in items or []:
        ev = str(m.get("evidence", "")).strip().lower()
        if ev not in EVIDENCE:
            raise ValueError(f"{label} '{m.get('item')}': evidence must be strong, partial or none, got {m.get('evidence')!r}")
        out.append({"item": m.get("item", ""), "evidence": ev})
    return out


def score(payload: dict, scoring: dict, rules: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("the ratings file must be one JSON object, like examples/demo/ratings/northwind-pay.json")
    for k in ("company", "role"):
        if not str(payload.get(k) or "").strip():
            raise ValueError(f"'{k}' is missing")
    weights: dict[str, float] = dict(scoring["weights"])
    if round(sum(weights.values()), 5) != 100:
        raise ValueError(f"Weights in scoring.yaml must add up to 100, got {sum(weights.values())}")

    comp_known = _bool(payload, "compensation_known", True)
    pri_kw = _bool(payload, "priority_keyword_title", False)
    must = _evidence(payload.get("must_haves"), "must-have")
    nice = _evidence(payload.get("nice_to_haves"), "nice-to-have")
    disq = payload.get("disqualifiers_hit", []) or []
    if not isinstance(disq, list):
        raise ValueError("'disqualifiers_hit' must be a list, e.g. [] or [\"reason\"]")

    dims = dict(payload.get("dimensions", {}))
    if not comp_known:
        weights.pop("compensation", None)
        dims.pop("compensation", None)
    missing, extra = set(weights) - set(dims), set(dims) - set(weights)
    if missing or extra:
        raise ValueError(f"Dimension mismatch. Missing: {sorted(missing)}. Extra: {sorted(extra)}")

    total_weight = sum(weights.values())
    breakdown, total = {}, 0.0
    for name, w in weights.items():
        item = dims[name]
        rating, why = item.get("rating"), str(item.get("rationale", "")).strip()
        if isinstance(rating, bool) or not isinstance(rating, (int, float)) or not 0 <= rating <= 100:
            raise ValueError(f"{name}: rating must be a number from 0 to 100, got {rating!r}")
        if not why:
            raise ValueError(f"{name}: every rating needs a rationale")
        eff_w = w * 100 / total_weight  # re-normalise when pay is unknown
        pts = eff_w * rating / 100
        breakdown[name] = {"weight": round(eff_w, 1), "rating": rating, "points": round(pts, 1), "rationale": why}
        total += pts

    raw = round(total)
    final, caps_applied = raw, []
    n_missing = sum(1 for m in must if m["evidence"] == "none")
    caps = scoring.get("caps", {})
    for key, applies in (("two_or_more_missing_must_haves", n_missing >= 2), ("missing_must_have", n_missing >= 1)):
        cfg = caps.get(key, {})
        if applies and cfg.get("enabled"):
            cap = cfg["max_score"]
            if final > cap:
                final = cap
                caps_applied.append(f"{n_missing} must-have(s) with no evidence: capped at {cap}")
            break

    bands = scoring["bands"]
    if disq:
        band = "SKIP"
    elif final >= bands["apply"]:
        band = "APPLY"
    elif final >= bands["referral_only"]:
        band = "REFERRAL-ONLY"
    else:
        band = "SKIP"

    r = rules.get("rules", {})
    prio_table = rules.get("route_priority", {})
    route = payload.get("route", "company_portal")
    if route not in prio_table:
        raise ValueError(f"Unknown route '{route}'. Use one of: {', '.join(prio_table)}")
    notes: list[str] = []
    company = str(payload.get("company", "")).strip().lower()
    big = r.get("big_brand_contact_only", {})
    if big.get("enabled") and any(company == b.lower() or company.startswith(b.lower() + " ") for b in big.get("brands", [])):
        if band == "APPLY" and route not in ("referral", "recruiter_inbound", "named_human_plus_portal"):
            band = "CONTACT-ONLY"
        notes.append("Big brand: apply only via a recruiter who contacted you, a named hiring manager, or a referrer.")
    if r.get("no_easy_apply", {}).get("enabled") and route in ("easy_apply", "job_board"):
        notes.append("Found on a board: apply on the company's own careers page and reach a named person instead.")
        route = "company_portal"
    if band == "REFERRAL-ONLY":
        notes.append("Referral-only: worth sending only through someone who knows you or a named hiring manager.")
    if r.get("ask_budget_on_first_call", {}).get("enabled") and not comp_known and band != "SKIP":
        notes.append("Pay not posted: ask the budgeted range on the first call.")

    priority = prio_table[route]
    if pri_kw and r.get("priority_keywords_first", {}).get("enabled"):
        priority *= 2
    if band == "SKIP":
        priority = 0.0

    return {
        "company": payload.get("company"), "role": payload.get("role"), "location": payload.get("location"),
        "url": payload.get("url"), "jd_file": payload.get("jd_file"),
        "raw_score": raw, "score": final, "band": band, "caps_applied": caps_applied,
        "disqualifiers_hit": disq, "route": route, "priority": round(priority, 1),
        "compensation_known": comp_known, "notes": notes, "breakdown": breakdown,
        "must_haves": must, "nice_to_haves": nice, "scored_on": date.today().isoformat(),
    }


LABELS = {
    "role_title_match": "Role / title", "jd_experience_match": "JD vs experience", "domain_match": "Domain",
    "must_have_coverage": "Must-haves", "compensation": "Compensation", "location": "Location",
    "company_desirability": "Company", "seniority_fit": "Seniority", "growth": "Growth",
}


def card(res: dict) -> str:
    out = [f"{res['company']}  |  {res['role']}  |  {res.get('location') or ''}",
           f"SCORE {res['score']}/100   BAND {res['band']}   ROUTE {res['route']}   PRIORITY {res['priority']}", ""]
    for k, b in res["breakdown"].items():
        out.append(f"  {LABELS.get(k, k):<18} {b['points']:>5.1f} / {b['weight']:<4}  {b['rationale']}")
    if not res["compensation_known"]:
        out.append(f"  {'Compensation':<18}   n/a          pay not posted: left out, other weights scaled up")
    if res["must_haves"]:
        out += ["", "  Must-haves:"] + [f"    [{m['evidence']:^7}] {m['item']}" for m in res["must_haves"]]
    if res["nice_to_haves"]:
        out += ["  Nice-to-haves:"] + [f"    [{m['evidence']:^7}] {m['item']}" for m in res["nice_to_haves"]]
    for c in res["caps_applied"]:
        out.append(f"\n  CAP: {c} (raw {res['raw_score']})")
    for d in res["disqualifiers_hit"]:
        out.append(f"  DISQUALIFIED: {d}")
    for n in res["notes"]:
        out.append(f"  NOTE: {n}")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Score one role from a ratings file.")
    ap.add_argument("ratings", type=Path)
    ap.add_argument("--json", action="store_true", help="print JSON instead of the card")
    ap.add_argument("--save", action="store_true", help="save the result to my-data/scores/")
    a = ap.parse_args()
    try:
        payload = json.loads(a.ratings.read_text(encoding="utf-8"))
        scoring, _ = kitconfig.load("scoring")
        rules, _ = kitconfig.load("rules")
        res = score(payload, scoring, rules)
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        sys.exit(f"Could not score {a.ratings}: {e}")
    if a.save:
        out = kitconfig.data_dir() / "scores" / f"{kitconfig.slug(res['company'], res['role'], res['scored_on'])}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=2), encoding="utf-8")
        res["saved_to"] = str(out)
    print(json.dumps(res, indent=2) if a.json else card(res) + (f"\n\n  saved: {res['saved_to']}" if a.save else ""))


if __name__ == "__main__":
    main()
