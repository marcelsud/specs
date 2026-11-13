"""Finite semantic validation of grading-methodology.md section 12.1.

Run: python validation/grading_health.py --baseline-ref <1.1.0 commit>

This is a review aid, not a production grading service. It reads the grade
order and S2 comparison from both documents, then evaluates their predicates
over concrete release facts. Reviewers must check the predicate-to-prose
mapping below. Unknown decision-tree forms fail rather than being guessed.
No project configuration, stored grade, or consumer policy is modified.
"""

import argparse
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import re
import subprocess


@dataclass(frozen=True)
class Facts:
    baseline_s2: int = 0
    candidate_s2: int = 0
    release_blocker: bool = False
    other_blocker: bool = False
    s3: bool = False
    release_gate_false_positive: bool = False
    release_gate_unavailable: bool = False
    unresolved_d_execution: bool = False
    ratchet_exception: bool = False
    expired_s1: bool = False
    expired_s2: bool = False
    executions: tuple = ("A",)
    ratchets_pass: bool = True
    new_s1_remaining: int = 0
    old_s1_remaining: int = 0
    required_check_weak: bool = False


def section(document):
    return document.split("### 12.1 Project health grade\n", 1)[1].split(
        "### 12.2 Delivery-value portfolio grade", 1
    )[0]


class DecisionTree:
    def __init__(self, document):
        self.text = section(document)
        self.order = re.findall(r"^\d\. \*\*([ABCD])\*\* when", self.text, re.M)
        self.corrected = self.order == ["D", "C", "A", "B"]
        if self.corrected:
            assert "S2 debt is neutral or reduced relative to the release baseline;" in self.text
            assert "**A** when all common conditions hold and:" in self.text
            assert "**B** when all common conditions hold but at least one additional A" in self.text
            assert "no S1 introduced by the release remains present at the release candidate;" in self.text
        else:
            assert self.order == ["D", "C", "B", "A"], self.order
            assert "S2 debt is neutral;" in self.text
            assert "**A** when all B conditions hold and:" in self.text

    def assess(self, facts):
        f = facts
        # Section 12.1 D: any release blocker, S3, unreliable/unavailable
        # required release gate, or unresolved emergency D execution.
        d = any((f.release_blocker, f.s3, f.release_gate_false_positive,
                 f.release_gate_unavailable, f.unresolved_d_execution))
        # Section 12.1 C: no D, then any net S2 addition, active ratchet
        # exception, expired S1/S2 follow-up, or included C execution.
        c = not d and any((f.candidate_s2 > f.baseline_s2, f.ratchet_exception,
                           f.expired_s1, f.expired_s2, "C" in f.executions))
        s2_floor = (f.candidate_s2 <= f.baseline_s2 if self.corrected
                    else f.candidate_s2 == f.baseline_s2)
        common = (not d and not c and f.ratchets_pass
                  and not (f.release_blocker or f.other_blocker or f.s3)
                  and s2_floor and all(g in ("A", "B") for g in f.executions))
        # The 1.1.0 A clause also depends on B; it is never reached after B.
        a = (common and (f.candidate_s2 < f.baseline_s2 or f.baseline_s2 == 0)
             and f.new_s1_remaining == 0 and not f.required_check_weak
             and all(g == "A" for g in f.executions))
        b = common and (not a if self.corrected else True)
        answers = {"D": d, "C": c, "A": a, "B": b}
        return next((g for g in self.order if answers[g]), None)


# Each expected result is a concrete observable decision, not a text match.
CASES = [
    ("A with no baseline S2", {}, "A"),
    ("A with reduced residual S2", {"baseline_s2": 3, "candidate_s2": 2}, "A"),
    ("A after removing all S2", {"baseline_s2": 1}, "A"),
    ("B with neutral existing S2", {"baseline_s2": 2, "candidate_s2": 2}, "B"),
    ("B with B execution", {"executions": ("A", "B")}, "B"),
    ("B with a remaining new S1", {"new_s1_remaining": 1}, "B"),
    ("B after S2 reduction but new S1 remains", {"baseline_s2": 2,
      "candidate_s2": 1, "new_s1_remaining": 1}, "B"),
    ("A permits nonexpired baseline S1", {"old_s1_remaining": 1}, "A"),
    ("A after release-introduced S1 is removed", {"new_s1_remaining": 0}, "A"),
    ("B with weak non-release required check", {"required_check_weak": True}, "B"),
    ("C on net S2 addition", {"candidate_s2": 1}, "C"),
    ("C on active ratchet exception", {"ratchet_exception": True}, "C"),
    ("C on expired S1 follow-up", {"expired_s1": True}, "C"),
    ("C on expired S2 follow-up despite reduction", {"baseline_s2": 2,
      "candidate_s2": 1, "expired_s2": True}, "C"),
    ("C with C execution", {"executions": ("A", "C")}, "C"),
    ("D on release-relevant blocker", {"release_blocker": True}, "D"),
    ("D on S3 despite S2 removal", {"s3": True, "baseline_s2": 2}, "D"),
    ("D on false-positive release gate", {"release_gate_false_positive": True}, "D"),
    ("D on unavailable release gate", {"release_gate_unavailable": True}, "D"),
    ("D on unresolved emergency execution", {"unresolved_d_execution": True}, "D"),
    ("D dominates simultaneous C and A extras", {"release_blocker": True,
      "ratchet_exception": True, "expired_s1": True}, "D"),
    ("Known failed ratchet does not default to B", {"ratchets_pass": False}, None),
    ("Other blocker does not get passing A or B", {"other_blocker": True}, None),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    baseline = subprocess.check_output(
        ["git", "show", args.baseline_ref + ":grading-methodology.md"],
        cwd=repo, text=True, encoding="utf-8"
    )
    current = (repo / "grading-methodology.md").read_text(encoding="utf-8")
    old, new = DecisionTree(baseline), DecisionTree(current)
    assert not old.corrected and new.corrected
    # D/C predicates must remain verbatim, not just agree in this model.
    def risk_rules(tree):
        return tree.text.split("1. **D**", 1)[1].split("3. **", 1)[0]
    assert risk_rules(old) == risk_rules(new), "D/C rules changed"
    regressions = []
    print("Case | 1.1.0 | corrected | expected")
    for name, changes, expected in CASES:
        facts = Facts(**changes)
        before, after = old.assess(facts), new.assess(facts)
        assert after == expected, (name, after, expected)
        if expected == "A":
            assert before != "A", (name, "baseline unexpectedly grants A")
            regressions.append(name)
        print(f"{name} | {before or 'no grade'} | {after or 'no grade'} | {expected or 'no grade'}")
    # Exhaust the relevant finite fact combinations, including concurrent
    # risks. In every case D/C dominate and old D/C outcomes are preserved.
    count = 0
    for baseline_s2, candidate_s2, flags in product(range(3), range(3), product((False, True), repeat=8)):
        f = Facts(baseline_s2=baseline_s2, candidate_s2=candidate_s2,
                  release_blocker=flags[0], s3=flags[1],
                  release_gate_false_positive=flags[2],
                  release_gate_unavailable=flags[3],
                  unresolved_d_execution=flags[4], ratchet_exception=flags[5],
                  expired_s1=flags[6], expired_s2=flags[7])
        before, after = old.assess(f), new.assess(f)
        if before in ("C", "D"):
            assert after == before, (f, before, after)
        if any((f.release_blocker, f.s3, f.release_gate_false_positive,
                f.release_gate_unavailable, f.unresolved_d_execution)):
            assert after == "D", f
        count += 1
    # Sections 8.3/12.2: derive the portfolio from actual issue/execution
    # pairs, independently of the same release's health facts.
    for issue_grade in ("A", "B", "C", "D"):
        pr_pairs = [("A", "A"), (issue_grade, "A")]
        overall = [max(pair, key="ABCD".index) for pair in pr_pairs]
        portfolio = max(overall, key="ABCD".index)
        health = new.assess(Facts(executions=tuple(p[1] for p in pr_pairs)))
        assert portfolio == issue_grade and health == "A"
        print(f"Issue {issue_grade}/execution A: portfolio {portfolio}, health {health}")
    print(f"PASS: {len(CASES)} release cases; {len(regressions)} A regressions; "
          f"{count} risk combinations; 4 health/portfolio pairs.")


if __name__ == "__main__":
    main()
