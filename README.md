# CareerOS

An agentic operating system for running a job search like a product.

CareerOS is a lightweight framework built from Markdown files, source-of-truth tables, and scheduled review loops. The design bet is simple: for a single person making high-stakes career decisions, a version-controlled folder plus adversarial AI review can be more useful than a complex multi-agent app.

A private version holds my own data. This public repo contains the architecture, prompts, and blank templates. It does not contain my personal data, employer data, interview notes, company research, or private evidence archive.

## Why This Exists

Most AI job-search tools optimize one artifact, usually the resume. CareerOS optimizes decisions:

- Which roles are worth applying to
- Which claims are defensible
- Which resume variant should be compiled
- Which interviewer questions should become permanent learning
- Which parts of the system should be deleted because they are not used

Three principles drive the design.

1. **Truth over optimization.** Every metric that can appear on a resume or in an interview carries a confidence verdict and a source. A claim without evidence does not ship.
2. **N=1 honesty.** A personal job search does not produce enough data for a statistical model. What works instead: written predictions, calibration tracking, and harvesting every recruiter and interviewer question as reusable intelligence.
3. **Survivability over intelligence.** A simple system still running in month four beats a clever system abandoned in week three. Logging an outcome must take under 30 seconds.

## Architecture

```text
TRUTH ENGINE
  metrics, ownership boundaries, confidence verdicts, retired claims
      |
EVIDENCE STORE
  one note per claim: source, date, defensibility
      |
ARTIFACT COMPILER
  resumes and outreach as build outputs, not hand-maintained documents
      |
REVIEW GATES
  five ordered adversarial agents with defined veto powers
      |
PIPELINE
  every application logged with a prediction before sending
      |
LOOPS
  per-application, per-outcome, weekly, monthly, meta
```

## The Five Gates

Every outgoing artifact passes ordered gates. Order matters: parallel critics tend to average the writing into something bland.

| Gate | Agent | Power |
|---|---|---|
| 0 | Economist | Runs before writing. Can kill the application on opportunity-cost grounds. |
| 1 | Truth Auditor | Absolute veto. Checks every number, title, date, and ownership claim. |
| 2 | Recruiter | The 7-second test. Can demand one structural rewrite. |
| 3 | Hiring Manager | Pressure-tests whether the claims would survive an interview. |
| 4 | Anti-AI Stylist | Final voice pass. Output ships without another review loop. |

Prompts for all five gates are in [AGENTS.md](AGENTS.md).

## The Loops

- **L0, per opportunity:** score fit, make an explicit apply/skip decision, compile the artifact from truth plus variant spec, run the gates, send, and write a prediction.
- **L1, per outcome:** log the result against the prediction, harvest every question asked, and update the running experiment.
- **L2, weekly:** review pipeline health, market signal, experiment results, and next week's time allocation.
- **L3, monthly:** review positioning and maintain an explicit accept threshold.
- **L4, meta:** delete any file no loop reads. Complexity has to pay rent.

## Quickstart

1. Copy [TEMPLATES.md](TEMPLATES.md) into private files for your own search.
2. Fill the Truth Engine before writing or rewriting a resume.
3. For each opportunity, run the Economist gate first.
4. Compile the artifact from verified claims only.
5. Run the remaining gates in order.
6. Before sending, write a prediction.
7. When the outcome arrives, grade the prediction and harvest the questions.

## Lessons From Real Use

- Resumes should be compiled, not maintained. Hand-edited variants drift; one truth source plus variant specs cannot.
- The highest-value data in a job search is the set of questions interviewers actually ask. Sample size required: one.
- Market facts decay in weeks. Company facts carry timestamps; expired facts degrade to "re-verify," not "true."

## What This Demonstrates

This project is intentionally small, but it shows the building blocks I care about as an AI builder:

- Agent roles with bounded authority
- Ordered review loops instead of generic chatbot feedback
- Evaluation through pre-registered predictions
- Source-backed claim management
- Human voice preservation
- System design that survives real use

## Repo Contents

- [CONSTITUTION.md](CONSTITUTION.md): the operating laws
- [AGENTS.md](AGENTS.md): the five review-gate prompts
- [TEMPLATES.md](TEMPLATES.md): blank schemas and fictional examples
- [MODULES.md](MODULES.md): the end-to-end module roadmap, from intake to inbox intelligence
- [ARCHITECTURE.md](ARCHITECTURE.md): the whole system in one diagram

## Stack

Claude / Claude Code, Markdown, spreadsheets, scheduled reminders, and git. Deliberately boring tools for a serious personal workflow.

---

Built by Subhasish Goswami. The private instance runs on personal data; this public version ships only the reusable system.
