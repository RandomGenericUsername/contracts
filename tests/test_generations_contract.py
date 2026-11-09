"""Fixture gates for the Generations v3 contract (REQ-016).

The generation manifest is the self-check written last inside
`state/generations/<genHash>/`. The appearance refresh result is the
generation-bound ack returned by a live app. The tests keep both schemas
draft-07/frozen, validate every positive/negative fixture, pin the protocol
documents and reject a response hash that differs from the request.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "generations-contract"

SCHEMAS = {
    "generation-manifest": SCHEMA_DIR / "generation-manifest.schema.json",
    "appearance-refresh-result": SCHEMA_DIR / "appearance-refresh-result.schema.json",
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

MANIFEST_REQUIRED = {
    "version",
    "generationHash",
    "created",
    "committed",
    "layers",
    "skin",
    "appearance",
    "mode",
    "intent",
    "source",
}
HASH_PATTERN = "^[0-9a-f]{64}$"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(name: str) -> Draft7Validator:
    return Draft7Validator(_load(SCHEMAS[name]))


def _errors(schema_name: str, document: Any) -> list[str]:
    return [error.message for error in _validator(schema_name).iter_errors(document)]


def _messages(error) -> Any:
    yield error.message
    for child in error.context:
        yield from _messages(child)


def _error_text(schema_name: str, document: Any) -> str:
    return "\n".join(
        message
        for error in _validator(schema_name).iter_errors(document)
        for message in _messages(error)
    )


def _fixture_id(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


def _schema_name(path: Path) -> str:
    return path.parent.name


class StaleAckError(ValueError):
    """The app answered for a generation other than the requested one."""


def classify_response(request_hash: str, response: dict) -> str:
    """Validate a v3 ack and reject a stale/mismatched generation.

    The JSON schema can validate the shape; equality with the request is a
    semantic rule the caller enforces. A mismatch is never `applied`.
    """
    errors = _errors("appearance-refresh-result", response)
    if errors:
        raise ValueError("; ".join(errors))
    if "applied" in response:
        kind = "applied"
        reported = response["applied"]
    elif "deferred" in response:
        kind = "deferred"
        reported = response["genHash"]
    else:
        kind = "failed"
        reported = response["genHash"]
    if reported != request_hash:
        raise StaleAckError(
            f"{kind} response names {reported}, request named {request_hash}"
        )
    return kind


def validate_host_identity(manifest: dict[str, Any]) -> None:
    """Enforce the host/intent equality JSON Schema cannot express.

    The schema enforces presence: ``intent.host`` is required when ``host`` is
    present and forbidden when it is absent. Equality is a runtime semantic
    rule; this helper is its contract-level fixture gate.
    """
    host = manifest.get("host")
    intent = manifest.get("intent", {})
    if host is None:
        if "host" in intent:
            raise ValueError("intent.host is present without a host block")
        return
    if intent.get("host") != host.get("fingerprint"):
        raise ValueError("intent.host does not equal host.fingerprint")


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
        ("stale-layer.invalid.json", "should not be valid"),
        ("unknown-layer.invalid.json", "cursors"),
        ("wrong-hash.invalid.json", "does not match"),
        ("missing-mode.invalid.json", "mode"),
        ("extra-key.invalid.json", "legacyPointer"),
        ("literal-hex.invalid.json", "#ff0000"),
        ("structure.invalid.json", "structure"),
        ("variant.invalid.json", "variant"),
        ("invalid-config-dir.invalid.json", "AGS"),
        ("host-without-intent-host.invalid.json", "required property"),
        ("host-empty-defaults.invalid.json", "non-empty"),
        ("host-unknown-default.invalid.json", "surface.card.radius"),
        ("host-bad-source.invalid.json", "sway"),
        ("host-bad-fingerprint.invalid.json", "does not match"),
        ("host-bad-version.invalid.json", "1 was expected"),
        ("intent-host-without-host.invalid.json", "should not be valid"),
    ],
)
def test_named_manifest_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "generation-manifest" / fixture)
    assert needle in _error_text("generation-manifest", document)


@pytest.mark.parametrize(
    ("fixture", "needle"),
    [
        ("old-ok.invalid.json", "not valid under any of the given schemas"),
        ("missing-genhash.invalid.json", "genHash"),
        ("failed-no-retryable.invalid.json", "retryable"),
        ("unknown-key.invalid.json", "ok"),
        ("uppercase-hash.invalid.json", "does not match"),
    ],
)
def test_named_refresh_negative_fixture_reports_the_offending_construct(
    fixture: str, needle: str
) -> None:
    document = _load(FIXTURE_DIR / "appearance-refresh-result" / fixture)
    assert needle in _error_text("appearance-refresh-result", document)


def test_manifest_declares_the_v3_required_fields() -> None:
    schema = _load(SCHEMAS["generation-manifest"])
    assert schema["required"] == [
        "version",
        "generationHash",
        "created",
        "committed",
        "layers",
        "skin",
        "appearance",
        "mode",
        "intent",
        "source",
    ]
    assert set(schema["required"]) == MANIFEST_REQUIRED
    assert schema["additionalProperties"] is False
    assert schema["properties"]["version"]["const"] == 3
    assert schema["properties"]["generationHash"]["$ref"].endswith("/hash")
    assert schema["definitions"]["hash"]["pattern"] == HASH_PATTERN


def test_manifest_layers_are_hashes_and_relative_paths() -> None:
    definitions = _load(SCHEMAS["generation-manifest"])["definitions"]
    layers = definitions["layers"]
    assert layers["required"] == ["wallpaper", "palette"]
    assert set(layers["properties"]) == {
        "wallpaper",
        "palette",
        "effects",
        "icons",
    }
    assert layers["additionalProperties"] is False
    layer = definitions["layer"]
    assert layer["required"] == ["entryHash", "path"]
    assert layer["additionalProperties"] is False
    assert definitions["relativePath"]["not"]["pattern"] == (
        r"(?:^|/)\.\.?(?:/|$)"
    )
    assert "#" not in definitions["relativePath"]["pattern"]


def test_manifest_skin_appearance_and_mode_fields() -> None:
    definitions = _load(SCHEMAS["generation-manifest"])["definitions"]
    skin = definitions["skin"]
    assert skin["required"] == ["name", "entryHash", "mode"]
    assert skin["additionalProperties"] is False

    appearance = definitions["appearance"]
    assert appearance["required"] == ["tokensPath", "targets"]
    assert appearance["properties"]["tokensPath"]["const"] == "appearance/tokens.json"
    assert appearance["properties"]["targets"]["minItems"] == 1

    target = definitions["target"]
    assert target["required"] == ["configDir", "path"]
    assert target["additionalProperties"] is False
    assert target["properties"]["path"]["pattern"] == (
        r"^appearance/[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.css$"
    )

    assert definitions["mode"]["enum"] == ["dark", "light"]
    assert definitions["intent"]["required"] == [
        "wallpaper",
        "palette",
        "skin",
        "mode",
    ]
    assert definitions["source"]["required"] == ["kind", "intentHash"]
    assert definitions["source"]["properties"]["kind"]["enum"] == [
        "daemon",
        "cli",
    ]


def test_manifest_host_block_is_optional_closed_and_participating_only() -> None:
    schema = _load(SCHEMAS["generation-manifest"])
    assert "host" in schema["properties"]
    ref = schema["properties"]["host"]["$ref"].split("/")[-1]
    host = schema["definitions"][ref]

    assert host["type"] == "object"
    assert host["additionalProperties"] is False
    assert host["required"] == ["source", "version", "fingerprint", "defaults"]
    assert set(host["properties"]) == {
        "source",
        "version",
        "fingerprint",
        "defaults",
    }
    assert host["properties"]["source"]["enum"] == ["hyprland"]
    assert host["properties"]["version"]["const"] == 1
    assert host["properties"]["fingerprint"]["$ref"].endswith("/hash")

    defaults = host["properties"]["defaults"]
    assert defaults["additionalProperties"] is False
    assert defaults["minProperties"] == 1
    assert set(defaults["properties"]) == {
        "surface.panel.radius",
        "surface.panel.border-width",
    }
    assert defaults["properties"]["surface.panel.radius"]["maximum"] == 64
    assert defaults["properties"]["surface.panel.border-width"]["maximum"] == 16

    intent = schema["definitions"]["intent"]
    assert "host" in intent["properties"]
    assert intent["properties"]["host"]["$ref"].endswith("/hash")

    conditional = schema["allOf"][0]
    assert conditional["if"] == {"required": ["host"]}
    assert conditional["then"]["properties"]["intent"]["required"] == ["host"]
    assert conditional["else"]["properties"]["intent"]["not"]["required"] == ["host"]

    no_host = _load(FIXTURE_DIR / "generation-manifest" / "glass-dark.valid.json")
    assert "host" not in no_host
    assert "host" not in no_host["intent"]
    assert _errors("generation-manifest", no_host) == []


def test_valid_host_manifest_records_only_participating_values() -> None:
    manifest = _load(FIXTURE_DIR / "generation-manifest" / "host.valid.json")
    assert manifest["host"]["source"] == "hyprland"
    assert manifest["host"]["version"] == 1
    assert manifest["host"]["fingerprint"] == manifest["intent"]["host"]
    assert manifest["host"]["defaults"] == {
        "surface.panel.radius": 0,
        "surface.panel.border-width": 1,
    }
    assert _errors("generation-manifest", manifest) == []
    validate_host_identity(manifest)


def test_host_identity_mismatch_is_rejected_semantically() -> None:
    manifest = _load(
        FIXTURE_DIR / "generation-manifest" / "host-intent-mismatch.semantic.json"
    )
    assert _errors("generation-manifest", manifest) == []
    with pytest.raises(ValueError, match="does not equal host.fingerprint"):
        validate_host_identity(manifest)


def test_structure_and_variant_are_rejected_at_every_manifest_level() -> None:
    schema = _load(SCHEMAS["generation-manifest"])
    assert "$ref" in schema["propertyNames"]
    ref = schema["propertyNames"]["$ref"].split("/")[-1]
    forbidden = schema["definitions"][ref]["not"]
    patterns = [entry["pattern"] for entry in forbidden["anyOf"]]
    assert r"(?:^|_)(?:structure|order|presence)(?:_|$)" in patterns
    assert "variant" in patterns

    for definition in schema["definitions"].values():
        if definition.get("type") == "object":
            assert "$ref" in definition["propertyNames"]


def test_no_manifest_string_accepts_literal_hex() -> None:
    document = _load(FIXTURE_DIR / "generation-manifest" / "glass-dark.valid.json")

    def strings(value: Any):
        if isinstance(value, dict):
            for child in value.values():
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
        elif isinstance(value, str):
            yield value

    assert all("#" not in value for value in strings(document))

    document["source"]["jobId"] = "#ff0000"
    assert _errors("generation-manifest", document) != []


def test_valid_manifest_identity_is_internally_consistent() -> None:
    document = _load(FIXTURE_DIR / "generation-manifest" / "glass-dark.valid.json")
    assert document["version"] == 3
    assert document["skin"]["mode"] == document["mode"]
    assert document["intent"]["mode"] == document["mode"]
    assert document["intent"]["skin"] == document["skin"]["name"]

    for name in ("wallpaper", "palette", "effects", "icons"):
        assert document["intent"][name] == document["layers"][name]["entryHash"]

    config_dirs = [target["configDir"] for target in document["appearance"]["targets"]]
    assert len(config_dirs) == len(set(config_dirs))
    for target in document["appearance"]["targets"]:
        assert target["path"] == f"appearance/{target['configDir']}.css"


def test_paper_light_omits_optional_layers_and_uses_the_cli_fallback() -> None:
    document = _load(FIXTURE_DIR / "generation-manifest" / "paper-light.valid.json")
    assert set(document["layers"]) == {"wallpaper", "palette"}
    assert document["mode"] == "light"
    assert document["skin"]["mode"] == "light"
    assert document["source"] == {"kind": "cli", "intentHash": "3" * 64}
    assert _errors("generation-manifest", document) == []


def test_refresh_result_has_exactly_the_three_v3_variants() -> None:
    schema = _load(SCHEMAS["appearance-refresh-result"])
    assert len(schema["oneOf"]) == 3
    names = [entry["$ref"].split("/")[-1] for entry in schema["oneOf"]]
    assert names == ["applied", "deferred", "failed"]

    definitions = schema["definitions"]
    assert definitions["applied"]["required"] == ["applied"]
    assert definitions["deferred"]["required"] == ["deferred", "genHash"]
    assert definitions["failed"]["required"] == ["failed", "retryable", "genHash"]
    assert definitions["genHash"]["pattern"] == HASH_PATTERN

    for variant in ("applied", "deferred", "failed"):
        assert definitions[variant]["additionalProperties"] is False
        assert "ok" not in definitions[variant]["properties"]


def test_response_with_the_requested_generation_is_applied() -> None:
    request_hash = "a" * 64
    response = _load(FIXTURE_DIR / "appearance-refresh-result" / "applied.valid.json")
    assert classify_response(request_hash, response) == "applied"


@pytest.mark.parametrize(
    "fixture",
    [
        "applied.valid.json",
        "deferred.valid.json",
        "failed-retryable.valid.json",
        "failed-terminal.valid.json",
    ],
)
def test_response_mismatch_is_rejected_for_every_variant(fixture: str) -> None:
    response = _load(FIXTURE_DIR / "appearance-refresh-result" / fixture)
    with pytest.raises(StaleAckError, match="request named"):
        classify_response("b" * 64, response)


def test_old_boolean_ack_is_not_accepted() -> None:
    response = _load(FIXTURE_DIR / "appearance-refresh-result" / "old-ok.invalid.json")
    with pytest.raises(ValueError, match="not valid"):
        classify_response("a" * 64, response)
    assert _errors("appearance-refresh-result", response) != []


def test_response_hash_must_equal_the_request_at_the_document_level() -> None:
    text = (REPO_ROOT / "appearance-refresh.md").read_text(encoding="utf-8")
    assert "response hash MUST equal the request" in text
    assert "never acks" in text
    assert "whatever `current` is" in text


def test_appearance_refresh_doc_pins_the_v3_protocol() -> None:
    text = (REPO_ROOT / "appearance-refresh.md").read_text(encoding="utf-8")
    for needle in (
        "Appearance refresh protocol v3",
        "supersedes the",
        '["appearance-refresh", "<genHash>"]',
        '{"applied":"<genHash>"}',
        '{"deferred":"reason","genHash":"<genHash>"}',
        '{"failed":"reason","retryable":true|false,"genHash":"<genHash>"}',
        "response hash MUST equal the request",
        "whatever `current` is",
        "never",
        "record `applied`",
        "generations/<genHash>/appearance/<configDir>.css",
        "appearance/tokens.json",
        "MUST NOT read",
        "app tag",
        "GTK_STYLE_PROVIDER_PRIORITY_USER",
        "800",
        "installed last",
        "Restart-lane",
        "deferred",
        "retryable",
        "ags-app-refresh.md",
        "provenance",
    ):
        assert needle in text


def test_v2_palette_refresh_doc_is_marked_superseded() -> None:
    text = (REPO_ROOT / "ags-app-refresh.md").read_text(encoding="utf-8")
    for needle in (
        "superseded",
        "appearance-refresh.md",
        '["appearance-refresh", "<genHash>"]',
        "palette-refresh",
        "retained for provenance",
    ):
        assert needle in text


def test_generations_doc_pins_the_v3_interface() -> None:
    text = (REPO_ROOT / "generations.md").read_text(encoding="utf-8")
    for needle in (
        "Generations v3 (frozen)",
        "state/generations/<genHash>/",
        "state/current -> generations/<genHash>",
        "manifest.json",
        "generationHash",
        "created",
        "committed",
        "layers",
        "wallpaper",
        "palette",
        "effects",
        "icons",
        "skin",
        "appearance",
        "tokensPath",
        "targets",
        "intent",
        "source",
        "additionalProperties: false",
        "atomic",
        "rename",
        "Crash matrix",
        "converge(intent)",
        "JobFinished",
        "JobStarted",
        "flock",
        "no retry loop",
        "generation-bound",
        "MOVED_TO",
        "NameOwnerChanged",
        "JobRemoved",
        "no polling",
        "Artifact locality and immutability",
        "never writes",
        "immutable app tag",
        "Lane policy",
        "refresh",
        "supervision",
        "launch",
        "mode",
        "generation identity",
        "Garbage collection and pins",
        "gc-pins.json",
        "grace",
        "keep",
        "appearance-refresh",
        "superseded",
        "host",
        "hostHash",
        "intent.host",
        "host.fingerprint",
        "queue key stays host-free",
        "appearance.v3",
    ):
        assert needle in text
