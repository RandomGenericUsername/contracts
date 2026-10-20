"""The kit's public surface and dependency floor."""

from __future__ import annotations

import inspect
from pathlib import Path

import cli_invocation_contract
import cli_invocation_contract.testkit as testkit

ALLOWED_MODULES = {"os", "re", "subprocess", "pathlib", "typing", "collections.abc"}


def _imports(source: str) -> list[str]:
    return [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]


def test_public_surface_is_exactly_two_assertions() -> None:
    assert testkit.__all__ == [
        "assert_cli_writes_artifacts",
        "assert_consumer_invocation",
    ]
    for name in testkit.__all__:
        assert callable(getattr(testkit, name))


def test_kit_source_has_no_third_party_import_and_no_pytest() -> None:
    source = Path(inspect.getfile(testkit)).read_text(encoding="utf-8")
    imports = _imports(source)
    assert not any("pytest" in line for line in imports)
    for line in imports:
        if line.startswith("from __future__"):
            continue
        module = line.split()[1].split(".")[0]
        if line.startswith("from collections"):
            module = "collections.abc"
        assert module in ALLOWED_MODULES, line


def test_package_has_no_third_party_import() -> None:
    source = Path(inspect.getfile(cli_invocation_contract)).read_text(encoding="utf-8")
    for line in _imports(source):
        if line.startswith("from __future__"):
            continue
        module = line.split()[1].split(".")[0]
        assert module not in {"pytest", "typer", "rich", "yaml"}, line
