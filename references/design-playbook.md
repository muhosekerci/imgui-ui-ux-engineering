# Dear ImGui Design Playbook

Read this reference only when detailed layout patterns, component contracts, UI copy, or a review rubric are needed. The core workflow and release gate are in `SKILL.md`.

## 1. Fast design brief

Before writing code, fill in the following in a short paragraph or table. State any assumption explicitly.

| Field | Decision to make | Example |
|---|---|---|
| User | Who uses the tool and at what level of expertise? | Technical artist, build engineer, live-operations analyst |
| Primary task | What is the most frequent and valuable job? | Adjust shader parameters for the selected asset quickly |
| Object scale | How many records, properties, or samples exist? | 10–50 settings, 10,000 assets, 60 telemetry samples per second |
| Reversibility | Which actions are risky? | Delete asset, publish a live setting, batch-convert files |
| Input | Which devices must work besides a mouse? | Keyboard, gamepad, remote session |
| Viewing priority | Which area must remain dominant? | Central canvas, table, or timeline |
| Density | Is the user discovering or producing? | Daily expert use: dense |

## 2. Layout recipes

### 2.1 Asset editor

Use a left pane for hierarchy and filtering, a central canvas or list for the selected asset, a right inspector, and a bottom issue/log surface. Give the hierarchy search and visible selection. Give the inspector category headers, affected-object identity, and reset-to-default affordances. When selection changes, ensure the central pane and inspector are driven by the same model.

**Success criterion:** Without searching, a user can distinguish the current selection, its type, and available editable properties at a glance.

### 2.2 Data or telemetry workspace

Place time range, filters, and refresh controls at the top; chart or table in the center; legend or details on the right; query, error, and workflow messages at the bottom. Start from the last useful time range and a few critical series. Move fine detail into a tooltip, drill-down, or details pane rather than overwhelming the chart with legend entries.

**Success criterion:** A user can tell what is current, failed, or filtered without interpretation ambiguity.

### 2.3 Job or queue panel

For every job, show an understandable name, stage, progress, expected outcome, cancel/retry action, and error detail. Do not lock long-running work inside a modal. In an error row, show a summary, cause, and next action; place technical logs behind optional disclosure.

**Success criterion:** A user never confuses queued, running, failed, and completed work, and knows how to recover a failed job.

### 2.4 Scene or canvas tool

Make the central canvas dominant. Use the left pane for tools and hierarchy, the right pane for inspection, the top bar for mode/tool switching, and the bottom for status, coordinates, or selection. Signal modes with text, icon, and/or status chip, not color alone. Make mouse operations explicitly cancellable with Escape, right-click, or a clear Cancel action.

**Success criterion:** The user can always identify the active tool mode, selection scope, and likely result of the next action.

## 3. State matrix

Design the following states deliberately. Non-default states often determine whether a tool feels production-ready.

| State | Visual signal | Behavior | Example copy |
|---|---|---|---|
| Empty | Calm surface, concise explanation, one starting action | Guide the user forward | `No assets yet. Import your first asset.` |
| No filter result | Filter summary and clear action | Preserve data; make clearing the filter easy | `No results for “metal”. Clear filter.` |
| Loading | Inline progress, skeleton, or percentage | Preserve safe interaction; show cancel if available | `Building preview — 64%` |
| Success | Brief, actionable confirmation | Offer undo when relevant | `42 assets tagged. Undo` |
| Error | Clear error surface, cause, safe next step | Keep technical details expandable | `Import could not finish. Check the file path.` |
| Disabled | Muted treatment and reason | Do not trigger the action | `Select a target before publishing.` |
| Destructive confirmation | Target name/count, impact, reversibility | Safe default and explicit verb | `Delete “Forest” collection? This cannot be undone.` |

## 4. Component contracts

### Table and asset browser

Keep the identifier/name, primary state, and the one to three supporting fields that drive a user's decision visible. Define column priority; hide low-priority columns or move them to the details pane in narrow space. Show readable sort direction, active-filter summary, and a selected row with clear but restrained contrast.

**Behavior:** If single, multiple, and range selection are supported, make their rules consistent. Context menu, row action, and keyboard focus must address the same target object. Build the filtered index first, process `ImGuiTableSortSpecs` on that index, then render it with `ImGuiListClipper` at scale.

### Inspector

Group fields by the user's mental model: Transform, Appearance, Physics, Build Settings, and similar categories. For each editable field, state the unit, valid range, mixed-value state, and change scope. Make reset fast but not easy to trigger accidentally.

**Behavior:** If a dragged value previews live, create the command/undo entry when dragging ends. In a multi-selection, display non-common values as mixed or blank; never silently impose the first object's value.

### Command palette

Design the command palette for keyboard use. Focus the search field when it opens. Display matches with command name, concise description, category, and shortcut. Make recent/frequent commands available with an empty search query.

**Behavior:** Escape closes it, Enter runs the selected command, and arrow keys move through results. Use a visible second safety step for destructive commands rather than executing them immediately.

### Metric card

A card contains value, name, time context, and directional information. Show a trend only when a meaningful comparison period exists. If a card is clickable, make that affordance visible and navigate to the associated detail view.

**Avoid:** Turning every value into a card, using charts as ornamental filler, or relying on red and green as the only semantic cue.

### Modal, popup, and toast

Use a modal for a short decision. The title should state verb and target, with explicit primary and cancel actions. Use a popup for contextual settings or small action groups, not as a replacement for the central work area. Use a toast for brief success feedback and undo; show safety, connection, and data-loss failures on a persistent surface as well.

## 5. Visual-token decisions

### Recommended naming

```cpp
// surface: panel backgrounds; content: text; accent: focus and primary actions; semantic: state
namespace ToolColor {
constexpr ImVec4 SurfaceBase;
constexpr ImVec4 SurfaceRaised;
constexpr ImVec4 SurfaceOverlay;
constexpr ImVec4 BorderSubtle;
constexpr ImVec4 BorderStrong;
constexpr ImVec4 ContentPrimary;
constexpr ImVec4 ContentMuted;
constexpr ImVec4 Accent;
constexpr ImVec4 AccentHover;
constexpr ImVec4 Success;
constexpr ImVec4 Warning;
constexpr ImVec4 Danger;
}
```

Do not apply the same `Danger` token at arbitrary strengths to an error icon, delete button, and alarm message. Keep the token's meaning and allowed uses stable. Check contrast against a 4.5:1 target for normal text and 3:1 target for large text. [1]

### Spacing and density

Choose a base scale of `4` or `5` px. Derive `FramePadding`, `ItemSpacing`, `CellPadding`, `WindowPadding`, and heading gaps from multiples of that scale. Do not increase density merely by shrinking text; preserve priority and row rhythm.

## 6. Technical review rubric

| Area | Symptom to look for | Correction |
|---|---|---|
| Identity | Repeated label in a loop, random index, state loss in a changing title | Use a stable object ID with `PushID`, `##`, or `###`. [2] |
| Focus | Selected row takes focus again on every frame | Request default focus only after explicit programmatic navigation or selection. |
| Nullable text | Pointer-backed model field reaches `Selectable`, `TextUnformatted`, or `strcmp` without a guarantee | Document a non-null invariant or render through a null-safe helper with meaningful fallbacks. |
| Stack | Conditional `PopStyleColor`, skipped `End`, unbalanced `PushID` | Pair every branch; consider scope guards/helpers. |
| State | Two copies of the same data in UI and application model | Keep one model source; limit temporary UI state. |
| Input | Underlying application shortcut fires while a UI control is active | Forward raw input to ImGui and separate application routing with capture signals. [2] |
| Large data | Stutter while scrolling, every row rebuilt each frame | Use filtered/sorted index views, `ImGuiListClipper`, and visible-geometry generation. |
| DPI | Tiny spacing/text, blurry fonts, or two systems writing `FontScaleDpi` | Reset style before `ScaleAllSizes()`; select either host-managed font scale or docking-branch `ConfigDpiScaleFonts`, never both. [3] |
| Error flow | Silent failure, disappearing toast, no recovery | Add persistent error summary and retry/cancel/undo action. |
| Visual | Ambiguous color meaning, low contrast, long-text overflow | Use tokens, contrast checks, text truncation/tooltip, and narrow-width tests. |

## References

[1] [W3C WCAG 2.2: Understanding Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)

[2] [Dear ImGui FAQ: ID system and input capture](https://github.com/ocornut/imgui/blob/master/docs/FAQ.md)

[3] [Dear ImGui: fonts and DPI](https://github.com/ocornut/imgui/blob/master/docs/FONTS.md)
