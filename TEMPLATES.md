# Templates

Blank schemas for the core files. All examples are fictional.

## 1. Truth Engine

One row per claim.

| Metric / Claim | Confidence | Verdict / Usage Rule | Source | Where used | Notes |
|---|---|---|---|---|---|
| "Reduced review cycle time 35%" | High | Use freely | Operations dashboard export, 2026-05-14 | Resume bullet 2 | Conservative basis: 30% if challenged |
| "Improved activation 18%" | Do not use | Two sources conflict; awaiting adjudication | Conflict ledger item C3 | Nowhere | Never use either value until adjudicated |
| "Led onboarding redesign" | Medium | Frame as "led product side"; design and engineering had named owners | Project charter, 2026-04-02 | Interview story bank | Never imply solo ownership |
| "12,000 monthly users" | Retired | Never use, regardless of what any older document says | Superseded 2026-06 | Purged | Current figure lives in row 1 |

Rules: every resume number must have a row. New numbers enter as Medium until sourced. Conflicts freeze both values until adjudicated once, in writing.

## 2. Pipeline

One row per application.

| Date | Company / Role | Variant sent | Referral? | Prediction before sending | Outcome | Prediction vs actual |
|---|---|---|---|---|---|---|
| 2026-06-02 | ExampleCo, Senior PM | Platform v2 | Yes | 70% response: strong domain match plus referral | Screen booked 2026-06-09 | Correct direction |
| 2026-06-04 | OtherCo, Lead PM | Growth v1 | No | 25% response: title mismatch | Rejected 2026-06-18, no interview | Correct; stop applying to this title pattern |

The prediction column is the point. Written before sending, graded after. Ten graded predictions teach more than a hundred ungraded applications.

## 3. Experiments

Pre-registered, one at a time.

```text
EXPERIMENT: referral vs cold for domain-matched roles
HYPOTHESIS: referral materially improves response rate for equivalent fit scores
DESIGN: next 6 domain-matched applications, 3 referred and 3 cold, matched on fit score
PREDICTION, written 2026-06-01: referred 60%+, cold under 25%
RESULT: filled when n=6
DECISION RULE: if confirmed, stop sending cold applications where any credible warm path exists
```

## 4. Conflict Ledger

One entry per contradiction.

```text
C1. [CLAIM]: figure X vs figure Y
SOURCES:
  [doc A, date, method] says X
  [doc B, date, method] says Y
PRECEDENCE NOTE:
  Later timestamp wins only when methods are equal.
  Direct source verification outranks aggregation regardless of recency.
OPTIONS:
  a. use X because...
  b. use Y because...
  c. drop the figure and use the verified mechanism instead
ADJUDICATED [date]: option b. X is retired permanently.
```

## 5. Interview Intelligence

One file per company, append-only.

```text
COMPANY: ExampleCo

2026-06-09, recruiter screen:
  Q: "Walk me through the onboarding redesign; what was specifically yours?"
  Q: "Why this role now?"
  A-quality: good / weak / rehearse

Pattern note:
  Two interviewers independently probed ownership boundaries.
  Keep the pre-emptive one-liner in the summary.
```

These files compound. When the same company calls again in two years, the questions are waiting.
