# Dear ImGui UI/UX Engineering Evaluation Suite

Use this suite after significant changes to the skill. Each case tests triggering behavior and output quality. The deterministic contracts live in `semantic-cases.json`; do not grade stylistic verbosity alone.

## Evaluation protocol

Run every prompt with no extra context unless the case supplies code. Mark an assertion as pass only when the response makes the requirement explicit, provides an equivalent technically correct alternative, or clearly explains why the requirement is not applicable. A response fails a case if it gives only generic UI advice where the requested ImGui-specific reasoning is needed. Run `failure-mode-regressions.md` alongside this suite to test incident-style state, scope, focus, and DPI failures.

| ID | Trigger prompt | Required assertions |
|---|---|---|
| E01 — Unlabelled framework restraint | `My C++ editor panel is overcrowded. It has a tree on the left, a viewport, and many properties on the right. How should I redesign it?` | The skill should not claim that Dear ImGui is in use when neither Dear ImGui nor direct API/header evidence is supplied. It should keep framework choice open and apply this skill only if the user explicitly asks whether Dear ImGui is suitable. |
| E02 — Asset browser | `Design a Dear ImGui asset browser for 20,000 records. Users need text filtering, sorting, single selection, and a property inspector.` | The answer uses a stable model ID, filtered/sorted index view, `ImGuiTableSortSpecs`, and `ImGuiListClipper`. It specifies no-results behavior, selection ownership, and a verification plan. |
| E03 — Duplicate-ID review | `Review this loop: for (auto& item : items) ImGui::Checkbox(item.name.c_str(), &item.enabled);` | The answer calls out duplicate visible labels/ID collisions, recommends `PushID(item.id)` or an equivalent stable-ID method, and distinguishes a visible label from a unique ID. |
| E04 — Stack-balance review | `I call PushStyleColor inside if (warning) and PopStyleColor after the if. Is this safe?` | The answer identifies branch-dependent stack imbalance, gives a balanced correction, and includes a verification step. It should not claim that superficial visual testing alone is sufficient. |
| E05 — DPI and docking | `My docking-branch tool moves between 100% and 200% DPI monitors. Should I set FontScaleDpi and ConfigDpiScaleFonts?` | The answer states that there must be one `FontScaleDpi` owner, describes the docking-branch automatic option, addresses size/padding scaling separately, and points to `references/version-notes.md` or asks the user to verify vendored headers. |
| E06 — Null-safe model review | `Our asset importer can emit null name, type, and status pointers. Make this ImGui row safe.` | The answer avoids passing null to `strcmp`, `Selectable`, `TextUnformatted`, or formatted `%s` output. It proposes a documented non-null invariant or a safe display adapter with meaningful fallback text. |
| E07 — Focus transfer | `When a command palette selects an asset, keyboard focus should move to it, but clicking a row must not steal focus every frame.` | The answer distinguishes pointer selection from explicit programmatic focus request, uses a pending focus ID or equivalent one-shot mechanism, and warns against unconditional `SetItemDefaultFocus()` for the selected row. |
| E08 — Theme request | `Create a dark Dear ImGui theme with a strong blue accent and destructive actions.` | The answer centralizes semantic tokens, includes normal/hover/active/disabled treatments, checks text contrast, avoids scattered hard-coded component colors, and labels any API/version assumption. |
| E09 — Custom component | `Build a custom timeline scrubber with ImDrawList.` | The answer evaluates whether standard widgets suffice, then specifies ID, hit area, hover/active/focus/disabled behavior, drag cancellation, clipping/performance, and keyboard or alternative interaction. |
| E10 — Non-docking compatibility | `I need the asset workspace to compile with a standard non-docking Dear ImGui build.` | The answer omits or guards docking-only APIs, preserves functional independent windows, and does not claim a master build always defines `IMGUI_HAS_DOCK`. |

## Regression gates

A skill revision is acceptable only when all ten standard cases and all five failure-mode cases pass, and when the following package checks also pass:

1. `scripts/check_imgui_cpp.py` can detect an intentionally unbalanced `PushID`/`PopID` fixture and return a nonzero exit code.
2. The same checker reports no error on the bundled panel template.
3. `python3 scripts/run_quality_suite.py` fetches temporary official `v1.92.0` and `master` sources by default, then compiles the panel template with warnings enabled against both.
4. Product CI additionally supplies `--imgui-dir /path/to/vendored/imgui` to compile against its own fork/pinned revision.
5. `SKILL.md` remains below 500 lines and points to version notes, the worked example, the evaluator, and the deterministic checker at the moment those resources are needed.

The bundled reference responses must score a perfect 30/30 with
`python3 scripts/run_semantic_suite.py`. To gate a target model, store its E01-E10 and
F01-F05 responses in the same JSON-object format as
`evals/fixtures/reference-responses.json`, then run
`python3 scripts/run_quality_suite.py --semantic-responses RESPONSES.json`.

## Suggested scoring

Score each case from 0 to 2: `0` for absent or unsafe behavior, `1` for partial/general guidance, and `2` for a concrete, technically correct, verifiable response. The release gate requires a perfect 20/20 standard score and 10/10 failure-mode score with no zero.
