---
name: setup
description: One-time guided setup. Interviews the user and builds my-data/ (profile, configs, experience library, resume variants, private terms). Use on first run, or for "set me up", "start over", "change my preferences".
---

# /setup

Goal: in about 30 minutes of questions, turn a resume and a conversation into a working `my-data/` folder.
Ask one small block of questions at a time. Show each file after you write it. Never invent anything:
if something is missing, write `[ASK]` and ask.

## Step 0: Prepare the folder
- Create `my-data/`. Copy `config/*.yaml` and everything in `templates/my-data/` into it, without overwriting existing files.
- Check `.gitignore` contains `/my-data/`.
- If this folder is a git repo (`git rev-parse --git-dir` works), run `bash scripts/install_guard.sh` and tell the user.
  If it isn't, say: "You're not using git here, so nothing you write can end up on GitHub. Skip the guard."
- Check `python3 -c "import yaml"`. If it fails, help install PyYAML (`python3 -m pip install --user pyyaml`).
  If it can't be installed, carry on: you'll do the scoring maths by hand.

## Step 1: Raw material
Ask for: current resume (paste or attach), LinkedIn About and Experience text, and anything that backs up numbers
(reviews, dashboards, launch notes, code or design links). Read all of it first.

## Step 2: Role family
Ask which describes them best: product, engineering, data, design, marketing/growth, sales/success, operations, other.
Use it to pick the title examples in `profile.yaml`, the source query in `sources.yaml`, and the words below.

## Step 3: Experience library (the most important file)
Fill `my-data/experience-library.md` from the template. For every role:
- Scope in their own terms (team, systems, users, budget, accounts: whatever fits the role family).
- 3 to 8 accomplishments: what, how, result with the exact number, evidence source, confidence.
- Ownership in plain words: **led** (you decided or drove it), **built** (you made it), **contributed** (part of a team effort).
Confidence rules: **High** needs a source they could show (a link, doc, dashboard, PR, review). No source = **Medium**.
A number they hesitate on = **Do-not-use**.
Then ask them to read every number back. Change what they correct.
**Stories:** ask them to tell 4 to 6 short stories (a conflict, a failure, influencing without authority, a hard
trade-off, a win backed by data, an ambiguous problem). Write each one down in their words as Situation / Task /
Action / Result. Never fill a story from the resume alone.

## Step 4: Resume variants
Ask which 1 to 3 resume versions they actually send (e.g. "Master", "Platform", "Leadership").
Save each as Markdown in `my-data/resumes/<name>.md` (from what they paste, or from the resume you read).
List them in `profile.yaml resume_variants` with `for` and `file`.

## Step 5: What they want -> my-data/profile.yaml
Ask in blocks, and don't finish until the REQUIRED fields are filled:
1. Level, years of experience, current location, **work authorization** (countries they can work in without a visa),
   goal and why now.
2. Titles they'd take, rated 1-5. Domains rated 1-5. Locations by priority. Remote?
3. Pay: currency, unit, **ideal, comfortable and floor**, what to do below the floor, and `market_notes`
   for how pay talks work where they are.
4. Companies: dream (tier A), strong targets (B), backups (C), never.
5. Voice: how their messages should sound, words and punctuation they hate.
Show the filled file.

## Step 6: Scoring and rules
- Show `scoring.yaml` weights as a table. Ask what matters more or less. Keep the total at 100.
  Their my-data copy only needs the keys they change; the rest comes from `config/`.
- Walk through `rules.yaml` one rule at a time: what it does and why, in one plain sentence.
  Say these are starting points, not laws. Ask keep, change or turn off.
  Fill `priority_keywords_first.keywords` with their niche. Edit `big_brand_contact_only.brands` for their market.
  For the US or UK, suggest `close_on_day: 21`.

## Step 7: Sources
- Ask which tools are connected: an email connector (Gmail or Outlook)? Claude in Chrome? Switch off any source
  that needs a tool they don't have.
- Turn on the region pack for their market.
- Help them create 2 to 4 tight job alerts (LinkedIn, Naukri, Wellfound, whatever fits) and give them the exact
  search to paste. Explain: alerts arrive by email, and reading email is safer than driving the sites.

## Step 8: Private terms
Write `my-data/private-terms.txt`, one per line: full name, every email, phone, current and recent employers,
salary figures as they'd write them, internal project names. Explain that the privacy guard blocks any commit
containing these.

## Step 9: Try it
- Ask for one real JD they're considering. Run /score on it end to end.
- Run `python3 scripts/tracker.py stats` (empty is fine).
- Scheduling /briefing: in the desktop app, ask Claude to make it a daily scheduled task. In Claude Code, see
  docs/SETUP.md (it needs the permissions in `.claude/settings.json`).
- Set `meta.setup_complete: true` and `meta.last_updated` in `my-data/profile.yaml`.

## Done
A short table: files created, rules on or off, sources on, and the next 3 things to do this week.
