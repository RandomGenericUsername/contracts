#!/usr/bin/env python3
"""Negative tests for the symmetric drift gate.

A gate that cannot fail is worthless. These prove ``gen/check_symmetry.py``
rejects drift by mutating a throwaway copy of the repo:

  (a) a hand-edited generated artifact (schema key and a constant)
  (b) a contract topic/key added without regenerating the artifacts
  (c) an extra schema key absent from the contract (the reverse check)
  (d) a hand-edited TypeScript table

Run: ``python3 -m unittest discover -s gen -p 'test_*.py'``.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

GEN_DIR = Path(__file__).resolve().parent
REPO_ROOT = GEN_DIR.parent
sys.path.insert(0, str(GEN_DIR))

import check_symmetry  # noqa: E402  (path set above)


class SymmetricDriftGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        shutil.copy(REPO_ROOT / "event-contract.json", self.root / "event-contract.json")
        shutil.copy(REPO_ROOT / "event-contract.xml", self.root / "event-contract.xml")
        shutil.copytree(REPO_ROOT / "generated", self.root / "generated")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _errors(self) -> list[str]:
        legs = check_symmetry.run_checks(self.root, self.root / "generated")
        return [error for errors in legs.values() for error in errors]

    def test_clean_tree_agrees(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_a_hand_edited_generated_file_fails(self) -> None:
        path = self.root / "generated" / "events.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        schema["$defs"]["Topic_capture_state"]["properties"]["bogus"] = {"type": "string"}
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.assertTrue(any("bogus" in e for e in self._errors()), "hand-added schema key not caught")

        py = self.root / "generated" / "contract.py"
        py.write_text(
            py.read_text(encoding="utf-8").replace("'org.dotfiles.Events'", "'org.dotfiles.EventsX'"),
            encoding="utf-8",
        )
        self.assertTrue(
            any("EVENTS_BUS_NAME" in e for e in self._errors()),
            "hand-edited constant not caught",
        )

    def test_b_contract_key_without_regeneration_fails(self) -> None:
        path = self.root / "event-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["topics"]["capture.state"]["payload"]["new_key"] = "s"
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("new_key" in e for e in self._errors()), "contract key not caught")

    def test_b2_contract_topic_without_regeneration_fails(self) -> None:
        path = self.root / "event-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["topics"]["brand.new"] = {"producer": "x", "payload": {"a": "s"}}
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("brand.new" in e for e in self._errors()), "contract topic not caught")

    def test_c_extra_schema_key_reverse_check_fails(self) -> None:
        path = self.root / "generated" / "events.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        node = schema["$defs"]["Topic_wallpaper_state"]
        node["properties"]["ghost"] = {"type": "string"}
        node["required"].append("ghost")
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.assertTrue(
            any("wallpaper.state" in e and "ghost" in e for e in self._errors()),
            "extra schema key not caught by the reverse check",
        )

    def test_d_hand_edited_typescript_table_fails(self) -> None:
        ts = self.root / "generated" / "contract.ts"
        ts.write_text(
            ts.read_text(encoding="utf-8").replace('"capture controller"', '"CAPTURE"'),
            encoding="utf-8",
        )
        self.assertTrue(any("capture.state" in e for e in self._errors()), "TS table edit not caught")


if __name__ == "__main__":
    unittest.main()
