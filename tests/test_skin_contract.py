"""Fixture gates for the frozen skin-plane contract v1 (REQ-011).

Both schemas are checked as draft-07 and exercised by positive and negative
fixtures. The manifest is the runtime-facing document; the token schema is the
flat vocabulary used to cross-check that every group token is declared exactly
once.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "skin-contract"

SCHEMAS = {
    "skin-token": SCHEMA_DIR / "skin-token.schema.json",
    "skin-manifest": SCHEMA_DIR / "skin-manifest.schema.json",
}

VALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.valid.json"))
INVALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.invalid.json"))

GROUPS = ("shape", "surface", "ink", "type", "rhythm", "layout")

PALETTE_V1_ROLES = {
    "background",
    "error",
    "error_container",
    "inverse_on_surface",
    "inverse_primary",
    "inverse_surface",
    "on_background",
    "on_error",
    "on_error_container",
    "on_primary",
    "on_primary_container",
    "on_primary_fixed",
    "on_primary_fixed_variant",
    "on_secondary",
    "on_secondary_container",
    "on_secondary_fixed",
    "on_secondary_fixed_variant",
    "on_surface",
    "on_surface_variant",
    "on_tertiary",
    "on_tertiary_container",
    "on_tertiary_fixed",
    "on_tertiary_fixed_variant",
    "outline",
    "outline_variant",
    "primary",
    "primary_container",
    "primary_fixed",
    "primary_fixed_dim",
    "scrim",
    "secondary",
    "secondary_container",
    "secondary_fixed",
    "secondary_fixed_dim",
    "shadow",
    "source_color",
    "surface",
    "surface_bright",
    "surface_container",
    "surface_container_high",
    "surface_container_highest",
    "surface_container_low",
    "surface_container_lowest",
    "surface_dim",
    "surface_tint",
    "surface_variant",
    "tertiary",
    "tertiary_container",
    "tertiary_fixed",
    "tertiary_fixed_dim",
    "on_backdrop",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(name: str) -> Draft7Validator:
    return Draft7Validator(_load(SCHEMAS[name]))


def _errors(schema_name: str, document: Any) -> list[str]:
    return [error.message for error in _validator(schema_name).iter_errors(document)]


def _error_text(schema_name: str, document: Any) -> str:
    return "\n".join(_errors(schema_name, document))


def _fixture_id(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_every_schema_is_draft_07_self_valid_and_frozen(name: str) -> None:
    schema = _load(SCHEMAS[name])
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["$id"] == f"https://dotfiles.local/schemas/{SCHEMAS[name].name}"
    assert schema["status"] == "frozen"
    Draft7Validator.check_schema(schema)


@pytest.mark.parametrize("path", VALID_FIXTURES, ids=_fixture_id)
def test_valid_fixture_is_accepted(path: Path) -> None:
    assert _errors(path.parent.name, _load(path)) == []


@pytest.mark.parametrize("path", INVALID_FIXTURES, ids=_fixture_id)
def test_invalid_fixture_is_rejected(path: Path) -> None:
    assert _errors(path.parent.name, _load(path)) != []


def test_manifest_requires_exactly_the_six_groups() -> None:
    groups = _load(SCHEMAS["skin-manifest"])["properties"]["groups"]
    assert list(groups["required"]) == list(GROUPS)
    assert set(groups["properties"]) == set(GROUPS)
    assert groups["additionalProperties"] is False


def test_token_vocabulary_matches_the_manifest_groups() -> None:
    token_schema = _load(SCHEMAS["skin-token"])
    manifest_groups = _load(SCHEMAS["skin-manifest"])["properties"]["groups"]["properties"]
    flat_tokens = set(token_schema["properties"])
    grouped_tokens = {
        token
        for group in GROUPS
        for token in manifest_groups[group]["properties"]
    }
    assert flat_tokens == grouped_tokens
    assert set(token_schema["required"]) == grouped_tokens
    for group in GROUPS:
        assert set(manifest_groups[group]["required"]) == set(
            manifest_groups[group]["properties"]
        )


def test_palette_enum_is_exactly_palette_v1() -> None:
    roles = _load(SCHEMAS["skin-token"])["definitions"]["paletteRole"]["enum"]
    assert len(roles) == 51
    assert set(roles) == PALETTE_V1_ROLES
    assert "on_backdrop" in roles


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("literal-hex.invalid.json", "#"),
        ("transition-value.invalid.json", "transition"),
        ("transition-key.invalid.json", "transition"),
        ("structure.invalid.json", "structure"),
        ("variant-token.invalid.json", "variant"),
        ("unknown-token.invalid.json", "radius-widget"),
        ("blur-value.invalid.json", "blur"),
        ("calc-percent.invalid.json", "calc"),
        ("unknown-role.invalid.json", "brand"),
        ("extra-top-level.invalid.json", "structure"),
    ],
)
def test_named_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "skin-manifest" / fixture)
    assert needle in _error_text("skin-manifest", document)


def test_structure_and_variant_are_rejected_at_every_level() -> None:
    manifest = _load(SCHEMAS["skin-manifest"])
    token = _load(SCHEMAS["skin-token"])
    for schema in (manifest, token):
        assert "$ref" in schema["propertyNames"]
        ref = schema["propertyNames"]["$ref"].split("/")[-1]
        forbidden = schema["definitions"][ref]["not"]
        patterns = [entry["pattern"] for entry in forbidden["anyOf"]]
        assert "(?:^|_)(?:structure|order|presence)(?:_|$)" in patterns
        assert "variant" in patterns


def test_ink_over_is_derived_and_only_auto_is_legal() -> None:
    manifest_schema = _load(SCHEMAS["skin-manifest"])
    ink_over = manifest_schema["properties"]["groups"]["properties"]["ink"]["properties"][
        "ink-over"
    ]
    assert ink_over["const"] == "auto"


def test_layout_tokens_are_numbers_and_surface_has_the_blur_exception() -> None:
    manifest = _load(SCHEMAS["skin-manifest"])
    groups = manifest["properties"]["groups"]["properties"]
    layout = groups["layout"]["properties"]
    assert set(layout) == {"panel-width", "bt-list-spacing", "bar-row-height", "chip-min"}
    assert all(schema["$ref"].endswith("/number") for schema in layout.values())
    surface = groups["surface"]["properties"]
    assert surface["blur"]["$ref"].endswith("/blurValue")
    for token in ("bg-panel", "bg-card", "border", "shadow"):
        assert surface[token]["$ref"].endswith("/paint")


def test_skins_doc_pins_the_runtime_contract() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        'desired.json',
        'skin: "<name>"',
        "sha256(template_set_hash ‖ manifest_hash)",
        "appearance hash",
        "Gtk.CssProvider",
        "USER priority (800)",
        "re-installed LAST",
        "module-scoped",
        "near-black",
        "ink-over",
        "glass",
        "flat",
        "paper",
        "restart",
    ):
        assert needle in text
