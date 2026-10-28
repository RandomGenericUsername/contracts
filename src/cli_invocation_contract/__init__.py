"""Versioned runtime <-> CLI invocation contract (spine AD-4).

The contract data lives in ``invocation-contract.json``: the repo-root file is the
single source, and the wheel carries a copy at
``cli_invocation_contract/invocation-contract.json`` so an installed distribution
loads the same records.

Public API::

    from cli_invocation_contract import CONTRACT_VERSION, load, get

Standard library only; no runtime dependencies.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

__all__ = [
    "CONTRACT_VERSION",
    "DATA_VERSION",
    "UnknownCliError",
    "get",
    "load",
]

#: Release version of the contract, equal to the ``contracts`` tag without its
#: leading ``v`` and to the distribution version (AD-9/AD-11: every consumer
#: pins one tag and the version each CLI reports equals it).
CONTRACT_VERSION = "0.4.0"

#: Version of the *data shape* in ``invocation-contract.json``. A document that
#: declares a different shape fails loudly instead of being misread.
DATA_VERSION = 2

_REQUIRED_RECORD_KEYS = ("argv", "env", "artifacts", "exit_codes", "timeout")

_PACKAGE_DATA = Path(__file__).with_name("invocation-contract.json")
_REPO_ROOT_DATA = Path(__file__).resolve().parents[2] / "invocation-contract.json"


class UnknownCliError(KeyError):
    """Raised by :func:`get` when the contract has no record for the CLI."""


def _default_path() -> Path:
    """Return the packaged data file, or the repo-root file in a source checkout."""
    for candidate in (_PACKAGE_DATA, _REPO_ROOT_DATA):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "invocation-contract.json not found: looked for "
        f"{_PACKAGE_DATA} and {_REPO_ROOT_DATA}"
    )


def load(path: str | os.PathLike[str] | None = None) -> dict[str, dict[str, Any]]:
    """Load the contract and return ``{cli: record}``.

    ``path`` overrides the default resolution (packaged data first, repo root
    second). A document whose ``contract_version`` differs from
    :data:`DATA_VERSION`, or whose records miss a contract field, raises
    ``ValueError``.
    """
    source = Path(path) if path is not None else _default_path()
    with source.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    if not isinstance(document, dict):
        raise ValueError(f"{source}: contract root must be a JSON object")

    version = document.get("contract_version")
    if version != DATA_VERSION:
        raise ValueError(
            f"{source}: contract data version mismatch: "
            f"expected {DATA_VERSION}, got {version!r}"
        )

    clis = document.get("clis")
    if not isinstance(clis, dict) or not clis:
        raise ValueError(f"{source}: 'clis' must be a non-empty JSON object")

    for cli, record in clis.items():
        if not isinstance(record, dict):
            raise ValueError(f"{source}: record for {cli!r} must be a JSON object")
        missing = [key for key in _REQUIRED_RECORD_KEYS if key not in record]
        if missing:
            raise ValueError(
                f"{source}: record for {cli!r} is missing field(s): {', '.join(missing)}"
            )

    return copy.deepcopy(clis)


def get(cli: str, path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Return the record for ``cli``; raise :class:`UnknownCliError` if absent."""
    records = load(path)
    try:
        return records[cli]
    except KeyError:
        known = ", ".join(sorted(records))
        raise UnknownCliError(f"unknown CLI {cli!r}; contract describes: {known}") from None
