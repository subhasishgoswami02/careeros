# The System in One Diagram

CareerOS has the same three layers as any decent platform: a source of truth, deterministic gates, and scheduled workers. The human sits at the only decision point that matters.

```mermaid
flowchart TD
    A[Constitution: single source-of-truth document\nverified claims, banned phrases, formatting rules] --> B[Gates: reusable quality checks]
    B --> B1[Evidence check\nclaim-tier verification]
    B --> B2[Resume QA\n5-gate release pipeline]
    B --> B3[Voice gate\nanti-AI writing standard]
    B --> B4[Multi-persona review\nstakeholder-lens document review]
    B1 & B2 & B3 & B4 --> C[Scheduled agents]
    C --> C1[Job board scans\nsearch and score only, never apply]
    C --> C2[Content orchestrator\ndecides post, engage, or stay quiet]
    C --> C3[Inbox intelligence and dashboard\npipeline updates itself]
    C1 & C2 & C3 --> D[Human decision point\nevery send, post, and apply is manual]
```

Three properties fall out of this shape:

**Conflicts get adjudicated once.** When two documents disagree on a number, both freeze until the human rules, and the losing figure is retired permanently. No claim is ever re-litigated.

**Agents score, humans commit.** Every scheduled agent stops at a recommendation. Nothing applies, posts, or sends on its own.

**Writing has a release gate too.** Anything published runs through the voice standard and an AI-detection pass, the way code runs through CI.

See [CONSTITUTION.md](CONSTITUTION.md) for the laws, [TEMPLATES.md](TEMPLATES.md) for the gate prompts, and [MODULES.md](MODULES.md) for the roadmap.
