# Customise

Edit the copies in `my-data/`, not `config/`. Your copy only needs the keys you change; anything you leave out comes from `config/`. A key the kit doesn't know (a typo) prints a warning. You can also just tell Claude, e.g. *"make domain match matter more and drop growth to 2"*, and it will edit the file and keep the weights at 100.

## profile.yaml: what you want
- **roles / domains**: rate 1 to 5. These are the biggest levers on the score.
- **compensation**: set a currency and unit (INR lakhs, USD thousands...). `below_minimum_policy: ask_me` keeps an exceptional role visible.
- **company_tiers**: tier A gets full company points; `never` hides a company completely.
- **resume_variants**: the 1 to 3 versions you actually send, each with a file in `my-data/resumes/`. `/tailor` starts from one before deciding to build anything new.
- **voice**: banned words and punctuation are enforced by the stylist gate.

## scoring.yaml: how a role is scored
| Dimension | Default weight | Raise it if... |
|---|---|---|
| jd_experience_match | 30 | you want strict fit to what you've actually done |
| role_title_match | 15 | title or level matters a lot to you |
| domain_match | 12 | you're staying in your industry |
| must_have_coverage | 10 | your market screens hard on requirements |
| compensation | 8 | pay is the main goal |
| location | 8 | you can't relocate |
| company_desirability | 7 | brand matters to your next move |
| seniority_fit | 6 | you're avoiding down-levels |
| growth | 4 | you're optimising for trajectory |

- **bands**: `apply` 75, `referral_only` 65. Raise them if you're getting too many marginal roles.
- **caps**: one must-have with no evidence caps the score at 70 (REFERRAL-ONLY at best); two or more cap it at 60 (SKIP). Keep these on: they stop a good title hiding a real gap.
- **Unknown pay** is dropped from the maths, not guessed. That keeps unposted-pay roles from looking average.

## rules.yaml: what to do next
Every rule has `enabled`, a plain-English `what`, and `why`. Turn one off by setting `enabled: false`. Rules worth tuning first:
- `priority_keywords_first.keywords`: your niche, e.g. `["payments", "risk"]` or `["infra", "platform"]`
- `big_brand_contact_only.brands`: the big names in your market
- `follow_up_then_close`: nudge on day 7, close from day 14 (at least 7 days after your nudge). For the US or UK try 21
- `route_priority`: starting guesses. `/retro` refits them from your own outcomes once you have data

## sources.yaml: where to look
- Turn on your region pack (India, UK/Europe, US).
- **LinkedIn, Naukri, Wellfound, IIMJobs, Instahyre**: read their alert *emails*, not the sites. Reading signed-in job sites with automation can break their terms and get your account restricted.
- **Community sheets**: add the link and Claude keeps a checkpoint so it only reads new rows.
- Add any careers page or board as a new entry with `name`, `access`, `url`, `enabled`.

## Adding your own command
Create `.claude/skills/<name>/SKILL.md` with a `name` and `description` header and the steps, and add a row to the table in `CLAUDE.md`. Look at `score/SKILL.md` for the pattern.
