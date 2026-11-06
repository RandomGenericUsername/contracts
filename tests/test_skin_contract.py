"""Fixture gates for the frozen skin-plane contract v1 (REQ-011).

Both schemas are checked as draft-07 and exercised by positive and negative
fixtures. The manifest is the runtime-facing document; the token schema is the
flat vocabulary used to cross-check that every group token is declared exactly
once.
"""

from __future__ import annotations

import json
import re
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
    "skin-json": SCHEMA_DIR / "skin-json.schema.json",
}

VALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.valid.json"))
INVALID_FIXTURES = sorted(FIXTURE_DIR.glob("*/*.invalid.json"))

GROUPS = ("shape", "surface", "ink", "type", "rhythm", "layout")

# The thirteen numeric tokens and the manifest group each one lives in. These are
# unitless JSON numbers; only cell-pad is a literal "Npx Npx" CSS length pair.
NUMERIC_TOKEN_GROUPS = {
    "radius-panel": "shape",
    "radius-card": "shape",
    "radius-cell": "shape",
    "radius-pill": "shape",
    "border-w": "shape",
    "hairline-w": "shape",
    "gap": "rhythm",
    "title-size": "type",
    "text-size": "type",
    "panel-width": "layout",
    "bt-list-spacing": "layout",
    "bar-row-height": "layout",
    "chip-min": "layout",
}

CSS_LENGTH_PLACEHOLDER = re.compile(r"<([a-z][a-z0-9-]*)>")

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
        ("numeric-string.invalid.json", "is not of type 'number'"),
        ("cell-pad-single.invalid.json", "does not match"),
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


def test_hairline_w_is_a_required_shape_number_in_all_three_schemas() -> None:
    token_schema = _load(SCHEMAS["skin-token"])
    assert len(token_schema["properties"]) == 24
    assert token_schema["properties"]["hairline-w"]["$ref"].endswith("/number")
    assert "hairline-w" in token_schema["required"]

    manifest_shape = _load(SCHEMAS["skin-manifest"])["properties"]["groups"][
        "properties"
    ]["shape"]
    skin_json_shape = _load(SCHEMAS["skin-json"])["properties"]["shape"]
    for shape in (manifest_shape, skin_json_shape):
        assert shape["properties"]["hairline-w"] == {"$ref": "#/definitions/number"}
        assert "hairline-w" in shape["required"]

    flat_document = _load(FIXTURE_DIR / "skin-token" / "glass.valid.json")
    manifest_document = _load(FIXTURE_DIR / "skin-manifest" / "glass.valid.json")
    resolved_document = _load(FIXTURE_DIR / "skin-json" / "glass.valid.json")
    assert flat_document["hairline-w"] == 1
    assert manifest_document["groups"]["shape"]["hairline-w"] == 1
    assert resolved_document["shape"]["hairline-w"] == 1
    assert _errors("skin-token", flat_document) == []
    assert _errors("skin-manifest", manifest_document) == []
    assert _errors("skin-json", resolved_document) == []


@pytest.mark.parametrize(
    ("token", "group"), sorted(NUMERIC_TOKEN_GROUPS.items())
)
def test_numeric_token_rejects_a_px_string_and_accepts_a_number(
    token: str, group: str
) -> None:
    token_document = _load(FIXTURE_DIR / "skin-token" / "glass.valid.json")
    token_document[token] = "12px"
    assert _errors("skin-token", token_document) != []

    token_document[token] = 12
    assert _errors("skin-token", token_document) == []

    manifest = _load(FIXTURE_DIR / "skin-manifest" / "glass.valid.json")
    manifest["groups"][group][token] = "12px"
    assert _errors("skin-manifest", manifest) != []

    manifest["groups"][group][token] = 12
    assert _errors("skin-manifest", manifest) == []


def test_every_numeric_token_resolves_to_a_unitless_number_definition() -> None:
    for schema_name in ("skin-token", "skin-manifest"):
        schema = _load(SCHEMAS[schema_name])
        if schema_name == "skin-token":
            properties = schema["properties"]
        else:
            properties = {
                token: definition
                for group in GROUPS
                for token, definition in schema["properties"]["groups"]["properties"][
                    group
                ]["properties"].items()
            }
        for token in NUMERIC_TOKEN_GROUPS:
            ref = properties[token]["$ref"]
            definition = schema["definitions"][ref.split("/")[-1]]
            assert definition["type"] == "number"
            assert "unitless" in definition["description"]
            assert definition["examples"]
            assert all(
                isinstance(value, (int, float)) for value in definition["examples"]
            )


@pytest.mark.parametrize(
    "value",
    ["8px", "8", "8 9", "8 9px", "8px 9", "8px 9px 10px", "8.5px 9px"],
)
def test_cell_pad_requires_exactly_two_integer_pixel_lengths(value: str) -> None:
    token_document = _load(FIXTURE_DIR / "skin-token" / "glass.valid.json")
    token_document["cell-pad"] = value
    assert _errors("skin-token", token_document) != []

    manifest = _load(FIXTURE_DIR / "skin-manifest" / "glass.valid.json")
    manifest["groups"]["rhythm"]["cell-pad"] = value
    assert _errors("skin-manifest", manifest) != []


@pytest.mark.parametrize("value", ["8px 9px", "0px 0px"])
def test_cell_pad_accepts_two_integer_pixel_lengths(value: str) -> None:
    token_document = _load(FIXTURE_DIR / "skin-token" / "glass.valid.json")
    token_document["cell-pad"] = value
    assert _errors("skin-token", token_document) == []

    manifest = _load(FIXTURE_DIR / "skin-manifest" / "glass.valid.json")
    manifest["groups"]["rhythm"]["cell-pad"] = value
    assert _errors("skin-manifest", manifest) == []


def test_schema_descriptions_state_the_unit_convention() -> None:
    for schema_name in ("skin-token", "skin-manifest"):
        definitions = _load(SCHEMAS[schema_name])["definitions"]
        assert "unitless" in definitions["number"]["description"].lower()
        assert "unitless" in definitions["nonNegativeNumber"]["description"].lower()
        assert "Npx Npx" in definitions["cellPad"]["description"]
        assert "inherit" in definitions["fontFamily"]["description"]
        top_level = _load(SCHEMAS[schema_name])["description"]
        assert "unitless" in top_level.lower()
        assert "Npx Npx" in top_level


def test_skins_doc_expander_renders_numbers_as_px() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    template = "border-radius: <radius-card>; width: <panel-width>;"
    assert template in text
    assert (
        "expanded:  border-radius: 12px; width: 312px;" in text
    )

    def expand(snippet: str, values: dict[str, int]) -> str:
        return CSS_LENGTH_PLACEHOLDER.sub(
            lambda match: f"{values[match.group(1)]}px", snippet
        )

    assert (
        expand(template, {"radius-card": 12, "panel-width": 312})
        == "border-radius: 12px; width: 312px;"
    )


def test_skins_doc_freezes_the_value_types_and_units() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        "Value types and units (normative)",
        "unitless JSON numbers",
        "as `<number>px`",
        "cell-pad",
        "literal CSS length-pair string",
        "font-family` for the default skin may be `\"inherit\"`",
        "MUST vendor",
        "local lookalike",
        "skins/schema.json",
    ):
        assert needle in text


def test_skins_doc_freezes_hairlines_and_layout_ownership() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        "Border ownership and row geometry (normative)",
        "`border-w` is the **outer panel/frame border** only",
        "`hairline-w` is the **card tile, row action and badge hairline** only",
        "The row/cell itself has **no border**",
        "`.settings-net` row has `border: none`",
        "`54px` instead of `50px`",
        "thirteen numeric",
        "`border-w`, `hairline-w`, `gap`",
        "consumed ONLY by `skinValue()`",
        "Templates MUST NOT expand layout tokens into CSS",
        "no `min-width`, `margin` or `min-height`",
        "Layout metrics are TSX-owned.",
        "to avoid dual ownership",
        "may still appear in `skin.json`",
        "the 24-token",
    ):
        assert needle in text


def test_skins_doc_documents_the_built_in_border_values() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        "Border values: `border-w` `1.5`, `hairline-w` `1`",
        "values: `border-w` `0`, `hairline-w` `0`",
        "values: `border-w` `1`, `hairline-w` `1`",
    ):
        assert needle in text

    expected = {
        "glass": (1.5, 1),
        "flat": (0, 0),
        "paper": (1, 1),
    }
    for name, (border_w, hairline_w) in expected.items():
        manifest = _load(FIXTURE_DIR / "skin-manifest" / f"{name}.valid.json")
        resolved = _load(FIXTURE_DIR / "skin-json" / f"{name}.valid.json")
        flat = _load(FIXTURE_DIR / "skin-token" / f"{name}.valid.json")
        assert manifest["groups"]["shape"]["border-w"] == border_w
        assert resolved["shape"]["border-w"] == border_w
        assert flat["border-w"] == border_w
        assert manifest["groups"]["shape"]["hairline-w"] == hairline_w
        assert resolved["shape"]["hairline-w"] == hairline_w
        assert flat["hairline-w"] == hairline_w


def test_skins_doc_pins_the_runtime_contract() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        'desired.json',
        'skin: "<name>"',
        "sha256(templates_hash ‖ manifest_hash)",
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


def test_skin_json_requires_version_and_the_six_groups() -> None:
    schema = _load(SCHEMAS["skin-json"])
    assert schema["required"] == ["version", *GROUPS]
    assert set(schema["properties"]) == {"version", *GROUPS}
    assert schema["additionalProperties"] is False
    assert schema["properties"]["version"]["const"] == 1
    for group in GROUPS:
        assert schema["properties"][group]["additionalProperties"] is False


def test_skin_json_group_token_schemas_match_the_manifest() -> None:
    skin_json_groups = _load(SCHEMAS["skin-json"])["properties"]
    manifest_groups = _load(SCHEMAS["skin-manifest"])["properties"]["groups"][
        "properties"
    ]
    for group in GROUPS:
        assert skin_json_groups[group] == manifest_groups[group]


@pytest.mark.parametrize("value", [0, 2, "1", None])
def test_skin_json_rejects_a_version_other_than_one(value: Any) -> None:
    document = _load(FIXTURE_DIR / "skin-json" / "glass.valid.json")
    document["version"] = value
    assert _errors("skin-json", document) != []


def test_skin_json_requires_the_version_key() -> None:
    document = _load(FIXTURE_DIR / "skin-json" / "glass.valid.json")
    document.pop("version")
    assert _errors("skin-json", document) != []


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("flat-tokens.invalid.json", "radius-panel"),
        ("string-numerics.invalid.json", "is not of type 'number'"),
        ("structure-group.invalid.json", "structure"),
        ("variant-group.invalid.json", "variant"),
        ("unknown-group.invalid.json", "density"),
    ],
)
def test_skin_json_named_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "skin-json" / fixture)
    assert needle in _error_text("skin-json", document)


@pytest.mark.parametrize(("token", "group"), sorted(NUMERIC_TOKEN_GROUPS.items()))
def test_skin_json_numeric_token_rejects_a_string_and_accepts_a_number(
    token: str, group: str
) -> None:
    document = _load(FIXTURE_DIR / "skin-json" / "glass.valid.json")
    document[group][token] = "12px"
    assert _errors("skin-json", document) != []

    document[group][token] = 12
    assert _errors("skin-json", document) == []


def test_skin_json_keeps_string_tokens_verbatim() -> None:
    document = _load(FIXTURE_DIR / "skin-json" / "glass.valid.json")
    assert document["rhythm"]["cell-pad"] == "6px 10px"
    assert document["ink"]["ink"] == "@on_surface"
    assert _errors("skin-json", document) == []


def test_skins_doc_freezes_the_template_set_and_consumer_artifacts() -> None:
    text = (REPO_ROOT / "skins.md").read_text(encoding="utf-8")
    for needle in (
        "Template set and consumer artifacts (normative)",
        "dotfiles-assets/skins/templates",
        "<configDir>.gtk.css.j2",
        "{{SKIN_<TOKEN>}}",
        "SKIN_RADIUS_PANEL",
        "current/skins/<configDir>.css",
        "current/skin.json",
        "{install}/config/<configDir>/skin.css",
        "{install}/config/<configDir>/skin.json",
        "$XDG_CONFIG_HOME/<configDir>/skin.css",
        "configDir = ags",
        "desired.json",
        "sha256(templates_hash ‖ manifest_hash)",
        "palette-refresh",
        "restart-only",
        "Fail closed",
        "no flat token map",
    ):
        assert needle in text
