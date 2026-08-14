#!/usr/bin/env python3
"""Check common Dear ImGui scope-stack balance mistakes in C++ source files.

This is a lightweight static guard, not a C++ parser. It ignores comments and string
literals, detects missing direct ImGui::End* calls, and tracks Push/Pop calls for ID,
font, style-color, and style-var stacks. It intentionally tolerates extra lexical End*
calls because the standard conditional Begin/End idiom contains mutually exclusive End()
paths. Run it alongside compilation and tests.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict


@dataclass(frozen=True)
class Call:
    name: str
    line: int
    argument: str


# Capture the remainder of a statement after the opening parenthesis. This intentionally
# tolerates nested constructor/function calls such as PushStyleColor(..., ImVec4(...)).
CALL_RE = re.compile(
    r"\bImGui::(?P<name>"
    r"Begin(?:[A-Za-z0-9_]*)|End(?:[A-Za-z0-9_]*)|"
    r"Push(?:ID|Font|StyleColor|StyleVar)|Pop(?:ID|Font|StyleColor|StyleVar)"
    r")\s*\((?P<argument>[^\n;{}]*)"
)


def mask_comments_and_literals(source: str) -> str:
    """Replace comments and literals with spaces while preserving newlines."""
    output: list[str] = []
    i = 0
    state = "code"
    while i < len(source):
        char = source[i]
        next_char = source[i + 1] if i + 1 < len(source) else ""

        if state == "code":
            if char == "/" and next_char == "/":
                output.extend((" ", " "))
                i += 2
                state = "line_comment"
                continue
            if char == "/" and next_char == "*":
                output.extend((" ", " "))
                i += 2
                state = "block_comment"
                continue
            if char == '"':
                output.append(" ")
                i += 1
                state = "string"
                continue
            if char == "'":
                output.append(" ")
                i += 1
                state = "character"
                continue
            output.append(char)
            i += 1
            continue

        if state == "line_comment":
            output.append("\n" if char == "\n" else " ")
            if char == "\n":
                state = "code"
            i += 1
            continue

        if state == "block_comment":
            if char == "*" and next_char == "/":
                output.extend((" ", " "))
                i += 2
                state = "code"
            else:
                output.append("\n" if char == "\n" else " ")
                i += 1
            continue

        # Handle C++ string/character literals and escaped delimiters.
        if char == "\\" and i + 1 < len(source):
            output.append(" ")
            output.append("\n" if source[i + 1] == "\n" else " ")
            i += 2
            continue
        if (state == "string" and char == '"') or (state == "character" and char == "'"):
            output.append(" ")
            i += 1
            state = "code"
            continue
        output.append("\n" if char == "\n" else " ")
        i += 1

    return "".join(output)


def collect_calls(source: str) -> list[Call]:
    masked = mask_comments_and_literals(source)
    calls: list[Call] = []
    for match in CALL_RE.finditer(masked):
        line = masked.count("\n", 0, match.start()) + 1
        calls.append(Call(match.group("name"), line, match.group("argument").strip()))
    return calls


def pop_count(call: Call) -> int:
    if call.name in {"PopStyleColor", "PopStyleVar"}:
        numeric = re.match(r"(\d+)", call.argument)
        return int(numeric.group(1)) if numeric else 1
    return 1


def check_scope_pairs(calls: list[Call]) -> list[str]:
    begins: DefaultDict[str, list[int]] = defaultdict(list)
    ends: DefaultDict[str, list[int]] = defaultdict(list)
    for call in calls:
        if call.name.startswith("Begin"):
            begins[call.name[5:]].append(call.line)
        elif call.name.startswith("End"):
            ends[call.name[3:]].append(call.line)

    errors: list[str] = []
    for suffix in sorted(set(begins) | set(ends)):
        opened = begins[suffix]
        closed = ends[suffix]
        # A conditional window commonly uses both an early End()+return branch and a
        # normal End() branch. Static lexical counting therefore cannot treat extra End*
        # calls as an error without false positives. Missing End* calls remain actionable.
        if len(opened) > len(closed):
            label = f"Begin{suffix}" if suffix else "Begin"
            end_label = f"End{suffix}" if suffix else "End"
            errors.append(
                f"{label}/{end_label}: {len(opened)} begin call(s) at lines {opened}; "
                f"only {len(closed)} end call(s) at lines {closed}."
            )
    return errors


def check_stack_pairs(calls: list[Call]) -> list[str]:
    mapping = {
        "PushID": "ID",
        "PopID": "ID",
        "PushFont": "Font",
        "PopFont": "Font",
        "PushStyleColor": "StyleColor",
        "PopStyleColor": "StyleColor",
        "PushStyleVar": "StyleVar",
        "PopStyleVar": "StyleVar",
    }
    depth: DefaultDict[str, int] = defaultdict(int)
    errors: list[str] = []

    for call in calls:
        kind = mapping.get(call.name)
        if kind is None:
            continue
        if call.name.startswith("Push"):
            depth[kind] += 1
            continue

        amount = pop_count(call)
        if amount > depth[kind]:
            errors.append(
                f"{call.name} at line {call.line} pops {amount} {kind} scope(s), "
                f"but only {depth[kind]} are open."
            )
            depth[kind] = 0
        else:
            depth[kind] -= amount

    for kind, remaining in sorted(depth.items()):
        if remaining:
            errors.append(f"{kind} stack has {remaining} unclosed Push call(s).")
    return errors


def check_file(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"Could not read {path}: {error}"]

    calls = collect_calls(source)
    return check_scope_pairs(calls) + check_stack_pairs(calls)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect common direct Dear ImGui Begin/End and Push/Pop balance errors."
    )
    parser.add_argument("sources", nargs="+", type=Path, help="C++ source or header files to inspect")
    parser.add_argument("--quiet", action="store_true", help="Print only errors")
    args = parser.parse_args()

    all_errors: list[str] = []
    for path in args.sources:
        errors = check_file(path)
        if errors:
            for error in errors:
                all_errors.append(f"{path}: {error}")
        elif not args.quiet:
            print(f"PASS {path}: common Dear ImGui scope stacks are balanced.")

    if all_errors:
        for error in all_errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
