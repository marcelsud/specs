# Continuous Audit Specification

**Version:** `1.1.0`

## Status

- Status: Draft
- Applies to: automated and semi-automated discovery of gradeable issues in an existing codebase
- Depends on: [Grading Methodology](./grading-methodology.md) `1.1.0`
- Related: [Multi-Agent Review Agreement](./multi-agent-review-agreement.md) `1.0.0`
- Primary objective: produce a sustained supply of eligible, evidence-backed issues without
  re-discovering resolved findings and without fabricating work

## 1. Purpose

The Grading Methodology defines whether an issue is eligible and how valuable it is. It does
not define where issues come from. A project that grades well can still starve for input, and
an agent asked to "find bugs" on a healthy codebase will invent them rather than return empty.

This specification defines a repeatable audit loop that:

- examines one bounded topic per run rather than sweeping the whole repository;
- selects that topic from recorded history rather than from agent preference;
- requires reproduction before an issue may be filed;
- records every finding's disposition, including rejections, so the loop converges;
- treats a run that finds nothing as a successful run.

It is agent-agnostic and agent-driven: the agent is the top-level process and invokes a
project-supplied tool for every deterministic step (section 10). Any agent that can run a command
and write a file can conform, without a per-agent adapter.

## 2. Normative language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are
normative.

- **MUST** and **MUST NOT** define conditions for filing an issue or recording a run.
- **SHOULD** and **SHOULD NOT** require a written justification when ignored.
- **MAY** identifies an optional practice.

## 3. Core principles

### 3.1 One topic per run

A run MUST audit exactly one topic. Breadth is achieved across runs, not within them.

Sweeping many areas in a single run divides a fixed budget among them, and shallow coverage
produces findings that cannot satisfy IE-2. A single topic per run concentrates the budget
where reproduction becomes affordable.

### 3.2 A dry run is a successful run

A run that examines its topic and reports no findings MUST be recorded as a completed run and
MUST NOT be treated as a failure, retried for a different result, or escalated to a broader
scope.

This is the central anti-fabrication rule. Any process that treats an empty result as failure
creates pressure to manufacture findings, and manufactured findings are expensive: they consume
review capacity, they pass superficial inspection, and they are only disproved by the same
reproduction work that should have prevented them.

### 3.3 Evidence precedes filing

A candidate finding MUST NOT be filed as an issue until its reproduction has been executed **by
the tool** and observed to fail at the commit under audit (section 7.2). A reasoned argument that
a defect exists is not a reproduction, and neither is an agent's report of having run one.

### 3.4 The agent does not choose its own target

The topic under audit MUST be selected by the tool from recorded history and supplied to the
agent. An agent that selects its own target will drift toward areas it finds legible, and the
resulting coverage cannot be measured.

### 3.5 History is the only memory

The loop has no session continuity. Everything that must survive between runs — what was
audited, when, at which commit, and what was concluded — MUST be written to the ledger. A fact
not in the ledger does not exist for the next run.

## 4. Definitions

### 4.1 Topic

A named, bounded audit target consisting of an identifier, one or more paths, and one or more
identifiers from the consuming project's objective registry, as defined in section 4.8 of the
Grading Methodology.

A topic is a unit of attention, not a directory. It MAY span paths when the property under
examination spans them.

### 4.2 Run

A single execution of the loop: one topic selected, examined, and recorded. A run produces zero
or more filed issues and exactly one topic-history entry.

### 4.3 Candidate finding

A suspected defect identified during a run, before reproduction and grading. A candidate is not
a finding until it has been reproduced.

### 4.4 Fingerprint

A stable identifier for a finding's root cause, used for deduplication. Defined in section 8.1.

### 4.5 Disposition

The recorded conclusion for a candidate finding. One of:

| Disposition   | Meaning                                                                 |
| ------------- | ----------------------------------------------------------------------- |
| `filed`       | Reproduced, graded eligible, and filed as an issue                       |
| `duplicate`   | Matched an existing ledger entry or open issue                           |
| `not-current` | The condition does not exist at the audited commit; already resolved     |
| `unproven`    | Plausible but the reproduction did not demonstrate it                    |
| `ineligible`  | Reproduced, but failed the eligibility gate and could not be repaired    |

### 4.6 Dry run

A run whose candidate findings all resolve to a disposition other than `filed`, including a run
that produced no candidates.

## 5. Topic registry

The consuming project MUST maintain a topic registry. It SHOULD live in the project
configuration artifact defined in section 4.7 of the Grading Methodology, alongside the
objective registry the topics cite.

The identifiers below are illustrative. Objective identifiers are project-specific; this
specification does not define them.

```yaml
topics:
  - id: input-lifecycle
    paths: [src/inputs/]
    objectives: [DEL-1, CON-1]
  - id: shutdown-drain
    paths: [src/core/pipeline.ts, src/inputs/]
    objectives: [DEL-1]
  - id: gate-trustworthiness
    paths: [tests/]
    objectives: [CON-1]
```

Each entry MUST declare `id`, `paths`, and `objectives`. Every listed objective MUST exist in
the project's objective registry, as defined in section 4.8 of the Grading Methodology, so that
a finding under that topic can satisfy IE-7 by construction.

A topic whose objectives are absent from that registry MUST NOT be selected for a run: any
finding it produced would fail IE-7 after the reproduction had already been paid for.

Topics SHOULD be revised when the project's structure changes. A topic that has been audited
repeatedly at high churn without ever producing a finding SHOULD be re-examined: it is either
genuinely sound or framed too vaguely to audit.

## 6. Run selection

### 6.1 Weighting

The tool MUST select the topic by weighted random sampling, with weight:

```text
weight(topic) = staleness(topic) × (1 + churn(topic))

staleness(topic) = runs recorded since this topic was last audited
churn(topic)     = commits touching topic.paths since it was last audited
```

Uniform random selection MUST NOT be used. Uniform sampling revisits some topics repeatedly
before others are examined once, and it ignores the strongest available signal for where
defects are: recent change.

### 6.2 Determinism

The tool MUST record the random seed used for selection in the topic-history entry. Given
the same ledger, the same commit, and the same seed, selection MUST produce the same topic.

### 6.3 New topics

A topic with no history has undefined staleness and MUST be treated as maximally stale, so that
newly registered topics are audited before previously covered ones.

## 7. The audit run

### 7.1 Stages

A run MUST proceed in this order:

1. **Select** — the tool picks the topic (section 6), records the commit under audit, and opens
   the run.
2. **Examine** — the agent examines the topic's paths against its objectives and proposes
   candidate findings.
3. **Deduplicate** — the tool checks candidates against the ledger (section 8). Matches are
   recorded and dropped before any further work.
4. **Reproduce** — the tool runs each surviving candidate's reproduction (section 7.2).
5. **Grade** — each reproduced candidate is graded as an issue record (section 7.3).
6. **File** — the tool files candidates that passed grading.
7. **Record** — the tool appends all dispositions and one topic-history entry, closing the run.

Stages 3 through 7 are tool operations, invoked by the agent (section 10.1). Only stage 2 is the
agent's own work.

Deduplication MUST precede reproduction. Reproduction is the most expensive stage, and spending
it on a known finding is waste.

### 7.2 Reproduction gate

For each surviving candidate the agent MUST supply an **executable reproduction**: a command the
tool can run unattended at the commit under audit.

The tool MUST run that command itself and MUST NOT rely on output the agent reports. An agent
transcript is a claim about a reproduction, not the reproduction. Verifying independently is the
only mechanism in this specification that distinguishes a demonstrated defect from a plausible
argument for one.

The command MUST **fail** at the commit under audit. A reproduction that succeeds does not
demonstrate a defect; it demonstrates working software. This makes the gate mechanically
decidable, so no judgement is required to reject a candidate.

A candidate whose command does not run, or runs and succeeds, MUST be recorded as `unproven` or
`not-current` and MUST NOT be filed.

Evidence that would be produced identically by a correct implementation does not satisfy this
gate. A command that fails for a reason unrelated to the claim — a missing dependency, a syntax
error, an unrelated pre-existing failure — is not a reproduction.

This is deliberately narrower than IE-2, which also admits incidents, metrics, source invariants,
and benchmarks. Findings that cannot be expressed as a failing command are out of scope for an
automated run. That trades recall for precision, and the trade is intentional: an unattended loop
that files unverifiable findings consumes more review capacity than it creates.

### 7.3 Grading gate

Each reproduced candidate MUST be written as a complete issue record per section 5.4 of the
Grading Methodology and evaluated against the eligibility gate IE-1 through IE-9.

Where the consuming project provides an executable grader, the tool MUST use it and MUST
treat its output as authoritative. A candidate that does not reach the project's configured
minimum grade MUST be recorded as `ineligible` and MUST NOT be filed.

The agent MUST NOT weaken scope, consequence, or acceptance criteria in order to pass the gate.
An issue that only becomes eligible after its claim is broadened is `ineligible`.

## 8. Deduplication

### 8.1 Fingerprint

```text
fingerprint = sha256(
  lowercase(path) || NUL || consequence_category || NUL || normalized_claim
)
```

- `path` is the primary source path of the root cause.
- `consequence_category` is a canonical category from section 4.6 of the Grading Methodology.
- `normalized_claim` is a lowercase, whitespace-collapsed statement of the root cause, at most
  120 characters, supplied by the agent.

Line numbers MUST NOT contribute to the fingerprint. Line numbers drift with unrelated edits,
and a fingerprint that includes them re-files the same finding after any change to the file.

### 8.2 Two-stage matching

1. **Exact** — a candidate whose fingerprint matches a ledger entry MUST be recorded as
   `duplicate` without further work.
2. **Adjudicated** — a candidate that shares `path` and `consequence_category` with a ledger
   entry but has a different fingerprint MUST be adjudicated before filing: the agent is shown
   the prior entry and MUST state whether the root cause is the same.

A single-stage exact match alone is insufficient. Two agents describe the same defect
differently often enough that exact matching re-files known findings, while matching on path
alone suppresses genuinely distinct defects in the same file.

### 8.3 Re-audit eligibility

Prior dispositions constrain later runs:

| Prior disposition | May be re-filed later                                                |
| ----------------- | -------------------------------------------------------------------- |
| `filed`           | No, while the issue is open or its resolution stands                 |
| `duplicate`       | No                                                                   |
| `not-current`     | No, unless the entry's `path` has changed since `commit_audited`     |
| `unproven`        | Yes, with new evidence                                               |
| `ineligible`      | Yes, if the missing eligibility evidence can now be supplied         |

Deduplicating only against filed issues does not converge: rejected candidates carry no record,
so every run rediscovers, re-reproduces, and re-rejects them.

## 9. The ledger

### 9.1 Location

The ledger MUST be durable, versioned, and readable by every run. It SHOULD be stored outside
the project's main development branch so that appending to it does not require code review and
does not interact with the project's merge gates.

A dedicated data branch satisfies this. Storing the ledger on the main branch couples every
audit run to the project's review process; storing it outside version control forfeits the
history that makes dispositions auditable.

### 9.2 Topic history

One entry per run, appended in `topics.jsonl`:

```json
{
  "topic_id": "http-input-lifecycle",
  "run_id": "2026-07-26T03:07:00Z",
  "commit_audited": "1813260",
  "seed": 48219,
  "outcome": "completed",
  "candidates": 3,
  "filed": 1,
  "dispositions": { "filed": 1, "duplicate": 1, "unproven": 1 }
}
```

`outcome` MUST be `completed` or `failed`. A failed run MUST NOT be recorded as `completed`,
and its topic MUST retain its prior staleness. A crashed or non-conforming run that marks its
topic audited silently removes that topic from selection pressure.

### 9.3 Findings

One entry per candidate, appended in `findings.jsonl`:

```json
{
  "fingerprint": "9f2c…",
  "topic_id": "http-input-lifecycle",
  "run_id": "2026-07-26T03:07:00Z",
  "commit_audited": "1813260",
  "path": "src/inputs/http-input.ts",
  "consequence_category": "reliability",
  "normalized_claim": "request bodies buffered without a byte limit",
  "disposition": "filed",
  "reason": "reproduced at 8 MiB; returned 200 and admitted the message",
  "issue": 115
}
```

`reason` MUST be present for every disposition other than `filed`. A rejection without a
recorded reason cannot be re-audited correctly, because section 8.3 keys re-eligibility on why
the candidate was rejected.

### 9.4 Append rules

Ledger writes MUST be append-only. A correction MUST be recorded as a new entry that supersedes
the prior one, not as an edit. Runs MUST NOT rewrite history.

## 10. Invocation contract

### 10.1 Topology

The loop is **agent-driven**. The agent is the top-level process; the project provides a **tool**
the agent invokes for every deterministic step. Nothing spawns or supervises the agent.

The alternative — a harness that spawns agents and reads what they leave behind — requires
per-vendor adapters, subprocess supervision, and timeout and retry handling, none of which
concerns auditing. Inverting the control flow removes that category of work entirely, and any
agent able to run a command conforms without an adapter.

The tool MUST expose at least these operations:

| Operation | Responsibility                                                              |
| --------- | --------------------------------------------------------------------------- |
| `start`   | Select the topic (section 6), open a run, report topic, run identifier, seed |
| `check`   | Fingerprint, deduplicate (section 8), verify reproduction (7.2), grade (7.3) |
| `file`    | Create the issue for a candidate that passed `check`                         |
| `finish`  | Append the run's dispositions and topic-history entry, then close the run    |

Candidates are passed as files. That keeps the contract agent-agnostic: no part of it depends on
a tool vocabulary, session model, or orchestration framework.

### 10.2 The candidate artifact

A candidate MUST contain:

- the issue record required by section 5.4 of the Grading Methodology;
- the proposed issue body;
- an executable reproduction command (section 7.2);
- `path`, `consequence_category`, and `normalized_claim` for fingerprinting.

### 10.3 Separation of authority

**The agent decides what to examine and what to claim. The tool decides what is allowed to leave
the machine.**

Every effect observable outside the run — creating an issue, writing the ledger — MUST be
performed by the tool and MUST be gated on state the tool itself recorded.

In particular, `file` MUST refuse any candidate that has not passed `check` **within the current
run**, and MUST determine that from its own records rather than from anything the agent asserts.

An agent-driven loop cannot assume a cooperative agent. An agent that skipped verification, or
that believes it already verified, is indistinguishable from one that did — unless the gate is
enforced by state the agent does not author.

### 10.4 Run integrity

A run that begins MUST be accounted for, including when the agent crashes, is interrupted, or
abandons it.

The tool MUST record the outcome of every started run. Because no process supervises the agent,
it MUST detect an abandoned run — one started and never finished — and record it as
`outcome: failed` before opening a new one.

An abandoned run MUST NOT be recorded as `completed`, and its topic MUST retain its prior
staleness. An agent that terminated without finishing is indistinguishable, from the ledger's
point of view, from one that examined the topic and found nothing — but recording the former as
completed marks the topic audited, removes it from selection pressure, and silently creates a
permanent coverage hole.

### 10.5 Agent conformance

A conforming agent MUST:

- audit only the topic reported by `start`;
- supply an executable reproduction rather than a description of one;
- submit every candidate through `check`;
- invoke `finish` for the run, including when it has no findings;
- create no issue, branch, or ledger entry by any means other than the tool.

Reporting no findings is conformant and successful (section 3.2).

## 11. Scheduling

The loop SHOULD run on a schedule proportional to the project's change rate. Because each run
audits one topic, cadence and coverage are independent: coverage is a function of run frequency
divided by topic count.

The schedule MUST survive the termination of any individual session. A scheduler bound to an
interactive session's lifetime does not satisfy this.

An audit MAY additionally be triggered on demand, and a topic MAY be named explicitly for such
a run. An explicitly named topic MUST still record a topic-history entry.

## 12. Relationship to other specifications

- **Grading Methodology `1.1.0`** — supplies the eligibility gate (IE-1..IE-9), severity, value
  grades, consequence categories, and the issue record. This specification adds only the
  conditions under which a candidate may reach that gate.
- **Multi-Agent Review Agreement `1.0.0`** — governs review of the pull requests that resolve
  filed issues. It does not apply to audit runs: the severity gate and two-round cap concern
  convergence between reviewers, whereas an audit run has no counterparty.

This specification defines issue **supply**. It does not define how filed issues are
implemented, reviewed, or merged.
