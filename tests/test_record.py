"""Record completeness: every CLI, every field, every S1 literal."""

from __future__ import annotations

import pytest

from cli_invocation_contract import CONTRACT_VERSION, DATA_VERSION, get, load

CSG_FILENAMES = [
    "colors.yaml",
    "colors.conf",
    "colors.gtk.css",
    "colors.adw.css",
    "colors.sequences",
    "colors.rasi",
    "colors.kitty",
    "colors.btop.theme",
]

CSG_ARGV = [
    "generate",
    "{wallpaper}",
    "--format",
    "yaml",
    "--format",
    "conf",
    "--format",
    "gtk.css",
    "--format",
    "adw.css",
    "--format",
    "sequences",
    "--format",
    "rasi",
    "--format",
    "kitty",
    "--format",
    "btop.theme",
]


def test_contract_version_is_the_release_version() -> None:
    # AD-11: the version a CLI reports equals the pinned `contracts` tag (v0.3.0).
    assert CONTRACT_VERSION == "0.3.0"


def test_data_version_is_the_json_shape_version() -> None:
    assert DATA_VERSION == 2


def test_three_cli_records() -> None:
    assert sorted(load()) == ["csg", "itr", "weg"]


@pytest.mark.parametrize("cli", ["csg", "weg", "itr"])
def test_every_record_carries_the_contract_fields(cli: str) -> None:
    record = get(cli)
    assert set(record) >= {"binary", "argv", "env", "artifacts", "exit_codes", "timeout"}
    assert record["binary"] == cli
    assert isinstance(record["argv"], list) and record["argv"]
    assert all(isinstance(token, str) and token for token in record["argv"])
    assert isinstance(record["timeout"], int) and record["timeout"] > 0


def test_csg_argv_is_the_observed_generation_call() -> None:
    assert get("csg")["argv"] == CSG_ARGV
    argv = get("csg")["argv"]
    assert argv.count("--format") == 8
    assert "-o" not in argv and "--output" not in argv


def test_csg_artifacts_are_exact_filenames() -> None:
    artifacts = get("csg")["artifacts"]
    assert artifacts["match"] == "exact_filename"
    assert artifacts["recursive"] is False
    assert artifacts["filenames"] == CSG_FILENAMES
    assert artifacts["min_count"] == 8


def test_weg_argv_keeps_the_separator() -> None:
    assert get("weg")["argv"] == ["batch", "all", "--", "{wallpaper}"]


def test_weg_artifacts_are_a_recursive_image_scan() -> None:
    artifacts = get("weg")["artifacts"]
    assert artifacts["match"] == "suffix"
    assert artifacts["recursive"] is True
    assert artifacts["suffixes"] == [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"]
    assert artifacts["min_count"] == 1


def test_itr_argv_has_an_optional_mappings_file() -> None:
    assert get("itr")["argv"] == ["render", "{mappings_file}?"]
    assert "{mappings_file}" in get("itr")["placeholders"]


def test_itr_artifacts_are_a_recursive_svg_scan() -> None:
    artifacts = get("itr")["artifacts"]
    assert artifacts["match"] == "suffix"
    assert artifacts["recursive"] is True
    assert artifacts["suffixes"] == [".svg"]
    assert artifacts["min_count"] == 1


def test_env_keys_and_injected_overrides() -> None:
    csg = get("csg")["env"]
    assert csg["required"] == [
        "COLORSCHEME__OUTPUT__DIRECTORY",
        "COLORSCHEME__OUTPUT__OVERWRITE",
    ]
    assert csg["injected"] == {
        "COLORSCHEME__OUTPUT__DIRECTORY": "{output_dir}",
        "COLORSCHEME__OUTPUT__OVERWRITE": "true",
    }

    weg = get("weg")["env"]
    assert weg["required"] == ["WALLPAPER__OUTPUT__DIRECTORY"]
    assert weg["injected"] == {"WALLPAPER__OUTPUT__DIRECTORY": "{output_dir}"}

    itr = get("itr")["env"]
    assert itr["required"] == [
        "ICON_RENDERER__OUTPUT__OUTPUT_DIR",
        "ICON_RENDERER__COLOR_SCHEME__PATH",
        "ICON_RENDERER__TEMPLATES__DIR",
    ]
    assert itr["injected"] == {
        "ICON_RENDERER__OUTPUT__OUTPUT_DIR": "{output_dir}",
        "ICON_RENDERER__COLOR_SCHEME__PATH": "{palette_colors_yaml}",
        "ICON_RENDERER__TEMPLATES__DIR": "{templates_dir}",
    }


def test_itr_env_names_the_templates_directory() -> None:
    # REQ-008: the runtime hashes templates_dir, so the invocation must forward it.
    # itr binds ICON_RENDERER__TEMPLATES__DIR to templates.dir (env > settings > discovery).
    env = get("itr")["env"]
    assert "ICON_RENDERER__TEMPLATES__DIR" in env["required"]
    assert env["injected"]["ICON_RENDERER__TEMPLATES__DIR"] == "{templates_dir}"
    assert set(env["required"]) == set(env["injected"])


@pytest.mark.parametrize("cli", ["csg", "weg"])
def test_templates_dir_env_key_is_itr_only(cli: str) -> None:
    env = get(cli)["env"]
    assert "ICON_RENDERER__TEMPLATES__DIR" not in env["required"]
    assert "ICON_RENDERER__TEMPLATES__DIR" not in env["injected"]


@pytest.mark.parametrize("cli", ["csg", "weg", "itr"])
def test_exit_codes_mean_zero_plus_artifacts(cli: str) -> None:
    exit_codes = get(cli)["exit_codes"]
    assert exit_codes["success"] == 0
    assert exit_codes["nonzero_is_failure"] is True
    assert exit_codes["success_requires_artifacts"] is True


@pytest.mark.parametrize(("cli", "timeout"), [("csg", 60), ("weg", 600), ("itr", 60)])
def test_default_timeouts(cli: str, timeout: int) -> None:
    assert get(cli)["timeout"] == timeout
