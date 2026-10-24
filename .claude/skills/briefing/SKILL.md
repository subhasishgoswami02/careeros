---
name: briefing
description: Daily job briefing. Follow-ups due, new roles from the user's sources (deduped, checked live, scored, ranked by route), this week's targets, saved to my-data/briefings/YYYY-MM-DD.md. Use for "morning briefing", "what's new today", or as a daily scheduled task.
---

# /briefing

On the web this is read-only: never apply, message, connect or click anything on any site.
It does update the user's own tracker (auto-closing dead applications). Aim for something they can read in 10 minutes.
If a step fails, carry on and list it under "Not done today". Start the file with a one-line run status.

## 1. Follow-ups
Run `python3 scripts/tracker.py due`. Copy NUDGE, STALE and CLOSE lines to the top.
For each NUDGE, draft a 2 to 3 line follow-up with /outreach rules (follow-up format, truth and stylist checks).
The user marks it sent with `tracker.py update <id> --status nudged` and `tracker.py ask ... --type follow_up`.

## 2. Collect new roles
For each `enabled: true` source in `sources.yaml`, in order:
- `email`: search the inbox with the source's `search`, from the last run date in `my-data/source-checkpoints.md`
  (first run: `limits.first_run_lookback_days` back).
- `public`: open the page and filter by their roles and locations. Careers pages: only every
  `limits.careers_pages_every_days` days per company (note the date in source-checkpoints.md).
- `browser`: only when the user is present and asked; never in a scheduled run.
- Update the checkpoint after each source.

## 3. Filter, then score
- Skip anything in `my-data/pipeline.json` or `my-data/scores/` from the last 30 days, and same company + title
  twice in today's list.
- Confirm the posting is live on the company's own site. Dead, filled or untraceable: drop.
- Run /score steps 1 to 5 on the rest (it saves the JD and the score). Stop at `limits.max_roles_per_briefing`.
- For APPLY and REFERRAL-ONLY roles, look in `my-data/contacts.md` for someone at the company.

## 4. Rank
By `priority` from score.py (route, doubled for niche titles), then score.

## 5. Write my-data/briefings/YYYY-MM-DD.md
```
# Briefing YYYY-MM-DD
Run: <n> sources checked, <n> new roles, <n> scored. Problems: <none / what failed>
## This week's commitments (from the last /retro)
## Do today (3 max)
## Follow-ups
## New roles
| # | Company | Role | Score | Band | Route today | Person to reach | Link (company site) |
## This week so far: warm asks n / floor, cold applications n / cap   (from `tracker.py stats`)
## Skipped: n roles (one line each)
## Not done today
```
Then a 5-line summary in chat.
