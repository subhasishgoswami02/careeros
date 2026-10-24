---
name: offer
description: Handle offers - break down and compare offers, plan the negotiation with the user's own numbers, use one offer to speed up other processes, references, and the accept, resign and start checklist. Use for "I got an offer", "how do I negotiate", "compare these offers", "should I accept".
---

# /offer <company>

This is not legal or financial advice. For tax, equity or contract questions, the user should check with a professional.

## 1. Write the offer down
Ask for the offer letter or the recruiter's numbers. Fill `my-data/offers/<slug>.md`:
| Part | Amount | Notes |
|---|---|---|
| Base / fixed | | |
| Variable / bonus (target, and how it's actually paid) | | |
| Equity (type, amount, vesting, cliff, current value basis) | | |
| Joining bonus (and clawback) | | |
| Benefits (insurance, leave, retirement, allowances) | | |
| Level and title | | |
| Location, remote policy, notice period they need | | |
| Deadline to answer | | |
Mark anything unknown as unknown and list the questions to ask.
Update the pipeline: `python3 scripts/tracker.py update <id> --status offer`.

## 2. Compare
- Against `profile.yaml compensation` (ideal, comfortable, floor), in the same currency and unit.
- Against other live processes (`tracker.py list`) and other offers in `my-data/offers/`.
- Non-money factors from their profile: domain, growth, location, team. One table, one honest recommendation.

## 3. Use the offer to speed up others
For each live process at screen or interview stage, draft a short note to the recruiter: you have an offer with a
deadline of <date> and would like to know where you stand. No numbers unless the user wants to share them.

## 4. Negotiation plan
- Their target and walk-away from their own profile numbers. Never invent market data; if they want a market range,
  research it with sources and dates.
- What to ask for, in order: usually base, then level or title, then joining bonus or equity, then start date.
- A short script for the call: thank them, say what would make it a yes, give one number, then stop talking.
- The written follow-up email after the call. Stylist check.
- Market norms from `market_notes` (for example, in India the hike is often discussed against current CTC).

## 5. References
Who 2 or 3 references should be, what each can speak to, and a short note to brief each one.

## 6. Accept, resign, start
- Accept in writing; confirm the start date and anything agreed verbally.
- Background check: what they'll ask for (documents, past employers, dates). Dates must match the experience library.
- Resignation note to the current manager: short, grateful, with the notice period. Decide in advance how to handle a counter-offer.
- Withdraw politely from other processes (draft the notes).
- First 30-60-90 days: a one-page plan from the JD, the prep files and what they learned in interviews.
- Close the search: `tracker.py update <id> --status accepted`, and clear `my-data/contacts.md` within 90 days.
