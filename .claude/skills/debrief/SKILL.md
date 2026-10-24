---
name: debrief
description: Debrief a real interview or recruiter call from the user's notes - grade each answer, keep every question asked, predict the next step, update the pipeline and interview log, and draft a thank-you. Use after any interview or call.
---

# /debrief <notes, or a transcript recorded with the interviewer's consent>

Inputs: the pipeline row (`tracker.py find <company>`), `my-data/prep/<slug>-<round>.md` (what they planned to say) and
`my-data/applications/<slug>/` (what they sent). Compare what happened with the plan.

Recording someone without their consent is illegal in some places and breaks trust everywhere. Notes are fine.

## 1. Keep every question
List each question asked, as close to verbatim as the notes allow. Append them to `my-data/interview-log.md`
with date, company and round. /prep ranks these first next time, so they're worth the 2 minutes.

## 2. Grade each answer, 1 to 5 on each
- **Clear:** did it have a start, a point and an end?
- **Specific:** a real example, a real number, their own part in it?
- **Adapted:** did they handle the follow-up, or repeat a prepared line?
Quote the weakest moment and show a better version using only library facts. Save the grades in the log.

## 3. Signals
What the interviewer showed: time overruns, how deep the follow-ups went, next steps mentioned, pay, timeline.

## 4. Predict and update
Write the chance of moving to the next step and why. Then:
`python3 scripts/tracker.py update <id> --status <screen|interview|offer|rejected> --round "<round>" --note "<prediction>"`
(find the id with `tracker.py find <company>`).

## 5. Patterns
If the same weakness shows up in 2 or more debriefs, add it to "Known weak spots" in interview-log.md.

## 6. Thank-you note
3 to 4 lines that mention one specific thing from the conversation. Stylist check. The user sends it.
