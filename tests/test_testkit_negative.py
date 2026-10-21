"""Negative conformance paths: every drift mode the kit exists to catch."""

from __future__ import annotations

import pytest

from cli_invocation_contract import get
from cli_invocation_contract.testkit import (
    assert_cli_writes_artifacts,
    assert_consumer_invocation,
)

from test_testkit_positive import CSG_FILENAMES, csg_argv, csg_env, write_csg_artifacts


def test_extra_argv_token_is_rejected() -> None:
    with pytest.raises(AssertionError, match="unexpected argv"):
        assert_consumer_invocation(
            get("csg"), "csg", csg_argv() + ["--output", "/tmp/out"], csg_env()
        )


def test_missing_template_token_is_rejected() -> None:
    with pytest.raises(AssertionError, match="render"):
        assert_consumer_invocation(get("itr"), "itr", ["itr"], csg_env())


def test_wrong_executable_is_rejected() -> None:
    with pytest.raises(AssertionError, match="does not address"):
        assert_consumer_invocation(get("csg"), "csg", csg_argv("/usr/bin/weg"), csg_env())


def test_missing_required_env_key_is_rejected() -> None:
    env = csg_env()
    del env["COLORSCHEME__OUTPUT__DIRECTORY"]
    with pytest.raises(AssertionError, match="COLORSCHEME__OUTPUT__DIRECTORY"):
        assert_consumer_invocation(get("csg"), "csg", csg_argv(), env)


def test_missing_itr_templates_dir_env_key_is_rejected() -> None:
    # REQ-008: the itr record requires the templates dir the runtime hashes.
    env = {
        "ICON_RENDERER__OUTPUT__OUTPUT_DIR": "/work/icons",
        "ICON_RENDERER__COLOR_SCHEME__PATH": "/work/pal/colors.yaml",
    }
    with pytest.raises(AssertionError, match="ICON_RENDERER__TEMPLATES__DIR"):
        assert_consumer_invocation(get("itr"), "itr", ["itr", "render"], env)


def test_wrong_literal_override_is_rejected() -> None:
    env = csg_env()
    env["COLORSCHEME__OUTPUT__OVERWRITE"] = "false"
    with pytest.raises(AssertionError, match="COLORSCHEME__OUTPUT__OVERWRITE"):
        assert_consumer_invocation(get("csg"), "csg", csg_argv(), env)


def test_empty_placeholder_is_rejected() -> None:
    argv = csg_argv()
    argv[2] = "   "
    with pytest.raises(AssertionError, match="empty value"):
        assert_consumer_invocation(get("csg"), "csg", argv, csg_env())


def test_record_paired_with_the_wrong_cli_is_rejected() -> None:
    with pytest.raises(AssertionError, match="describes binary"):
        assert_consumer_invocation(get("weg"), "csg", csg_argv(), csg_env())


def test_missing_exact_artifact_is_rejected(tmp_path) -> None:
    incomplete = [name for name in CSG_FILENAMES if name != "colors.btop.theme"]
    with pytest.raises(AssertionError, match="colors.btop.theme"):
        assert_cli_writes_artifacts(
            get("csg"), "csg", write_csg_artifacts(tmp_path, incomplete), tmp_path
        )


def test_missing_suffix_artifact_is_rejected(tmp_path) -> None:
    def run() -> int:
        (tmp_path / "battery-0.png").write_text("png", encoding="utf-8")
        return 0

    with pytest.raises(AssertionError, match="suffix"):
        assert_cli_writes_artifacts(get("itr"), "itr", run, tmp_path)


def test_nonzero_exit_is_rejected_even_with_artifacts(tmp_path) -> None:
    def run() -> int:
        write_csg_artifacts(tmp_path)()
        return 1

    with pytest.raises(AssertionError, match="exited 1"):
        assert_cli_writes_artifacts(get("csg"), "csg", run, tmp_path)


def test_unusable_runner_is_a_type_error(tmp_path) -> None:
    with pytest.raises(TypeError, match="callable or a sequence"):
        assert_cli_writes_artifacts(get("csg"), "csg", object(), tmp_path)
