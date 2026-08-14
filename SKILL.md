---
name: imgui-ui-ux-engineering
description: Proactively design, improve, or review high-quality Dear ImGui tools, C++ editor panels, game-development interfaces, debugging dashboards, visualization screens, and desktop workflows. Use when Dear ImGui is named or supplied code contains direct evidence such as `ImGui::`, `imgui.h`, `ImGuiContext`, or ImGui backend symbols. For an unlabelled C++ editor/tooling request, use only when the user explicitly asks whether Dear ImGui is suitable; otherwise keep framework choice open. Do not trigger for a task that explicitly names another UI framework such as Qt, GTK, WPF, wxWidgets, JUCE, or Slate. Cover UI architecture, information hierarchy, dockspace layouts, design systems, custom components, UX states, keyboard/gamepad interaction, DPI/fonts, performance, and code quality.
license: MIT
compatibility: Portable Agent Skills open-standard package. Works with skills-compatible CLI agents; bundled validation requires Python 3.9+, and complete C++ gates require Git, network access, and a C++17 compiler.
metadata:
  author: muhosekerci
  version: "1.0.0"
  repository: "https://github.com/muhosekerci/imgui-ui-ux-engineering"
  keywords: "agent-skills, dear-imgui, imgui, ui-ux, cpp, editor-tools, game-development, code-review, accessibility, dpi, performance"
---

# Dear ImGui UI/UX Engineering

## Purpose and boundaries

Build **professional tool interfaces** with Dear ImGui. Design around the immediate-mode model: application data remains the single source of truth, while UI code reflects the current model and dispatches user intent back to it. Dear ImGui is especially well suited to content-creation tools, editor and game tooling, debugging panels, operations screens, and real-time visualizations. Explicitly assess suitability when a consumer product needs complete accessibility support, RTL text, or complex text shaping. [1] [2]

Do not treat a review as a cosmetic reskin. Improve functional hierarchy, interaction cost, error recovery, information density, technical correctness, and visual consistency together.

## Classify the request

Match the request to one primary workflow. If Dear ImGui is neither named nor evidenced in supplied code, do not assume it is the framework; offer a framework-selection assessment only when explicitly asked. Make reasonable assumptions when missing information does not materially change the solution; ask only for a critical ambiguity.

| Request | Primary deliverable | Start by determining |
|---|---|---|
| New tool or editor | Information architecture, workspace shell, design system, production-oriented C++ | User role, top three tasks, target platform |
| Existing UI improvement | Audit, redesign proposal, focused code changes | Screenshot or code, hierarchy issues, missing states |
| Component design | Behavioral contract, state matrix, ImGui implementation | Data, actions, empty/error state, keyboard behavior |
| Theme or visual identity | Design tokens, palette, typography, theme code | Task density, brand constraints, contrast requirements |
| Code review | Prioritized findings and safe fixes | IDs, stack balance, state ownership, input, clipping, DPI, performance |

## Required workflow

1. **Extract the context.** Identify the user, principal tasks, data scale, display sizes, input devices, density preference, and destructive actions.
2. **Create the hierarchy.** Keep the primary action visible and close to its task; place contextual actions near the selected object or inspector; move rare settings into menus or disclosure controls. Define selected, empty, loading, error, unauthorized, and completed states for every view.
3. **Select the workspace shell.** When appropriate, use a command bar, left navigation or asset pane, central work area, right inspector, bottom log/progress surface, and status bar. Persist docking and window layout only when personalization provides real value. Verify that the chosen Dear ImGui branch/version supports any docking API. [2]
4. **Build the design system.** Centralize spacing, radii, borders, typography, surface layers, and semantic colors. Start from `templates/imgui_design_system.h.in`, then adapt it to the product and density requirements.
5. **Build components around tasks.** Prefer built-in widgets, the table API, and standard interactions. Use custom draw-list code only when a distinctive behavior or visual treatment is genuinely required. Design normal, hovered, active, selected, focused, disabled, loading, and error states.
6. **Design interaction.** Validate keyboard and, when relevant, gamepad navigation, focus, shortcuts, cancellation, and undo. Always forward raw input to Dear ImGui; use `io.WantCaptureMouse`, `io.WantCaptureKeyboard`, and `io.WantTextInput` to decide whether the underlying application also receives it. [2]
7. **Perform the technical audit.** Check identity collisions, `Push`/`Pop` and `Begin`/`End` balance, frame-local allocations, clipping of large lists, DPI handling, contrast, and version-specific APIs.
8. **Validate tasks, not just pixels.** Test narrow and wide panels, long text, no data, hundreds of records, failed work, and keyboard-only operation. Verify alignment, action feedback, and recovery paths.

## Workspace composition

Use the following as an adaptable composition system, not a rigid pixel template.

| Region | Purpose | Implementation guidance |
|---|---|---|
| Command bar | Frequent global actions, search, workspace switching | Keep the action count low; move secondary commands into menus or a command palette. |
| Navigation or asset pane | Hierarchy, collection, scene, files, filters | Provide search, collapsible groups, visible selection, and small counts. |
| Central work area | Canvas, table, timeline, chart, or main editor | Allocate the greatest area and contrast here; remove nonessential chrome. |
| Inspector | Selected-object properties and contextual actions | Group fields by mental model; offer live preview and a safe reset action. |
| Supporting surface | Log, performance, job queue, issue list | Make it dismissible or collapsible when it is not needed. |
| Status bar | Connection, selection, process, coordinate, or performance state | Keep it concise, live, and actionable. |

### Density and hierarchy

Choose the density from task frequency and data scale, then express priority with surface elevation, typography, whitespace, color, and placement. Never make color the only carrier of meaning. For detailed density guidance and component contracts, read `references/design-playbook.md`. [5]

## Choose the right component

| Component | Use it for | Avoid using it for |
|---|---|---|
| Table or asset browser | Sortable, filterable, multi-column data | Rendering thousands of records as cards |
| Inspector | Editable properties of the selected object | Unrelated global settings |
| Metric card | A small number of critical KPIs and trends | Every number on the screen |
| Command palette | Many commands and expert keyboard workflows | Hiding a core action from the main UI |
| Modal | Confirmation or a short focused decision | A long-lived editor or comprehensive form |
| Toast | Brief success feedback and undo affordance | The only presentation of a critical error |
| Empty state | First use or an empty filter result | Leaving the user in an unexplained blank panel |

Read `references/design-playbook.md` when detailed layout patterns, component contracts, state copy, or a review rubric is needed. Read `references/worked-example.md` before writing a review or before/after proposal when a concrete output model would improve consistency.

## Dear ImGui implementation rules

### State, identity, and structure

Keep the application model as the **single source of truth**. Store UI state only when it is presentation-specific, such as an open pane, temporary filter text, or drag preview. For pointer-backed display fields, either enforce and document a non-null model invariant or route every UI read through a null-safe display adapter; never rely on an implicit nullable-string convention.

Guarantee unique IDs for repeated widgets. Use `##` to add an invisible suffix, `PushID()`/`PopID()` with a stable object key for loops and dynamic collections, and `###` to keep an ID stable while a visible label changes. Repeating labels in the same scope creates collisions. [2]

Balance every `Push*` with the matching `Pop*` and every `Begin*` with the corresponding `End*`. Follow each API's contract; for example, do not skip a required `End()` merely because a window is currently collapsed.

### Layout and large data

Use fixed pixel coordinates only as a last resort. Compose layouts with `BeginTable`, child regions, available width, flexible columns, and spacing tokens. Align inspector labels and inputs in two columns, then test the narrowest supported panel.

For large collections, build a filtered stable-ID view and render visible rows with `ImGuiListClipper`. Process `ImGuiTableSortSpecs` when exposing sortable columns; a `Sortable` flag without actual model ordering is an incomplete interaction. Provide sort direction, active-filter summary, visible selection, and a meaningful empty result.

### Theme, typography, and DPI

Centralize measurements. Derive padding, spacing, and radii from a small scale. Separate layers with `WindowBg`, `ChildBg`, `PopupBg`, and borders rather than assigning an arbitrary tone to every panel.

Target a minimum **4.5:1** contrast ratio for normal text and **3:1** for large text. [4] Choose an appropriate font if the default is not readable at the tool's intended size. Select exactly one owner for `FontScaleDpi`: use the template's host-managed policy with a host-provided scale, or select its Dear-ImGui-managed policy when the docking branch's `io.ConfigDpiScaleFonts` automatically updates it as monitor DPI changes. Continue to reset the style and apply `ScaleAllSizes()` for size/padding scaling when the content scale changes. Confirm target version and backend capabilities before relying on newer APIs. [3]

### Keyboard, gamepad, and accessibility

Enable `ImGuiConfigFlags_NavEnableKeyboard` and, when needed, `ImGuiConfigFlags_NavEnableGamepad`. Test Tab/Shift+Tab traversal, visible focus, Escape cancellation, Enter confirmation, and critical application shortcuts. Move default keyboard focus only when an explicit navigation or programmatic-selection request requires it; do not reassert focus for a selected row every frame. Clearly report Dear ImGui's built-in accessibility and complete internationalization limitations rather than presenting a theme change as a complete solution. [1]

Make focus, hover, and selection visually distinct. Use a tooltip to supplement an ambiguous icon or abbreviation, not to explain a required task. When a control is disabled, expose the reason briefly.

## Custom drawing and component contract

Before writing custom draw-list code, first determine whether a composition of built-in widgets, tables, selectables, trees, popups, and child regions satisfies the need. For every custom control:

1. Define the visible boundary and hit area in the same coordinate model.
2. Generate a unique ID and specify normal, hover, active, selected, focused, disabled, loading, and error behavior.
3. Define click, drag, cancellation, and no-data behavior in writing.
4. Respect clipping; generate only visible geometry for large data; minimize persistent per-frame allocation.
5. Draw colors, spacing, and fonts from central tokens; never embed arbitrary visual constants in a component.
6. Visually verify narrow/wide panels, low/high DPI, and every interaction state.

## Deliverable contract

| Deliverable | Must include |
|---|---|
| Design proposal | User/task list, screen regions, priority hierarchy, state matrix, interaction notes, implementation order |
| C++ implementation | Theme tokens, component functions, ID strategy, state ownership, empty/error states, version assumptions |
| Redesign | Before/after issue table, proposed structure, measurable improvement goal, targeted changes |
| Code review | `Critical / High / Medium / Low` priority, evidence, impact, fix, and verification step |

Use `templates/imgui_panel_skeleton.cpp.in` for a dockspace-oriented workspace shell and `templates/imgui_design_system.h.in` for a centralized token system. Read `references/version-notes.md` before copying version-sensitive code into a vendored or pinned Dear ImGui project. When reviewing or generating C++ source, run `scripts/check_imgui_cpp.py <source...>` to catch common direct `Begin`/`End` and `Push`/`Pop` balance mistakes; treat it as a narrow static guard, not a replacement for compilation or runtime testing. For automated structural, semantic, contrast, static-checker, and compile regression checks, run `python3 scripts/run_quality_suite.py`; every normal run fetches temporary official `v1.92.0` and `master` sources and compiles the templates against both. The bundled semantic reference responses must score 30/30; pass `--semantic-responses RESPONSES.json` to gate target-model outputs against the same contracts. To validate a product fork, additionally supply `--imgui-dir /path/to/vendored/imgui`. Use `--skip-official-revisions` only for an explicitly offline diagnostic run; it is not a release gate. Use `evals/quality-suite.md` and `evals/failure-mode-regressions.md` only when revising or regression-testing this skill; the latter tests concrete state, scope, focus, and DPI failures rather than generic output quality.

## Release quality gate

- Does the primary task have an obvious, visible, nearby entry point?
- Are selected, hovered, focused, disabled, error, loading, and empty states distinguishable?
- Is the primary action clearly separate from secondary and destructive actions?
- Are shortcuts, focus flow, Escape/cancel, and input capture correct?
- Do tables/lists work with large data, filtering, sorting, selection, and empty results?
- Are widget IDs unique and `Push`/`Pop`, `Begin`/`End` calls balanced?
- Do nullable model values render safely, and does default focus move only after an explicit request?
- Have contrast, font legibility, DPI, narrow panels, and long content been tested?
- Have clipping, avoidable allocations, and profiling been considered?
- Has `scripts/run_quality_suite.py` passed against each supported vendored Dear ImGui header revision?
- Are accessibility and internationalization limitations explicit where relevant?

## References

[1] [Dear ImGui official repository](https://github.com/ocornut/imgui)

[2] [Dear ImGui FAQ: paradigm, IDs, input capture, navigation, and docking](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md)

[3] [Dear ImGui: fonts, DPI scaling, and icons](https://github.com/ocornut/imgui/blob/master/docs/FONTS.md)

[4] [W3C WCAG 2.2: Understanding Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

[5] [Nielsen Norman Group: 10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
