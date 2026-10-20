"""The two conformance assertions of AD-4.

Public surface is intentionally exactly two functions:

- :func:`assert_consumer_invocation` — a consumer's *recorded* invocation
  (executable + argv + env) matches the contract record;
- :func:`assert_cli_writes_artifacts` — running the CLI (or an injected stand-in)
  exits 0 and writes the artifacts the record requires.

No pytest import: the kit runs inside a consumer's own runner (pytest, unittest,
or a plain script) and against either an in-process callable or an installed
binary.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

__all__ = ["assert_cli_writes_artifacts", "assert_consumer_invocation"]

_PLACEHOLDER_RE = re.compile(r"^\{([a-z0-9_]+)\}(\?)?$")
_RECORD_FIELDS = ("argv", "env", "artifacts", "exit_codes", "timeout")


def _check_record(record: Mapping[str, Any], cli: str) -> None:
    if not isinstance(record, Mapping):
        raise TypeError(f"{cli}: record must be a mapping, got {type(record).__name__}")
    if record.get("binary") != cli:
        raise AssertionError(
            f"{cli}: record describes binary {record.get('binary')!r}, not {cli!r}"
        )
    missing = [field for field in _RECORD_FIELDS if field not in record]
    if missing:
        raise AssertionError(f"{cli}: record is missing field(s): {', '.join(missing)}")


def _argv_tokens(argv: Sequence[str], cli: str) -> list[str]:
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence):
        raise TypeError(f"{cli}: argv must be a sequence of strings")
    tokens = list(argv)
    if not tokens:
        raise AssertionError(f"{cli}: argv is empty")
    for token in tokens:
        if not isinstance(token, str) or not token:
            raise AssertionError(f"{cli}: argv contains a non-string or empty token: {token!r}")
    return tokens


def _env_mapping(env: Mapping[str, str], cli: str) -> Mapping[str, str]:
    if not isinstance(env, Mapping):
        raise TypeError(f"{cli}: env must be a mapping")
    return env


def assert_consumer_invocation(
    record: Mapping[str, Any],
    cli: str,
    argv: Sequence[str],
    env: Mapping[str, str],
) -> None:
    """Assert that a consumer's recorded invocation matches ``record``.

    ``argv`` is the complete argv the consumer passed to its process launcher,
    executable first. ``argv[0]`` may be the contract binary name (``"csg"``) or
    a path whose basename is it — S1 §1.2 shows both forms (literal name, explicit
    ``*_bin`` path). The remaining tokens walk the record's ``argv`` template: a
    literal token must match exactly, ``{name}`` must be a non-empty string, and a
    trailing ``{name}?`` may be absent (``itr render [<mappings-file>]``).

    Every key in ``record["env"]["required"]`` must be present. An
    ``record["env"]["injected"]`` literal (for example
    ``COLORSCHEME__OUTPUT__OVERWRITE = "true"``) must match exactly; a placeholder
    value must be non-empty. Extra env keys are allowed: the child env is an
    allowlisted copy of the host env, not the override map alone (S1 §1.5).

    Raises ``AssertionError`` on any mismatch, ``TypeError`` on unusable inputs.
    """
    _check_record(record, cli)
    tokens = _argv_tokens(argv, cli)
    environment = _env_mapping(env, cli)

    executable = Path(tokens[0]).name
    if executable != record["binary"]:
        raise AssertionError(
            f"{cli}: argv[0] {tokens[0]!r} does not address the contract binary "
            f"{record['binary']!r}"
        )

    tail = tokens[1:]
    position = 0
    for index, template_token in enumerate(record["argv"]):
        match = _PLACEHOLDER_RE.match(template_token)
        if match is not None:
            name, optional = match.groups()
            if position >= len(tail):
                if optional:
                    break
                raise AssertionError(
                    f"{cli}: argv is missing the placeholder {name!r} "
                    f"(template position {index})"
                )
            value = tail[position]
            if not value.strip():
                raise AssertionError(
                    f"{cli}: argv placeholder {name!r} resolved to an empty value"
                )
            position += 1
            continue

        if position >= len(tail):
            raise AssertionError(
                f"{cli}: argv is missing the literal token {template_token!r} "
                f"(template position {index})"
            )
        if tail[position] != template_token:
            raise AssertionError(
                f"{cli}: argv token {position + 1} is {tail[position]!r}, "
                f"expected {template_token!r}"
            )
        position += 1

    if position != len(tail):
        raise AssertionError(
            f"{cli}: unexpected argv token(s) after the template: {tail[position:]!r}"
        )

    env_record = record["env"]
    for key in env_record["required"]:
        if key not in environment:
            raise AssertionError(f"{cli}: required env key {key!r} is missing")

    for key, expected in env_record["injected"].items():
        if key not in environment:
            raise AssertionError(f"{cli}: injected env key {key!r} is missing")
        value = environment[key]
        if _PLACEHOLDER_RE.match(expected) is not None:
            if not isinstance(value, str) or not value.strip():
                raise AssertionError(
                    f"{cli}: env {key} must be a non-empty path/value, got {value!r}"
                )
        elif value != expected:
            raise AssertionError(
                f"{cli}: env {key} is {value!r}, expected literal {expected!r}"
            )


def _run_once(run: Any, cwd: Path, cli: str) -> int:
    if callable(run):
        result = run()
        if result is None:
            return 0
        if isinstance(result, bool):
            raise TypeError(
                f"{cli}: run() returned a bool; return None, an int exit code, "
                "or an object with a returncode"
            )
        if isinstance(result, int):
            return result
        returncode = getattr(result, "returncode", None)
        if isinstance(returncode, int):
            return returncode
        raise TypeError(
            f"{cli}: run() returned {type(result).__name__}; return None, an int "
            "exit code, or an object with a returncode"
        )

    if isinstance(run, Sequence) and not isinstance(run, (str, bytes)):
        argv = [str(part) for part in run]
        if not argv:
            raise ValueError(f"{cli}: argv for run is empty")
        completed = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
        return completed.returncode

    raise TypeError(
        f"{cli}: run must be a callable or a sequence of argv strings, "
        f"got {type(run).__name__}"
    )


def _iter_files(root: Path, recursive: bool) -> list[Path]:
    if not recursive:
        return [path for path in root.iterdir() if path.is_file()]
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        found.extend(Path(dirpath) / name for name in filenames)
    return found


def assert_cli_writes_artifacts(
    record: Mapping[str, Any],
    cli: str,
    run: Callable[[], Any] | Sequence[str],
    cwd: str | os.PathLike[str],
) -> list[Path]:
    """Run the CLI and assert the record's artifacts exist under ``cwd``.

    ``run`` is either a zero-argument callable (returning ``None``, an exit code,
    or an object with ``returncode``) or a complete argv executed with
    ``subprocess.run`` in ``cwd``. After a zero exit:

    - ``artifacts.match == "exact_filename"``: every listed filename must be a
      regular file directly in ``cwd``;
    - ``artifacts.match == "suffix"``: at least ``min_count`` files with one of
      the listed suffixes, scanning recursively when ``recursive`` is true.

    Returns the sorted matched paths. Raises ``AssertionError`` for a non-zero
    exit or a missing artifact, ``TypeError``/``ValueError`` for unusable input.
    """
    _check_record(record, cli)
    root = Path(cwd)
    if not root.is_dir():
        raise AssertionError(f"{cli}: cwd {str(root)!r} is not a directory")

    returncode = _run_once(run, root, cli)
    if returncode != 0:
        raise AssertionError(
            f"{cli}: invocation exited {returncode}; a zero exit is required before "
            "artifacts count"
        )

    artifacts = record["artifacts"]
    match = artifacts["match"]

    if match == "exact_filename":
        filenames = list(artifacts["filenames"])
        found: list[Path] = []
        for filename in filenames:
            path = root / filename
            if not path.is_file():
                raise AssertionError(
                    f"{cli}: required artifact {filename!r} is missing under {str(root)!r}"
                )
            found.append(path)
        needed = int(artifacts.get("min_count", len(filenames)))
        if len(found) < needed:
            raise AssertionError(
                f"{cli}: {len(found)} of {needed} required artifacts are present under "
                f"{str(root)!r}"
            )
        return sorted(found)

    if match == "suffix":
        suffixes = {suffix.lower() for suffix in artifacts["suffixes"]}
        if not suffixes:
            raise ValueError(f"{cli}: artifacts.suffixes is empty for a suffix match")
        candidates = _iter_files(root, bool(artifacts.get("recursive", False)))
        found = sorted(path for path in candidates if path.suffix.lower() in suffixes)
        needed = int(artifacts.get("min_count", 1))
        if len(found) < needed:
            raise AssertionError(
                f"{cli}: found {len(found)} artifact(s) with suffix(es) "
                f"{sorted(suffixes)!r}; at least {needed} required under {str(root)!r}"
            )
        return found

    raise ValueError(f"{cli}: unknown artifacts.match {match!r}")
