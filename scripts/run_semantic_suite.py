#!/usr/bin/env python3
"""Deterministically score responses against the 15 semantic skill contracts."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CASES = SKILL_DIR / "evals" / "semantic-cases.json"
DEFAULT_RESPONSES = SKILL_DIR / "evals" / "fixtures" / "reference-responses.json"


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not load {path}: {error}") from error


def assertion_matches(response: str, assertion: dict[str, object]) -> bool:
    normalized = response.casefold()
    any_terms = [str(term).casefold() for term in assertion.get("any", [])]
    all_terms = [str(term).casefold() for term in assertion.get("all", [])]
    return (not any_terms or any(term in normalized for term in any_terms)) and all(
        term in normalized for term in all_terms
    )


def score_case(case: dict[str, object], response: str) -> tuple[int, list[str], list[str]]:
    normalized = response.casefold()
    fatal_hits = [str(term) for term in case.get("fatal", []) if str(term).casefold() in normalized]
    assertions = list(case.get("assertions", []))
    missed = [
        str(assertion.get("label", "unnamed assertion"))
        for assertion in assertions
        if not assertion_matches(response, assertion)
    ]
    if fatal_hits:
        return 0, missed, fatal_hits
    matched = len(assertions) - len(missed)
    if matched == len(assertions):
        return 2, missed, fatal_hits
    if matched >= math.ceil(len(assertions) / 2):
        return 1, missed, fatal_hits
    return 0, missed, fatal_hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--responses", type=Path, default=DEFAULT_RESPONSES)
    args = parser.parse_args()

    try:
        case_document = load_json(args.cases)
        responses = load_json(args.responses)
    except ValueError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    if not isinstance(case_document, dict) or not isinstance(responses, dict):
        print("FAIL cases and responses must be JSON objects.", file=sys.stderr)
        return 1

    cases = case_document.get("cases", [])
    suites = case_document.get("suites", {})
    if not isinstance(cases, list) or not isinstance(suites, dict):
        print("FAIL invalid semantic case schema.", file=sys.stderr)
        return 1

    case_ids = [str(case.get("id", "")) for case in cases if isinstance(case, dict)]
    expected_ids = {f"E{index:02d}" for index in range(1, 11)} | {f"F{index:02d}" for index in range(1, 6)}
    if len(case_ids) != len(set(case_ids)) or set(case_ids) != expected_ids:
        print("FAIL semantic cases must contain exactly E01-E10 and F01-F05 once.", file=sys.stderr)
        return 1
    missing_responses = sorted(expected_ids - set(responses))
    extra_responses = sorted(set(responses) - expected_ids)
    if missing_responses or extra_responses:
        print(
            f"FAIL response ID mismatch; missing={missing_responses}, extra={extra_responses}",
            file=sys.stderr,
        )
        return 1

    totals: defaultdict[str, int] = defaultdict(int)
    zero_cases: list[str] = []
    for case in cases:
        case_id = str(case["id"])
        suite = str(case["suite"])
        response = responses[case_id]
        if not isinstance(response, str) or not response.strip():
            print(f"FAIL {case_id}: response must be a non-empty string.", file=sys.stderr)
            return 1
        score, missed, fatal_hits = score_case(case, response)
        totals[suite] += score
        if score == 0:
            zero_cases.append(case_id)
        details: list[str] = []
        if missed:
            details.append("missed=" + ", ".join(missed))
        if fatal_hits:
            details.append("fatal=" + ", ".join(fatal_hits))
        suffix = f" ({'; '.join(details)})" if details else ""
        print(f"{'PASS' if score == 2 else 'FAIL'} {case_id} score={score}/2{suffix}")

    passed = not zero_cases
    for suite_name, contract in suites.items():
        required = int(contract["required_score"])
        maximum = int(contract["maximum_score"])
        actual = totals[suite_name]
        suite_passed = actual >= required
        passed = passed and suite_passed
        print(f"{'PASS' if suite_passed else 'FAIL'} {suite_name} semantic score={actual}/{maximum} required={required}")
    if zero_cases:
        print(f"FAIL zero-score cases: {', '.join(zero_cases)}", file=sys.stderr)
    if passed:
        print("ALL SEMANTIC CONTRACTS PASSED (30/30)")
        return 0
    print("SEMANTIC CONTRACTS FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
