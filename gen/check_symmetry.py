#!/usr/bin/env python3
"""Symmetric drift gate: check the generated artifacts against the canonical contract.

A plain regenerate-and-diff only proves that the committed files equal a *fresh*
generation. It cannot see a key that the generator itself drops, and it only
looks one way (contract -> artifact). This checker compares the **committed**
artifacts against the canonical contract in BOTH directions:

    contract -> generated : every contract topic / key / type / enum is present
    generated -> contract : every generated topic / key / enum is in the contract

so an extra key hand-added to a generated file, or a contract key the generator
silently dropped, is caught. The legs:

    event-contract.json  <-> generated/events.schema.json   topics: keys, types, enums
    event-contract.xml   <-> generated/contract.py          wire methods / signals
    event-contract.json  <-> generated/contract.py          constants, topics, payloads
    event-contract.xml   <-> generated/contract.ts          wire methods / signals
    event-contract.json  <-> generated/contract.ts          constants, topics, payloads

The runtime-tables leg (the Python runtime's hand-embedded wire tables and
per-topic validation schemas) is CROSS-REPO and belongs to REQ-004; it is left
as a named hook below and is not faked.

Run:  python3 gen/check_symmetry.py [--repo-root DIR] [--generated DIR]
Exit: 0 when every leg agrees; 1 with a per-leg report otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import typing
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ---- REQ-004 hook (do not fake) --------------------------------------------
RUNTIME_TABLES_HOOK = (
    "TODO(REQ-004): cross-repo leg — assert the runtime's hand-embedded wire "
    "tables and per-topic validation schemas (dotfiles-v3) match this contract. "
    "Not asserted here: REQ-004 repoints the runtime to the generated bindings."
)

# D-Bus signature -> Python / TypeScript / JSON-Schema type. These are the
# contract's fixed mappings; a disagreement with the generator is a drift.
PY_CLASS: dict[str, Any] = {
    "s": str,
    "u": int,
    "i": int,
    "x": int,
    "d": float,
    "b": bool,
    "a{sv}": dict[str, object],
    "a{ss}": dict[str, str],
    "as": list[str],
}
TS_TYPE: dict[str, str] = {
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
JSON_TYPE: dict[str, dict[str, Any]] = {
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

_MISSING = object()


# ---- shared helpers --------------------------------------------------------
def _scream(name: str) -> str:
    """camelCase / dotted name -> SCREAMING_SNAKE (mirrors the generator)."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _topic_class(topic: str) -> str:
    """``capture.state`` -> ``CaptureState`` (mirrors the generator)."""
    return "".join(part.capitalize() for part in re.split(r"[._]", topic))


def _json_args(entries: list[str]) -> list[tuple[str, str]]:
    """``["topic:s", ...]`` -> ``[("topic", "s"), ...]``."""
    out: list[tuple[str, str]] = []
    for entry in entries:
        name, sig = entry.split(":", 1)
        out.append((name, sig))
    return out


def parse_xml(path: Path) -> dict[str, dict[str, Any]]:
    """Parse the D-Bus introspection XML, keyed by interface name."""
    root = ET.parse(path).getroot()
    root_name = root.attrib["name"]
    interfaces: dict[str, dict[str, Any]] = {}
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
                    (out_args if arg.get("direction", "in") == "out" else in_args).append(entry)
                methods[method.attrib["name"]] = {"in": in_args, "out": out_args}
            for signal in iface.findall("signal"):
                signals[signal.attrib["name"]] = [
                    (a.attrib["name"], a.attrib["type"]) for a in signal.findall("arg")
                ]
            interfaces[iface.attrib["name"]] = {
                "object_path": object_path,
                "methods": methods,
                "signals": signals,
            }
    return interfaces


def load_python(generated_dir: Path) -> Any:
    """Import the generated contract.py as a fresh module for introspection."""
    path = generated_dir / "contract.py"
    name = f"_generated_contract_drift_{id(path)}_{len(sys.modules)}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _expected_scalars(doc: dict[str, Any], *, sequence: type) -> dict[str, Any]:
    """Constant name -> value. ``sequence`` is ``tuple`` (Python) or ``list`` (TS)."""
    out: dict[str, Any] = {
        "EVENTS_BUS": doc["bus"],
        "EVENTS_BUS_NAME": doc["well_known_name"],
        "EVENTS_OWNER": doc["owner"],
        "EVENTS_OBJECT_PATH": doc["object_path"],
        "EVENTS_INTERFACE": doc["interface"],
        "JOB_OBJECT_PATH": doc["job_interface"]["object_path"],
        "JOB_INTERFACE": doc["job_interface"]["interface"],
        "EVENTS_ERRORS": sequence(doc["errors"]),
        "VALIDATION_IDENTITY": doc["validation"]["identity"],
        "VALIDATION_STRUCTURAL": sequence(doc["validation"]["structural"]),
    }
    for key, value in doc["versioning"].items():
        out[f"VERSIONING_{_scream(key)}"] = value
    for key, value in doc["delivery"].items():
        out[f"DELIVERY_{_scream(key)}"] = value
    for key, value in doc["job_lease"].items():
        out[f"JOB_LEASE_{_scream(key)}"] = value
    return out


def _compare_object(
    label: str,
    node: Any,
    members: list[tuple[str, str]],
    enums: dict[str, list[str]],
    errs: list[str],
) -> None:
    """Compare one schema object node's keys/required/types/enums, both ways."""
    if node is None:
        errs.append(f"{label}: definition missing")
        return
    payload = dict(members)
    props = node.get("properties", {})
    required = set(node.get("required", []))
    for key in sorted(set(payload) - set(props)):
        errs.append(f"{label}: contract key {key!r} missing from schema")
    for key in sorted(set(props) - set(payload)):
        errs.append(f"{label}: schema key {key!r} not in contract")
    if required != set(payload):
        errs.append(
            f"{label}: required {sorted(required)} != contract keys {sorted(payload)}"
        )
    for key, sig in payload.items():
        prop = props.get(key)
        if prop is None:
            continue
        expected = dict(JSON_TYPE[sig])
        if key in enums:
            expected["enum"] = list(enums[key])
        if prop != expected:
            errs.append(f"{label}.{key}: schema {prop} != contract {expected}")


# ---- leg 1: contract.json <-> events.schema.json ---------------------------
def check_schema(doc: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    defs = schema.get("$defs", {})
    topics = doc["topics"]

    expected_topic_defs = {f"Topic_{t.replace('.', '_')}" for t in topics}
    got_topic_defs = {k for k in defs if k.startswith("Topic_")}
    for name in sorted(expected_topic_defs - got_topic_defs):
        errs.append(f"[schema] topic definition {name!r} missing")
    for name in sorted(got_topic_defs - expected_topic_defs):
        errs.append(f"[schema] topic definition {name!r} not in contract")

    env = defs.get("TopicEnvelope")
    if env is None:
        errs.append("[schema] TopicEnvelope missing")
    else:
        enum = set(env["properties"]["topic"]["enum"])
        for topic in sorted(set(topics) - enum):
            errs.append(f"[schema] TopicEnvelope enum missing contract topic {topic!r}")
        for topic in sorted(enum - set(topics)):
            errs.append(f"[schema] TopicEnvelope enum has {topic!r} not in contract")

    for topic, spec in topics.items():
        node = defs.get(f"Topic_{topic.replace('.', '_')}")
        members = [(key, spec["payload"][key]) for key in sorted(spec["payload"])]
        optional = set(spec.get("optional", []))
        enums = spec.get("enum", {})
        if node is None:
            errs.append(f"[schema] Topic_{topic}: definition missing")
            continue
        props = node.get("properties", {})
        required = set(node.get("required", []))
        for key in sorted(set(spec["payload"]) - set(props)):
            errs.append(f"[schema] {topic}: contract key {key!r} missing from schema")
        for key in sorted(set(props) - set(spec["payload"])):
            errs.append(f"[schema] {topic}: schema key {key!r} not in contract")
        expected_required = set(spec["payload"]) - optional
        for key in sorted(expected_required - required):
            errs.append(f"[schema] {topic}: required key {key!r} not marked required")
        for key in sorted(required - expected_required):
            errs.append(f"[schema] {topic}: key {key!r} required but contract has it optional/absent")
        for key, sig in spec["payload"].items():
            prop = props.get(key)
            if prop is None:
                continue
            expected = dict(JSON_TYPE[sig])
            if key in enums:
                expected["enum"] = list(enums[key])
            if prop != expected:
                errs.append(f"[schema] {topic}.{key}: schema {prop} != contract {expected}")

    signals = {name: _json_args(entries) for name, entries in doc["signals"].items()}
    methods = {
        name: {"in": _json_args(spec.get("in", [])), "out": _json_args(spec.get("out", []))}
        for name, spec in doc["methods"].items()
    }

    expected_signal_defs = {f"Signal_{n}" for n in signals}
    got_signal_defs = {k for k in defs if k.startswith("Signal_")}
    for name in sorted(expected_signal_defs - got_signal_defs):
        errs.append(f"[schema] signal definition {name!r} missing")
    for name in sorted(got_signal_defs - expected_signal_defs):
        errs.append(f"[schema] signal definition {name!r} not in contract")

    expected_method_defs = {f"Method{side}_{n}" for n in methods for side in ("In", "Out")}
    got_method_defs = {k for k in defs if re.match(r"^Method(In|Out)_", k)}
    for name in sorted(expected_method_defs - got_method_defs):
        errs.append(f"[schema] method definition {name!r} missing")
    for name in sorted(got_method_defs - expected_method_defs):
        errs.append(f"[schema] method definition {name!r} not in contract")

    for name, args in signals.items():
        _compare_object(f"[schema] Signal_{name}", defs.get(f"Signal_{name}"), args, {}, errs)
    for name, spec in methods.items():
        _compare_object(f"[schema] MethodIn_{name}", defs.get(f"MethodIn_{name}"), spec["in"], {}, errs)
        _compare_object(f"[schema] MethodOut_{name}", defs.get(f"MethodOut_{name}"), spec["out"], {}, errs)

    for label, key, names in (
        ("SignalEnvelope", "signal", signals),
        ("MethodEnvelope", "method", methods),
    ):
        node = defs.get(label)
        if node is None:
            errs.append(f"[schema] {label} missing")
            continue
        enum = set(node["properties"][key]["enum"])
        for name in sorted(set(names) - enum):
            errs.append(f"[schema] {label} enum missing {name!r}")
        for name in sorted(enum - set(names)):
            errs.append(f"[schema] {label} enum has {name!r} not in contract")
    return errs


# ---- leg 2: contract <-> contract.py ---------------------------------------
def _compare_wire_py(
    label: str, methods: Any, expected: dict[str, Any], errs: list[str], *, signals: bool
) -> None:
    got: dict[str, Any] = {}
    for method in methods:
        if signals:
            got[method.name] = [(a.name, a.dbus) for a in method.out_args]
        else:
            got[method.name] = {
                "in": [(a.name, a.dbus) for a in method.in_args],
                "out": [(a.name, a.dbus) for a in method.out_args],
            }
    exp: dict[str, Any] = {}
    for name, spec in expected.items():
        exp[name] = list(spec) if signals else {"in": list(spec["in"]), "out": list(spec["out"])}
    for name in sorted(set(got) - set(exp)):
        errs.append(f"{label}: {name!r} not in contract")
    for name in sorted(set(exp) - set(got)):
        errs.append(f"{label}: {name!r} missing")
    for name in sorted(set(got) & set(exp)):
        if got[name] != exp[name]:
            errs.append(f"{label}.{name}: {got[name]} != contract {exp[name]}")


def check_python(doc: dict[str, Any], xml: dict[str, Any], mod: Any) -> list[str]:
    errs: list[str] = []
    events = xml[doc["interface"]]
    job = xml[doc["job_interface"]["interface"]]

    for name, value in _expected_scalars(doc, sequence=tuple).items():
        got = getattr(mod, name, _MISSING)
        if got != value:
            errs.append(f"[contract.py] {name}: {got!r} != contract {value!r}")

    _compare_wire_py("[contract.py] EVENTS_METHODS", getattr(mod, "EVENTS_METHODS", ()), events["methods"], errs, signals=False)
    _compare_wire_py("[contract.py] EVENTS_SIGNALS", getattr(mod, "EVENTS_SIGNALS", ()), events["signals"], errs, signals=True)
    _compare_wire_py("[contract.py] JOB_METHODS", getattr(mod, "JOB_METHODS", ()), job["methods"], errs, signals=False)

    got_topics = {t.name: t.producer for t in getattr(mod, "EVENTS_TOPICS", ())}
    exp_topics = {t: s["producer"] for t, s in doc["topics"].items()}
    for topic in sorted(set(got_topics) - set(exp_topics)):
        errs.append(f"[contract.py] topic {topic!r} not in contract")
    for topic in sorted(set(exp_topics) - set(got_topics)):
        errs.append(f"[contract.py] topic {topic!r} missing")
    for topic in sorted(set(got_topics) & set(exp_topics)):
        if got_topics[topic] != exp_topics[topic]:
            errs.append(f"[contract.py] topic {topic!r} producer {got_topics[topic]!r} != {exp_topics[topic]!r}")

    for topic, spec in doc["topics"].items():
        class_name = _topic_class(topic) + "Payload"
        cls = getattr(mod, class_name, None)
        if cls is None:
            errs.append(f"[contract.py] payload class {class_name} missing for {topic!r}")
            continue
        try:
            hints = typing.get_type_hints(cls, include_extras=True)
        except Exception as exc:  # noqa: BLE001 - report any resolution failure
            errs.append(f"[contract.py] {class_name}: cannot resolve annotations: {exc}")
            continue
        enums = spec.get("enum", {})
        optional = set(spec.get("optional", []))
        expected: dict[str, Any] = {}
        for key, sig in spec["payload"].items():
            base = typing.Literal[tuple(enums[key])] if key in enums else PY_CLASS[sig]
            expected[key] = typing.NotRequired[base] if key in optional else base
        for key in sorted(set(hints) - set(expected)):
            errs.append(f"[contract.py] {class_name}: field {key!r} not in contract")
        for key in sorted(set(expected) - set(hints)):
            errs.append(f"[contract.py] {class_name}: contract field {key!r} missing")
        for key in sorted(set(hints) & set(expected)):
            if hints[key] != expected[key]:
                errs.append(f"[contract.py] {class_name}.{key}: {hints[key]} != contract {expected[key]}")
    return errs


# ---- leg 3: contract <-> contract.ts ---------------------------------------
_TS_SCALAR = re.compile(r"^export const (\w+) = (.+?) as const;$", re.M)
_TS_TOPIC_LINE = re.compile(r'^("(?:[^"\\]|\\.)*"): \{ producer: ("(?:[^"\\]|\\.)*") \},$')
_TS_SIGNAL_LINE = re.compile(r"^(\w+): \{(.*)\},$")
_TS_ARG = re.compile(r'(\w+): "([^"]*)"')
_TS_INTERFACE = re.compile(r"export interface (\w+) \{\n(.*?)\n\}", re.S)


def _ts_block(ts: str, const_name: str) -> str:
    match = re.search(rf"export const {const_name} = \{{(.*?)\}} as const;", ts, re.S)
    if match is None:
        raise ValueError(f"{const_name} block not found in contract.ts")
    return match.group(1)


def _parse_ts_scalars(ts: str) -> dict[str, Any]:
    return {m.group(1): json.loads(m.group(2)) for m in _TS_SCALAR.finditer(ts)}


def _parse_ts_topics(ts: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in _ts_block(ts, "EVENTS_TOPICS").splitlines():
        line = line.strip()
        if not line:
            continue
        match = _TS_TOPIC_LINE.match(line)
        if match is None:
            raise ValueError(f"unparsed EVENTS_TOPICS line: {line!r}")
        out[json.loads(match.group(1))] = json.loads(match.group(2))
    return out


def _parse_ts_signals(ts: str) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    for line in _ts_block(ts, "EVENTS_SIGNALS").splitlines():
        line = line.strip()
        if not line:
            continue
        match = _TS_SIGNAL_LINE.match(line)
        if match is None:
            raise ValueError(f"unparsed EVENTS_SIGNALS line: {line!r}")
        out[match.group(1)] = _TS_ARG.findall(match.group(2))
    return out


def _parse_ts_methods(ts: str, const_name: str) -> dict[str, dict[str, list[tuple[str, str]]]]:
    out: dict[str, dict[str, list[tuple[str, str]]]] = {}
    current: str | None = None
    for raw in _ts_block(ts, const_name).splitlines():
        line = raw.strip()
        if not line:
            continue
        head = re.match(r"^(\w+): \{$", line)
        if head:
            current = head.group(1)
            out[current] = {"in": [], "out": []}
            continue
        side = re.match(r"^(in|out): \{(.*)\},$", line)
        if side and current is not None:
            out[current][side.group(1)] = _TS_ARG.findall(side.group(2))
            continue
        if line == "},":
            current = None
    return out


def _parse_ts_interfaces(ts: str) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for match in _TS_INTERFACE.finditer(ts):
        fields: dict[str, dict[str, Any]] = {}
        for line in match.group(2).splitlines():
            line = line.strip()
            if not line:
                continue
            field = re.match(r"^(\w+)(\?)?: (.+);$", line)
            if field is None:
                raise ValueError(f"unparsed interface field: {line!r}")
            fields[field.group(1)] = {"optional": bool(field.group(2)), "type": field.group(3)}
        out[match.group(1)] = fields
    return out


def _compare_wire_ts(
    label: str, got: dict[str, Any], expected: dict[str, Any], errs: list[str], *, signals: bool
) -> None:
    exp: dict[str, Any] = {}
    for name, spec in expected.items():
        exp[name] = list(spec) if signals else {"in": list(spec["in"]), "out": list(spec["out"])}
    for name in sorted(set(got) - set(exp)):
        errs.append(f"{label}: {name!r} not in contract")
    for name in sorted(set(exp) - set(got)):
        errs.append(f"{label}: {name!r} missing")
    for name in sorted(set(got) & set(exp)):
        if got[name] != exp[name]:
            errs.append(f"{label}.{name}: {got[name]} != contract {exp[name]}")


def check_typescript(doc: dict[str, Any], xml: dict[str, Any], ts: str) -> list[str]:
    errs: list[str] = []
    events = xml[doc["interface"]]
    job = xml[doc["job_interface"]["interface"]]

    scalars = _parse_ts_scalars(ts)
    for name, value in _expected_scalars(doc, sequence=list).items():
        got = scalars.get(name, _MISSING)
        if got != value:
            errs.append(f"[contract.ts] {name}: {got!r} != contract {value!r}")

    _compare_wire_ts("[contract.ts] EVENTS_METHODS", _parse_ts_methods(ts, "EVENTS_METHODS"), events["methods"], errs, signals=False)
    _compare_wire_ts("[contract.ts] EVENTS_SIGNALS", _parse_ts_signals(ts), events["signals"], errs, signals=True)
    _compare_wire_ts("[contract.ts] JOB_METHODS", _parse_ts_methods(ts, "JOB_METHODS"), job["methods"], errs, signals=False)

    got_topics = _parse_ts_topics(ts)
    exp_topics = {t: s["producer"] for t, s in doc["topics"].items()}
    for topic in sorted(set(got_topics) - set(exp_topics)):
        errs.append(f"[contract.ts] topic {topic!r} not in contract")
    for topic in sorted(set(exp_topics) - set(got_topics)):
        errs.append(f"[contract.ts] topic {topic!r} missing")
    for topic in sorted(set(got_topics) & set(exp_topics)):
        if got_topics[topic] != exp_topics[topic]:
            errs.append(f"[contract.ts] topic {topic!r} producer {got_topics[topic]!r} != {exp_topics[topic]!r}")

    interfaces = _parse_ts_interfaces(ts)
    expected_names = {_topic_class(t) + "Payload" for t in doc["topics"]}
    got_names = set(interfaces)
    for name in sorted(expected_names - got_names):
        errs.append(f"[contract.ts] payload interface {name} missing")
    for name in sorted(got_names - expected_names):
        errs.append(f"[contract.ts] payload interface {name} not in contract")

    for topic, spec in doc["topics"].items():
        name = _topic_class(topic) + "Payload"
        fields = interfaces.get(name)
        if fields is None:
            continue
        enums = spec.get("enum", {})
        optional = set(spec.get("optional", []))
        expected: dict[str, Any] = {}
        for key, sig in spec["payload"].items():
            typ = " | ".join(json.dumps(v) for v in enums[key]) if key in enums else TS_TYPE[sig]
            expected[key] = {"optional": key in optional, "type": typ}
        for key in sorted(set(fields) - set(expected)):
            errs.append(f"[contract.ts] {name}: field {key!r} not in contract")
        for key in sorted(set(expected) - set(fields)):
            errs.append(f"[contract.ts] {name}: contract field {key!r} missing")
        for key in sorted(set(fields) & set(expected)):
            if fields[key] != expected[key]:
                errs.append(f"[contract.ts] {name}.{key}: {fields[key]} != contract {expected[key]}")
    return errs


# ---- driver ----------------------------------------------------------------
def run_checks(repo_root: Path, generated_dir: Path) -> dict[str, list[str]]:
    """Run every leg; return ``{leg_name: [errors]}`` (empty list == agreement)."""
    with (repo_root / "event-contract.json").open(encoding="utf-8") as handle:
        doc = json.load(handle)
    xml = parse_xml(repo_root / "event-contract.xml")
    with (generated_dir / "events.schema.json").open(encoding="utf-8") as handle:
        schema = json.load(handle)
    ts = (generated_dir / "contract.ts").read_text(encoding="utf-8")
    mod = load_python(generated_dir)

    return {
        "schema": check_schema(doc, schema),
        "python": check_python(doc, xml, mod),
        "typescript": check_typescript(doc, xml, ts),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Symmetric contract drift check.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--generated", type=Path, default=None)
    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root
    generated_dir: Path = args.generated or (repo_root / "generated")

    try:
        legs = run_checks(repo_root, generated_dir)
    except Exception as exc:  # noqa: BLE001 - a load failure is itself drift
        print(f"[drift] FAILED to read contract/artifacts: {exc}", file=sys.stderr)
        return 1

    total = 0
    for leg, errors in legs.items():
        if errors:
            total += len(errors)
            print(f"[fail] {leg} <-> contract: {len(errors)} mismatch(es)")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[ok]   {leg} <-> contract")

    print(f"[skip] runtime tables <-> contract — {RUNTIME_TABLES_HOOK}")
    if total:
        print(f"[drift] {total} mismatch(es) — regenerate and commit, or fix the contract")
        return 1
    print("[drift] symmetric: contract and generated/ agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
