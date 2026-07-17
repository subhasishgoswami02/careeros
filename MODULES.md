# Modules: The End-to-End Roadmap

CareerOS started as a truth engine plus review gates. The full system covers the whole journey from "a job exists" to "offer decision," with the human approving every external action. Status reflects the private instance; this repo ships the designs.

| # | Module | What it does | Status |
|---|---|---|---|
| M1 | Opportunity Intake & Fit | Parses a JD, scores hard fit, skill fit, and expected career value; the Economist gate issues PROCEED or SKIP before any writing starts | Running (private) |
| M2 | Artifact Compiler | Compiles the resume variant from the Truth Engine plus a per-audience variant spec; nothing is hand-edited | Running (private) |
| M3 | Cover Letter Composer | Why this company, why now, why me, gap handling, in that order; evidence-only, no flattery; passes gates 1 and 4 | Designed |
| M4 | Application Kit | Generates everything a specific application needs: tailored artifacts, answers to standard form questions, salary framing. A human clicks submit | Designed |
| M5 | Inbox Intelligence | A daily scheduled agent reads the job-search mailbox: classifies interview invites, rejections, and recruiter replies; updates the pipeline automatically; extracts interviewer names and roles; drafts replies and 7-day follow-up nudges | In build |
| M6 | Live Dashboard | One page, always current: funnel stage counts, prediction calibration, aging applications needing a nudge, upcoming interviews | In build |
| M7 | Outreach Targeting | Researches the hiring team from public sources and drafts first-touch messages in the owner's voice, response-probability over word count | Designed |
| M8 | Interview Prep Packs | Per-company prep files built from the JD, the interview-intelligence store, and past question patterns | Running (private) |
| M9 | Learning Loop | Pre-registered predictions, graded outcomes, one live experiment at a time | Running (private) |

## Why M5 matters most

Every personal system dies the same way: the human stops logging outcomes, the loops starve, the files fossilize. Inbox Intelligence exists so the system pulls its own data instead of waiting to be fed. Law 12 (logging must cost under 30 seconds) is really Law 0.

## Deliberate non-goals

- **No automated submissions.** Job platforms forbid it, and volume was never the constraint; decision quality is.
- **No scraping.** Outreach research uses public sources only.
- **No mailbox data in this repo, ever.** Inbox Intelligence runs only in the private instance. This repo ships the design, not the data.
- **No interview-probability numbers dressed up as statistics.** Predictions are written in plain language with reasons, then graded. That is calibration, not clairvoyance.

## Distribution note

Several modules run as reusable Claude skills in the private instance (resume QA gates, evidence checking, interview prep, voice preservation). Packaging agent workflows as skills turned out to be the most practical deployment model: no server, no app, versioned alongside the data they operate on.
