"""Parse clingo JSON models into the project's network representation."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any

from src.network import Network, validate_network

_SELECTED_RE = re.compile(r"^selected\((\d+),(\d+),(\d+)\)$")
CLINGO_JSON_STATUSES = {"SATISFIABLE", "UNSATISFIABLE", "UNKNOWN"}


def parse_clingo_json(stdout: str) -> dict[str, Any]:
    """Parse clingo ``--outf=2`` output."""
    data = json.loads(stdout)
    if not isinstance(data, dict):
        raise ValueError("clingo JSON output must be an object")
    return data


def parse_clingo_json_status(stdout: str) -> str:
    """Return clingo's machine-readable result status."""
    data = parse_clingo_json(stdout)
    result = data.get("Result")
    if result not in CLINGO_JSON_STATUSES:
        raise ValueError(f"unexpected clingo JSON result: {result!r}")
    return result


def parse_selected_network(stdout: str, *, n: int, depth: int) -> list[list[tuple[int, int]]]:
    """Extract selected comparators from clingo ``--outf=2`` JSON output."""
    data = parse_clingo_json(stdout)
    result = data.get("Result")
    if result != "SATISFIABLE":
        raise ValueError(f"clingo result is not SATISFIABLE: {result!r}")

    atoms = _first_witness_atoms(data)
    layers: list[list[tuple[int, int]]] = [[] for _ in range(depth)]

    for atom in atoms:
        match = _SELECTED_RE.match(atom)
        if match is None:
            continue
        layer, i, j = (int(part) for part in match.groups())
        if not 1 <= layer <= depth:
            raise ValueError(f"selected comparator references invalid layer: {atom}")
        layers[layer - 1].append((i, j))

    for layer in layers:
        layer.sort()
    validate_network(layers, n)
    return layers


def network_to_json(
    network: Network,
    *,
    n: int,
    t: int,
    kind: str,
) -> dict[str, Any]:
    """Return the canonical JSON-serializable network object."""
    validate_network(network, n)
    return {
        "n": n,
        "t": t,
        "kind": kind,
        "depth": len(network),
        "layers": [[[i, j] for i, j in layer] for layer in network],
    }


def _first_witness_atoms(data: dict[str, Any]) -> Sequence[str]:
    for call in data.get("Call", []):
        witnesses = call.get("Witnesses", [])
        if witnesses:
            values = witnesses[0].get("Value", [])
            if not isinstance(values, list) or not all(isinstance(atom, str) for atom in values):
                raise ValueError("clingo witness values must be a list of strings")
            return values
    if data.get("Result") == "SATISFIABLE":
        return []
    raise ValueError("SATISFIABLE clingo output did not contain a witness")
