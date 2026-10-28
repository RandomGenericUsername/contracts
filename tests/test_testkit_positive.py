"""Positive conformance paths: matching invocations and artifact-writing stand-ins."""

from __future__ import annotations

import sys
from pathlib import Path

from cli_invocation_contract import get
from cli_invocation_contract.testkit import (
    assert_cli_writes_artifacts,
    assert_consumer_invocation,
)

WALLPAPER = "/w/wallpaper.png"
CSG_FILENAMES = get("csg")["artifacts"]["filenames"]
TPR_FILENAMES = get("tpr")["artifacts"]["filenames"]


def csg_argv(executable: str = "csg") -> list[str]:
    return [executable, "generate", WALLPAPER, *get("csg")["argv"][2:]]


def csg_env(output_dir: str = "/work/pal") -> dict[str, str]:
    return {
        "COLORSCHEME__OUTPUT__DIRECTORY": output_dir,
        "COLORSCHEME__OUTPUT__OVERWRITE": "true",
        "PATH": "/usr/bin:/bin",
        "HOME": "/home/test",
    }


def write_csg_artifacts(root: Path, names: list[str] | None = None):
    def run() -> int:
        for name in names if names is not None else CSG_FILENAMES:
            (root / name).write_text("artifact", encoding="utf-8")
        return 0

    return run


def tpr_argv(executable: str = "tpr") -> list[str]:
    return [executable, "generate", WALLPAPER, *get("tpr")["argv"][2:]]


def tpr_env(output_dir: str = "/work/theme") -> dict[str, str]:
    return {
        "THEME__OUTPUT__DIRECTORY": output_dir,
        "THEME__OUTPUT__OVERWRITE": "true",
        "PATH": "/usr/bin:/bin",
        "HOME": "/home/test",
    }


def write_tpr_artifacts(root: Path, names: list[str] | None = None):
    def run() -> int:
        for name in names if names is not None else TPR_FILENAMES:
            (root / name).write_text("artifact", encoding="utf-8")
        return 0

    return run


def test_csg_recorded_invocation_is_accepted() -> None:
    assert_consumer_invocation(get("csg"), "csg", csg_argv(), csg_env())


def test_path_qualified_executable_is_accepted() -> None:
    assert_consumer_invocation(get("csg"), "csg", csg_argv("/usr/local/bin/csg"), csg_env())


def test_weg_recorded_invocation_is_accepted() -> None:
    env = {"WALLPAPER__OUTPUT__DIRECTORY": "/work/effects", "PATH": "/usr/bin"}
    argv = ["/opt/bin/weg", "batch", "all", "--", WALLPAPER]
    assert_consumer_invocation(get("weg"), "weg", argv, env)


def test_itr_optional_mappings_file_may_be_omitted_or_present() -> None:
    env = {
        "ICON_RENDERER__OUTPUT__OUTPUT_DIR": "/work/icons",
        "ICON_RENDERER__COLOR_SCHEME__PATH": "/work/pal/colors.yaml",
        "ICON_RENDERER__TEMPLATES__DIR": "/work/templates",
    }
    assert_consumer_invocation(get("itr"), "itr", ["itr", "render"], env)
    assert_consumer_invocation(
        get("itr"), "itr", ["itr", "render", "/spine/icon-mappings/icons.yaml"], env
    )


def test_tpr_recorded_invocation_is_accepted() -> None:
    assert_consumer_invocation(get("tpr"), "tpr", tpr_argv(), tpr_env())


def test_fake_tpr_writes_all_eight_artifacts(tmp_path: Path) -> None:
    found = assert_cli_writes_artifacts(
        get("tpr"), "tpr", write_tpr_artifacts(tmp_path), tmp_path
    )
    assert [path.name for path in found] == sorted(TPR_FILENAMES)
    assert len(found) == 8


def test_fake_csg_writes_all_exact_artifacts(tmp_path: Path) -> None:
    found = assert_cli_writes_artifacts(
        get("csg"), "csg", write_csg_artifacts(tmp_path), tmp_path
    )
    assert [path.name for path in found] == sorted(CSG_FILENAMES)
    assert len(found) == 8


def test_fake_itr_writes_a_nested_svg(tmp_path: Path) -> None:
    def run() -> None:
        (tmp_path / "battery").mkdir()
        (tmp_path / "battery" / "battery-0.svg").write_text("<svg/>", encoding="utf-8")

    found = assert_cli_writes_artifacts(get("itr"), "itr", run, tmp_path)
    assert [path.name for path in found] == ["battery-0.svg"]


def test_fake_weg_writes_nested_images(tmp_path: Path) -> None:
    def run() -> int:
        nested = tmp_path / "deep" / "deeper"
        nested.mkdir(parents=True)
        (nested / "wallpaper.webp").write_text("img", encoding="utf-8")
        (tmp_path / "top.jpeg").write_text("img", encoding="utf-8")
        (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")
        return 0

    found = assert_cli_writes_artifacts(get("weg"), "weg", run, tmp_path)
    assert sorted(path.name for path in found) == ["top.jpeg", "wallpaper.webp"]


def test_argv_runner_is_executed_in_cwd(tmp_path: Path) -> None:
    script = (
        "from pathlib import Path\n"
        f"for name in {CSG_FILENAMES!r}:\n"
        "    Path(name).write_text('artifact', encoding='utf-8')\n"
    )
    argv = [sys.executable, "-c", script]
    found = assert_cli_writes_artifacts(get("csg"), "csg", argv, tmp_path)
    assert len(found) == 8
    assert all(path.is_file() for path in found)
