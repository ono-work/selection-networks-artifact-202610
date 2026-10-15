"""Structural reductions for the six remaining V(4,9), depth-6 leaves."""

from __future__ import annotations

from typing import Literal, NamedTuple

from src.network import Comparator, Layer, validate_layer

N = 9


class Leaf(NamedTuple):
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    residual_forbid_l5: tuple[Comparator, ...]


LEAVES: dict[str, Leaf] = {
    "A5": Leaf("A5", ((2, 3), (4, 5)), ((2, 3), (4, 5))),
    "A6": Leaf("A6", ((2, 3), (4, 6)), ((2, 3), (4, 6))),
    "B6": Leaf("B6", ((1, 6), (2, 3), (4, 5)), ((1, 6), (2, 3), (4, 5))),
    "B7": Leaf("B7", ((1, 7), (2, 3), (4, 5)), ((1, 7), (2, 3), (4, 5))),
    "B8": Leaf("B8", ((1, 8), (2, 3), (4, 5)), ((1, 8), (2, 3), (4, 5))),
    "B9": Leaf("B9", ((1, 9), (2, 3), (4, 5)), ((1, 9), (2, 3), (4, 5))),
}

ReductionKind = Literal["prior_unsat", "to_A5", "residual"]


class Reduction(NamedTuple):
    kind: ReductionKind
    target: str
    reason: str


def all_matchings(n: int = N) -> list[tuple[Comparator, ...]]:
    wires = tuple(range(1, n + 1))

    def rec(remaining: tuple[int, ...]):
        if not remaining:
            yield []
            return
        first = remaining[0]
        rest = remaining[1:]
        yield from rec(rest)
        for index, other in enumerate(rest):
            next_remaining = rest[:index] + rest[index + 1 :]
            for suffix in rec(next_remaining):
                yield [(first, other), *suffix]

    return [tuple(sorted(matching)) for matching in rec(wires)]


def classify_l5(leaf_id: str, l5: Layer) -> Reduction:
    validate_layer(l5, N)
    l5_set = set(l5)
    if leaf_id == "A5":
        if (2, 3) in l5_set:
            return Reduction("prior_unsat", "T_4", "repeated (2,3), delete it from L6")
        if (4, 5) in l5_set:
            return Reduction("prior_unsat", "T_23", "repeated (4,5), delete it from L6")
        return Reduction("residual", "A5_residual", "neither final comparator repeats in L5")
    if leaf_id == "A6":
        if (2, 3) in l5_set:
            return Reduction("prior_unsat", "T_4", "repeated (2,3), delete it from L6")
        if (4, 6) in l5_set:
            return Reduction("prior_unsat", "T_23", "repeated (4,6), delete it from L6")
        return Reduction("residual", "A6_residual", "neither final comparator repeats in L5")
    if leaf_id in {"B6", "B7", "B8", "B9"}:
        s = int(leaf_id[1])
        if (2, 3) in l5_set:
            return Reduction("prior_unsat", "T_14", "repeated (2,3), delete it from L6")
        if (4, 5) in l5_set:
            return Reduction("prior_unsat", "T_123", "repeated (4,5), delete it from L6")
        if (1, s) in l5_set:
            return Reduction("to_A5", "A5", f"repeated (1,{s}), delete it from L6")
        return Reduction("residual", f"B{s}_residual", "none of the final comparators repeats in L5")
    raise ValueError(f"unknown leaf {leaf_id!r}")


def reduction_table() -> list[tuple[str, tuple[Comparator, ...], tuple[Comparator, ...]]]:
    return [(leaf.leaf_id, leaf.final_layer, leaf.residual_forbid_l5) for leaf in LEAVES.values()]


def cover_summary() -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for leaf_id in LEAVES:
        counts: dict[str, int] = {}
        for l5 in all_matchings():
            reduction = classify_l5(leaf_id, l5)
            key = f"{reduction.kind}:{reduction.target}"
            counts[key] = counts.get(key, 0) + 1
        summary[leaf_id] = counts
    return summary


def main() -> None:
    for leaf_id, counts in cover_summary().items():
        print(leaf_id)
        for key, count in sorted(counts.items()):
            print(" ", key, count)


if __name__ == "__main__":
    main()
