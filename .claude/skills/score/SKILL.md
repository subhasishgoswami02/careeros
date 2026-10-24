---
name: score
description: Score one job against the user's profile and experience library, apply the gates and caps, and say what to do (APPLY, REFERRAL-ONLY, CONTACT-ONLY, SKIP, WATCH or BLOCK) and through whom. Use for "score this", "is this worth it", "should I apply", or a pasted JD or link.
---

# /score <JD text or link>

## 1. Get the real JD and save it
- From a link: open the actual posting. If it's on a board or aggregator, find the same role on the company's own
  careers page and use that link.
- Only a title? Outcome is **WATCH**: say what's missing and stop.
- Save `my-data/jds/<slug>.md`: company, role, location, link, date read, then the JD text as posted.

## 2. Read it literally (show this)
- Quote the main responsibilities (if the JD has none, say so and use the must-haves and the team description).
- List every stated **must-have** and every **nice-to-have**.
- Note the experience band, location and remote policy, pay if posted, visa or sponsorship language.

## 3. Gates (stop at the first failure)
1. `python3 scripts/tracker.py check --company "<company>" --role "<role>"`
   BLOCK = already applied. CONTACT-ONLY = too many silent applications there.
2. `scoring.yaml hard_disqualifiers` (location without work authorization, pay below the floor if that's set to
   reject, a `never` company, an `avoid` theme). Any hit goes in `disqualifiers_hit`.
3. Seniority vs `candidate.years_experience` (`scoring.yaml seniority`): PASS, DOWN-LEVEL (go through a named
   person and ask the range early) or STRETCH (only if the library carries it).

## 4. Rate each dimension 0-100 with one line of reason
- `role_title_match`: their roles rating (5=100, 4=80, 3=60, 2=40, 1=0), adjusted for the real scope.
- `jd_experience_match`: map each responsibility (or must-have) to a specific library entry. Count real matches.
- `domain_match`: their domains rating the same way; an unrated domain is 50.
- `must_have_coverage`: share of must-haves at strong (full) or partial (half).
  **strong** = a library entry shows it directly. **partial** = adjacent or transferable evidence.
  **none** = nothing in the library shows it, even indirectly. When torn between partial and none, quote the
  library line you'd rely on. No line, no partial.
- `compensation`: at or above ideal 100, comfortable 80, floor 50, below the floor 10.
  Pay not posted: `"compensation_known": false` and leave the dimension out.
- `location`: priority_5 100, priority_3 60, priority_1 30.
- `company_desirability`: tier A 100, B 75, C 50, untiered 40.
- `seniority_fit`: PASS 100, STRETCH 50, DOWN-LEVEL 40.
- `growth`: does it move them toward their stated goal?

## 5. Compute and save
Write the ratings file (copy the shape of `examples/demo/ratings/northwind-pay.json`) to a temp file, with:
`company, role, location, url, jd_file, route, priority_keyword_title, compensation_known, disqualifiers_hit,
must_haves, nice_to_haves, dimensions`. `route` is how they could apply today: referral, recruiter_inbound,
named_human_plus_portal, company_portal, agency, job_board or easy_apply.
Run `python3 scripts/score.py <file> --save`. It prints the card and saves `my-data/scores/<slug>-<date>.json`.
If you're unsure, rate it twice from scratch. If the totals differ by more than 8 (`calibration.double_pass_if_disagree_by`), rate a third time and use the middle of the three.
No Python? Do the same arithmetic by hand, show it, and save the same fields.

## 6. Answer in this shape
Check `my-data/contacts.md` for anyone at the company before naming the route.
```
<Company> | <Role> | <Location>
SCORE xx/100  BAND <band>
Why yes (3, each tied to a JD quote) / Why not (3)
Gaps: must-haves with no evidence
Best route today: <route> via <named person, or "find: the hiring manager for <team>">
Next step: one line
```
Add: "This is a fit score, not your odds of a reply. Who you go through matters more."
Bands: APPLY = go. REFERRAL-ONLY = only through someone who knows you or a named hiring manager.
CONTACT-ONLY = don't apply cold; find a person first. SKIP = not worth your time.

## 7. Hand off
APPLY or REFERRAL-ONLY: offer /outreach (to find and message the person), then /tailor, then log it with
`tracker.py add --score-file <saved file>`.
