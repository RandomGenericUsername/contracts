#!/usr/bin/env python3
"""Coverage + determinism tests for the event-contract generator.

Run: ``python3 -m unittest discover -s gen -p 'test_*.py'``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

GEN_DIR = Path(__file__).resolve().parent
REPO_ROOT = GEN_DIR.parent
sys.path.insert(0, str(GEN_DIR))

import generate  # noqa: E402  (path set above)

EXPECTED_TOPICS = {
    "icme.saved",
    "capture.state",
    "speedtest.state",
    "clipboard.update",
    "clipboard.state",
    "wallpaper.state",
}
EXPECTED_HUB_METHODS = {
    "Emit",
    "BeginJob",
    "RenewJob",
    "AdoptJob",
    "ReportProgress",
    "EndJob",
    "Control",
    "GetActiveJobs",
    "GetTopicState",
}
EXPECTED_SIGNALS = {
    "JobStarted",
    "JobProgress",
    "JobFinished",
    "DomainEvent",
    "JobsCleared",
}
# Required (non-optional) payload keys per topic, from the canonical contract.
EXPECTED_REQUIRED = {
    "icme.saved": {"path"},
    "capture.state": {"state", "elapsed_seconds"},
    "speedtest.state": {"state", "trigger"},
    "clipboard.update": {"type", "hash", "path", "preview"},
    "clipboard.state": {"state", "job_id"},
    "wallpaper.state": {"state", "wallpaper_hash"},
}
# Enum-constrained payload fields per topic.
EXPECTED_ENUMS = {
    "capture.state": {"state": {"idle", "recording", "paused"}},
    "speedtest.state": {
        "state": {"starting", "done", "error"},
        "trigger": {"scheduled", "manual", "connect"},
    },
    "clipboard.update": {"type": {"text", "image", "link", "code", "color", "emoji"}},
    "clipboard.state": {"state": {"idle", "running", "paused"}},
    "wallpaper.state": {
        "state": {"applying", "visible", "done", "error"},
        "trigger": {"set", "regenerate", "reconcile", "reactive"},
    },
}


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("generated_contract", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_contract"] = module
    spec.loader.exec_module(module)
    return module


class GeneratorCoverageTest(unittest.TestCase):
    def test_python_bindings_cover_the_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate.generate(REPO_ROOT, Path(tmp))
            mod = _load_module(Path(tmp) / "contract.py")

            self.assertEqual({m.name for m in mod.EVENTS_METHODS}, EXPECTED_HUB_METHODS)
            self.assertEqual({s.name for s in mod.EVENTS_SIGNALS}, EXPECTED_SIGNALS)
            self.assertEqual({t.name for t in mod.EVENTS_TOPICS}, EXPECTED_TOPICS)
            self.assertEqual({m.name for m in mod.JOB_METHODS}, {"Control"})
            self.assertEqual(mod.JOB_INTERFACE, "org.dotfiles.Job1")
            self.assertEqual(mod.EVENTS_INTERFACE, "org.dotfiles.Events1")

    def test_typescript_bindings_cover_the_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate.generate(REPO_ROOT, Path(tmp))
            ts = (Path(tmp) / "contract.ts").read_text(encoding="utf-8")

            for name in EXPECTED_TOPICS | EXPECTED_HUB_METHODS | EXPECTED_SIGNALS:
                self.assertIn(name, ts, f"{name!r} missing from contract.ts")
            self.assertIn("org.dotfiles.Job1", ts)
            self.assertIn("export const JOB_METHODS", ts)
            self.assertIn("export interface SpeedtestStatePayload", ts)

    def test_json_schema_covers_the_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate.generate(REPO_ROOT, Path(tmp))
            schema = json.loads((Path(tmp) / "events.schema.json").read_text(encoding="utf-8"))
            defs = schema["$defs"]

            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            for env in ("SignalEnvelope", "MethodEnvelope", "TopicEnvelope"):
                self.assertIn(env, defs)

            for topic in EXPECTED_TOPICS:
                node = defs[f"Topic_{topic.replace('.', '_')}"]
                self.assertEqual(
                    set(node["required"]), EXPECTED_REQUIRED[topic], f"required keys for {topic}"
                )
                for field, values in EXPECTED_ENUMS.get(topic, {}).items():
                    self.assertEqual(
                        set(node["properties"][field]["enum"]),
                        values,
                        f"{topic}.{field} enum",
                    )
                # optional keys must never be required
                for field in node["properties"]:
                    if field not in EXPECTED_REQUIRED[topic]:
                        self.assertNotIn(field, node["required"])

            # spot-check scalar types are explicit
            capture = defs["Topic_capture_state"]
            self.assertEqual(capture["properties"]["elapsed_seconds"]["type"], "integer")
            self.assertEqual(defs["Topic_speedtest_state"]["properties"]["down_mbps"]["type"], "number")


class GeneratorDeterminismTest(unittest.TestCase):
    def test_two_runs_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            generate.generate(REPO_ROOT, Path(first))
            generate.generate(REPO_ROOT, Path(second))
            for name in ("contract.py", "contract.ts", "events.schema.json"):
                self.assertEqual(
                    (Path(first) / name).read_bytes(),
                    (Path(second) / name).read_bytes(),
                    f"{name} differs between runs",
                )


if __name__ == "__main__":
    unittest.main()
