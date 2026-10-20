"""Loader and get() behavior, including the failure modes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli_invocation_contract import DATA_VERSION, UnknownCliError, get, load


def _write(tmp_path: Path, document: object) -> Path:
    path = tmp_path / "invocation-contract.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_default_load_returns_all_records() -> None:
    records = load()
    assert sorted(records) == ["csg", "itr", "weg"]
    assert all(isinstance(record, dict) for record in records.values())


def test_explicit_path_is_honoured(tmp_path: Path) -> None:
    path = _write(tmp_path, {"contract_version": DATA_VERSION, "clis": load()})
    records = load(path)
    assert sorted(records) == ["csg", "itr", "weg"]
    assert records["csg"]["binary"] == "csg"


def test_get_returns_one_record() -> None:
    assert get("csg")["binary"] == "csg"
    assert get("weg")["binary"] == "weg"
    assert get("itr")["binary"] == "itr"


def test_unknown_cli_raises_unknown_cli_error() -> None:
    with pytest.raises(UnknownCliError) as caught:
        get("nope")
    assert isinstance(caught.value, KeyError)
    assert "nope" in str(caught.value)
    assert "csg" in str(caught.value)


def test_version_mismatch_raises_value_error(tmp_path: Path) -> None:
    path = _write(tmp_path, {"contract_version": DATA_VERSION + 1, "clis": load()})
    with pytest.raises(ValueError, match="version mismatch"):
        load(path)


def test_record_missing_a_contract_field_raises_value_error(tmp_path: Path) -> None:
    records = load()
    del records["itr"]["timeout"]
    path = _write(tmp_path, {"contract_version": DATA_VERSION, "clis": records})
    with pytest.raises(ValueError, match="timeout"):
        load(path)


def test_empty_clis_raises_value_error(tmp_path: Path) -> None:
    path = _write(tmp_path, {"contract_version": DATA_VERSION, "clis": {}})
    with pytest.raises(ValueError, match="clis"):
        load(path)


def test_returned_records_are_copies() -> None:
    first = load()
    first["csg"]["binary"] = "mutated"
    assert load()["csg"]["binary"] == "csg"
