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

TPR_FILENAMES = [
    "colors.yaml",
    "colors.conf",
    "colors.gtk.css",
    "colors.adw.css",
    "colors.sequences",
    "colors.rasi",
    "colors.kitty",
    "colors.btop.theme",
]

TPR_ARGV = [
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
    # AD-11: the version a CLI reports equals the pinned `contracts` tag (v0.4.0).
    assert CONTRACT_VERSION == "0.4.0"


def test_data_version_is_the_json_shape_version() -> None:
    assert DATA_VERSION == 2


def test_four_cli_records() -> None:
    assert sorted(load()) == ["csg", "itr", "tpr", "weg"]


@pytest.mark.parametrize("cli", ["csg", "weg", "itr", "tpr"])
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


def test_tpr_argv_is_the_observed_generation_call() -> None:
    record = get("tpr")
    assert record["binary"] == "tpr"
    assert record["argv"] == TPR_ARGV
    assert record["argv"].count("--format") == 8
    assert "-o" not in record["argv"] and "--output" not in record["argv"]


def test_tpr_artifacts_are_the_eight_consumer_files() -> None:
    artifacts = get("tpr")["artifacts"]
    assert artifacts["match"] == "exact_filename"
    assert artifacts["recursive"] is False
    assert artifacts["filenames"] == TPR_FILENAMES
    assert len(artifacts["filenames"]) == 8
    assert artifacts["min_count"] == 8
    # theme.json is canonical for tpr but not a palette-entry artifact (non-goal).
    assert "theme.json" not in artifacts["filenames"]


def test_tpr_env_carries_the_theme_output_overrides() -> None:
    env = get("tpr")["env"]
    assert env["required"] == [
        "THEME__OUTPUT__DIRECTORY",
        "THEME__OUTPUT__OVERWRITE",
    ]
    assert env["injected"] == {
        "THEME__OUTPUT__DIRECTORY": "{output_dir}",
        "THEME__OUTPUT__OVERWRITE": "true",
    }


def test_tpr_placeholder_is_the_plain_wallpaper_positional() -> None:
    assert get("tpr")["placeholders"] == {
        "{wallpaper}": (
            "path to the input wallpaper file, supplied as a plain positional argument"
        )
    }


@pytest.mark.parametrize("cli", ["csg", "weg", "itr"])
def test_existing_records_are_unchanged(cli: str) -> None:
    # REQ-010 is additive: the tpr record must not touch the other three.
    record = get(cli)
    assert record["binary"] == cli
    assert record["timeout"] == {"csg": 60, "weg": 600, "itr": 60}[cli]
    assert "THEME__OUTPUT__DIRECTORY" not in record["env"]["required"]
    assert "THEME__OUTPUT__OVERWRITE" not in record["env"]["required"]
    if cli == "csg":
        assert record["argv"] == CSG_ARGV
        assert record["artifacts"]["filenames"] == CSG_FILENAMES
    elif cli == "weg":
        assert record["argv"] == ["batch", "all", "--", "{wallpaper}"]
    else:
        assert record["argv"] == ["render", "{mappings_file}?"]


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


@pytest.mark.parametrize("cli", ["csg", "weg", "itr", "tpr"])
def test_exit_codes_mean_zero_plus_artifacts(cli: str) -> None:
    exit_codes = get(cli)["exit_codes"]
    assert exit_codes["success"] == 0
    assert exit_codes["nonzero_is_failure"] is True
    assert exit_codes["success_requires_artifacts"] is True


@pytest.mark.parametrize(
    ("cli", "timeout"), [("csg", 60), ("weg", 600), ("itr", 60), ("tpr", 60)]
)
def test_default_timeouts(cli: str, timeout: int) -> None:
    assert get(cli)["timeout"] == timeout
