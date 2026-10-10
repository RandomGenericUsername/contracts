#!/usr/bin/env python3
"""Generate the event-contract bindings from the canonical contract.

Reads the canonical, imported contract (REQ-001):

  - the XML file  -> D-Bus wire: hub methods, hub signals, the job interface
  - the JSON file -> semantics: topics, payloads, delivery, versioning

and emits, deterministically and byte-for-byte reproducibly:

  generated/contract.py         constants + TypedDicts + wire tables + payload types
  generated/contract.ts         constants + types + per-topic payload interfaces
  generated/events.schema.json  JSON Schema (2020-12): topic payloads + envelopes

Scope: the EVENT contract only. The structural schemas under ``schemas/`` are
NOT generated here and are left untouched.

Determinism: every emitted collection is ordered (mapping keys are sorted,
wire argument order is preserved), and each file ends in a single trailing
newline. Two consecutive runs produce byte-identical output.

Run: ``python3 gen/generate.py`` (stdlib only). ``--out DIR`` overrides the
output directory (used by the coverage test).
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# The canonical contract is named by a stem plus an extension so that this
# generator never references a private/duplicate copy of the contract.
CONTRACT_STEM = "event-contract"

# D-Bus signature -> Python / TypeScript types.
PY_TYPES: dict[str, str] = {
    "s": "str",
    "u": "int",
    "i": "int",
    "x": "int",
    "d": "float",
    "b": "bool",
    "a{sv}": "dict[str, object]",
    "a{ss}": "dict[str, str]",
    "as": "list[str]",
}

TS_TYPES: dict[str, str] = {
    "s": "string",
    "u": "number",
    "i": "number",
    "x": "number",
    "d": "number",
    "b": "boolean",
    "a{sv}": "Record<string, unknown>",
    "a{ss}": "Record<string, string>",
    "as": "string[]",
}

# D-Bus signature -> JSON Schema (draft 2020-12) fragment.
JSON_TYPES: dict[str, dict[str, Any]] = {
    "s": {"type": "string"},
    "u": {"type": "integer", "minimum": 0},
    "i": {"type": "integer"},
    "x": {"type": "integer"},
    "d": {"type": "number"},
    "b": {"type": "boolean"},
    "a{sv}": {"type": "object"},
    "a{ss}": {"type": "object", "additionalProperties": {"type": "string"}},
    "as": {"type": "array", "items": {"type": "string"}},
}


# ---- parsing ---------------------------------------------------------------
def _scream(name: str) -> str:
    """camelCase / dotted name -> SCREAMING_SNAKE."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _topic_class(topic: str) -> str:
    """``capture.state`` -> ``CaptureState``."""
    return "".join(part.capitalize() for part in re.split(r"[._]", topic))


def _parse_xml(path: Path) -> dict[str, Any]:
    """Parse the D-Bus introspection XML into interfaces/methods/signals."""
    root = ET.parse(path).getroot()
    root_name = root.attrib["name"]
    interfaces: dict[str, Any] = {}

    for node in root.findall("node"):
        object_path = f"{root_name}/{node.attrib['name']}"
        for iface in node.findall("interface"):
            methods: dict[str, dict[str, list[tuple[str, str]]]] = {}
            signals: dict[str, list[tuple[str, str]]] = {}
            for method in iface.findall("method"):
                in_args: list[tuple[str, str]] = []
                out_args: list[tuple[str, str]] = []
                for arg in method.findall("arg"):
                    entry = (arg.attrib["name"], arg.attrib["type"])
                    if arg.get("direction", "in") == "out":
                        out_args.append(entry)
                    else:
                        in_args.append(entry)
                methods[method.attrib["name"]] = {"in": in_args, "out": out_args}
            for signal in iface.findall("signal"):
                signals[signal.attrib["name"]] = [
                    (arg.attrib["name"], arg.attrib["type"]) for arg in signal.findall("arg")
                ]
            interfaces[iface.attrib["name"]] = {
                "object_path": object_path,
                "methods": methods,
                "signals": signals,
            }
    return interfaces


def _source(repo_root: Path, ext: str) -> Path:
    return repo_root / f"{CONTRACT_STEM}.{ext}"


def load_contract(repo_root: Path) -> dict[str, Any]:
    """Load the canonical XML + JSON and cross-check the two encodings."""
    xml = _parse_xml(_source(repo_root, "xml"))
    with _source(repo_root, "json").open(encoding="utf-8") as handle:
        doc = json.load(handle)

    events_iface = xml[doc["interface"]]
    job_iface = xml[doc["job_interface"]["interface"]]

    # The XML is the wire source; the JSON is the semantics. Both name the same
    # methods/signals — a mismatch is a contract defect, not a codegen choice.
    if set(events_iface["methods"]) != set(doc["methods"]):
        raise ValueError("XML/JSON method mismatch")
    if set(events_iface["signals"]) != set(doc["signals"]):
        raise ValueError("XML/JSON signal mismatch")
    if set(job_iface["methods"]) != set(doc["job_interface"]["methods"]):
        raise ValueError("XML/JSON job method mismatch")

    return {"xml": xml, "doc": doc, "events": events_iface, "job": job_iface}


# ---- shared emitters -------------------------------------------------------
def _py_type(sig: str, enum: list[str] | None) -> str:
    if enum:
        return "Literal[" + ", ".join(repr(value) for value in enum) + "]"
    return PY_TYPES[sig]


def _ts_type(sig: str, enum: list[str] | None) -> str:
    if enum:
        return " | ".join(json.dumps(value) for value in enum)
    return TS_TYPES[sig]


def _members(members: list[tuple[str, str]]) -> str:
    return ", ".join(f"Member({name!r}, {sig!r}, {PY_TYPES[sig]!r})" for name, sig in members)


def _py_args(members: list[tuple[str, str]]) -> str:
    """Emit a Python tuple literal: a trailing comma keeps one element a tuple.

    ``(Member(...))`` is a bare ``Member``; ``(Member(...),)`` is a 1-tuple. The
    wire tables are annotated ``tuple[Member, ...]``, so the trailing comma is
    load-bearing for every single-argument method/signal.
    """
    inner = _members(members)
    return f"({inner},)" if inner else "()"


def _table(methods: dict[str, Any], *, signals: bool = False) -> list[str]:
    lines = ["("]
    for name in sorted(methods):
        spec = methods[name]
        lines.append("    Method(")
        lines.append(f"        {name!r},")
        if signals:
            lines.append(f"        out_args={_py_args(spec)},")
        else:
            lines.append(f"        in_args={_py_args(spec['in'])},")
            lines.append(f"        out_args={_py_args(spec['out'])},")
        lines.append("    ),")
    lines.append(")")
    return lines


# ---- Python emission -------------------------------------------------------
def emit_python(contract: dict[str, Any]) -> str:
    doc = contract["doc"]
    events = contract["events"]
    job = contract["job"]
    topics = doc["topics"]

    out: list[str] = [
        '"""GENERATED by gen/generate.py — DO NOT EDIT.',
        "",
        "Source of truth: the canonical event contract (XML wire + JSON semantics).",
        "Regenerate with `make generate`.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from typing import Final, Literal, NotRequired, TypedDict",
        "",
        "",
        "# ---- identity --------------------------------------------------------------",
        f"EVENTS_BUS: Final[str] = {doc['bus']!r}",
        f"EVENTS_BUS_NAME: Final[str] = {doc['well_known_name']!r}",
        f"EVENTS_OWNER: Final[str] = {doc['owner']!r}",
        f"EVENTS_OBJECT_PATH: Final[str] = {doc['object_path']!r}",
        f"EVENTS_INTERFACE: Final[str] = {doc['interface']!r}",
        f"JOB_OBJECT_PATH: Final[str] = {doc['job_interface']['object_path']!r}",
        f"JOB_INTERFACE: Final[str] = {doc['job_interface']['interface']!r}",
        "EVENTS_ERRORS: Final[tuple[str, ...]] = ("
        + ", ".join(repr(e) for e in doc["errors"])
        + ",)",
        "",
        "",
        "# ---- versioning ------------------------------------------------------------",
    ]
    for key in sorted(doc["versioning"]):
        out.append(f"VERSIONING_{_scream(key)}: Final[str] = {doc['versioning'][key]!r}")
    out += ["", "", "# ---- delivery --------------------------------------------------------------"]
    for key in sorted(doc["delivery"]):
        out.append(f"DELIVERY_{_scream(key)}: Final[str] = {doc['delivery'][key]!r}")
    out += ["", "", "# ---- validation ------------------------------------------------------------"]
    out.append(f"VALIDATION_IDENTITY: Final[str] = {doc['validation']['identity']!r}")
    out.append(
        "VALIDATION_STRUCTURAL: Final[tuple[str, ...]] = ("
        + ", ".join(repr(v) for v in doc["validation"]["structural"])
        + ",)"
    )
    out += ["", "", "# ---- job lease -------------------------------------------------------------"]
    for key in sorted(doc["job_lease"]):
        out.append(f"JOB_LEASE_{_scream(key)}: Final = {doc['job_lease'][key]!r}")
    out += [
        "",
        "",
        "# ---- wire tables -----------------------------------------------------------",
        "@dataclass(frozen=True, slots=True)",
        "class Member:",
        "    name: str",
        "    dbus: str",
        "    py: str",
        "",
        "",
        "@dataclass(frozen=True, slots=True)",
        "class Method:",
        "    name: str",
        "    in_args: tuple[Member, ...] = field(default_factory=tuple)",
        "    out_args: tuple[Member, ...] = field(default_factory=tuple)",
        "",
        "",
        "EVENTS_METHODS: Final[tuple[Method, ...]] = "
        + "\n".join(_table(events["methods"])),
        "",
        "",
        "EVENTS_SIGNALS: Final[tuple[Method, ...]] = "
        + "\n".join(_table(events["signals"], signals=True)),
        "",
        "",
        "JOB_METHODS: Final[tuple[Method, ...]] = " + "\n".join(_table(job["methods"])),
        "",
        "",
        "# ---- topic payloads --------------------------------------------------------",
    ]
    for topic in sorted(topics):
        spec = topics[topic]
        enums = spec.get("enum", {})
        optional = set(spec.get("optional", []))
        out.append(f"class {_topic_class(topic)}Payload(TypedDict):")
        for key in sorted(spec["payload"]):
            annotation = _py_type(spec["payload"][key], enums.get(key))
            if key in optional:
                annotation = f"NotRequired[{annotation}]"
            out.append(f"    {key}: {annotation}")
        out.append("")
        out.append("")
    out += [
        "@dataclass(frozen=True, slots=True)",
        "class Topic:",
        "    name: str",
        "    producer: str",
        "",
        "",
        "EVENTS_TOPICS: Final[tuple[Topic, ...]] = (",
    ]
    for topic in sorted(topics):
        out.append(f"    Topic({topic!r}, {topics[topic]['producer']!r}),")
    out.append(")")
    out.append("")
    return "\n".join(out) + "\n"


# ---- TypeScript emission ---------------------------------------------------
def _ts_members(members: list[tuple[str, str]]) -> str:
    return ", ".join(f"{name}: {json.dumps(sig)}" for name, sig in members)


def _ts_obj(members: list[tuple[str, str]]) -> str:
    inner = _ts_members(members)
    return "{}" if not inner else "{ " + inner + " }"


def emit_typescript(contract: dict[str, Any]) -> str:
    doc = contract["doc"]
    events = contract["events"]
    job = contract["job"]
    topics = doc["topics"]

    out: list[str] = [
        "// GENERATED by gen/generate.py — DO NOT EDIT.",
        "// Source of truth: the canonical event contract (XML wire + JSON semantics).",
        "// Regenerate with `make generate`.",
        "",
        "// ---- identity --------------------------------------------------------------",
        f"export const EVENTS_BUS = {json.dumps(doc['bus'])} as const;",
        f"export const EVENTS_BUS_NAME = {json.dumps(doc['well_known_name'])} as const;",
        f"export const EVENTS_OWNER = {json.dumps(doc['owner'])} as const;",
        f"export const EVENTS_OBJECT_PATH = {json.dumps(doc['object_path'])} as const;",
        f"export const EVENTS_INTERFACE = {json.dumps(doc['interface'])} as const;",
        f"export const JOB_OBJECT_PATH = {json.dumps(doc['job_interface']['object_path'])} as const;",
        f"export const JOB_INTERFACE = {json.dumps(doc['job_interface']['interface'])} as const;",
        "export const EVENTS_ERRORS = ["
        + ", ".join(json.dumps(e) for e in doc["errors"])
        + "] as const;",
        "export type EventError = (typeof EVENTS_ERRORS)[number];",
        "",
        "// ---- versioning ------------------------------------------------------------",
    ]
    for key in sorted(doc["versioning"]):
        out.append(
            f"export const VERSIONING_{_scream(key)} = {json.dumps(doc['versioning'][key])} as const;"
        )
    out += ["", "// ---- delivery --------------------------------------------------------------"]
    for key in sorted(doc["delivery"]):
        out.append(
            f"export const DELIVERY_{_scream(key)} = {json.dumps(doc['delivery'][key])} as const;"
        )
    out += ["", "// ---- validation ------------------------------------------------------------"]
    out.append(
        f"export const VALIDATION_IDENTITY = {json.dumps(doc['validation']['identity'])} as const;"
    )
    out.append(
        "export const VALIDATION_STRUCTURAL = ["
        + ", ".join(json.dumps(v) for v in doc["validation"]["structural"])
        + "] as const;"
    )
    out += ["", "// ---- job lease -------------------------------------------------------------"]
    for key in sorted(doc["job_lease"]):
        out.append(
            f"export const JOB_LEASE_{_scream(key)} = {json.dumps(doc['job_lease'][key])} as const;"
        )
    out += [
        "",
        "// ---- wire tables -----------------------------------------------------------",
        "export const EVENTS_METHODS = {",
    ]
    for name in sorted(events["methods"]):
        spec = events["methods"][name]
        out.append(f"  {name}: {{")
        out.append(f"    in: {_ts_obj(spec['in'])},")
        out.append(f"    out: {_ts_obj(spec['out'])},")
        out.append("  },")
    out += ["} as const;", "", "export const EVENTS_SIGNALS = {"]
    for name in sorted(events["signals"]):
        out.append(f"  {name}: {{ {_ts_members(events['signals'][name])} }},")
    out += ["} as const;", "", "export const JOB_METHODS = {"]
    for name in sorted(job["methods"]):
        spec = job["methods"][name]
        out.append(f"  {name}: {{")
        out.append(f"    in: {_ts_obj(spec['in'])},")
        out.append(f"    out: {_ts_obj(spec['out'])},")
        out.append("  },")
    out += ["} as const;", "", "export const EVENTS_TOPICS = {"]
    for topic in sorted(topics):
        out.append(f"  {json.dumps(topic)}: {{ producer: {json.dumps(topics[topic]['producer'])} }},")
    out += [
        "} as const;",
        "export type EventTopic = keyof typeof EVENTS_TOPICS;",
        "",
        "// ---- topic payloads --------------------------------------------------------",
    ]
    for topic in sorted(topics):
        spec = topics[topic]
        enums = spec.get("enum", {})
        optional = set(spec.get("optional", []))
        out.append(f"export interface {_topic_class(topic)}Payload {{")
        for key in sorted(spec["payload"]):
            mark = "?" if key in optional else ""
            out.append(f"  {key}{mark}: {_ts_type(spec['payload'][key], enums.get(key))};")
        out.append("}")
        out.append("")
    return "\n".join(out) + "\n"


# ---- JSON Schema emission --------------------------------------------------
def _json_members(entries: list[str]) -> list[tuple[str, str]]:
    """``["topic:s", "payload:a{sv}"]`` -> ``[("topic", "s"), ...]``."""
    members: list[tuple[str, str]] = []
    for entry in entries:
        name, sig = entry.split(":", 1)
        members.append((name, sig))
    return members


def _object_schema(
    members: list[tuple[str, str]],
    enums: dict[str, list[str]] | None = None,
    optional: set[str] | None = None,
) -> dict[str, Any]:
    """An object schema with explicit required/optional keys, types and enums."""
    enums = enums or {}
    optional = optional or set()
    properties: dict[str, Any] = {}
    for name, sig in sorted(members):
        prop = dict(JSON_TYPES[sig])
        if name in enums:
            prop["enum"] = list(enums[name])
        properties[name] = prop
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(name for name, _ in members if name not in optional),
        "properties": properties,
    }


def emit_events_schema(contract: dict[str, Any]) -> str:
    """Emit the event wire schema, derived from the canonical JSON semantics.

    Per-topic definitions make required/optional keys, types and enums
    explicit (the shape the runtime's per-topic TOPIC_SCHEMAS validation
    expresses); the envelopes discriminate signal/method/topic payloads.
    """
    doc = contract["doc"]
    signals = {name: _json_members(entries) for name, entries in doc["signals"].items()}
    methods = {
        name: {"in": _json_members(spec.get("in", [])), "out": _json_members(spec.get("out", []))}
        for name, spec in doc["methods"].items()
    }
    topics = doc["topics"]

    defs: dict[str, Any] = {}
    for name in sorted(signals):
        defs[f"Signal_{name}"] = _object_schema(signals[name])
    for name in sorted(methods):
        defs[f"MethodIn_{name}"] = _object_schema(methods[name]["in"])
        defs[f"MethodOut_{name}"] = _object_schema(methods[name]["out"])
    for topic in sorted(topics):
        spec = topics[topic]
        members = [(key, spec["payload"][key]) for key in sorted(spec["payload"])]
        defs[f"Topic_{topic.replace('.', '_')}"] = _object_schema(
            members, spec.get("enum", {}), set(spec.get("optional", []))
        )

    defs["SignalEnvelope"] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["signal", "members"],
        "properties": {
            "signal": {"enum": sorted(signals)},
            "members": {"type": "object"},
        },
        "allOf": [
            {
                "if": {"properties": {"signal": {"const": name}}, "required": ["signal"]},
                "then": {"properties": {"members": {"$ref": f"#/$defs/Signal_{name}"}}},
            }
            for name in sorted(signals)
        ],
    }
    defs["MethodEnvelope"] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["method", "args"],
        "properties": {
            "method": {"enum": sorted(methods)},
            "args": {"type": "object"},
        },
        "allOf": [
            {
                "if": {"properties": {"method": {"const": name}}, "required": ["method"]},
                "then": {"properties": {"args": {"$ref": f"#/$defs/MethodIn_{name}"}}},
            }
            for name in sorted(methods)
        ],
    }
    defs["TopicEnvelope"] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["topic", "producer", "payload"],
        "properties": {
            "topic": {"enum": sorted(topics)},
            "producer": {"type": "string"},
            "payload": {"type": "object"},
        },
        "allOf": [
            {
                "if": {"properties": {"topic": {"const": topic}}, "required": ["topic"]},
                "then": {
                    "properties": {
                        "payload": {"$ref": f"#/$defs/Topic_{topic.replace('.', '_')}"}
                    }
                },
            }
            for topic in sorted(topics)
        ],
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://dotfiles.local/generated/events.schema.json",
        "$defs": defs,
        "oneOf": [
            {"$ref": "#/$defs/SignalEnvelope"},
            {"$ref": "#/$defs/MethodEnvelope"},
            {"$ref": "#/$defs/TopicEnvelope"},
        ],
    }
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


# ---- entry point -----------------------------------------------------------
def generate(repo_root: Path, out_dir: Path) -> dict[str, str]:
    contract = load_contract(repo_root)
    artifacts = {
        "contract.py": emit_python(contract),
        "contract.ts": emit_typescript(contract),
        "events.schema.json": emit_events_schema(contract),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in artifacts.items():
        (out_dir / name).write_text(text, encoding="utf-8")
    return artifacts


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Generate event-contract bindings.")
    parser.add_argument("--out", type=Path, default=repo_root / "generated")
    args = parser.parse_args()
    artifacts = generate(repo_root, args.out)
    for name, text in artifacts.items():
        print(f"[gen] {name} ({len(text)} bytes, {text.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
