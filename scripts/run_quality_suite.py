#!/usr/bin/env python3
"""Run structural, semantic, static-checker, and compile regression gates for this skill.

Usage:
  python3 scripts/run_quality_suite.py
  python3 scripts/run_quality_suite.py --imgui-dir /path/to/vendored/imgui
  python3 scripts/run_quality_suite.py --semantic-responses /path/to/responses.json

Every normal run fetches temporary official Dear ImGui v1.92.0 and master sources, then
compiles the bundled templates against both. --imgui-dir adds a product fork or pinned
revision. The harness never executes generated C++ binaries. Use --skip-official-revisions
only for an explicitly offline structural/static-checker run; it is not a release gate.
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CHECKER = SKILL_DIR / "scripts" / "check_imgui_cpp.py"
PANEL_TEMPLATE = SKILL_DIR / "templates" / "imgui_panel_skeleton.cpp.in"
THEME_TEMPLATE = SKILL_DIR / "templates" / "imgui_design_system.h.in"
BALANCED_FIXTURE = SKILL_DIR / "evals" / "fixtures" / "balanced_scopes.cpp"
UNBALANCED_FIXTURE = SKILL_DIR / "evals" / "fixtures" / "unbalanced_push_id.cpp"
QUALITY_SUITE = SKILL_DIR / "evals" / "quality-suite.md"
FAILURE_MODE_REGRESSIONS = SKILL_DIR / "evals" / "failure-mode-regressions.md"
SEMANTIC_CASES = SKILL_DIR / "evals" / "semantic-cases.json"
SEMANTIC_RESPONSES = SKILL_DIR / "evals" / "fixtures" / "reference-responses.json"
SEMANTIC_RUNNER = SKILL_DIR / "scripts" / "run_semantic_suite.py"
REQUIRED_FILES = (
    SKILL_DIR / "LICENSE",
    SKILL_DIR / "README.md",
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "design-playbook.md",
    SKILL_DIR / "references" / "version-notes.md",
    SKILL_DIR / "references" / "worked-example.md",
    QUALITY_SUITE,
    FAILURE_MODE_REGRESSIONS,
    SEMANTIC_CASES,
    SEMANTIC_RESPONSES,
    SEMANTIC_RUNNER,
    CHECKER,
    PANEL_TEMPLATE,
    THEME_TEMPLATE,
    BALANCED_FIXTURE,
    UNBALANCED_FIXTURE,
)

# Keep this matrix small and evidence-backed. It checks the documented baseline and
# the maintained mainline API surface without placing cloned sources in the skill package.
OFFICIAL_IMGUI_REVISIONS = ("v1.92.0", "master")
OFFICIAL_IMGUI_REPOSITORY = "https://github.com/ocornut/imgui.git"


def run(command: list[str], label: str, expect_success: bool = True) -> bool:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    actual_success = completed.returncode == 0
    passed = actual_success == expect_success
    print(f"{'PASS' if passed else 'FAIL'} {label}")
    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.stderr.strip():
        stream = sys.stdout if passed and not expect_success else sys.stderr
        print(completed.stderr.strip(), file=stream)
    return passed


def check_required_files() -> bool:
    missing = [str(path.relative_to(SKILL_DIR)) for path in REQUIRED_FILES if not path.is_file() or path.stat().st_size == 0]
    if missing:
        print(f"FAIL package resources missing or empty: {', '.join(missing)}", file=sys.stderr)
        return False
    print("PASS package resources are present.")
    return True


def check_agent_skills_frontmatter() -> bool:
    """Validate the portable Agent Skills fields without adding a YAML dependency."""
    source = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    if not source.startswith("---\n") or "\n---\n" not in source[4:]:
        print("FAIL SKILL.md must begin with a YAML frontmatter block.", file=sys.stderr)
        return False
    frontmatter = source.split("\n---\n", 1)[0][4:]

    def scalar(field: str) -> str | None:
        match = re.search(rf"^{re.escape(field)}:\s*(.+?)\s*$", frontmatter, re.MULTILINE)
        return match.group(1).strip().strip('"\'') if match else None

    name = scalar("name")
    description = scalar("description")
    license_name = scalar("license")
    compatibility = scalar("compatibility")
    errors: list[str] = []
    if name is None or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None or len(name) > 64:
        errors.append("name must be 1-64 lowercase alphanumeric/hyphen characters")
    elif name != SKILL_DIR.name:
        errors.append(f"name '{name}' must match parent directory '{SKILL_DIR.name}'")
    if description is None or not 1 <= len(description) <= 1024:
        errors.append("description must contain 1-1024 characters")
    if license_name != "MIT":
        errors.append("license must reference the bundled MIT license")
    if compatibility is None or not 1 <= len(compatibility) <= 500:
        errors.append("compatibility must contain 1-500 characters")
    if not re.search(r"^metadata:\s*$", frontmatter, re.MULTILINE):
        errors.append("metadata mapping is required for author and index fields")
    if errors:
        print(f"FAIL Agent Skills frontmatter: {'; '.join(errors)}", file=sys.stderr)
        return False
    print("PASS Agent Skills frontmatter, naming, license, compatibility, and metadata checks.")
    return True


def check_english_and_markers() -> bool:
    turkish_specific = re.compile(r"[\u011f\u00fc\u015f\u0131\u00f6\u00e7\u011e\u00dc\u015e\u0130\u00d6\u00c7]")
    unfinished_marker = "TO" + "DO"
    todo = re.compile(r"\[" + unfinished_marker + r"\]|" + unfinished_marker + ":")
    offenders: list[str] = []
    content_suffixes = {".md", ".yaml", ".json", ".py", ".in", ".cpp"}
    for path in SKILL_DIR.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix not in content_suffixes:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if turkish_specific.search(text) or todo.search(text):
            offenders.append(str(path.relative_to(SKILL_DIR)))
    if offenders:
        print(f"FAIL language/template-marker check: {', '.join(offenders)}", file=sys.stderr)
        return False
    print("PASS English-only and unfinished-marker checks.")
    return True


def check_skill_size() -> bool:
    line_count = len((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines())
    if line_count >= 500:
        print(f"FAIL SKILL.md has {line_count} lines; expected fewer than 500.", file=sys.stderr)
        return False
    print(f"PASS SKILL.md line-count guard ({line_count}/499).")
    return True


def check_eval_inventory() -> bool:
    quality_text = QUALITY_SUITE.read_text(encoding="utf-8")
    failure_text = FAILURE_MODE_REGRESSIONS.read_text(encoding="utf-8")
    quality_case_count = len(re.findall(r"\| E\d\d\s+—", quality_text))
    failure_case_count = len(re.findall(r"\| F\d\d\s+—", failure_text))
    if quality_case_count < 10 or failure_case_count < 5:
        print(
            f"FAIL evaluation coverage has {quality_case_count} standard and "
            f"{failure_case_count} failure-mode cases; expected at least 10 and 5.",
            file=sys.stderr,
        )
        return False
    print(
        f"PASS evaluation inventory declares {quality_case_count} standard and "
        f"{failure_case_count} failure-mode scenarios."
    )
    return True


def check_theme_contrast() -> bool:
    """Verify normal-size text contrast for every filled button interaction state."""
    source = THEME_TEMPLATE.read_text(encoding="utf-8")
    color_re = re.compile(
        r"ImVec4\s+(?P<name>\w+)\s*=\s*ImVec4\("
        r"(?P<r>[0-9.]+)f,\s*(?P<g>[0-9.]+)f,\s*(?P<b>[0-9.]+)f,"
    )
    colors = {
        match.group("name"): tuple(float(match.group(channel)) for channel in ("r", "g", "b"))
        for match in color_re.finditer(source)
    }
    required_backgrounds = (
        "buttonSurface",
        "buttonSurfaceHover",
        "buttonSurfaceActive",
        "dangerSurface",
        "dangerSurfaceHover",
        "dangerSurfaceActive",
    )
    missing = [name for name in ("contentPrimary", *required_backgrounds) if name not in colors]
    if missing:
        print(f"FAIL theme contrast tokens missing: {', '.join(missing)}", file=sys.stderr)
        return False

    def luminance(rgb: tuple[float, float, float]) -> float:
        channels = [
            value / 12.92 if value <= 0.04045 else math.pow((value + 0.055) / 1.055, 2.4)
            for value in rgb
        ]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    foreground_luminance = luminance(colors["contentPrimary"])
    failures: list[str] = []
    for name in required_backgrounds:
        background_luminance = luminance(colors[name])
        lighter = max(foreground_luminance, background_luminance)
        darker = min(foreground_luminance, background_luminance)
        contrast = (lighter + 0.05) / (darker + 0.05)
        if contrast < 4.5:
            failures.append(f"{name}={contrast:.2f}:1")
    if failures:
        print(f"FAIL filled-button text contrast below 4.5:1: {', '.join(failures)}", file=sys.stderr)
        return False
    print("PASS filled-button text contrast is at least 4.5:1 in every interaction state.")
    return True


def compile_templates(imgui_dir: Path) -> bool:
    imgui_header = imgui_dir / "imgui.h"
    if not imgui_header.is_file():
        print(f"FAIL {imgui_dir}: imgui.h not found.", file=sys.stderr)
        return False
    compiler = shutil.which("g++") or shutil.which("c++")
    if compiler is None:
        print("FAIL no C++ compiler found (expected g++ or c++).", file=sys.stderr)
        return False

    # Keep generated build inputs inside the writable skill workspace. Managed runners may
    # expose a readable system temp directory while denying child work-tree creation there.
    with tempfile.TemporaryDirectory(prefix=".imgui-skill-compile-", dir=SKILL_DIR) as temp_dir:
        temp = Path(temp_dir)
        shutil.copy2(PANEL_TEMPLATE, temp / "imgui_panel_skeleton.cpp")
        shutil.copy2(THEME_TEMPLATE, temp / "imgui_design_system.h")
        command = [
            compiler,
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-I{imgui_dir}",
            f"-I{temp}",
            "-c",
            str(temp / "imgui_panel_skeleton.cpp"),
            "-o",
            str(temp / "imgui_panel_skeleton.o"),
        ]
        return run(command, f"compile templates against {imgui_dir}")


def compile_official_revisions() -> list[bool]:
    git = shutil.which("git")
    if git is None:
        print("FAIL git is required for --official-revisions.", file=sys.stderr)
        return [False]

    results: list[bool] = []
    with tempfile.TemporaryDirectory(prefix=".imgui-skill-official-", dir=SKILL_DIR) as temp_dir:
        root = Path(temp_dir)
        for revision in OFFICIAL_IMGUI_REVISIONS:
            destination = root / revision.replace("/", "_")
            fetched = False
            for attempt in range(1, 4):
                if destination.exists():
                    shutil.rmtree(destination)
                fetched = run(
                    [git, "clone", "--depth", "1", "--branch", revision,
                     OFFICIAL_IMGUI_REPOSITORY, str(destination)],
                    f"fetch official Dear ImGui {revision} (attempt {attempt}/3)",
                )
                if fetched:
                    break
                if attempt < 3:
                    time.sleep(float(attempt))
            results.append(fetched)
            if fetched:
                results.append(compile_templates(destination))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Dear ImGui UI/UX Engineering quality gates.")
    parser.add_argument(
        "--imgui-dir",
        type=Path,
        action="append",
        default=[],
        metavar="DIR",
        help="Directory containing the target project's imgui.h; may be supplied multiple times.",
    )
    parser.add_argument(
        "--require-compile",
        action="store_true",
        help="Compatibility flag; official v1.92.0 and master compilation already run by default.",
    )
    parser.add_argument(
        "--official-revisions",
        action="store_true",
        help="Compatibility flag; official v1.92.0 and master compilation already run by default.",
    )
    parser.add_argument(
        "--skip-official-revisions",
        action="store_true",
        help="Explicit offline opt-out. Runs structural/semantic/static checks but is not a release gate.",
    )
    parser.add_argument(
        "--semantic-responses",
        type=Path,
        metavar="FILE",
        help="Additionally score a target model's E01-E10/F01-F05 response JSON object.",
    )
    args = parser.parse_args()

    checks = [
        check_required_files(),
        check_agent_skills_frontmatter(),
        check_english_and_markers(),
        check_skill_size(),
        check_eval_inventory(),
        check_theme_contrast(),
    ]

    try:
        compile(CHECKER.read_text(encoding="utf-8"), str(CHECKER), "exec")
        print("PASS static checker syntax compiles.")
    except (OSError, SyntaxError) as error:
        print(f"FAIL static checker syntax: {error}", file=sys.stderr)
        checks.append(False)

    checks.append(run([sys.executable, str(CHECKER), str(PANEL_TEMPLATE), str(BALANCED_FIXTURE)],
                      "static checker passes production template and balanced fixture"))
    checks.append(run([sys.executable, str(CHECKER), "--quiet", str(UNBALANCED_FIXTURE)],
                      "static checker rejects intentionally unbalanced fixture", expect_success=False))
    checks.append(run([sys.executable, str(SEMANTIC_RUNNER), "--cases", str(SEMANTIC_CASES),
                       "--responses", str(SEMANTIC_RESPONSES)],
                      "reference responses satisfy every semantic contract"))
    if args.semantic_responses is not None:
        checks.append(run([sys.executable, str(SEMANTIC_RUNNER), "--cases", str(SEMANTIC_CASES),
                           "--responses", str(args.semantic_responses.resolve())],
                          "target model responses satisfy every semantic contract"))

    if args.skip_official_revisions and args.require_compile and not args.imgui_dir:
        print("FAIL --require-compile cannot be combined with an offline-only run.", file=sys.stderr)
        checks.append(False)
    for imgui_dir in args.imgui_dir:
        checks.append(compile_templates(imgui_dir.resolve()))
    if args.skip_official_revisions:
        print("WARNING official compile regression explicitly skipped; this is not a release-gate result.")
    else:
        checks.extend(compile_official_revisions())
    if all(checks):
        print("ALL AUTOMATED STRUCTURAL, SEMANTIC, AND COMPILE GATES PASSED")
        return 0
    print("QUALITY GATES FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
