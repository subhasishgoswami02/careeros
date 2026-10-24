---
name: track
description: Log applications with a written prediction, update status, list and find applications, show follow-ups and the funnel. Use for "I applied to", "log this", "update status", "what's due", "pipeline", "where am I with X".
---

# /track

Uses `scripts/tracker.py`. Data: `my-data/pipeline.json` (applications) and `my-data/asks.json` (warm asks).

## Log a new application
Ask only what's missing. Before logging, ask for the prediction: "What are the chances of a human reply, and why?"
(e.g. 0.3, "named hiring manager, strong match, but cold"). That's what /retro grades later.
```
python3 scripts/tracker.py add --company "<c>" --role "<r>" --score-file my-data/scores/<file>.json \
  --contact "<name, title>" --p 0.3 --prediction "<why>"
```
`--score-file` fills in the score, band, route and link from /score. Without it, pass `--route` and `--score`.

## Find an id
`python3 scripts/tracker.py list` (active) or `find <company>`.

## Update
`python3 scripts/tracker.py update <id> --status <status> [--round "HM round"] --note "<what happened>"`
Statuses: applied, nudged, replied, screen, interview, offer, accepted, declined, rejected (by a person),
rejected_auto (automated email), withdrawn, closed_no_response.
After sending a follow-up: `--status nudged`. After a screen or interview: suggest /debrief.
After an offer: suggest /offer. After a rejection: ask for any reason they gave.

## Follow-ups
`python3 scripts/tracker.py due` shows nudges (day 7), stale interview processes, and auto-closes.
Draft each nudge with /outreach (follow-up format).

## Funnel
`python3 scripts/tracker.py stats` (add `--days 7` for the week): reply and interview rate by route, warm asks vs
the floor, cold applications vs the cap, and predictions vs what happened.

## No Python?
Edit the JSON by hand with exactly these fields: id, company, role, route, score, band, score_file, url, jd_file,
contact, p_reply, prediction, date_applied, status, round, history (list of {date, from, to, note}).
