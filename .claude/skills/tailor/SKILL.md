---
name: tailor
description: Prepare the application for a scored role - pick the resume variant, tailor only if a trigger fires, write the cover note, run the review gates, and give a send checklist. Use for "tailor my resume", "cover letter for this", "prepare the application".
---

# /tailor <company + role>

## 0. Inputs
Read `my-data/jds/<slug>.md` and the newest `my-data/scores/<slug>-*.json`. If either is missing, run /score first.
Read `my-data/experience-library.md` and `profile.yaml resume_variants`.

## 1. Pick the variant
Take the JD's top 3 requirements. Pick the variant whose top section answers them. Say which and why.
Open its file in `my-data/resumes/`.

## 2. Does it need tailoring?
Check `rules.yaml tailor_only_with_trigger.triggers`. If none fire: send the variant unchanged, write the cover note
(step 4), and say "No trigger fired, so tailoring would be wasted effort."

## 3. If a trigger fires, build it
- Every line comes from the experience library. Reorder, re-emphasise, reword; never add a fact.
- Use the JD's own words only where the library supports them.
- Numbers copied exactly. **Do-not-use** never appears.
- **Medium** confidence: phrase it the way the library supports, for example "contributed to", "part of the team that",
  or "about" only if the library says about. Never upgrade the verb.
- Can't trace a line: `[UNVERIFIED]` and ask.
- Put `Coverage: x of y must-haves evidenced` at the top of the draft.

## 4. Cover note (under 200 words)
The JD's top 3 needs, each matched to one library result in a short paragraph. One specific line on why this
company, from their product or a recent change, not their About page. No flattery, no "I am excited to apply".

## 5. Review gates, in order, one pass each
Give each gate the draft, the JD file and the experience library:
truth-auditor -> recruiter -> hiring-manager -> stylist (`.claude/agents/`). Apply fixes. Write what changed to the gate log.

## 6. Save and hand over
Save `my-data/applications/<slug>/resume.md`, `cover-note.md`, `gate-log.md`.
If they need a file, make a .docx or PDF from the Markdown (Claude can do this) and save it in the same folder.
In chat, give the send checklist:
1. Apply on the company's own site: <link from the JD file>
2. Within 24 hours, message <named person> (/outreach)
3. Log it: `python3 scripts/tracker.py add --company "..." --role "..." --score-file <file> --contact "..." --p <0-1> --prediction "..."`
