---
name: outreach
description: Find the right person for a role and draft a short message in the user's voice - referral ask, hiring-manager note, recruiter note, follow-up or connection request - then log the ask. Use for "who should I message", "ask for a referral", "connection request", "follow up".
---

# /outreach <company + role, and the person if known>

Drafts only. The user sends.

## 1. Check first
`python3 scripts/tracker.py check --company "<company>"`. If it says HOLD outreach (already contacted enough people
there this week), stop and say so.

## 2. Find the person (if there isn't one yet)
In this order, using public, professional sources only:
1. `my-data/contacts.md` and the user's own network: anyone they know at the company, or who used to work there.
2. The person who posted the job (often named on the LinkedIn post or the careers page).
3. The likely hiring manager: search LinkedIn for the team name plus "manager", "head of" or "lead" at the company.
4. A recruiter at the company who hires for this function.
Give the user 1 to 3 names with why each, and let them pick. Never guess an email address.
Log the person in `my-data/contacts.md`: work channels only (LinkedIn, work email they published), never personal
phone numbers or home addresses. Delete the file's contents 90 days after the search ends.

## 3. One real connection point
Shared employer, school, community, something they wrote or shipped. If there isn't one, say so; don't fake one.

## 4. Pick the format
| Type | Length | Must contain |
|---|---|---|
| Connection request | under 300 characters | the connection point and one line on why |
| Referral ask (knows you) | 4 to 6 lines | the job link, why you fit in one line, an easy way to say no |
| Referral ask (doesn't know you) | 3 to 5 lines | the connection point, one proof line, ask for 10 minutes or a referral |
| Hiring manager | 5 to 7 lines | one specific observation about their product or problem, one matching result from the library |
| Recruiter | 3 to 5 lines | the role, fit in one line, notice period or availability. No pay talk in writing |
| Follow-up (day 7-10) | 2 to 3 lines | the application, plus one new thing (a relevant result, a short idea, a portfolio link) |

## 5. Write it
- Proof lines only from the experience library, with the user's real ownership ("led the rebuild", not "I rebuilt" if a team built it).
- Voice from `profile.yaml voice`. Open with the point, not pleasantries. Give 2 versions when it matters.

## 6. Check it
Run truth-auditor and stylist. For hiring manager and cold referral notes, also ask the hiring-manager gate's
question: could this be sent to another company unchanged? If yes, make it specific.

## 7. Log it once sent
`python3 scripts/tracker.py ask --company "<company>" --person "<name>" --type <referral|hiring_manager|recruiter|follow_up|connection> [--app <id>]`
It prints the warm-ask count for the week.
