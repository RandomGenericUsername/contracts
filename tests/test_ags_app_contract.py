"""Fixture gates for the standalone AGS app contract (REQ-009).

Each schema is checked as draft-07 and exercised by a positive and a negative
fixture. The install list also enforces the cross-entry uniqueness that draft-07
cannot express itself (``x-uniqueKeys`` in the schema).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "ags-app-contract"

SCHEMAS = {
    "ags-app-manifest": SCHEMA_DIR / "ags-app-manifest.schema.json",
    "ags-apps-install-list": SCHEMA_DIR / "ags-apps-install-list.schema.json",
    "program-tuple": SCHEMA_DIR / "program-tuple.schema.json",
    "ags-app-refresh-result": SCHEMA_DIR / "ags-app-refresh-result.schema.json",
}

VALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.valid.json"))
INVALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.invalid.json"))


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(name: str) -> Draft7Validator:
    return Draft7Validator(_load(SCHEMAS[name]))


def _unique_key_errors(document: Any, schema: dict[str, Any]) -> list[str]:
    """Enforce ``x-uniqueKeys`` on the install list's ``apps`` array."""
    if not isinstance(document, dict):
        return []
    apps_schema = schema.get("properties", {}).get("apps", {})
    keys = apps_schema.get("x-uniqueKeys", [])
    apps = document.get("apps", [])
    errors: list[str] = []
    if not isinstance(apps, list):
        return errors
    for key in keys:
        seen: dict[Any, int] = {}
        for index, entry in enumerate(apps):
            if not isinstance(entry, dict) or key not in entry:
                continue
            value = entry[key]
            if value in seen:
                errors.append(
                    f"apps[{index}].{key} duplicates apps[{seen[value]}].{key}: {value!r}"
                )
            else:
                seen[value] = index
    return errors


def _errors(schema_name: str, document: Any) -> list[str]:
    validator = _validator(schema_name)
    errors = [error.message for error in validator.iter_errors(document)]
    if schema_name == "ags-apps-install-list":
        errors.extend(_unique_key_errors(document, validator.schema))
    return errors


def _fixture_id(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_every_schema_is_draft_07_and_self_valid(name: str) -> None:
    schema = _load(SCHEMAS[name])
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["$id"] == f"https://dotfiles.local/schemas/{SCHEMAS[name].name}"
    Draft7Validator.check_schema(schema)


@pytest.mark.parametrize("path", VALID_FIXTURES, ids=_fixture_id)
def test_valid_fixture_is_accepted(path: Path) -> None:
    assert _errors(path.parent.name, _load(path)) == []


@pytest.mark.parametrize("path", INVALID_FIXTURES, ids=_fixture_id)
def test_invalid_fixture_is_rejected(path: Path) -> None:
    assert _errors(path.parent.name, _load(path)) != []


def test_manifest_rejects_restart_with_unsaved_state() -> None:
    document = _load(FIXTURE_DIR / "ags-app-manifest" / "restart-unsaved.invalid.json")
    errors = list(_validator("ags-app-manifest").iter_errors(document))
    assert any(list(error.path) == ["holdsUnsavedState"] for error in errors)


@pytest.mark.parametrize(
    ("fixture", "key"),
    [
        ("duplicate-app.invalid.json", "app"),
        ("duplicate-instance.invalid.json", "instance"),
        ("duplicate-config-link.invalid.json", "configLink"),
    ],
)
def test_install_list_rejects_duplicate_identity_key(fixture: str, key: str) -> None:
    document = _load(FIXTURE_DIR / "ags-apps-install-list" / fixture)
    errors = _errors("ags-apps-install-list", document)
    assert any("duplicates" in error and f".{key}" in error for error in errors)


def test_install_list_schema_names_every_unique_key() -> None:
    schema = _load(SCHEMAS["ags-apps-install-list"])
    assert schema["properties"]["apps"]["x-uniqueKeys"] == [
        "app",
        "instance",
        "configDir",
        "configLink",
        "spineLink",
        "xdgLink",
        "installDir",
    ]


def test_program_tuple_pins_exactly_the_three_program_tags() -> None:
    schema = _load(SCHEMAS["program-tuple"])
    assert set(schema["required"]) == {
        "schemaVersion",
        "ags-platform",
        "contracts",
        "dotfiles-assets",
    }
    assert set(schema["properties"]) == {
        "schemaVersion",
        "ags-platform",
        "contracts",
        "dotfiles-assets",
    }
    assert schema["additionalProperties"] is False


def test_refresh_result_covers_every_status_and_a_retryable_failure() -> None:
    statuses: set[str] = set()
    for path in sorted((FIXTURE_DIR / "ags-app-refresh-result").glob("*.valid.json")):
        document = _load(path)
        statuses.add(document["status"])
        if document["status"] == "failed" and document["retryable"] is True:
            assert document["reason"]
    assert statuses == {"applied", "deferred", "failed", "skipped"}


def test_wallpaper_state_note_is_progress_ui_not_the_refresh_trigger() -> None:
    notes = _load(REPO_ROOT / "event-contract.json")["topics"]["wallpaper.state"]["notes"]
    assert "progress/UI" in notes
    assert "not the palette-refresh trigger" in notes
    assert "LIVE refresh" not in notes

    prose = (REPO_ROOT / "event-contract.md").read_text(encoding="utf-8")
    paragraph = prose.split("`wallpaper.state` is emitted by", 1)[1].split(
        "`reload_failures` is", 1
    )[0]
    assert "not the palette-refresh trigger" in paragraph


def test_refresh_protocol_document_pins_the_transport_and_timeout() -> None:
    text = (REPO_ROOT / "ags-app-refresh.md").read_text(encoding="utf-8")
    for needle in (
        "ags request palette-refresh <appearance-hash> -i <instance>",
        "res(JSON.stringify(",
        "exactly once",
        "5 s",
        '{"ok":true}',
        '{"ok":true,"deferred":"reason"}',
        '{"ok":false,"error":"reason","retryable":true}',
        '{"ok":false,"error":"reason","retryable":false}',
    ):
        assert needle in text
