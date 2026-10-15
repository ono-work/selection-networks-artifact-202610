"""Closure audit for the V(4,9), depth-6 hard-instance reductions."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.analyze_v49_d6_six_leaf_reductions import LEAVES, all_matchings, classify_l5
from src.network import Comparator, Layer, apply_layer, validate_layer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments" / "v49_d6_closure_audit"
CERTIFICATE_PATH = OUTPUT_DIR / "coverage_certificate.json"

SUPPORT_DIR = ROOT / "experiments" / "v49_d6_support_partitioned" / "branches"
REFINED_DIR = ROOT / "experiments" / "v49_d6_refined_partitioned" / "branches"
PARTNER_DIR = ROOT / "experiments" / "v49_d6_partner_partitioned" / "branches"
BP5_DIR = ROOT / "experiments" / "v49_d6_bp5_final_layer_partitioned" / "branches"
SIX_LEAF_DIR = ROOT / "experiments" / "v49_d6_six_leaf_reduced" / "branches"

AuditStatus = Literal["COVERAGE_AUDIT_PASSED", "COVERAGE_AUDIT_INCOMPLETE"]

PRIOR_SUPPORT_UNSAT = (
    "T_1",
    "T_2",
    "T_3",
    "T_4",
    "T_12",
    "T_13",
    "T_14",
    "T_23",
    "T_24",
    "T_34",
    "T_123",
    "T_124",
    "T_134",
)
PRIOR_REFINED_UNSAT = ("T_234_L6_3", "T_1234_L6_2", "T_1234_L6_4")
PRIOR_PARTNER_UNSAT = (
    "A_p2",
    "A_p3",
    "A_p7",
    "A_p8",
    "A_p9",
    "B_p1",
    "B_p2",
    "B_p3",
    "B_p6",
    "B_p7",
    "B_p8",
    "B_p9",
)
PRIOR_BP5_UNSAT = (
    "OO_12_OS_36",
    "OO_12_OS_37",
    "OO_12_OS_38",
    "OO_12_OS_39",
    "OO_13_OS_26",
    "OO_13_OS_27",
    "OO_13_OS_28",
    "OO_13_OS_29",
)
PRIOR_SIX_LEAF_UNSAT = ("A6_residual",)

EXPECTED_OPEN_RESIDUALS = ("A5_residual", "B6_residual", "B7_residual", "B8_residual", "B9_residual")


@dataclass(frozen=True)
class Provenance:
    branch: str
    artifact: str
    status: str


@dataclass(frozen=True)
class L5Classification:
    leaf: str
    l5: tuple[Comparator, ...]
    class_id: str
    predicate: str
    transformation: str
    destination: str
    provenance: Provenance | None
    dependency_path: tuple[str, ...]


def status_artifact(branch: str) -> Path:
    if branch in PRIOR_SUPPORT_UNSAT:
        return SUPPORT_DIR / branch / "parsed_status.json"
    if branch in PRIOR_REFINED_UNSAT:
        return REFINED_DIR / branch / "parsed_status.json"
    if branch in PRIOR_PARTNER_UNSAT:
        return PARTNER_DIR / branch / "parsed_status.json"
    if branch in PRIOR_BP5_UNSAT:
        return BP5_DIR / branch / "parsed_status.json"
    if branch in PRIOR_SIX_LEAF_UNSAT:
        return SIX_LEAF_DIR / branch / "parsed_status.json"
    raise KeyError(branch)


def read_status(branch: str) -> Provenance:
    path = status_artifact(branch)
    if not path.exists():
        return Provenance(branch, str(path), "MISSING")
    try:
        status = str(json.loads(path.read_text(encoding="utf-8")).get("status", "UNKNOWN"))
    except json.JSONDecodeError:
        status = "ERROR"
    return Provenance(branch, str(path), status)


def repeated_comparator_redundant(l5: Layer, l6: Layer, comparator: Comparator, state: tuple[int, ...]) -> bool:
    validate_layer(l5, 9)
    validate_layer(l6, 9)
    if comparator not in l5 or comparator not in l6:
        raise ValueError("comparator must appear in both L5 and L6")
    after_full = apply_layer(apply_layer(state, l5), l6)
    reduced_l6 = tuple(edge for edge in l6 if edge != comparator)
    after_reduced = apply_layer(apply_layer(state, l5), reduced_l6)
    return after_full == after_reduced


def dependency_edges() -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    edges.extend(("ROOT", branch) for branch in PRIOR_SUPPORT_UNSAT)
    edges.append(("T_234", "T_234_L6_3"))
    edges.extend(("T_1234", branch) for branch in ("T_1234_L6_2", "T_1234_L6_4"))
    edges.extend(("T_234_L6_2", branch) for branch in ("A_p2", "A_p3", "A_p7", "A_p8", "A_p9", "A5", "A6"))
    edges.extend(("T_1234_L6_3", branch) for branch in ("B_p1", "B_p2", "B_p3", "B6", "B7", "B8", "B9", "B_p5"))
    edges.extend(("B_p5", branch) for branch in PRIOR_BP5_UNSAT)
    edges.append(("A6", "A6_residual"))
    edges.extend((leaf, f"{leaf}_residual") for leaf in ("A5", "B6", "B7", "B8", "B9"))
    return edges


def graph_is_acyclic(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = defaultdict(int)
    nodes: set[str] = set()
    for src, dst in edges:
        graph[src].append(dst)
        indegree[dst] += 1
        nodes.update((src, dst))
        indegree.setdefault(src, indegree.get(src, 0))
    queue = deque([node for node in nodes if indegree[node] == 0])
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for dst in graph[node]:
            indegree[dst] -= 1
            if indegree[dst] == 0:
                queue.append(dst)
    return seen == len(nodes)


def classify_leaf_l5(leaf_id: str, l5: tuple[Comparator, ...]) -> L5Classification:
    reduction = classify_l5(leaf_id, l5)
    if reduction.kind == "prior_unsat":
        provenance = read_status(reduction.target)
        return L5Classification(
            leaf=leaf_id,
            l5=l5,
            class_id="C",
            predicate=reduction.reason,
            transformation="delete repeated final-layer comparator",
            destination=reduction.target,
            provenance=provenance,
            dependency_path=(leaf_id, reduction.target),
        )
    if reduction.kind == "to_A5":
        return L5Classification(
            leaf=leaf_id,
            l5=l5,
            class_id="B",
            predicate=reduction.reason,
            transformation="delete repeated (1,s) final-layer comparator",
            destination="A5",
            provenance=None,
            dependency_path=(leaf_id, "A5", "A5_residual"),
        )
    return L5Classification(
        leaf=leaf_id,
        l5=l5,
        class_id="A",
        predicate=reduction.reason,
        transformation="retained residual case",
        destination=reduction.target,
        provenance=None,
        dependency_path=(leaf_id, reduction.target),
    )


def closure_steps() -> list[dict[str, Any]]:
    return [
        {
            "source_subspace": "original special hard-instance universe",
            "predicate": "V-type n=9 t=4 depth=6, all layers nonempty, v_boundary validated, no suffix-only final comparator",
            "argument": "definition of current special hard-instance mode",
            "target": "15 final-prefix-support classes",
            "preserves_feasibility": True,
            "preserves_hard_mode": True,
            "evidence": "generated branch ASP constraints and support pilot artifacts",
        },
        {
            "source_subspace": "13 support classes excluding T_234 and T_1234",
            "predicate": "support branch status UNSAT",
            "argument": "direct clingo UNSAT artifact",
            "target": "closed",
            "preserves_feasibility": True,
            "preserves_hard_mode": True,
            "evidence": [asdict(read_status(branch)) for branch in PRIOR_SUPPORT_UNSAT],
        },
        {
            "source_subspace": "T_234 and T_1234",
            "predicate": "final-layer size refinements",
            "argument": "matching-size partition",
            "target": "closed refined children plus A5/A6/B leaves",
            "preserves_feasibility": True,
            "preserves_hard_mode": True,
            "evidence": [asdict(read_status(branch)) for branch in PRIOR_REFINED_UNSAT],
        },
        {
            "source_subspace": "A5/A6/B6/B7/B8/B9 terminal leaves",
            "predicate": "repeated comparator in adjacent L5/L6",
            "argument": "matching, commutation on disjoint wires, compare-exchange idempotence",
            "target": "prior UNSAT branches, A5, or residual leaves",
            "preserves_feasibility": True,
            "preserves_hard_mode": True,
            "evidence": "tests/test_v49_d6_closure_audit.py",
        },
    ]


def build_certificate() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    classifications: list[L5Classification] = []
    uncovered: list[dict[str, Any]] = []
    for leaf_id in LEAVES:
        for l5 in all_matchings():
            item = classify_leaf_l5(leaf_id, l5)
            classifications.append(item)
            if item.class_id == "D":
                uncovered.append(asdict(item))
    status_provenance = {branch: asdict(read_status(branch)) for branch in (
        *PRIOR_SUPPORT_UNSAT,
        *PRIOR_REFINED_UNSAT,
        *PRIOR_PARTNER_UNSAT,
        *PRIOR_BP5_UNSAT,
        *PRIOR_SIX_LEAF_UNSAT,
    )}
    missing_or_bad = {
        branch: prov
        for branch, prov in status_provenance.items()
        if prov["status"] != "UNSAT"
    }
    edges = dependency_edges()
    acyclic = graph_is_acyclic(edges)
    residuals = sorted({item.destination for item in classifications if item.class_id == "A"} - set(PRIOR_SIX_LEAF_UNSAT))
    status: AuditStatus = "COVERAGE_AUDIT_PASSED"
    incomplete_reasons: list[str] = []
    if uncovered:
        status = "COVERAGE_AUDIT_INCOMPLETE"
        incomplete_reasons.append("uncovered L5 matching exists")
    if missing_or_bad:
        status = "COVERAGE_AUDIT_INCOMPLETE"
        incomplete_reasons.append("UNSAT provenance missing or not UNSAT")
    if not acyclic:
        status = "COVERAGE_AUDIT_INCOMPLETE"
        incomplete_reasons.append("dependency graph has a cycle")
    if tuple(residuals) != EXPECTED_OPEN_RESIDUALS:
        status = "COVERAGE_AUDIT_INCOMPLETE"
        incomplete_reasons.append(f"unexpected residual set {residuals!r}")
    payload = {
        "status": status,
        "incomplete_reasons": incomplete_reasons,
        "scope": {
            "universe": "V(4,9), depth=6 special hard-instance mode",
            "open_residuals_after_prior_unsat": residuals,
        },
        "closure_steps": closure_steps(),
        "dependency_graph": {"edges": edges, "acyclic": acyclic},
        "status_provenance": status_provenance,
        "coverage_counts": coverage_counts(classifications),
        "classifications": [asdict(item) for item in classifications],
        "uncovered": uncovered,
    }
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def coverage_counts(classifications: list[L5Classification]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for item in classifications:
        leaf_counts = counts.setdefault(item.leaf, {})
        key = f"{item.class_id}:{item.destination}"
        leaf_counts[key] = leaf_counts.get(key, 0) + 1
    return counts


def main() -> None:
    payload = build_certificate()
    print(payload["status"])
    print(CERTIFICATE_PATH)


if __name__ == "__main__":
    main()
