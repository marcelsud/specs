# Grading Methodology Specification

**Version:** `1.1.0`

## Status

- Status: Draft
- Rubric version: `1.1.0`
- Applies to: issues, pull requests, review consensus, and release quality
- Primary objective: make code-quality decisions repeatable without rewarding cosmetic work or subjective nitpicking

## 1. Purpose

This specification defines how Cascade determines whether proposed work makes
the project better or worse. It converts independently answered binary checks
into grades instead of asking reviewers to grade an overall impression.

The methodology must:

- reward work with demonstrated value;
- prevent a valuable issue from hiding a poor implementation;
- identify material code-quality liabilities without grading style preferences;
- use machine-enforced ratchets wherever a tool can answer reliably;
- require two independent reviewers to agree on the ship decision and its evidence;
- make every non-trivial grade explainable from stored facts;
- improve or preserve project health at every release.

## 2. Normative language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and
**MAY** are normative.

- **MUST** and **MUST NOT** define merge or release gates.
- **SHOULD** and **SHOULD NOT** require a written justification when ignored.
- **MAY** identifies an optional practice.

## 3. Core principles

### 3.1 Binary checks produce grades

Reviewers answer evidence-backed yes/no questions. Grade calculation is
mechanical. A reviewer MUST NOT select a letter first and reverse-engineer the
checklist afterward.

### 3.2 Eligibility is not value

A well-written issue is gradeable, but not necessarily valuable. Issue
eligibility and issue value are evaluated separately.

### 3.3 Issue value is not implementation quality

Every PR has separate grades:

- **Issue grade**: the justified value of doing the work.
- **Execution grade**: the quality of the implementation.
- **Overall PR grade**: the worse of the issue and execution grades.

An A-grade issue does not make its PR A automatically.

### 3.4 Ship safety is not negotiable through grading

Grades do not override hard ship gates. A PR with a failed hard gate is
`REWORK`, not a mergeable low-grade PR.

### 3.5 Only consequential slop counts

A slop finding MUST identify at least one concrete consequence from the
canonical categories in section 4.6. Style, naming preference, and
alternative-but-equivalent formulations do not count.

### 3.6 Existing debt is a baseline, not an excuse

A PR is responsible for debt it introduces or worsens. It is not required to
repair unrelated baseline debt. When it touches an existing hotspot, it MUST
not make the measured condition worse without an approved exception.

## 4. Definitions

### 4.1 Finding severity

- **Blocker**: factually wrong behavior, security exposure, data-loss risk, or
  another condition that makes merging or releasing unsafe.
- **Material**: information that would change a reasonable merge, design, or
  operational decision.
- **Cosmetic**: a preference or refinement that would not change a reasonable
  decision.

Only Blocker and Material findings participate in the ship gate. Cosmetic
findings MUST be omitted from grading and consensus.

### 4.2 Grade order

From best to worst:

```text
A > B > C > D
```

`UNGRADED` is a state, not a grade. It means required information or evidence
is missing.

Throughout this specification, `worse(grades...)` returns the lowest of its
arguments according to this order. Each argument MUST be a grade from A
through D; with no arguments, it returns A as the identity value. `UNGRADED`
MUST block calculation rather than be passed to `worse`.

### 4.3 Slop

Slop is a new or worsened code liability that adds maintenance or operational
cost without proportionate capability, safety, or evidence.

### 4.4 Ratchet

A ratchet is a machine-enforced quality condition compared with the merge base
or another versioned baseline. It may remain equal or improve, but may not
worsen without an approved exception.

### 4.5 Release

A release is the set of PRs included since the previous published release or
another explicitly recorded baseline commit.

### 4.6 Canonical consequence categories

Every rule that requires a concrete consequence MUST use one or more of these
categories:

- correctness or data integrity;
- reliability;
- security or privacy;
- operability or observability;
- testing or test trust;
- maintenance or ownership cost.

Equivalent wording MAY be used in a finding, but its evidence MUST map to at
least one category above. A preference that cannot be mapped does not count.

### 4.7 Project configuration

A project adopting this methodology MUST publish a configuration artifact
declaring its rubric version, its objective registry, and its ratchet
configuration. Section 10.1 already requires thresholds and exclusions to be
versioned in repository configuration; this section names that artifact and
fixes its required contents.

The artifact MUST be versioned alongside the code it grades and MUST be
readable by both reviewers and automated checks. Its location and file format
are a project choice. This specification does not assume a hosting platform,
directory layout, or configuration language.

```yaml
rubric_version: 1.1.0

objectives:
  DEL-1: >-
    Delivery guarantees: documented delivery paths hold across the full
    system boundary.
  CON-1: >-
    Documented component contracts behave as documented.

ratchets:
  RT-1:
    check: "<command>"
    enforcement: ci-blocking
```

### 4.8 Objective registry

The objective registry is the set of objectives declared in the project
configuration. Each objective MUST declare a stable identifier and a statement
of the guarantee it protects.

- IE-7 is satisfied by citing an identifier present in the registry at the time
  of grading, or by the D path in section 5.1.
- An issue citing an identifier absent from the registry does not satisfy IE-7.
- Identifiers MUST be stable. A retired objective's identifier MUST NOT be
  reused for a different guarantee, because stored grade records cite it and
  those records are expected to remain explainable.
- Adding, retiring, or restating an objective is a policy change and MUST
  follow the same separate-review rule as section 10.1.

The registry is project-specific by construction. This specification defines
what an objective is and how it is cited; it does not enumerate objectives.

## 5. Issue grading

Issue grading occurs during triage, before implementation review.

### 5.1 Issue eligibility gate

Every check requires `yes` and cited evidence. Any `no` result makes the issue
`UNGRADED` and prevents it from authorizing a non-exempt PR.

| ID   | Binary check                                                                                          | Required evidence                                                            |
| ---- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| IE-1 | Is the problem or opportunity stated without prescribing an unverified implementation?                | Issue summary                                                                |
| IE-2 | Is there direct evidence?                                                                             | Reproduction, incident, metric, user request, source invariant, or benchmark |
| IE-3 | Is the consequence stated, including an explicit `none` for a non-consequential request?              | Consequence evidence, or a cited request with `consequence: none`            |
| IE-4 | Is the scope bounded?                                                                                 | Explicit in-scope and out-of-scope boundaries                                |
| IE-5 | Are completion criteria binary and observable?                                                        | Acceptance criteria                                                          |
| IE-6 | Is the required regression proof identified?                                                          | Test, check, benchmark, or runtime observation                               |
| IE-7 | Is the work tied to a current objective, or is it a recorded administrative request using the D path? | Objective identifier from the registry (section 4.8), or request link        |
| IE-8 | Is a 2–3 sentence grade rationale present?                                                            | `Grade rationale` section                                                    |
| IE-9 | Has duplicate or intentional-overlap status been checked?                                             | Search result or linked related issue                                        |

The rationale MUST answer:

1. Why does this matter now?
2. What material decision or outcome changes if it is resolved, or why does
   none change for a D candidate?
3. Why does the selected value grade follow from the rules below?

IE-3 MUST NOT be satisfied by a fabricated impact. A request with no material
consequence MAY record `consequence: none` and cite the underlying request.
That request MAY also satisfy IE-7 without a broader objective. These
alternatives are available only through the D path and force issue grade D
when the remaining eligibility checks pass.

### 5.2 Issue severity

Severity is recorded independently from value grade:

```yaml
severity: blocker | material | cosmetic
```

A feature or debt item may be Material when its evidence would change a
reasonable product, design, or operational decision, even if it is not a bug.

### 5.3 Issue value-grade decision tree

Apply the first matching rule:

1. **D**: The outcome is cosmetic, preference-driven, administrative, or has
   no measurable capability, safety, reliability, or maintenance consequence.
2. **C**: The outcome removes measurable and bounded maintenance or test debt,
   but does not change a user-visible, operational, security, correctness, or
   release decision.
3. **A**: The issue is eligible and any of the following is true:
   - it addresses a Blocker;
   - it protects or restores a core documented guarantee;
   - it affects two or more independent components or user flows;
   - it repairs a project-wide release, security, reliability, or test-trust gate;
   - it is explicitly designated as a release-critical objective with an
     observable outcome.
4. **B**: The issue is eligible and Material, but its demonstrated effect is
   localized and no A rule applies.

An issue MUST NOT receive A solely because it is clearly written, large, or
difficult.

### 5.4 Required issue record

```yaml
rubric_version: 1.1.0
eligibility:
  IE-1: { answer: yes, evidence: "Problem section" }
  IE-2: { answer: yes, evidence: "Reproduction output" }
  IE-3: { answer: yes, evidence: "Impact section" }
  IE-4: { answer: yes, evidence: "Scope section" }
  IE-5: { answer: yes, evidence: "Acceptance criteria" }
  IE-6: { answer: yes, evidence: "Regression test plan" }
  IE-7: { answer: yes, evidence: "Reliability objective R-2" }
  IE-8: { answer: yes, evidence: "Grade rationale" }
  IE-9: { answer: yes, evidence: "No duplicate found" }
severity: material
issue_grade: A
grade_rationale: >-
  This restores an at-least-once delivery guarantee and prevents acknowledged
  messages from being lost after downstream failure. The behavior is a core
  reliability invariant and has a deterministic reproduction.
```

The grade label SHOULD be computed from this record. A manually applied label
without the record is not authoritative.

## 6. Pull request linkage and exemptions

### 6.1 Required linkage

Every non-trivial PR MUST link exactly one primary graded issue. Additional
issues MAY be linked as secondary scope.

All behavioral changes in the diff MUST trace to the primary issue acceptance
criteria or to documented supporting work required to satisfy them.

If the PR discovers additional independent work, that work MUST be removed or
moved to another issue and PR.

### 6.2 Exempt PR classes

The following MAY be issue-exempt when explicitly labeled:

- clean revert;
- emergency containment;
- automated dependency metadata update with no runtime behavior change;
- administrative repository change;
- release metadata generated from already graded work.

An exemption MUST state why normal issue grading is inapplicable. It does not
skip hard ship gates. Emergency containment MUST receive a follow-up graded
issue before the next release is approved.

An unlinked, non-exempt PR is `UNGRADED` and blocked.

## 7. Hard PR ship gate

Both reviewers answer every check independently. Any `no` result produces
`REWORK`; no execution grade is issued until the failure is resolved.

| ID    | Binary check                                                                        |
| ----- | ----------------------------------------------------------------------------------- |
| SG-1  | Is the primary issue eligible and graded, or is a valid exemption recorded?         |
| SG-2  | Does every behavioral diff segment trace to issue scope?                            |
| SG-3  | Is every acceptance criterion proven by cited evidence?                             |
| SG-4  | Are correctness, security, data-integrity, and resource-bound invariants preserved? |
| SG-5  | Do tests exercise the changed behavior and its material failure path?               |
| SG-6  | Were no tests, assertions, type checks, or CI gates weakened to obtain a pass?      |
| SG-7  | Are all Blocker and Material review findings resolved?                              |
| SG-8  | Do all non-exempt machine ratchets pass?                                            |
| SG-9  | Is the slop ledger complete and evidence-backed?                                    |
| SG-10 | Does the PR contain no S3 slop?                                                     |

Passing CI alone does not prove SG-3, SG-4, or SG-5. Reviewers MUST inspect
whether the evidence covers the stated behavior.

## 8. Execution grading

Execution grading occurs only after all hard ship gates pass.

### 8.1 Execution evidence checks

| ID   | Binary check                                                                                            |
| ---- | ------------------------------------------------------------------------------------------------------- |
| EX-1 | Is the implementation the smallest coherent change that satisfies the issue without unrelated behavior? |
| EX-2 | Does the implementation use existing boundaries and capabilities where appropriate?                     |
| EX-3 | Are public contracts, failure semantics, and lifecycle behavior explicit?                               |
| EX-4 | Do regression tests fail for the pre-change defect or otherwise prove the new capability?               |
| EX-5 | Are tests behavioral rather than assertions of construction, key presence, or line execution only?      |
| EX-6 | Does the implementation avoid new unbounded work, hidden side effects, and silent failure?              |
| EX-7 | Are introduced dependencies and abstractions justified by a current consumer or boundary?               |
| EX-8 | Is observability added or preserved where the changed failure mode requires it?                         |
| EX-9 | Are documentation and examples consistent with the implemented contract?                                |

### 8.2 Mechanical execution grade

After the hard gate passes:

- **A**: EX-1 through EX-9 are `yes`; no S1, S2, or S3 is added; all ratchets
  pass without exception.
- **B**: all hard gates pass; no S2 or S3 is added; one or more S1 entries are
  justified, owned, and linked to follow-up work. Every `no` EX answer MUST
  correspond to one of those S1 entries; an unclassified `no` cannot be used
  to derive a grade.
- **C**: all hard gates pass; no S3 is added; at least one S2 entry or ratchet
  exception is explicitly approved and linked. Every `no` EX answer MUST
  correspond to an approved S1 or S2 entry, and all behavior remains proven.
- **D execution**: the change requires an emergency policy exception that
  cannot satisfy the normal execution floor. It MUST NOT be merged through the
  ordinary workflow and caps project health at D until resolved.

Multiple weak observations MUST NOT be accumulated into a grade penalty unless
each independently qualifies as S1 or higher.

An `EX=no` answer that cannot be classified as S1 or S2 produces `REWORK`.
No execution grade is issued until the implementation makes the answer `yes`
or the reviewer records a qualifying, evidence-backed S1 or S2 entry. An S3
classification fails the hard ship gate.

### 8.3 Overall PR grade

For ordinary PRs:

```text
overall_pr_grade = worse(issue_grade, execution_grade)
```

Examples:

| Issue | Execution | Overall PR |
| ----- | --------- | ---------- |
| A     | A         | A          |
| A     | B         | B          |
| B     | A         | B          |
| C     | A         | C          |
| D     | A         | D          |

A D overall grade may be mergeable when it results from a D-value issue and
the execution grade passes the normal floor. A D execution grade is not
ordinarily mergeable.

## 9. Slop ledger

### 9.1 Slop tiers

| Tier | Definition                                                                         | Policy                                              |
| ---- | ---------------------------------------------------------------------------------- | --------------------------------------------------- |
| S3   | New correctness, security, data-loss, privacy, or unbounded-resource exposure      | Blocks ordinary merge; cannot be waived             |
| S2   | Material reliability, test, coupling, type-safety, dependency, or maintenance debt | Requires approved exception and caps execution at C |
| S1   | Bounded local compromise with a concrete consequence                               | Requires owner and follow-up; caps execution at B   |
| S0   | Cosmetic preference or equivalent formulation                                      | Excluded from reviews and grades                    |

### 9.2 Countable slop categories

A finding counts only when the answer to both questions is `yes`:

1. Is a liability newly introduced or measurably worsened by this PR?
2. Can the reviewer map its concrete consequence to at least one canonical
   category from section 4.6?

Countable categories include:

- dead or unreachable code;
- duplicated business logic that can diverge;
- unchecked type escape such as unjustified `any`, ignored diagnostics, or
  unsafe assertion at a trust boundary;
- swallowed or misclassified error;
- unbounded retry, queue, request, memory, concurrency, or lifecycle behavior;
- implicit or contradictory public contract, failure semantic, or lifecycle
  behavior with a concrete consequence;
- missing or misleading observability for a material failure mode;
- weakened assertion or test that no longer proves the contract;
- dependency duplicating an existing capability with measurable ownership,
  security, size, or runtime cost;
- public abstraction with no current consumer, external contract, test seam,
  or architectural boundary;
- hidden side effect or behavior outside the primary issue scope;
- placeholder, compatibility shim, or temporary branch with no removal path.

### 9.3 Excluded signals

The following do not independently count as slop:

- comment wording;
- naming or formatting preference;
- raw lines changed;
- file length alone;
- a one-caller abstraction with a demonstrated boundary purpose;
- duplication percentage without an identified duplicated business rule;
- complexity score that remains below the configured ceiling;
- preference for extraction over local duplication, or the reverse, without a
  concrete divergence or coupling consequence.

These MAY trigger inspection but MUST NOT affect a grade without qualifying
evidence.

### 9.4 Required slop entry

```yaml
tier: S1
category: bounded_workaround
location: src/example.ts:42
consequence: "A second protocol implementation could classify the error differently."
introduced_by: "PR #123"
justification: "The shared boundary is outside the bounded issue scope."
disposition: follow_up
owner: "@owner"
follow_up_issue: "#124"
target_release: "next"
```

No `file:line`, no consequence, or no introduction evidence means no slop flag.

### 9.5 Slop delta

PRs and releases report counts by tier rather than a single weighted score:

```yaml
slop_delta:
  added: { S3: 0, S2: 0, S1: 1 }
  removed: { S3: 0, S2: 2, S1: 0 }
```

Higher-tier debt MUST NOT be numerically canceled by removing many lower-tier
items.

## 10. Machine ratchets

### 10.1 Baseline

Ratchets compare the PR head with its merge base. Release ratchets compare the
release candidate with the previous release baseline.

Thresholds and exclusions MUST be versioned in the project configuration
artifact defined in section 4.7. Changing the baseline or exclusion list
requires a separately reviewed policy change and MUST NOT be hidden inside a
feature PR.

### 10.2 Required ratchets

| ID   | Machine check              | Pass condition                                                                                       |
| ---- | -------------------------- | ---------------------------------------------------------------------------------------------------- |
| RT-1 | Build and type safety      | No new build, lint, or type error relative to baseline                                               |
| RT-2 | Test integrity             | No new skipped, focused-only, quarantined, or ignored failing test                                   |
| RT-4 | Coverage floor             | Changed scope meets its configured floor and project/package coverage does not cross below its floor |
| RT-5 | Complexity ceiling         | No touched function newly crosses the ceiling; existing hotspot does not worsen                      |
| RT-6 | Duplicate-rule signal      | No new duplicated block is accepted without reviewer classification and evidence                     |
| RT-7 | Dependency policy          | Every new runtime dependency has capability, ownership, and security justification                   |
| RT-8 | Public contract validation | Public configuration/API changes have schema, compatibility, docs, and behavioral tests              |

`RT-3` is intentionally unused in rubric 1.1.0. Behavioral proof is evaluated
by reviewers under SG-5 because a tool cannot determine whether assertions
prove the intended contract. Tools MAY emit test-execution evidence for SG-5,
but that evidence is not itself a machine ratchet.

Coverage percentage and duplication percentage are signals, not proof of test
quality or design quality.

### 10.3 Ratchet exceptions

An exception MUST record:

- failed ratchet ID;
- measured before/after values;
- why satisfying the ratchet would create greater material risk;
- owner;
- follow-up issue;
- target release;
- approving reviewers.

An approved ratchet exception caps execution at C. An expired exception blocks
the next release. RT-1, RT-2, and S3 protections cannot be waived through the
ordinary exception process.

## 11. Two-reviewer consensus protocol

### 11.1 Independent first pass

Both reviewers receive the same frozen inputs:

- issue body and authoritative issue-grade record;
- PR diff and merge-base SHA;
- CI and ratchet output;
- acceptance criteria and test evidence;
- rubric version.

Each reviewer completes the full structured review independently before seeing
the other review.

### 11.2 Required reviewer output

```yaml
rubric_version: 1.1.0
reviewer: reviewer-id
issue_grade: A
ship_gate:
  SG-1: { answer: yes, evidence: "Issue #29" }
  SG-2: { answer: yes, evidence: "All diff paths map to AC-1 or AC-2" }
  SG-3: { answer: yes, evidence: "redis-streams-input.test.ts" }
  SG-4: { answer: yes, evidence: "ACK remains pending on send failure" }
  SG-5: { answer: yes, evidence: "Failure-path integration test" }
  SG-6: { answer: yes, evidence: "No weakened tests or checks" }
  SG-7: { answer: yes, evidence: "No open Blocker/Material findings" }
  SG-8: { answer: yes, evidence: "Ratchet check URL" }
  SG-9: { answer: yes, evidence: "Slop ledger reviewed" }
  SG-10: { answer: yes, evidence: "S3 added = 0" }
execution_checks:
  EX-1: yes
  EX-2: yes
  EX-3: yes
  EX-4: yes
  EX-5: yes
  EX-6: yes
  EX-7: yes
  EX-8: yes
  EX-9: yes
slop_delta:
  added: { S3: 0, S2: 0, S1: 0 }
  removed: { S3: 1, S2: 0, S1: 0 }
findings: []
execution_grade: A
overall_pr_grade: A
decision: APPROVED
```

Every Blocker or Material finding MUST include:

- severity;
- violated rubric or acceptance-criterion ID;
- `file:line` or external evidence;
- concrete consequence;
- binary resolution condition.

### 11.3 Consensus requirements

Consensus requires all of the following:

- same `APPROVED` or `REWORK` decision;
- same answer for every SG check;
- no unresolved Blocker or Material finding from either reviewer;
- same issue grade;
- same execution grade;
- compatible slop entries and tiers.

Matching letters alone do not constitute consensus.

### 11.4 Disagreement resolution

1. Compare only the disagreeing binary checks and evidence.
2. Each reviewer cites the exact rubric clause supporting the answer.
3. Verify disputed factual claims against source, tests, or runtime evidence.
4. Discard Cosmetic disagreements.
5. Update the artifact or finding once for Blocker/Material corrections.
6. The second review round verifies that the correction landed.

If a hard-gate disagreement remains, the PR stays blocked for bounded human
adjudication. The lower grade does not win automatically. The adjudicator MUST
record the decisive fact and clause.

There is no third review round unless a genuine Blocker is discovered.

Final ship-gate question:

> Any Blocker or Material issue? If no → APPROVED.

## 12. Project and release grading

Project health measures code quality. It uses execution grades, ratchets, open
material debt, test trust, and slop delta. It does not use issue value as a
proxy for code health.

Issue and overall PR grades are reported separately as the delivery-value
portfolio.

### 12.1 Project health grade

Apply the first matching rule:

1. **D** when any condition holds:
   - an open release-relevant Blocker exists;
   - S3 debt exists;
   - a required release gate is known to produce false positives or cannot run;
   - an emergency D-execution PR remains unresolved.
2. **C** when no D condition holds and any condition holds:
   - the release adds net S2 debt;
   - a ratchet exception is active;
   - an S1 or S2 follow-up has expired;
   - a C execution PR is included.
3. **B** when no D or C condition holds and:
   - all required ratchets pass;
   - no Blocker or S3 debt exists;
   - S2 debt is neutral;
   - included execution grades are A or B.
4. **A** when all B conditions hold and:
   - the release reduces S2 debt, or the baseline contains no S2 debt;
   - no S1 introduced by the release remains present at the release baseline;
   - no required check depends on a known weak or false-positive assertion;
   - all included execution grades are A.

One high-grade PR cannot numerically hide a Blocker or S3 condition.

### 12.2 Delivery-value portfolio grade

The delivery-value portfolio grade is the worst overall PR grade among
non-exempt PRs included in the release:

```text
release_portfolio_grade = worse(included_overall_pr_grades...)
```

Equivalently:

- **A**: every included overall PR grade is A;
- **B**: at least one B is included and no C or D is included;
- **C**: at least one C is included and no D is included;
- **D**: at least one D is included.

This grade measures the value/quality portfolio selected for the release. It
does not replace the project health grade.

### 12.3 Release reporting and current project grade

```text
current_project_grade = project_health_grade
```

The delivery-value portfolio grade MUST be reported alongside project health,
but MUST NOT be combined with it or used as a proxy for code quality. This
keeps B/C/D-value work visible without treating a well-executed lower-value PR
as a project-health regression.

Every release reports its distribution and derived grades:

```yaml
release: 0.7.0
overall_pr_grades: { A: 7, B: 2, C: 1, D: 0 }
execution_grades: { A: 9, B: 1, C: 0, D: 0 }
slop_delta:
  added: { S3: 0, S2: 0, S1: 1 }
  removed: { S3: 0, S2: 3, S1: 2 }
exceptions: { active: 0, expired: 0 }
project_health_grade: A
release_portfolio_grade: C
current_project_grade: A
```

GPA MAY be displayed as a secondary summary, but MUST NOT determine the project
health or portfolio grade or override their ceilings.

### 12.4 Release ratchet

A release MUST NOT reduce the project health grade without an explicit release
exception. The exception MUST name the material reason, affected grade rule,
owner, and recovery issue. The delivery-value portfolio grade is reported but
is not ratcheted.

An exception records regression; it does not redefine the lower grade as a
higher one.

## 13. GitHub integration contract

### 13.1 Issue fields

Issue templates SHOULD contain:

- objective;
- evidence;
- consequence;
- scope and non-scope;
- acceptance criteria with stable IDs;
- regression-proof plan;
- duplicate search;
- severity;
- grade rationale;
- machine-readable grading record.

Suggested computed labels:

```text
grading:eligible
severity:blocker | severity:material | severity:cosmetic
issue-grade:A | issue-grade:B | issue-grade:C | issue-grade:D
```

### 13.2 PR fields

PR templates SHOULD contain:

- `Closes #<primary-issue>`;
- acceptance-evidence mapping;
- behavioral and failure-path test evidence;
- slop added/removed ledger;
- ratchet exceptions;
- author-proposed execution grade with derived rationale.

The author proposal is not authoritative. Reviewer consensus and automated
calculation produce the final grade.

### 13.3 Required checks

```text
grading/issue-eligibility
grading/issue-value
grading/ratchets
grading/reviewer-consensus
grading/final-grade
```

The final check MUST recompute the grade from stored binary answers. It MUST
reject manually inconsistent letter grades.

## 14. Examples

### 14.1 A issue, A execution

- A data-loss defect has a deterministic reproduction and restores a core
  delivery guarantee.
- The PR defers acknowledgement, adds a regression test for downstream failure,
  and adds no slop.
- Result: issue A, execution A, overall A.

### 14.2 A issue, B execution

- The issue remains A.
- The implementation requires one bounded S1 workaround with owner and
  follow-up.
- Result: issue A, execution B, overall B.

### 14.3 C issue, A execution

- The issue removes measured local test debt without material runtime impact.
- The implementation is minimal, fully proven, and adds no slop.
- Result: issue C, execution A, overall C.
- Project health uses execution A; the delivery portfolio records overall C.

### 14.4 Cosmetic request

- The only justification is that one naming or formatting form is preferred.
- IE-2 cites the request; IE-3 records `consequence: none`; the rationale states
  that no material decision or outcome changes.
- Result: eligible issue D if the remaining eligibility checks pass.
- Cosmetic review comments remain excluded from the ship gate.

### 14.5 Orphan PR

- A non-exempt PR has no primary graded issue.
- SG-1 is `no`.
- Result: `UNGRADED`, `REWORK`, blocked.

### 14.6 CI passes but test is weak

- A test asserts that an `apiResponse` key exists but accepts `{}` when the
  contract requires populated response data.
- SG-5 or EX-5 is `no` because the behavior is not proven.
- Result: `REWORK` even though coverage and CI are green.

## 15. Governance and calibration

### 15.1 Versioning

Every issue and PR grading record MUST store the rubric version used. Rubric
changes apply prospectively unless a migration is explicitly approved.

### 15.2 Calibration

At each release boundary, reviewers SHOULD independently regrade a small fixed
sample of previously merged PRs without seeing their original grades.

Calibration examines:

- disagreement frequency by binary-check ID;
- checks repeatedly requiring adjudication;
- false-positive and false-negative ratchets;
- unsupported slop flags;
- grade overrides and their decisive evidence;
- open and expired debt entries.

Rubric wording changes only when a repeated disagreement reveals an ambiguous
decision rule. A one-off preference disagreement is not sufficient.

### 15.3 No moving the goalposts during review

The rubric version is frozen when substantive PR review begins. If the review
uncovers a methodology defect, adjudicate the current PR under the frozen
version and update the rubric separately for future work.

### 15.4 Auditability

The repository MUST retain enough information to reconstruct:

- why an issue received its grade;
- which acceptance evidence authorized a merge;
- what slop was introduced or removed;
- why an exception was approved;
- how the two reviewers reached consensus;
- how the release health grade was derived.

## 16. Implementation sequence

1. Adopt the issue template and eligibility/value calculator.
2. Add the PR evidence, slop, and exception sections.
3. Implement merge-base ratchet checks without enforcing historical debt repair.
4. Run two-reviewer structured grading in report-only mode and collect
   disagreement data.
5. Correct ambiguous binary checks using observed disagreements.
6. Enable issue linkage, hard ship gates, and reviewer-consensus enforcement.
7. Publish the first project-health baseline and apply the release ratchet.

The methodology is successful when reviewers mostly disagree about verifiable
facts rather than taste, every grade can be recomputed, and each release either
preserves or improves the explicit project-health state.
