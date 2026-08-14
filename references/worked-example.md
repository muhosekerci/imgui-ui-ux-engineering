# Worked Example: Asset Browser Review

Read this file when producing a design review, a before/after recommendation, or a structured output for a crowded C++ editor panel. Adapt the structure to the task; do not copy its domain details blindly.

## Input request

> Review this Dear ImGui asset browser. It feels crowded, slows down with many assets, and selection sometimes behaves strangely. Give me a practical redesign and focused code fixes.

```cpp
ImGui::Begin("Assets");
for (Asset& asset : assets) {
    if (ImGui::Button(asset.name))
        selected = &asset;
    ImGui::SameLine();
    ImGui::Text("%s | %s", asset.type, asset.status);
}
ImGui::End();
```

## Expected review output

# Asset Browser Review

## Executive assessment

The panel has three high-impact defects. It uses the visible asset name as the widget ID, so duplicate names collide. It creates one horizontal button/text row per asset without clipping, so large collections perform unnecessary per-frame work. It also lacks filtering, sorting, visible row selection, and an empty-result state; as a result, the user cannot scan or recover from a crowded view efficiently.

## Findings

| Priority | Evidence | Impact | Recommended correction | Verification |
|---|---|---|---|---|
| High | `Button(asset.name)` uses a potentially duplicate visible label as the ID. | Clicking or state handling can target the wrong asset. | Wrap each row in `PushID(asset.id)`/`PopID()` and use the stable ID. | Add two assets with the same name; each remains independently selectable. |
| High | Every asset is emitted on every frame. | Scrolling becomes costly as asset count grows. | Filter/sort an index view, then render visible rows with `ImGuiListClipper`. | Profile 10,000 assets; visible-row work scales with viewport height. |
| Medium | Button list has no persistent selected-row treatment. | The current context is difficult to scan. | Use `Selectable` with row spanning and a right-side inspector. | Keyboard and pointer selection remain visible after scrolling. |
| Medium | No filter/no-result flow exists. | Users cannot narrow a large collection or understand an empty view. | Add search, active-filter feedback, and a clear-filter affordance. | A no-match query presents recovery text and Clear. |

## Proposed interaction model

Use a three-region workspace. The left/central asset browser contains a search field and table. Its first column exposes name and selection, while Type and Status support sorting. The right inspector displays selected-asset properties. The table preserves row identity through `asset.id`; the model owns selection as `selectedAssetId` rather than retaining a raw element pointer.

The browser must compute a stable filtered/sorted index list. It should handle normal data, no filter result, and no selection explicitly. Pointer selection updates selection without forcibly taking keyboard focus. A command or explicit navigation action can request focus by setting a pending focus ID.

## Focused implementation outline

```cpp
// Application model: do not retain a pointer into a vector that may reallocate.
int selectedAssetId = -1;
std::vector<int> filteredSortedAssetIndices;

// 1. Rebuild the index list only when data, filter, or sort specs change.
// 2. In BeginTable(), call TableGetSortSpecs() and sort the index list.
// 3. Use ImGuiListClipper over filteredSortedAssetIndices.
// 4. For every visible row:
ImGui::PushID(asset.id);
if (ImGui::Selectable(SafeText(asset.name, "<Unnamed asset>"), selected,
                      ImGuiSelectableFlags_SpanAllColumns | ImGuiSelectableFlags_AllowOverlap)) {
    RequestAssetSelection(ui, asset.id); // Pointer selection: no forced keyboard focus.
}
ImGui::PopID();
```

Use `templates/imgui_panel_skeleton.cpp.in` for the complete implementation pattern, including null-safe display strings, table sort handling, clipping, and explicit focus-transfer requests.

## Acceptance checks

| Scenario | Expected result |
|---|---|
| Two assets share a display name | Each row has independent input/state because `asset.id` owns the widget scope. |
| 10,000 assets with a narrow viewport | Only visible filtered/sorted rows are emitted. |
| Filter matches no assets | User sees a no-results message and can clear the filter. |
| Selection arrives from a command palette | The requested row becomes default keyboard focus once it is visible. |
| A data source provides null name/type/status | UI renders fallback text and does not pass null to `strcmp`, `Selectable`, or text widgets. |
| Project uses a non-docking Dear ImGui build | Browser and inspector work; dockspace code remains excluded. |

## Output conventions illustrated

The review gives an assessment before recommendations, classifies findings by priority, includes code evidence, distinguishes design behavior from implementation work, and ends with testable acceptance checks. Use this structure for reviews. For a new-screen request, begin with the user/task model and state matrix instead of an issue table.
