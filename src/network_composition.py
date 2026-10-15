"""Utilities for composing comparator-network artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

Comparator = tuple[int, int]
Network = list[list[Comparator]]


def normalize_network(layers: Sequence[Sequence[Sequence[int] | Comparator]]) -> Network:
    return [[tuple(edge) for edge in layer] for layer in layers]


def load_network(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    payload["layers"] = normalize_network(payload.get("layers", []))
    return payload


def network_depth(network: Sequence[Sequence[Comparator]]) -> int:
    return len(network)


def relabel_network(network: Sequence[Sequence[Comparator]], wire_map: dict[int, int]) -> Network:
    relabeled: Network = []
    for layer in network:
        new_layer: list[Comparator] = []
        for i, j in layer:
            if i not in wire_map or j not in wire_map:
                raise ValueError(f"wire map missing endpoint for comparator {(i, j)}")
            a = wire_map[i]
            b = wire_map[j]
            if a == b:
                raise ValueError(f"wire map collapses comparator {(i, j)}")
            if a > b:
                a, b = b, a
            new_layer.append((a, b))
        relabeled.append(sorted(new_layer))
    return relabeled


def shift_network(network: Sequence[Sequence[Comparator]], offset: int) -> Network:
    return relabel_network(network, {wire: wire + offset for layer in network for edge in layer for wire in edge})


def embed_network_on_wires(network: Sequence[Sequence[Comparator]], wires: Sequence[int]) -> Network:
    wire_map = {old: new for old, new in enumerate(wires, start=1)}
    return relabel_network(network, wire_map)


def concatenate_phases(*networks: Sequence[Sequence[Comparator]]) -> Network:
    out: Network = []
    for network in networks:
        out.extend([list(layer) for layer in network])
    return out


def compose_binary_candidate_merge(
    *,
    n1: int,
    n2: int,
    t: int,
    left_network: Sequence[Sequence[Comparator]],
    right_network: Sequence[Sequence[Comparator]],
    final_network: Sequence[Sequence[Comparator]],
) -> Network:
    """Compose two block candidate collectors and a final network on 2t wires.

    The left block uses wires 1..n1. The right block uses wires n1+1..n1+n2.
    Final network wires 1..2t are embedded on candidates
    [1..t, n1+1..n1+t].
    """
    if n1 < t or n2 < t:
        raise ValueError("binary merge requires n1,n2 >= t")
    left = relabel_network(left_network, {i: i for i in range(1, n1 + 1)})
    right = relabel_network(right_network, {i: n1 + i for i in range(1, n2 + 1)})
    candidate_wires = list(range(1, t + 1)) + list(range(n1 + 1, n1 + t + 1))
    final = embed_network_on_wires(final_network, candidate_wires)
    return concatenate_phases(left, right, final)


def network_to_payload(network: Sequence[Sequence[Comparator]], *, kind: str, n: int, t: int) -> dict[str, Any]:
    return {
        "kind": kind,
        "n": n,
        "t": t,
        "depth": len(network),
        "layers": [[[i, j] for i, j in layer] for layer in network],
    }


def write_network(path: str | Path, network: Sequence[Sequence[Comparator]], *, kind: str, n: int, t: int) -> None:
    Path(path).write_text(json.dumps(network_to_payload(network, kind=kind, n=n, t=t), indent=2, sort_keys=True) + "\n", encoding="utf-8")
