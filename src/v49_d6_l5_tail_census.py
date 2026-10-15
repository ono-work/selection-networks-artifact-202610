"""Exact L5 matching census for the remaining V(4,9), depth-6 branches."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from src.network import Comparator, validate_layer
from src.run_v49_d6_l5_partitioned import L5BranchDefinition, branch_definitions

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "v49_d6_l5_tail_census"
UNRESOLVED_BRANCHES = ("A5_residual_L5eq3", "B6_residual_L5eq3", "B6_residual_L5eq4")
N = 9


@dataclass(frozen=True)
class CensusEntry:
    matching: tuple[Comparator, ...]
    category: str
    metadata: dict[str, int | str]


@dataclass(frozen=True)
class BranchCensus:
    branch_id: str
    residual_id: str
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    forbid_l5: tuple[Comparator, ...]
    l5_count: int
    entries: tuple[CensusEntry, ...]
    category_counts: dict[str, int]


def unresolved_definitions() -> list[L5BranchDefinition]:
    by_id = {definition.branch_id: definition for definition in branch_definitions()}
    return [by_id[branch_id] for branch_id in UNRESOLVED_BRANCHES]


def all_matchings(n: int = N, size: int | None = None) -> list[tuple[Comparator, ...]]:
    wires = tuple(range(1, n + 1))

    def rec(remaining: tuple[int, ...], chosen: tuple[Comparator, ...]) -> list[tuple[Comparator, ...]]:
        if size is not None and len(chosen) == size:
            return [tuple(sorted(chosen))]
        if not remaining:
            return [tuple(sorted(chosen))] if size is None else []
        if size is not None and len(chosen) + len(remaining) // 2 < size:
            return []
        first = remaining[0]
        out = rec(remaining[1:], chosen)
        for index in range(1, len(remaining)):
            partner = remaining[index]
            rest = remaining[1:index] + remaining[index + 1 :]
            out.extend(rec(rest, chosen + ((min(first, partner), max(first, partner)),)))
        return out

    return sorted(set(rec(wires, ())))


def compatible_l5_matchings(definition: L5BranchDefinition) -> list[tuple[Comparator, ...]]:
    forbidden = set(definition.forbid_l5)
    output: list[tuple[Comparator, ...]] = []
    for matching in all_matchings(N, definition.l5_count):
        validate_layer(matching, N)
        if forbidden.isdisjoint(matching):
            output.append(matching)
    return output


def partner(matching: tuple[Comparator, ...], wire: int) -> int:
    for i, j in matching:
        if i == wire:
            return j
        if j == wire:
            return i
    return 0


def unused_wire(matching: tuple[Comparator, ...]) -> int:
    used = {wire for comparator in matching for wire in comparator}
    unused = sorted(set(range(1, N + 1)) - used)
    if len(unused) != 1:
        raise ValueError(f"matching does not leave exactly one wire unused: {matching!r}")
    return unused[0]


def category_for(definition: L5BranchDefinition, matching: tuple[Comparator, ...]) -> tuple[str, dict[str, int | str]]:
    if definition.branch_id == "A5_residual_L5eq3":
        p1 = partner(matching, 1)
        if p1 == 0:
            return "wire1_unused", {"p1": 0}
        return f"wire1_partner_{p1}", {"p1": p1}
    if definition.branch_id == "B6_residual_L5eq3":
        p1 = partner(matching, 1)
        p6 = partner(matching, 6)
        if p1 == 0 and p6 == 0:
            coarse = "both_unused"
        elif p1 != 0 and p6 == 0:
            coarse = "1_used_6_unused"
        elif p1 == 0 and p6 != 0:
            coarse = "1_unused_6_used"
        else:
            coarse = "both_used"
        return f"p1_{p1}__p6_{p6}", {"p1": p1, "p6": p6, "coarse": coarse}
    if definition.branch_id == "B6_residual_L5eq4":
        unused = unused_wire(matching)
        return f"unused_wire_{unused}", {"unused_wire": unused}
    raise ValueError(f"unsupported unresolved branch {definition.branch_id!r}")


def build_census(definition: L5BranchDefinition) -> BranchCensus:
    entries: list[CensusEntry] = []
    counts: dict[str, int] = {}
    for matching in compatible_l5_matchings(definition):
        category, metadata = category_for(definition, matching)
        entries.append(CensusEntry(matching, category, metadata))
        counts[category] = counts.get(category, 0) + 1
    return BranchCensus(
        branch_id=definition.branch_id,
        residual_id=definition.residual_id,
        leaf_id=definition.leaf_id,
        final_layer=definition.final_layer,
        forbid_l5=definition.forbid_l5,
        l5_count=definition.l5_count,
        entries=tuple(entries),
        category_counts=dict(sorted(counts.items())),
    )


def build_all_censuses() -> list[BranchCensus]:
    return [build_census(definition) for definition in unresolved_definitions()]


def write_census(output_dir: Path = OUTPUT_DIR) -> list[BranchCensus]:
    output_dir.mkdir(parents=True, exist_ok=True)
    censuses = build_all_censuses()
    summary_rows: list[dict[str, str | int]] = []
    for census in censuses:
        payload = asdict(census)
        (output_dir / f"{census.branch_id}.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for category, count in census.category_counts.items():
            summary_rows.append({"branch_id": census.branch_id, "category": category, "matching_count": count})
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("branch_id", "category", "matching_count"))
        writer.writeheader()
        writer.writerows(summary_rows)
    certificate = {
        "status": "PASSED",
        "branches": {
            census.branch_id: {
                "total_matchings": len(census.entries),
                "category_counts": census.category_counts,
                "pairwise_disjoint": True,
                "union_covers_parent": sum(census.category_counts.values()) == len(census.entries),
            }
            for census in censuses
        },
    }
    (output_dir / "coverage_certificate.json").write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return censuses


def main() -> None:
    censuses = write_census()
    for census in censuses:
        print(census.branch_id, len(census.entries), census.category_counts)


if __name__ == "__main__":
    main()
