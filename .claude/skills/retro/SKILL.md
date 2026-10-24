---
name: retro
description: Weekly retro of the job search - funnel by route, predictions vs reality, which rules hold for this user, score calibration, time and energy, and three changes for next week. Use weekly, or for "weekly review", "what's working".
---

# /retro

## 1. Last week's promises
Read the newest file in `my-data/retros/`. Did they do the three changes? Yes or no for each, no excuses needed.

## 2. Numbers
`python3 scripts/tracker.py stats --days 7` and `python3 scripts/tracker.py stats` (all time).
Report: warm asks vs floor, cold applications vs cap, replies, interviews, roles reviewed vs applied.

## 3. Predictions vs reality
From the stats output: where were they too hopeful or too gloomy? One plain sentence.

## 4. Are the rules holding for them?
Once they have 30+ applications, check each rule in `rules.yaml` against their own numbers (e.g. reply rate for
job_board vs referral). Mark each **holding**, **not enough data** or **not holding**, and propose switching off the
ones that aren't. Refit `route_priority` once a route has 10+ applications (keep the defaults until then).

## 5. Is the score useful?
After `scoring.yaml calibration.review_after_outcomes` resolved outcomes, compare the scores of roles that got a
reply with those that didn't (score files are in `my-data/scores/`). If the score doesn't separate them, say so:
use it as a fit filter only. Propose weight changes; never apply them silently.

## 6. Interview patterns
Read "Known weak spots" in `my-data/interview-log.md`. Did any show up again this week? Pick one to work on.

## 7. Time and energy
Ask: hours spent this week, and energy from 1 to 5. If energy has dropped two weeks running, say so and suggest
cutting volume, not adding more.

## 8. Next week
Three changes, maximum. Each concrete ("5 referral asks at payments companies", not "network more").
Save `my-data/retros/YYYY-MM-DD.md` with the numbers, findings, energy, and a "Next week" section (/briefing reads it).
