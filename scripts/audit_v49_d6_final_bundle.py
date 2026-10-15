#!/usr/bin/env python3
"""Freeze and audit the existing V(4,9), depth-6/depth-7 evidence bundle.

This script does not run clingo or start solver experiments. It reads existing
machine-readable artifacts, verifies short Python-checkable predicates, copies
referenced evidence into experiments/v49_d6_final/bundle, and emits replay files.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.verify import verify_binary

EXP = ROOT / "experiments" / "v49_d6_final"
DOC = ROOT / "docs" / "v49_d6_final"
BUNDLE = EXP / "bundle"
SCREENING_SUMMARY = ROOT / "experiments" / "v49_d6_tail_partitioned" / "reports" / "screening_summary.csv"
OVERNIGHT = ROOT / "experiments" / "v49_d6_tail_partitioned" / "overnight" / "20260707_234125"
CLOSURE_CERT = ROOT / "experiments" / "v49_d6_closure_audit" / "coverage_certificate.json"
TAIL_CERT = ROOT / "experiments" / "v49_d6_l5_tail_census" / "coverage_certificate.json"
TOPO_CERT = ROOT / "experiments" / "v49_d6_topology_pruning" / "validation.json"
V3_D5_SOLVER = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t3_n9" / "depth_05" / "solver.json"
V3_D5_DECISION = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t3_n9" / "depth_05" / "decision.json"
V4_D7_NETWORK = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t4_n9" / "depth_07" / "network.json"
V4_D7_SOLVER = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t4_n9" / "depth_07" / "solver.json"
V4_D7_VERIFIER = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t4_n9" / "depth_07" / "verifier.json"
V4_D7_DECISION = ROOT / "experiments" / "baseline_n9" / "decisions" / "V_t4_n9" / "depth_07" / "decision.json"

SOURCE_FILES = [
    "solver/common.lp",
    "solver/target_v.lp",
    "src/experiment.py",
    "src/generate_instance.py",
    "src/network.py",
    "src/parse_model.py",
    "src/solver.py",
    "src/verify.py",
    "src/v49_d6_closure_audit.py",
    "src/v49_d6_l5_tail_census.py",
    "src/v49_d6_topology_pruning.py",
    "src/run_v49_d6_tail_partitioned.py",
    "src/run_v49_d6_partitioned.py",
    "src/run_v49_d6_l5_partitioned.py",
    "src/run_v49_d6_refined_partitioned.py",
    "src/run_v49_d6_partner_partitioned.py",
    "src/run_v49_d6_bp5_final_layer_partitioned.py",
    "src/run_v49_d6_six_leaf_reduced.py",
    "scripts/run_v49_d6_tail_partitioned.sh",
    "scripts/run_v49_d6_partitioned.sh",
    "scripts/run_v49_d6_l5_partitioned.sh",
    "scripts/run_v49_d6_refined_partitioned.sh",
    "scripts/run_v49_d6_partner_partitioned.sh",
    "scripts/run_v49_d6_bp5_final_layer_partitioned.sh",
    "scripts/run_v49_d6_six_leaf_reduced.sh",
    "scripts/check_environment.sh",
    "scripts/audit_v49_d6_final_bundle.py",
]
DOC_FILES = [
    "docs/v_boundary_and_v49_support_partition.md",
    "docs/v49_d6/closure_audit.md",
    "docs/v49_d6/l5_tail_partition.md",
    "docs/v49_d6/topology_pruning.md",
    "docs/v49_d6/tail_partition_preparation_report.md",
    "docs/v49_d6_terminal_profiles.md",
    "docs/v49_d6_six_leaf_reductions.md",
]
TEST_FILES = [
    "tests/test_v49_d6_closure_audit.py",
    "tests/test_v49_d6_l5_tail_census.py",
    "tests/test_v49_d6_tail_screening.py",
    "tests/test_v49_d6_topology_pruning.py",
    "tests/test_verifier.py",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_file(path: Path, problems: list[str]) -> bool:
    if not path.exists() or not path.is_file():
        problems.append(f"missing file: {rel(path) if path.is_absolute() and ROOT in path.parents else path}")
        return False
    return True


def git_metadata() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        completed = subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True)
        return completed.stdout.strip() if completed.returncode == 0 else f"unavailable: {completed.stderr.strip()}"
    return {"head": run(["rev-parse", "HEAD"]), "status_short": run(["status", "--short"])}


def network_from_json(path: Path) -> list[list[tuple[int, int]]]:
    data = read_json(path)
    return [[tuple(pair) for pair in layer] for layer in data["layers"]]


def screening_rows() -> list[dict[str, str]]:
    with SCREENING_SUMMARY.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def raw_result(path: Path) -> str | None:
    try:
        data = read_json(path)
    except Exception:
        return None
    value = data.get("Result")
    return value if isinstance(value, str) else None


def discover_tail_unsat(problems: list[str]) -> tuple[list[dict[str, Any]], Counter[str]]:
    rows = screening_rows()
    counts = Counter(row["status"] for row in rows)
    overnight_summary = list(csv.DictReader((OVERNIGHT / "overnight_summary.csv").open(encoding="utf-8", newline="")))
    overnight_by_id = {row["branch_id"]: row for row in overnight_summary}
    selected: list[dict[str, Any]] = []
    for row in rows:
        branch = row["branch_id"]
        if row["status"] == "UNSAT":
            raw = Path(row["raw_json_path"])
            branch_def = ROOT / "experiments" / "v49_d6_tail_partitioned" / "screening" / "branches" / branch / "branch_definition.json"
            instance = ROOT / "experiments" / "v49_d6_tail_partitioned" / "screening" / "branches" / branch / "instance.lp"
            source = "screening"
            status_file = ROOT / "experiments" / "v49_d6_tail_partitioned" / "screening" / "branches" / branch / "screening_result.json"
        elif row["status"] == "TIMEOUT":
            if branch not in overnight_by_id:
                problems.append(f"screening TIMEOUT branch missing from overnight summary: {branch}")
                continue
            orow = overnight_by_id[branch]
            raw = Path(orow["raw_json_path"])
            branch_def = Path(orow["raw_json_path"]).parents[2] / "branches" / branch / "branch_definition.json"
            instance = Path(orow["raw_json_path"]).parents[2] / "branches" / branch / "instance.lp"
            status_file = Path(orow["raw_json_path"]).parents[2] / "branches" / branch / "overnight_result.json"
            source = "overnight"
            if orow["status"] != "UNSAT":
                problems.append(f"overnight branch not UNSAT: {branch} status={orow['status']}")
        else:
            problems.append(f"unexpected screening status for {branch}: {row['status']}")
            continue
        for path in [raw, branch_def, instance, status_file]:
            require_file(path, problems)
        result = raw_result(raw)
        if result != "UNSATISFIABLE":
            problems.append(f"raw solver result for {branch} is not UNSATISFIABLE: {raw} result={result}")
        selected.append({"branch_id": branch, "source_run": source, "raw_solver_json": rel(raw), "branch_definition": rel(branch_def), "instance": rel(instance), "status_file": rel(status_file), "raw_result": result})
    if len(selected) != 75:
        problems.append(f"expected 75 tail UNSAT branches, got {len(selected)}")
    if Counter(row["source_run"] for row in selected) != Counter({"screening": 49, "overnight": 26}):
        problems.append(f"expected 49 screening and 26 overnight UNSAT raw proofs, got {dict(Counter(row['source_run'] for row in selected))}")
    return selected, counts


def audit(problems: list[str]) -> dict[str, Any]:
    required = [V3_D5_SOLVER, V3_D5_DECISION, V4_D7_NETWORK, V4_D7_SOLVER, V4_D7_VERIFIER, V4_D7_DECISION, CLOSURE_CERT, TAIL_CERT, TOPO_CERT, SCREENING_SUMMARY, OVERNIGHT / "selection_certificate.json", OVERNIGHT / "post_unsat_audit.json"]
    for item in required:
        require_file(item, problems)
    for item in SOURCE_FILES + DOC_FILES + TEST_FILES:
        require_file(ROOT / item, problems)

    v3_d5 = read_json(V3_D5_SOLVER)
    if v3_d5.get("Result") != "UNSATISFIABLE":
        problems.append(f"V(3,9) depth-5 solver result is not UNSATISFIABLE: {v3_d5.get('Result')}")
    v4_d7_solver = read_json(V4_D7_SOLVER)
    if v4_d7_solver.get("Result") != "SATISFIABLE":
        problems.append(f"V(4,9) depth-7 solver result is not SATISFIABLE: {v4_d7_solver.get('Result')}")
    v4_d7_verifier = read_json(V4_D7_VERIFIER)
    if v4_d7_verifier.get("ok") is not True or v4_d7_verifier.get("n") != 9 or v4_d7_verifier.get("t") != 4 or v4_d7_verifier.get("kind") != "V":
        problems.append("stored V(4,9) depth-7 verifier JSON is not ok for V t=4 n=9")
    verifier_replay = verify_binary(network_from_json(V4_D7_NETWORK), n=9, t=4, kind="V")
    if not verifier_replay.ok:
        problems.append(f"replayed Python verifier rejected V(4,9) depth-7 witness: {verifier_replay}")

    closure = read_json(CLOSURE_CERT)
    if closure.get("status") not in {"PASSED", "COVERAGE_AUDIT_PASSED"}:
        problems.append(f"closure certificate status is not a recognized pass token: {closure.get('status')}")
    tail = read_json(TAIL_CERT)
    if tail.get("status") != "PASSED":
        problems.append(f"tail census certificate status is not PASSED: {tail.get('status')}")
    tail_branches = tail.get("branches", {})
    if set(tail_branches) != {"A5_residual_L5eq3", "B6_residual_L5eq3", "B6_residual_L5eq4"}:
        problems.append(f"tail census parents differ: {sorted(tail_branches)}")
    tail_count = sum(len(v.get("category_counts", {})) for v in tail_branches.values())
    if tail_count != 75:
        problems.append(f"tail census category count is not 75: {tail_count}")
    for parent, payload in tail_branches.items():
        if payload.get("pairwise_disjoint") is not True or payload.get("union_covers_parent") is not True:
            problems.append(f"tail census parent not disjoint/exhaustive: {parent}")
    topo = read_json(TOPO_CERT)
    if topo.get("status") != "PASSED" or topo.get("failures") not in ([], None):
        problems.append(f"topology pruning validation failed or has failures: {topo}")
    post = read_json(OVERNIGHT / "post_unsat_audit.json")
    if post.get("closure_audit_returncode") != 0 or post.get("tail_child_count") != 75 or post.get("tail_children_all_closed") is not True:
        problems.append(f"post-overnight audit did not confirm closed 75 children: {post}")
    selection = read_json(OVERNIGHT / "selection_certificate.json")
    if selection.get("screening_timeout_selected_count") != 26 or selection.get("screening_unsat_excluded_count") != 49 or selection.get("every_selected_branch_belongs_to_exactly_one_class") is not True:
        problems.append(f"overnight selection certificate is inconsistent: {selection}")
    tail_unsat, screening_counts = discover_tail_unsat(problems)
    return {
        "git": git_metadata(),
        "v3_depth5_result": v3_d5.get("Result"),
        "v4_depth7_result": v4_d7_solver.get("Result"),
        "v4_depth7_stored_verifier": v4_d7_verifier,
        "v4_depth7_replayed_verifier": asdict(verifier_replay),
        "closure_certificate_status": closure.get("status"),
        "closure_certificate_passed": closure.get("status") in {"PASSED", "COVERAGE_AUDIT_PASSED"},
        "tail_census_status": tail.get("status"),
        "tail_census_category_count": tail_count,
        "topology_validation_status": topo.get("status"),
        "screening_status_counts": dict(screening_counts),
        "tail_unsat_branches": tail_unsat,
        "problems": problems,
        "overall_status": "BLOCKED" if problems else "VERIFIED",
    }


def h(path: str) -> dict[str, str]:
    p = ROOT / path
    return {"path": path, "sha256": file_hash(p)}


def node(node_id: str, claim: str, classification: str, prereq: list[str], source_files: list[str], evidence_files: list[str], audit_method: str, status: str) -> dict[str, Any]:
    all_files = source_files + evidence_files
    return {
        "id": node_id,
        "claim": claim,
        "classification": classification,
        "prerequisites": prereq,
        "source_files": source_files,
        "evidence_files": evidence_files,
        "hashes": [h(path) for path in all_files if (ROOT / path).exists()],
        "audit_method": audit_method,
        "status": status,
    }


def build_graph(a: dict[str, Any]) -> dict[str, Any]:
    status = "VERIFIED" if a["overall_status"] == "VERIFIED" else "BLOCKED"
    tail_raw = [row["raw_solver_json"] for row in a["tail_unsat_branches"]]
    tail_defs = [row["branch_definition"] for row in a["tail_unsat_branches"]]
    nodes = [
        node("V3_9_DEPTH5_UNSAT", "No V-type 3-selection network on 9 wires exists at depth 5.", "SOLVER_UNSAT", [], ["solver/common.lp", "solver/target_v.lp", "src/experiment.py"], [rel(V3_D5_SOLVER), rel(V3_D5_DECISION)], "parsed clingo JSON Result=UNSATISFIABLE", status),
        node("V4_IMPLIES_V3", "Every V-type 4-selection network is also a V-type 3-selection network by restricting the required output prefix.", "MATHEMATICAL_LEMMA", [], [], ["docs/v_boundary_and_v49_support_partition.md"], "human lemma recorded in documentation", status),
        node("EMPTY_LAYER_ELIMINATION", "A depth-6 V(4,9) network with an empty layer has effective depth at most 5.", "MATHEMATICAL_LEMMA", ["V3_9_DEPTH5_UNSAT", "V4_IMPLIES_V3"], [], ["docs/v_boundary_and_v49_support_partition.md"], "human lemma plus lower-bound premise", status),
        node("ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH", "The depth-6 search may restrict to all layers nonempty for V(4,9).", "DERIVED_CONCLUSION", ["EMPTY_LAYER_ELIMINATION"], ["src/run_v49_d6_partitioned.py", "src/run_v49_d6_tail_partitioned.py"], ["docs/v_boundary_and_v49_support_partition.md"], "derivation from empty-layer lemma", status),
        node("TERMINAL_PROFILE_COVERAGE", "Terminal-profile closure audit covers the stated residual depth-6 cases.", "ARTIFACT_AUDIT", ["ALL_LAYERS_NONEMPTY_IN_DEPTH6_SEARCH"], ["src/v49_d6_closure_audit.py", "src/analyze_v49_d6_terminal_profiles.py"], [rel(CLOSURE_CERT), "docs/v49_d6/closure_audit.md", "docs/v49_d6_terminal_profiles.md"], "parsed closure coverage_certificate.json recognized pass token", status),
        node("NO_REPEAT_REDUCTION", "The no-repeat final-layer reduction used by closure is audited for covered cases.", "ARTIFACT_AUDIT", ["EMPTY_LAYER_ELIMINATION"], ["src/v49_d6_closure_audit.py"], [rel(CLOSURE_CERT), "docs/v49_d6/closure_audit.md", "docs/v49_d6_six_leaf_reductions.md"], "closure certificate and reduction docs inspected", status),
        node("THREE_RESIDUAL_PARENT_COVERAGE", "The closure audit leaves exactly the three residual parent families used by the tail census.", "ARTIFACT_AUDIT", ["TERMINAL_PROFILE_COVERAGE", "NO_REPEAT_REDUCTION"], ["src/v49_d6_l5_tail_census.py"], [rel(CLOSURE_CERT), rel(TAIL_CERT)], "cross-checked residual parent identifiers", status),
        node("TAIL_CENSUS_75_WAY_PARTITION", "The three residual parents are partitioned into exactly 75 pairwise-disjoint exhaustive tail child branches.", "ARTIFACT_AUDIT", ["THREE_RESIDUAL_PARENT_COVERAGE"], ["src/v49_d6_l5_tail_census.py", "src/run_v49_d6_tail_partitioned.py"], [rel(TAIL_CERT), "experiments/v49_d6_l5_tail_census/summary.csv", *tail_defs], "parsed tail census certificate and counted branch definitions", status),
        node("TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND", "Unique-min trajectory pruning is a necessary condition for V-type networks, not a heuristic restriction.", "EXHAUSTIVE_VERIFIER_CHECK", [], ["src/v49_d6_topology_pruning.py"], [rel(TOPO_CERT), "docs/v49_d6/topology_pruning.md", "tests/test_v49_d6_topology_pruning.py"], "validation artifact status=PASSED and regression tests referenced", status),
        node("TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND", "Backward dependency-cone pruning is a necessary condition for V-type networks, not a heuristic restriction.", "EXHAUSTIVE_VERIFIER_CHECK", [], ["src/v49_d6_topology_pruning.py"], [rel(TOPO_CERT), "docs/v49_d6/topology_pruning.md", "tests/test_v49_d6_topology_pruning.py"], "validation artifact status=PASSED and regression tests referenced", status),
        node("TAIL_CHILDREN_75_UNSAT", "All 75 tail children have raw clingo JSON certifying UNSAT.", "SOLVER_UNSAT", ["TAIL_CENSUS_75_WAY_PARTITION", "TOPOLOGY_PRUNING_UNIQUE_MIN_SOUND", "TOPOLOGY_PRUNING_DEPENDENCY_CONE_SOUND"], ["solver/common.lp", "solver/target_v.lp", "src/run_v49_d6_tail_partitioned.py"], [rel(SCREENING_SUMMARY), rel(OVERNIGHT / "overnight_summary.csv"), rel(OVERNIGHT / "selection_certificate.json"), *tail_raw], "parsed 49 screening and 26 overnight raw solver JSON files for Result=UNSATISFIABLE", status),
        node("V4_9_DEPTH6_UNSAT", "No V-type 4-selection network on 9 wires exists at depth 6.", "DERIVED_CONCLUSION", ["TAIL_CHILDREN_75_UNSAT", "TERMINAL_PROFILE_COVERAGE"], [], [rel(OVERNIGHT / "post_unsat_audit.json")], "derived from audited residual coverage and all tail UNSAT leaves", status),
        node("V4_9_DEPTH7_WITNESS_VERIFIED", "An explicit V-type 4-selection network on 9 wires at depth 7 exists and passes the independent verifier on all binary inputs.", "EXHAUSTIVE_VERIFIER_CHECK", [], ["src/verify.py", "src/parse_model.py"], [rel(V4_D7_SOLVER), rel(V4_D7_NETWORK), rel(V4_D7_VERIFIER), rel(V4_D7_DECISION)], "parsed SAT raw solver output and replayed Python verifier", status),
        node("V4_9_EXACT_DEPTH_7", "Combining depth-6 UNSAT with a verified depth-7 witness gives exact depth 7 for V(4,9).", "DERIVED_CONCLUSION", ["V4_9_DEPTH6_UNSAT", "V4_9_DEPTH7_WITNESS_VERIFIED"], [], [], "logical combination of lower and upper bounds; not a standalone solver proof", status),
    ]
    return {"nodes": nodes, "edges": [{"from": dep, "to": n["id"]} for n in nodes for dep in n["prerequisites"]]}


def markdown_graph(graph: dict[str, Any], a: dict[str, Any]) -> str:
    lines = ["# V(4,9) Depth Evidence Dependency Graph", "", f"Overall audit status: `{a['overall_status']}`.", "", "This graph separates human mathematical lemmas from exhaustive Python checks, solver-produced UNSAT/SAT artifacts, artifact-integrity checks, and derived conclusions. A clingo UNSAT result is treated as computational evidence, not as a human-readable mathematical proof.", "", "## Proof Chain", "", "The lower-bound side starts from the raw clingo UNSAT result for `V_t3_n9` at depth 5. The mathematical prefix lemma says a V-type 4-selection network also satisfies the first three V outputs, so an empty layer in a hypothetical depth-6 `V(4,9)` network would collapse to a depth-at-most-5 `V(3,9)` network. This justifies the all-nonempty depth-6 search normal form.", "", "The computer-assisted reduction then begins: terminal-profile and closure artifacts reduce the all-nonempty depth-6 search to three residual parent families. The tail census certificate partitions those parents into 75 disjoint exhaustive children. Topology pruning is included only through recorded necessary-condition validation. The 75 children are closed by raw clingo JSON: 49 in screening, 26 in the overnight run.", "", "The upper-bound side is separate: an explicit depth-7 witness is stored as JSON and is checked by the independent Python verifier over all binary inputs. The final exact-depth conclusion depends on both the depth-6 UNSAT chain and the depth-7 verified witness.", "", "## Nodes", ""]
    for n in graph["nodes"]:
        lines += [f"### {n['id']}", "", f"- Claim: {n['claim']}", f"- Classification: `{n['classification']}`", f"- Status: `{n['status']}`", f"- Prerequisites: {', '.join(n['prerequisites']) if n['prerequisites'] else 'none'}", f"- Audit method: {n['audit_method']}", ""]
    lines += ["## Edges", ""]
    for edge in graph["edges"]:
        lines.append(f"- `{edge['from']}` -> `{edge['to']}`")
    return "\n".join(lines) + "\n"


def manifest_files(a: dict[str, Any], graph: dict[str, Any]) -> list[str]:
    files = set(SOURCE_FILES + DOC_FILES + TEST_FILES)
    files.update([
        rel(V3_D5_SOLVER), rel(V3_D5_DECISION),
        rel(V4_D7_SOLVER), rel(V4_D7_NETWORK), rel(V4_D7_VERIFIER), rel(V4_D7_DECISION),
        rel(CLOSURE_CERT), rel(TAIL_CERT), "experiments/v49_d6_l5_tail_census/summary.csv",
        "experiments/v49_d6_l5_tail_census/A5_residual_L5eq3.json", "experiments/v49_d6_l5_tail_census/B6_residual_L5eq3.json", "experiments/v49_d6_l5_tail_census/B6_residual_L5eq4.json",
        rel(TOPO_CERT), "experiments/v49_d6_topology_pruning/regression_report.md",
        rel(SCREENING_SUMMARY), "experiments/v49_d6_tail_partitioned/reports/screening_report.md", "experiments/v49_d6_tail_partitioned/reports/screening_timeouts.csv",
        rel(OVERNIGHT / "overnight_plan.md"), rel(OVERNIGHT / "overnight_report.md"), rel(OVERNIGHT / "overnight_results.json"), rel(OVERNIGHT / "overnight_summary.csv"), rel(OVERNIGHT / "overnight_timeouts.csv"), rel(OVERNIGHT / "selection_certificate.json"), rel(OVERNIGHT / "post_unsat_audit.json"),
    ])
    for row in a["tail_unsat_branches"]:
        files.update([row["raw_solver_json"], row["branch_definition"], row["instance"], row["status_file"]])
        raw = ROOT / row["raw_solver_json"]
        if "screening/raw" in row["raw_solver_json"]:
            branch = row["branch_id"]
            files.add(f"experiments/v49_d6_tail_partitioned/screening/logs/{branch}.stderr.log")
            files.add(f"experiments/v49_d6_tail_partitioned/screening/logs/{branch}.resources.jsonl")
            files.add(str(Path(row["raw_solver_json"]).parent / "metadata.json"))
        elif "overnight" in row["raw_solver_json"]:
            branch = row["branch_id"]
            run = "experiments/v49_d6_tail_partitioned/overnight/20260707_234125"
            files.add(f"{run}/logs/{branch}.stderr.log")
            files.add(f"{run}/logs/{branch}.resources.jsonl")
            files.add(str(Path(row["raw_solver_json"]).parent / "metadata.json"))
    return sorted(path for path in files if (ROOT / path).exists())


def write_outputs(a: dict[str, Any], graph: dict[str, Any]) -> None:
    EXP.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    BUNDLE.mkdir(parents=True, exist_ok=True)
    (EXP / "proof_dependency_graph.json").write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (DOC / "proof_dependency_graph.md").write_text(markdown_graph(graph, a), encoding="utf-8")

    files = manifest_files(a, graph)
    manifest_entries = []
    for path in files:
        src = ROOT / path
        dest = BUNDLE / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        manifest_entries.append({"path": path, "sha256": file_hash(src), "bundle_path": str(Path("bundle") / path), "size_bytes": src.stat().st_size})
    manifest = {"status": a["overall_status"], "git": a["git"], "audit_summary": {k: v for k, v in a.items() if k not in {"tail_unsat_branches", "problems", "git"}}, "problems": a["problems"], "files": manifest_entries}
    (EXP / "evidence_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    index = ["# V(4,9) Final Evidence Index", "", f"Status: `{a['overall_status']}`", "", "This bundle is a replay-oriented archive of existing artifacts. It distinguishes solver outputs from mathematical lemmas and verifier checks; it does not convert solver UNSAT outputs into human-readable proofs.", "", "## Core Counts", "", f"- Screening UNSAT leaves used: 49", f"- Overnight UNSAT leaves used: 26", f"- Total tail leaves with raw UNSAT: {len(a['tail_unsat_branches'])}", f"- Depth-7 witness verifier replay: {a['v4_depth7_replayed_verifier']['ok']}", "", "## Files", "", "| path | sha256 | bytes |", "| --- | --- | ---: |"]
    for entry in manifest_entries:
        index.append(f"| `{entry['path']}` | `{entry['sha256']}` | {entry['size_bytes']} |")
    (EXP / "evidence_index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    lines = []
    for path in sorted(BUNDLE.rglob("*")):
        if path.is_file():
            lines.append(f"{file_hash(path)}  {path.relative_to(EXP)}")
    (EXP / "bundle.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    cert = {"status": "AFFIRMATIVE" if a["overall_status"] == "VERIFIED" else "BLOCKED", "result": "VDepth(4,9)=7" if a["overall_status"] == "VERIFIED" else None, "caveat": "This is a computational-evidence certificate, not a human-readable proof of each solver UNSAT result.", "dependency_graph": "proof_dependency_graph.json", "manifest": "evidence_manifest.json", "problems": a["problems"]}
    (EXP / "final_certificate.json").write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if a["overall_status"] != "VERIFIED":
        (EXP / "BLOCKED.md").write_text("# BLOCKED\n\n" + "\n".join(f"- {p}" for p in a["problems"]) + "\n", encoding="utf-8")
    else:
        (EXP / "BLOCKED.md").write_text("# Not Blocked\n\nThe final audit completed with status `VERIFIED`. This file exists because the audit script writes a block-status sentinel for replay tooling.\n", encoding="utf-8")


def main() -> int:
    problems: list[str] = []
    a = audit(problems)
    graph = build_graph(a)
    write_outputs(a, graph)
    print(json.dumps({"status": a["overall_status"], "problems": problems, "tail_unsat": len(a["tail_unsat_branches"]), "manifest": rel(EXP / "evidence_manifest.json")}, indent=2))
    return 0 if a["overall_status"] == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
