---
name: prep
description: Build a one-file interview prep pack for a specific company and round (recruiter screen, hiring manager, case, take-home, panel, final) from the JD, what was sent, fresh research, the experience library and past interview questions. Use for "interview tomorrow", "prep me for", "prep pack".
---

# /prep <company + role + round, interviewer if known>

## Inputs
`my-data/jds/<slug>.md`, `my-data/applications/<slug>/` (what they actually sent, and the hiring-manager gate's
hardest questions in gate-log.md), the pipeline row (`tracker.py find <company>`), `my-data/interview-log.md`,
`my-data/experience-library.md`, `my-data/contacts.md`.
Save `my-data/prep/<slug>-<round>.md`. One file, readable in 15 minutes.
Update the pipeline: `tracker.py update <id> --status interview --round "<round>"` (or `screen`).

## Sections
1. **30-second read.** What they sell, to whom, how they make money, one recent change. Sources with dates; older than
   6 months gets [VERIFY].
2. **What this round tests.** From the round type and the interviewer's professional background (LinkedIn, talks,
   posts; not personal social media).
3. **Likely questions (8 to 12).** From the JD, the round type, the gate log's hardest questions, and questions asked
   before in `interview-log.md` (those rank first).
4. **Answers as beats, not scripts.** For each: which library story, 3 beats, the number, and the likely follow-up.
   No word-for-word lines: they should sound like a conversation.
5. **Round-specific:**
   - Recruiter screen: why you're looking, notice period, location, visa, expected pay (from `profile.yaml
     compensation` and `market_notes`), and their range (rules.yaml `ask_budget_on_first_call`).
   - Case or product sense: a 5-step structure for this company's product, and 2 practice prompts.
   - Take-home: scope it (time cap, what to leave out), what a strong submission shows, questions to ask first.
   - Panel or final: who's in the room, what each one cares about, the one story each needs to hear.
6. **Known weak spots** from interview-log grades, one fix each.
7. **Your 3 questions for them**, specific to their product or team.
8. **Final rounds only: references.** Who 2 or 3 references would be, and a one-line brief for each.

Only facts from the experience library. No new claims.
