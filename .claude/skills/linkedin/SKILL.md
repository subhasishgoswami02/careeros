---
name: linkedin
description: Rewrite the user's LinkedIn headline, About section and top experience bullets from their experience library, aimed at the roles in their profile. Use for "fix my LinkedIn", "rewrite my headline", "LinkedIn profile".
---

# /linkedin

Recruiters search LinkedIn by title and skills, then read the headline and About. This makes those match the roles
the user is going for, using only true facts.

1. Ask for their current headline, About, and the experience entries (paste).
2. Read `profile.yaml` (target roles, domains) and `my-data/experience-library.md`.
3. Draft:
   - **Headline** (under 220 characters): target title, the domain or problem they're strongest at, one proof point.
   - **About** (under 1,500 characters): who they are in one line, 3 results with numbers from the library, what
     they want next, how to reach them. First person, plain words.
   - **Top 3 bullets** for the current role, from the library.
   - **Skills**: the 10 that appear most in their target JDs (from `my-data/jds/`) and that the library supports.
4. Run truth-auditor and stylist.
5. Show before and after side by side. They paste it in. Never claim the current job title is different from reality.
