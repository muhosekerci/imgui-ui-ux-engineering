# Dear ImGui UI/UX Engineering

![Dear ImGui](https://img.shields.io/badge/Dear%20ImGui-1.92%2B-4c8bf5)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard-6f42c1)
![Semantic evals](https://img.shields.io/badge/semantic%20evals-30%2F30-success)
[![GitHub](https://img.shields.io/badge/GitHub-muhosekerci-181717?logo=github)](https://github.com/muhosekerci)

Created and maintained by **[muhosekerci](https://github.com/muhosekerci)**.

A production-oriented, portable **Agent Skill** for designing, reviewing, and hardening **Dear ImGui**
tools, editor panels, debugging dashboards, asset browsers, visualization screens, and
desktop workflows.

The package follows the [Agent Skills open standard](https://agentskills.io/specification)
and is designed for skills-compatible CLI agents. Codex is one supported client, not a
requirement or the defining platform.

This skill treats UI improvement as an engineering problem, not a cosmetic reskin. It
combines information architecture, interaction design, immediate-mode state ownership,
stable widget identity, keyboard navigation, DPI handling, performance, and regression
validation in one reusable workflow.

## What it helps with

| Area | Coverage |
|---|---|
| Workspace design | Dockspace shells, command bars, navigation, central work areas, inspectors, logs, and status bars |
| UI/UX review | Prioritized findings with evidence, impact, correction, and verification |
| Component engineering | Tables, asset browsers, inspectors, command palettes, modals, toasts, empty states, and custom draw-list controls |
| Immediate-mode correctness | Stable IDs, state ownership, focus transfer, input capture, and balanced scope stacks |
| Large datasets | Filtered/sorted index views, `ImGuiTableSortSpecs`, and `ImGuiListClipper` |
| Design systems | Centralized spacing, typography, semantic colors, interaction states, and contrast checks |
| DPI and fonts | Non-cumulative metric scaling and explicit `FontScaleDpi` ownership |
| Compatibility | Dear ImGui 1.92+, optional docking, official tag/master compilation, and vendored-header checks |
| Quality gates | Static scope checking, C++ template compilation, contrast validation, and 15 semantic regression cases |

## Agent and CLI compatibility

This repository uses the portable `SKILL.md` directory format defined by the
[Agent Skills specification](https://agentskills.io/specification). It does not depend on one
model provider or one CLI.

| Client | Support path |
|---|---|
| [Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) | Native Agent Skills support and direct URL installation |
| [Claude Code](https://code.claude.com/docs/en/skills) | Native Agent Skills support through `.claude/skills` |
| [GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Native Agent Skills support through `.agents/skills`, `.copilot/skills`, or `copilot skill add` |
| [OpenCode](https://opencode.ai/docs/skills) | Native discovery through `.agents/skills`, `.opencode/skills`, and compatible paths |
| Codex | Skill-directory installation using the same `SKILL.md` package |
| Other skills-compatible agents | Install the complete repository in the client's configured skills directory |

Clients that do not yet implement Agent Skills can still load `SKILL.md` as reusable project
instructions, but automatic discovery and activation depend on that client's capabilities.

## When the skill activates

The skill is intended for requests that:

- explicitly mention Dear ImGui;
- include direct evidence such as `ImGui::`, `imgui.h`, `ImGuiContext`, or backend symbols;
- ask whether Dear ImGui is suitable for an otherwise unlabelled C++ tooling interface.

It keeps framework choice open when a generic C++ UI request provides no Dear ImGui
evidence. It also stays out of tasks that explicitly select another framework such as Qt,
GTK, WPF, wxWidgets, JUCE, or Slate.

## Quick start

### Install with Skills CLI (recommended)

Install the skill with one command:

```bash
npx skills add muhosekerci/imgui-ui-ux-engineering
```

The Skills CLI detects supported coding agents and installs the skill into the appropriate
location. This gives the same repository package to compatible clients such as Claude Code,
Codex, Gemini CLI, GitHub Copilot CLI, OpenCode, Cursor, and other Agent Skills clients.

For a global, non-interactive installation:

```bash
npx skills add muhosekerci/imgui-ui-ux-engineering -g -y
```

### Manual universal installation (`.agents/skills`)

The shared `.agents/skills` location is recognized by multiple compatible clients,
including Gemini CLI, GitHub Copilot CLI, and OpenCode.

#### Windows PowerShell

```powershell
git clone https://github.com/muhosekerci/imgui-ui-ux-engineering.git `
  (Join-Path $HOME ".agents\skills\imgui-ui-ux-engineering")
```

#### macOS or Linux

```bash
git clone https://github.com/muhosekerci/imgui-ui-ux-engineering.git \
  "$HOME/.agents/skills/imgui-ui-ux-engineering"
```

### Client-specific installation

| Client | Installation |
|---|---|
| Gemini CLI | `gemini skills install https://github.com/muhosekerci/imgui-ui-ux-engineering` |
| GitHub Copilot CLI | `copilot skill add https://github.com/muhosekerci/imgui-ui-ux-engineering` |
| Claude Code | Clone into `~/.claude/skills/imgui-ui-ux-engineering` |
| OpenCode | Clone into `~/.config/opencode/skills/imgui-ui-ux-engineering` or use `~/.agents/skills` |
| Codex | Clone into `${CODEX_HOME:-$HOME/.codex}/skills/imgui-ui-ux-engineering` |
| Other compatible CLIs | Point the client's skill installer at this repository, or clone it into that client's Agent Skills directory |

Reload or restart the client after installation if it does not support live skill discovery.
Gemini CLI and GitHub Copilot CLI also provide `/skills reload` in an active session.

### Update an existing installation

```bash
npx skills check
npx skills update
```

For a manually cloned installation, update it with:

```bash
git -C "$HOME/.agents/skills/imgui-ui-ux-engineering" pull
```

### Use the skill

Skills-compatible agents can activate the skill automatically from the task description.
You can also name it explicitly using the syntax supported by your client:

```text
Use the imgui-ui-ux-engineering skill to review this asset browser for ID
collisions, keyboard focus bugs, DPI problems, and performance bottlenecks.
```

```text
Review this asset browser for ID collisions, keyboard focus bugs, DPI
problems, and performance bottlenecks using imgui-ui-ux-engineering.
```

```text
Design a Dear ImGui editor for 20,000 assets with filtering, sorting,
single selection, a property inspector, and a collapsible activity log.
```

```text
Review this ImGui C++ panel and return Critical / High / Medium / Low
findings with fixes and verification steps.
```

## Discoverability and sharing

If this project helps your workflow, star the repository and share the direct link:

```text
https://github.com/muhosekerci/imgui-ui-ux-engineering
```

Good places to introduce the skill include:

- the [`agent-skills`](https://github.com/topics/agent-skills) and [`codex-skills`](https://github.com/topics/codex-skills) GitHub topics;
- Agent Skills directories and client showcases;
- [Awesome GitHub Copilot](https://github.com/github/awesome-copilot) and [Awesome Codex Skills](https://github.com/ComposioHQ/awesome-codex-skills) through contributions;
- the [Dear ImGui Discussions](https://github.com/ocornut/imgui/discussions) community;
- communities for Claude Code, Gemini CLI, GitHub Copilot, Codex, OpenCode, and Dear ImGui;
- developer posts on DEV Community, Hashnode, LinkedIn, X, or a Show HN submission;
- C++ game-tooling, engine-development, editor-tooling, and technical-art communities.

When sharing, include one screenshot or short GIF, three example prompts, the 30/30 semantic
eval result, and the one-command installation snippet above. This makes the purpose and value
of the skill understandable without requiring readers to inspect the repository first.

## Expected deliverables

Depending on the task, the skill returns:

- user and primary-task definitions;
- workspace regions and priority hierarchy;
- selected, empty, loading, error, disabled, and completed states;
- interaction and keyboard-navigation behavior;
- centralized theme and spacing tokens;
- production-oriented C++ implementation guidance;
- stable-ID and state-ownership strategy;
- version and docking assumptions;
- prioritized review findings;
- concrete verification steps.

## Included templates

### `templates/imgui_design_system.h.in`

A centralized Dear ImGui theme with:

- semantic surface, content, accent, success, warning, and danger colors;
- filled-button states that maintain at least 4.5:1 text contrast;
- spacing, padding, radius, border, and density tokens;
- host-managed and Dear-ImGui-managed font DPI policies;
- non-cumulative `ScaleAllSizes()` handling;
- reusable primary and destructive button helpers.

### `templates/imgui_panel_skeleton.cpp.in`

A workspace starter demonstrating:

- optional guarded docking;
- a sortable and filterable asset table;
- stable model IDs and null-safe display strings;
- a filtered/sorted derived index view;
- `ImGuiListClipper` for large collections;
- one-shot programmatic keyboard focus, including off-screen rows;
- inspector, activity-log, metrics, empty, and locked states.

## Repository structure

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml                  # Optional Codex/OpenAI adapter metadata
├── evals/
│   ├── quality-suite.md
│   ├── failure-mode-regressions.md
│   ├── semantic-cases.json
│   └── fixtures/
│       ├── balanced_scopes.cpp
│       ├── unbalanced_push_id.cpp
│       └── reference-responses.json
├── references/
│   ├── design-playbook.md
│   ├── version-notes.md
│   └── worked-example.md
├── scripts/
│   ├── check_imgui_cpp.py
│   ├── run_semantic_suite.py
│   └── run_quality_suite.py
└── templates/
    ├── imgui_design_system.h.in
    └── imgui_panel_skeleton.cpp.in
```

## Quality gates

### Complete release gate

```bash
python scripts/run_quality_suite.py
```

The complete gate:

1. validates required package files and unfinished markers;
2. verifies portable Agent Skills frontmatter and naming constraints;
3. checks the `SKILL.md` size guard;
4. verifies theme contrast;
5. runs the ImGui scope checker against valid and intentionally invalid fixtures;
6. scores all semantic reference cases at a required **30/30**;
7. downloads temporary official Dear ImGui `v1.92.0` and `master` sources;
8. compiles the templates against both with C++17 and warnings as errors.

### Offline diagnostic gate

```bash
python scripts/run_quality_suite.py --skip-official-revisions
```

This runs structural, semantic, contrast, and static checks without downloading official
Dear ImGui revisions. It is useful for fast local feedback, but it is not the release gate.

### Validate a vendored Dear ImGui revision

```bash
python scripts/run_quality_suite.py --imgui-dir /path/to/vendored/imgui
```

The supplied directory must contain `imgui.h`. The command can be repeated with multiple
`--imgui-dir` arguments.

### Check project C++ files directly

```bash
python scripts/check_imgui_cpp.py path/to/panel.cpp path/to/widgets.h
```

The checker detects common direct `Begin`/`End` and `Push`/`Pop` mistakes. It is deliberately
narrow and should be used alongside compilation and Dear ImGui runtime debug tools.

## Semantic evaluation

The package contains ten standard cases (`E01`-`E10`) and five incident-style failure cases
(`F01`-`F05`). The release contract requires:

- standard score: **20/20**;
- failure-mode score: **10/10**;
- combined score: **30/30**;
- no zero-score case and no fatal unsafe recommendation.

Run the bundled reference responses:

```bash
python scripts/run_semantic_suite.py
```

To grade target-model output, create a JSON object containing all 15 response IDs:

```json
{
  "E01": "Response for E01",
  "E02": "Response for E02",
  "F05": "Response for F05"
}
```

The real file must contain every ID from `E01` through `E10` and `F01` through `F05` exactly
once. Then run:

```bash
python scripts/run_quality_suite.py --semantic-responses responses.json
```

## Design principles

1. **Application data is the source of truth.** Persist only presentation-specific UI state.
2. **Every repeated widget has a stable unique ID.** Never rely on visible text alone.
3. **Derived views do not mutate the source model.** Filtering and sorting operate on indices.
4. **Focus moves only after explicit navigation intent.** Pointer selection does not steal it.
5. **Large collections are clipped.** Rendering cost should scale with visible rows.
6. **Theme values are semantic and centralized.** Color is never the only status signal.
7. **DPI has one font-scale owner.** Metric scaling is reset and applied non-cumulatively.
8. **Version-sensitive APIs are verified against real headers.** Numeric versions do not prove docking support.
9. **Tasks are validated, not only screenshots.** Empty, error, narrow, long-content, and keyboard-only states matter.

## Requirements

- Python 3.9 or newer;
- Git for fetching official Dear ImGui revisions;
- `g++` or another `c++` executable with C++17 support for compile gates;
- network access for the complete official-revision gate.

The generated C++ templates require Dear ImGui **1.92.0 or newer**. Docking remains optional
and is guarded with `IMGUI_HAS_DOCK`.

## Important limitations

Dear ImGui is particularly effective for game tools, editors, debugging interfaces, and
real-time technical workflows. Before choosing it for a consumer-facing application, assess
requirements for complete screen-reader integration, RTL text, complex text shaping, and
platform-native accessibility behavior.

Custom draw-list controls also require more work than built-in widgets: define their ID,
hit area, interaction states, keyboard path, cancellation behavior, clipping, and semantic
representation before implementation.

## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 [muhosekerci](https://github.com/muhosekerci).

## References

- [Dear ImGui repository](https://github.com/ocornut/imgui)
- [Dear ImGui FAQ](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md)
- [Dear ImGui fonts and DPI documentation](https://github.com/ocornut/imgui/blob/master/docs/FONTS.md)
- [Dear ImGui docking wiki](https://github.com/ocornut/imgui/wiki/Docking)
- [WCAG 2.2 contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

## Contributing

When changing behavior:

1. update the relevant guidance or template;
2. add or revise a semantic regression case;
3. run the offline gate during development;
4. run the complete release gate before publishing;
5. verify against the product's vendored Dear ImGui headers when available.

## Author

**muhosekerci** — creator and maintainer of Dear ImGui UI/UX Engineering.

- GitHub: [github.com/muhosekerci](https://github.com/muhosekerci)
