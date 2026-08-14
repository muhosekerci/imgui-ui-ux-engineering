# Dear ImGui Compatibility Notes

Read this file before copying a template into a project with a pinned or vendored Dear ImGui revision. Treat the project's local `imgui.h` as the final authority: compile against it, call `IMGUI_CHECKVERSION()`, and prefer feature/branch checks over assumptions derived from a version label.

## Tested baseline and validation method

The templates are compiled in this skill against the official **v1.92.0** tag and the then-current official `master` checkout. The code includes a numeric `IMGUI_VERSION_NUM >= 19200` guard because its font/DPI implementation depends on the 1.92 API surface. That guard is a baseline, not proof that an arbitrary vendor fork carries every optional feature.

| API or behavior | v1.92.0 official master tag | Current official master checked for this skill | Docking branch | Template treatment |
|---|---|---|---|---|
| `IMGUI_VERSION_NUM` | `19200` | Version is expected to advance | Present | Require `>= 19200`; compile against the vendored header. |
| `ImGuiStyle::FontScaleDpi` | Present | Present | Present | Use only through the explicit `FontDpiPolicy`. |
| `ImGuiStyle::ScaleAllSizes()` | Available public style API | Available | Available | Reset style, then apply once at startup or after a confirmed scale change. |
| `ImGuiCol_TabSelected` | Present | Present | Present | Used by the theme. |
| `ImGuiCol_TabSelectedOverline` | Present | Present | Present | Used by the theme; let the template's version guard and real project compilation reject unsupported forks. |
| `ImGuiTableSortSpecs` / `TableGetSortSpecs()` | Present | Present | Present | Use to sort the model/index view, not merely table headers. |
| `ImGuiListClipper` | Present | Present | Present | Use for large filtered/sorted lists. |
| `IMGUI_HAS_DOCK` | Not a master-branch promise | Not a master-branch promise | Defined | Guard all docking-only names with this macro. |
| `ImGui::DockSpaceOverViewport()` | Not a master-branch promise | Not a master-branch promise | Present | Compile only behind `IMGUI_HAS_DOCK`; submit before hosted windows. |
| `io.ConfigDpiScaleFonts` | Not a master-branch promise | Not a master-branch promise | Present and experimental | Do not set `FontScaleDpi` manually when this configuration owns it. |
| `io.ConfigDpiScaleViewports` | Not a master-branch promise | Not a master-branch promise | Present and experimental | Treat as a host/platform integration choice; verify against the docking branch. |

> **Rule:** A numeric version check can establish a minimum baseline, but it cannot prove the availability of docking-branch symbols in a custom fork. Guard optional APIs by branch capability and compile the final code against the project's local Dear ImGui headers.

## Integration checklist

Run these checks before adopting the templates:

1. Compare the project's `IMGUI_VERSION_NUM` with the template baseline.
2. Search the vendored `imgui.h` for every optional enum or function used by the copied template.
3. If `IMGUI_HAS_DOCK` is absent, keep the non-docking workspace path and do not call `DockSpaceOverViewport()`.
4. Select one `FontScaleDpi` owner: the host or the docking branch's `ConfigDpiScaleFonts`; do not let both write the value.
5. Compile with warnings enabled, run the project's Dear ImGui demo/metrics window, and visually test target DPI scales.

## Sources and provenance

The v1.92.0 tag's `imgui.h` defines `IMGUI_VERSION_NUM` as `19200` and contains `FontScaleDpi`, `ImGuiCol_TabSelected`, and `ImGuiCol_TabSelectedOverline`. The current docking branch defines `IMGUI_HAS_DOCK`, `DockSpaceOverViewport()`, `ConfigDpiScaleFonts`, and `ConfigDpiScaleViewports`. Dear ImGui's font documentation describes `FontScaleDpi` and `ScaleAllSizes()` for DPI handling, while the docking documentation describes the dockspace submission rules. [1] [2] [3] [4]

[1] [Dear ImGui v1.92.0 tag: `imgui.h`](https://github.com/ocornut/imgui/blob/v1.92.0/imgui.h)

[2] [Dear ImGui docking branch: `imgui.h`](https://github.com/ocornut/imgui/blob/docking/imgui.h)

[3] [Dear ImGui: using fonts and DPI](https://github.com/ocornut/imgui/blob/master/docs/FONTS.md)

[4] [Dear ImGui docking wiki](https://github.com/ocornut/imgui/wiki/Docking)
