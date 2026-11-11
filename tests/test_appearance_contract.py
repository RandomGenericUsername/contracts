"""Fixture gates for the Appearance plane v2 contract (REQ-015).

The manifest is the authored document; `appearance-json` is the resolved,
mode-resolved token map; `appearance-artifact` is the `appearance.json`
metadata. The tests also exercise the v2 template flattening rule with a pure
helper so a layout token can never leak into a template.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "appearance-contract"

SCHEMAS = {
    "appearance-manifest": SCHEMA_DIR / "appearance-manifest.schema.json",
    "appearance-json": SCHEMA_DIR / "appearance-json.schema.json",
    "appearance-artifact": SCHEMA_DIR / "appearance-artifact.schema.json",
}

VALID_FIXTURES = sorted(
    path
    for name in SCHEMAS
    for path in (FIXTURE_DIR / name).glob("*.valid.json")
)
INVALID_FIXTURES = sorted(
    path
    for name in SCHEMAS
    for path in (FIXTURE_DIR / name).glob("*.invalid.json")
)

GROUPS = ("surface", "state", "type", "ink", "layout")
SURFACE_ROLES = ("panel", "card", "cell", "control", "pill")
STATE_ROLES = ("hover", "selected", "focus", "disabled")

SURFACE_TOKENS = {
    "panel": {"bg", "border", "border-width", "radius", "padding", "shadow", "blur"},
    "card": {"bg", "border", "border-width", "radius", "padding"},
    "cell": {"bg", "border", "border-width", "radius", "padding", "hover-bg"},
    "control": {
        "bg",
        "border",
        "border-width",
        "radius",
        "padding",
        "font-size",
        "font-weight",
    },
    "pill": {
        "bg",
        "border",
        "border-width",
        "radius",
        "padding",
        "font-size",
        "letter-spacing",
    },
}

TYPE_TOKENS = {
    "font-family",
    "font-weight",
    "letter-spacing",
    "size-caption",
    "size-meta",
    "size-body",
    "size-title",
    "size-display",
}

INK_TOKENS = {"ink", "ink-dim", "accent", "accent-muted", "ink-over"}

PLACEHOLDER = re.compile(r"\{\{SKIN_([A-Z0-9_]+)\}\}")
CONDITIONAL = re.compile(r"\{%|%\}|\{\{#|\{\{/")

HOST_PATHS = [
    "surface.panel.radius",
    "surface.panel.border-width",
    "surface.card.radius",
    "surface.control.radius",
    "surface.cell.radius",
]

#: Every numeric path in the v2 manifest/resolved shape, with a legal sample
#: value. A unit-bearing string must be rejected at each path.
NUMERIC_PATHS: dict[tuple[str, ...], float] = {
    ("surface", "panel", "border-width"): 1.5,
    ("surface", "panel", "radius"): 18,
    ("surface", "panel", "padding"): 11,
    ("surface", "card", "border-width"): 1,
    ("surface", "card", "radius"): 14,
    ("surface", "card", "padding"): 10,
    ("surface", "cell", "border-width"): 0,
    ("surface", "cell", "radius"): 10,
    ("surface", "cell", "padding"): 8,
    ("surface", "control", "border-width"): 1,
    ("surface", "control", "radius"): 8,
    ("surface", "control", "padding"): 4,
    ("surface", "control", "font-size"): 12,
    ("surface", "control", "font-weight"): 600,
    ("surface", "pill", "border-width"): 1,
    ("surface", "pill", "radius"): 20,
    ("surface", "pill", "padding"): 2,
    ("surface", "pill", "font-size"): 9.5,
    ("surface", "pill", "letter-spacing"): 0.05,
    ("type", "font-weight"): 600,
    ("type", "letter-spacing"): 0.05,
    ("type", "size-caption"): 10.5,
    ("type", "size-meta"): 11,
    ("type", "size-body"): 12,
    ("type", "size-title"): 15,
    ("type", "size-display"): 20,
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


def _schema_name(path: Path) -> str:
    return path.parent.name


def _set_path(document: dict, path: tuple[str, ...], value: Any) -> None:
    cursor = document
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def _get_path(document: dict, path: tuple[str, ...]) -> Any:
    cursor = document
    for part in path:
        cursor = cursor[part]
    return cursor


def resolve_tokens(manifest: dict, mode: str) -> dict:
    """Resolve a v2 manifest for one palette mode.

    An override group replaces the base group as a whole; omitted groups
    inherit. This is the same rule `appearance.md` pins for generation.
    """
    groups = copy.deepcopy(manifest["groups"])
    override = manifest.get("mode", {}).get(mode, {})
    groups.update(copy.deepcopy(override))
    return {"version": 2, **groups}


def flatten_token_path(path: tuple[str, ...]) -> str:
    joined = re.sub(r"[^A-Za-z0-9]+", "_", ".".join(path)).strip("_")
    return f"{{{{SKIN_{joined.upper()}}}}}"


def _flattened_tokens(tokens: dict) -> dict[str, tuple[str, Any]]:
    flattened: dict[str, tuple[str, Any]] = {}

    def walk(value: Any, path: tuple[str, ...]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, (*path, key))
            return
        if not path or path[0] == "version":
            return
        flattened[flatten_token_path(path)] = (path, value)

    walk(tokens, ())
    return flattened


def _format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def render_token(path: tuple[str, ...], value: Any) -> str:
    if not isinstance(value, (int, float)):
        return str(value)
    if path[-1] == "font-weight":
        return _format_number(value)
    if path[-1] == "letter-spacing":
        return f"{_format_number(value)}em"
    return f"{_format_number(value)}px"


def expand_template(template: str, tokens: dict) -> str:
    """Expand a v2 template; fail closed on layout tokens, unknowns and conditionals."""
    if CONDITIONAL.search(template):
        raise ValueError("templates have no conditionals")
    flattened = _flattened_tokens(tokens)

    def replace(match: re.Match[str]) -> str:
        name = match.group(0)
        if name not in flattened:
            raise ValueError(f"unknown placeholder {name}")
        path, value = flattened[name]
        if path[0] == "layout":
            raise ValueError(
                f"layout token {'.'.join(path)} must not appear in a template; "
                "layout metrics are TSX-owned"
            )
        return render_token(path, value)

    expanded = PLACEHOLDER.sub(replace, template)
    if "{{SKIN_" in expanded:
        raise ValueError("unresolved placeholder after expansion")
    return expanded


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_every_schema_is_draft_07_self_valid_and_frozen(name: str) -> None:
    schema = _load(SCHEMAS[name])
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["$id"] == f"https://dotfiles.local/schemas/{SCHEMAS[name].name}"
    assert schema["status"] == "frozen"
    Draft7Validator.check_schema(schema)


@pytest.mark.parametrize("path", VALID_FIXTURES, ids=_fixture_id)
def test_valid_fixture_is_accepted(path: Path) -> None:
    assert _errors(_schema_name(path), _load(path)) == []


@pytest.mark.parametrize("path", INVALID_FIXTURES, ids=_fixture_id)
def test_invalid_fixture_is_rejected(path: Path) -> None:
    assert _errors(_schema_name(path), _load(path)) != []


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("literal-hex.invalid.json", "#"),
        ("transition-value.invalid.json", "transition"),
        ("transition-key.invalid.json", "transition"),
        ("structure.invalid.json", "structure"),
        ("variant.invalid.json", "variant"),
        ("unknown-surface-role.invalid.json", "widget"),
        ("unknown-palette-role.invalid.json", "brand"),
        ("unit-string.invalid.json", "not of type 'number'"),
        ("flat-layout.invalid.json", "type 'object'"),
        ("missing-mode-override.invalid.json", "required"),
        ("unknown-mode.invalid.json", "sepia"),
        ("host-empty-inherit.invalid.json", "non-empty"),
        ("host-duplicate-inherit.invalid.json", "non-unique"),
        ("host-unknown-inherit.invalid.json", "surface.card.border-width"),
        ("host-pill-inherit.invalid.json", "surface.pill.radius"),
        ("host-bad-fallback.invalid.json", "is not one of"),
        ("host-extra-key.invalid.json", "colour"),
    ],
)
def test_named_manifest_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "appearance-manifest" / fixture)
    assert needle in _error_text("appearance-manifest", document)


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("version-one.invalid.json", "2 was expected"),
        ("unit-string.invalid.json", "not of type 'number'"),
        ("flat-layout.invalid.json", "type 'object'"),
        ("structure.invalid.json", "structure"),
        ("variant.invalid.json", "variant"),
        ("unknown-surface-role.invalid.json", "widget"),
    ],
)
def test_named_resolved_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "appearance-json" / fixture)
    assert needle in _error_text("appearance-json", document)


def test_manifest_declares_exactly_the_five_groups() -> None:
    groups = _load(SCHEMAS["appearance-manifest"])["properties"]["groups"]
    assert list(groups["required"]) == list(GROUPS)
    assert set(groups["properties"]) == set(GROUPS)
    assert groups["additionalProperties"] is False


def test_resolved_tokens_require_version_two_and_the_five_groups() -> None:
    schema = _load(SCHEMAS["appearance-json"])
    assert schema["required"] == ["version", *GROUPS]
    assert set(schema["properties"]) == {"version", *GROUPS}
    assert schema["additionalProperties"] is False
    assert schema["properties"]["version"]["const"] == 2


def test_manifest_and_resolved_group_shapes_match() -> None:
    manifest = _load(SCHEMAS["appearance-manifest"])["definitions"]
    resolved = _load(SCHEMAS["appearance-json"])["definitions"]
    for group in GROUPS:
        assert manifest[f"{group}Group"] == resolved[f"{group}Group"]


def test_surface_roles_have_exactly_the_v2_token_sets() -> None:
    definitions = _load(SCHEMAS["appearance-manifest"])["definitions"]
    surface = definitions["surfaceGroup"]
    assert list(surface["required"]) == list(SURFACE_ROLES)
    assert set(surface["properties"]) == set(SURFACE_ROLES)
    for role, expected in SURFACE_TOKENS.items():
        role_schema = definitions[f"{role}Role"]
        assert set(role_schema["properties"]) == expected
        assert set(role_schema["required"]) == expected
        assert role_schema["additionalProperties"] is False


def test_state_roles_carry_fill_ink_and_ring() -> None:
    definitions = _load(SCHEMAS["appearance-manifest"])["definitions"]
    state = definitions["stateGroup"]
    assert list(state["required"]) == list(STATE_ROLES)
    assert set(state["properties"]) == set(STATE_ROLES)
    for role in STATE_ROLES:
        role_schema = definitions["stateRole"]
        assert set(role_schema["properties"]) == {"fill", "ink", "ring"}
        assert set(role_schema["required"]) == {"fill", "ink", "ring"}


def test_type_and_ink_vocabularies_are_exact() -> None:
    definitions = _load(SCHEMAS["appearance-manifest"])["definitions"]
    type_group = definitions["typeGroup"]
    ink_group = definitions["inkGroup"]
    assert set(type_group["properties"]) == TYPE_TOKENS
    assert set(type_group["required"]) == TYPE_TOKENS
    assert set(ink_group["properties"]) == INK_TOKENS
    assert set(ink_group["required"]) == INK_TOKENS
    assert ink_group["properties"]["ink-over"]["const"] == "auto"


def test_layout_is_namespaced_by_app_and_numeric() -> None:
    definitions = _load(SCHEMAS["appearance-manifest"])["definitions"]
    layout = definitions["layoutGroup"]
    assert layout["additionalProperties"] == {"$ref": "#/definitions/layoutApp"}
    app_schema = definitions["layoutApp"]
    assert app_schema["additionalProperties"] is False
    assert app_schema["patternProperties"]["^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"] == {
        "$ref": "#/definitions/nonNegativeNumber"
    }

    manifest = _load(FIXTURE_DIR / "appearance-manifest" / "glass.valid.json")
    assert manifest["groups"]["layout"]["bar"]["panel-width"] == 380
    assert _errors("appearance-manifest", manifest) == []

    flat_layout = _load(FIXTURE_DIR / "appearance-manifest" / "flat-layout.invalid.json")
    assert "380 is not of type 'object'" in _error_text("appearance-manifest", flat_layout)


def test_mode_overrides_are_same_shape_group_replacements() -> None:
    definitions = _load(SCHEMAS["appearance-manifest"])["definitions"]
    mode = definitions["modeOverride"]
    assert set(mode["properties"]) == set(GROUPS)
    assert mode["additionalProperties"] is False
    assert mode["minProperties"] == 1
    for group in GROUPS:
        assert mode["properties"][group] == {"$ref": f"#/definitions/{group}Group"}

    paper = _load(FIXTURE_DIR / "appearance-manifest" / "paper.valid.json")
    assert set(paper["mode"]) == {"light"}
    light = paper["mode"]["light"]
    assert set(light) == {"surface", "state", "ink"}
    for group, document in light.items():
        base = paper["groups"][group]
        assert set(document) == set(base)
        for name, value in document.items():
            if isinstance(value, dict):
                assert set(value) == set(base[name])


def test_host_policy_is_optional_closed_and_allowlisted() -> None:
    schema = _load(SCHEMAS["appearance-manifest"])
    assert "host" in schema["properties"]
    ref = schema["properties"]["host"]["$ref"].split("/")[-1]
    policy = schema["definitions"][ref]

    assert policy["type"] == "object"
    assert policy["additionalProperties"] is False
    assert policy["required"] == ["inherit"]
    assert set(policy["properties"]) == {"inherit", "fallback"}

    inherit = policy["properties"]["inherit"]
    assert inherit["type"] == "array"
    assert inherit["minItems"] == 1
    assert inherit["uniqueItems"] is True
    assert inherit["items"]["enum"] == HOST_PATHS

    fallback = policy["properties"]["fallback"]
    assert fallback["enum"] == ["skin", "error"]
    assert fallback["default"] == "skin"


def test_host_policy_is_not_a_token_group_and_no_host_manifest_stays_valid() -> None:
    schema = _load(SCHEMAS["appearance-manifest"])
    groups = schema["properties"]["groups"]
    assert "host" not in groups["properties"]
    assert "host" not in groups["required"]

    glass = _load(FIXTURE_DIR / "appearance-manifest" / "glass.valid.json")
    assert "host" not in glass
    assert _errors("appearance-manifest", glass) == []

    host_manifest = _load(FIXTURE_DIR / "appearance-manifest" / "host.valid.json")
    assert host_manifest["host"] == {
        "inherit": HOST_PATHS,
        "fallback": "skin",
    }
    assert _errors("appearance-manifest", host_manifest) == []

    resolved = resolve_tokens(host_manifest, "dark")
    assert _errors("appearance-json", resolved) == []
    assert isinstance(resolved["surface"]["panel"]["radius"], (int, float))
    assert isinstance(resolved["surface"]["panel"]["border-width"], (int, float))


@pytest.mark.parametrize(
    "fixture",
    [
        "host.valid.json",
        "host-old-two-path.valid.json",
        "host-card-radius.valid.json",
        "host-control-radius.valid.json",
        "host-cell-radius.valid.json",
    ],
)
def test_host_policy_accepts_rectangle_radius_allowlists(fixture: str) -> None:
    manifest = _load(FIXTURE_DIR / "appearance-manifest" / fixture)
    assert _errors("appearance-manifest", manifest) == []


def test_pill_radius_is_never_delegable() -> None:
    schema = _load(SCHEMAS["appearance-manifest"])
    ref = schema["properties"]["host"]["$ref"].split("/")[-1]
    inherit = schema["definitions"][ref]["properties"]["inherit"]

    assert "surface.pill.radius" not in inherit["items"]["enum"]
    assert "surface.pill.radius" not in HOST_PATHS
    pill = _load(FIXTURE_DIR / "appearance-manifest" / "host-pill-inherit.invalid.json")
    assert _errors("appearance-manifest", pill) != []


def test_paper_light_is_explicit_and_resolves_before_validation() -> None:
    paper = _load(FIXTURE_DIR / "appearance-manifest" / "paper.valid.json")
    base = resolve_tokens(paper, "dark")
    light = resolve_tokens(paper, "light")

    assert _errors("appearance-json", base) == []
    assert _errors("appearance-json", light) == []

    assert light["surface"] == paper["mode"]["light"]["surface"]
    assert light["state"] == paper["mode"]["light"]["state"]
    assert light["ink"] == paper["mode"]["light"]["ink"]
    assert light["type"] == paper["groups"]["type"]
    assert light["layout"] == paper["groups"]["layout"]

    assert (
        light["surface"]["panel"]["bg"]
        == paper["mode"]["light"]["surface"]["panel"]["bg"]
    )
    assert light["surface"]["panel"]["bg"] != base["surface"]["panel"]["bg"]
    assert light["ink"]["ink-dim"] != base["ink"]["ink-dim"]


def test_every_built_in_manifest_resolves_for_both_modes() -> None:
    for name in ("glass", "flat", "paper"):
        manifest = _load(FIXTURE_DIR / "appearance-manifest" / f"{name}.valid.json")
        for mode in ("dark", "light"):
            resolved = resolve_tokens(manifest, mode)
            assert _errors("appearance-json", resolved) == []


@pytest.mark.parametrize(("path", "sample"), sorted(NUMERIC_PATHS.items()))
def test_numeric_token_rejects_a_unit_string_and_accepts_a_number(
    path: tuple[str, ...], sample: float
) -> None:
    manifest = _load(FIXTURE_DIR / "appearance-manifest" / "glass.valid.json")
    _set_path(manifest["groups"], path, "12px")
    assert _errors("appearance-manifest", manifest) != []

    _set_path(manifest["groups"], path, sample)
    assert _errors("appearance-manifest", manifest) == []

    resolved = _load(FIXTURE_DIR / "appearance-json" / "glass.valid.json")
    _set_path(resolved, path, "12px")
    assert _errors("appearance-json", resolved) != []

    _set_path(resolved, path, sample)
    assert _errors("appearance-json", resolved) == []


def test_layout_token_values_are_unitless_numbers() -> None:
    manifest = _load(FIXTURE_DIR / "appearance-manifest" / "glass.valid.json")
    manifest["groups"]["layout"]["bar"]["panel-width"] = "380px"
    assert _errors("appearance-manifest", manifest) != []

    manifest["groups"]["layout"]["bar"]["panel-width"] = 380
    assert _errors("appearance-manifest", manifest) == []

    resolved = _load(FIXTURE_DIR / "appearance-json" / "glass.valid.json")
    resolved["layout"]["bar"]["panel-width"] = "380px"
    assert _errors("appearance-json", resolved) != []


def test_structure_and_variant_are_rejected_at_every_object_level() -> None:
    for schema_name in ("appearance-manifest", "appearance-json"):
        schema = _load(SCHEMAS[schema_name])
        assert "$ref" in schema["propertyNames"]
        ref = schema["propertyNames"]["$ref"].split("/")[-1]
        forbidden = schema["definitions"][ref]["not"]
        patterns = [entry["pattern"] for entry in forbidden["anyOf"]]
        assert "(?:^|_)(?:structure|order|presence)(?:_|$)" in patterns
        assert "variant" in patterns


def test_artifact_requires_the_v2_metadata_fields() -> None:
    schema = _load(SCHEMAS["appearance-artifact"])
    assert schema["properties"]["version"]["const"] == 2
    assert schema["properties"]["mode"]["enum"] == ["dark", "light"]
    assert schema["properties"]["tokenRef"]["const"] == "tokens.json"
    assert set(schema["required"]) == {
        "version",
        "skin",
        "mode",
        "paletteHash",
        "skinHash",
        "appearanceHash",
        "generationHash",
        "tokenRef",
    }
    for field in ("paletteHash", "skinHash", "appearanceHash", "generationHash"):
        assert schema["properties"][field]["pattern"] == "^[0-9a-f]{64}$"


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("version-one.invalid.json", "2 was expected"),
        ("missing-token-ref.invalid.json", "tokenRef"),
        ("bad-hash.invalid.json", "does not match"),
        ("unknown-mode.invalid.json", "sepia"),
    ],
)
def test_named_artifact_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "appearance-artifact" / fixture)
    assert needle in _error_text("appearance-artifact", document)


def test_placeholder_flattening_uses_the_full_nested_path() -> None:
    assert flatten_token_path(("surface", "panel", "bg")) == "{{SKIN_SURFACE_PANEL_BG}}"
    assert flatten_token_path(("surface", "cell", "hover-bg")) == "{{SKIN_SURFACE_CELL_HOVER_BG}}"
    assert flatten_token_path(("state", "selected", "ring")) == "{{SKIN_STATE_SELECTED_RING}}"
    assert flatten_token_path(("type", "size-body")) == "{{SKIN_TYPE_SIZE_BODY}}"
    assert flatten_token_path(("layout", "bar", "panel-width")) == (
        "{{SKIN_LAYOUT_BAR_PANEL_WIDTH}}"
    )


def test_valid_template_expands_without_leftover_placeholders() -> None:
    template = (
        FIXTURE_DIR / "templates" / "valid" / "ags.gtk.css.j2"
    ).read_text(encoding="utf-8")
    tokens = _load(FIXTURE_DIR / "appearance-json" / "glass.valid.json")
    expanded = expand_template(template, tokens)
    assert "{{" not in expanded
    assert "font-size: 12px;" in expanded
    assert "letter-spacing: 0.05em;" in expanded
    assert "18px" in expanded


def test_mode_is_resolved_before_template_expansion() -> None:
    paper = _load(FIXTURE_DIR / "appearance-manifest" / "paper.valid.json")
    light = resolve_tokens(paper, "light")
    template = "{{SKIN_SURFACE_PANEL_BG}}"
    expanded = expand_template(template, light)
    assert expanded == paper["mode"]["light"]["surface"]["panel"]["bg"]
    assert expanded != paper["groups"]["surface"]["panel"]["bg"]


def test_layout_token_in_a_template_is_rejected() -> None:
    template = (
        FIXTURE_DIR / "templates" / "invalid" / "layout-token.gtk.css.j2"
    ).read_text(encoding="utf-8")
    tokens = _load(FIXTURE_DIR / "appearance-json" / "glass.valid.json")
    with pytest.raises(ValueError, match="layout token"):
        expand_template(template, tokens)


def test_template_conditionals_are_rejected() -> None:
    template = (
        FIXTURE_DIR / "templates" / "invalid" / "conditional.gtk.css.j2"
    ).read_text(encoding="utf-8")
    tokens = _load(FIXTURE_DIR / "appearance-json" / "glass.valid.json")
    with pytest.raises(ValueError, match="no conditionals"):
        expand_template(template, tokens)


def test_templates_have_no_layout_placeholders() -> None:
    template = (
        FIXTURE_DIR / "templates" / "valid" / "ags.gtk.css.j2"
    ).read_text(encoding="utf-8")
    names = PLACEHOLDER.findall(template)
    assert names
    assert all(not name.startswith("LAYOUT_") for name in names)


def test_appearance_doc_pins_the_v2_contract() -> None:
    text = (REPO_ROOT / "appearance.md").read_text(encoding="utf-8")
    for needle in (
        "Appearance plane v2 (frozen)",
        "cache/appearance/<hash>/",
        "colors.yaml",
        "tokens.json",
        "appearance.json",
        "<configDir>.css",
        "current/appearance",
        "config/<configDir>/appearance.css",
        "MUST watch `current/appearance`",
        "inotify",
        "GTK_STYLE_PROVIDER_PRIORITY_USER",
        "800",
        "installed last",
        "one monitor",
        "one apply",
        "palette-refresh",
        "theme.apply()",
        "systemd user unit",
        "KillMode=control-group",
        "org.freedesktop.Notifications",
        "ags quit -i",
        "restart lane",
        "appearanceHash",
        "sha256",
        "mode is resolved before expansion",
        "no conditionals",
        "no v1.1 hotfix",
        "border-w",
        "hover-bg",
        "layout.<app>",
        "letter-spacing",
        "font-weight",
        "surface.panel.bg",
        "{{SKIN_SURFACE_PANEL_BG}}",
        "no literal hex",
        "no transitions",
        "structure/variant",
        "[host]",
        "surface.panel.radius",
        "surface.panel.border-width",
        "surface.card.radius",
        "surface.control.radius",
        "surface.cell.radius",
        "surface.pill.radius",
        "intentionally not delegable",
        "outer panel",
        "card/control/cell rectangle radii",
        "no border-width expansion beyond",
        "mode override > host > skin fallback",
        'fallback = "skin"',
        'fallback = "error"',
        "appearance.v3",
        "hostHash",
        "one-time identity churn",
    ):
        assert needle in text
