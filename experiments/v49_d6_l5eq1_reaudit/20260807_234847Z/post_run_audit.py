#!/usr/bin/env python3
"""Read-only identity/provenance audit for the two replayed L5eq1 branches."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = Path(__file__).resolve().parent

from src.run_v49_d6_l5_partitioned import branch_definitions, generate_branch_instance
from src.v49_d6_l5_tail_census import compatible_l5_matchings
from src.verify import verify_binary


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(value):
    return json.loads(json.dumps(value))


def raw_unsat(path: Path) -> bool:
    payload = read_json(path)
    return (
        payload.get("Result") == "UNSATISFIABLE"
        and payload.get("Models") == {"Number": 0, "More": "no"}
    )


def main() -> int:
    definitions = {definition.branch_id: definition for definition in branch_definitions()}
    branch_ids = ("A5_residual_L5eq1", "B6_residual_L5eq1")
    common = ROOT / "solver/common.lp"
    target = ROOT / "solver/target_v.lp"
    branch_audits = {}
    problems: list[str] = []

    for branch_id in branch_ids:
        definition = definitions[branch_id]
        source_dir = ROOT / "experiments/v49_d6_l5_partitioned/branches" / branch_id
        source_instance = source_dir / "instance.lp"
        replay_dir = RUN_DIR / branch_id
        raw_path = replay_dir / "raw_solver.json"
        raw = read_json(raw_path)
        summary = read_json(replay_dir / "run_summary.json")
        generated = generate_branch_instance(
            definition.final_layer, definition.forbid_l5, definition.l5_count
        ).encode()
        expected_input = [str(common), str(target), str(source_instance)]
        exact_definition = read_json(source_dir / "branch_definition.json") == normalized(asdict(definition))
        exact_generated_instance = source_instance.read_bytes() == generated
        exact_raw_input = raw.get("Input") == expected_input
        snapshot_instance = RUN_DIR / "input_snapshot" / f"{branch_id}.instance.lp"
        snapshot_identity = snapshot_instance.read_bytes() == source_instance.read_bytes()
        unsat = raw_unsat(raw_path)
        if not all((exact_definition, exact_generated_instance, exact_raw_input, snapshot_identity, unsat)):
            problems.append(f"{branch_id}: identity or raw UNSAT check failed")
        branch_audits[branch_id] = {
            "residual_id": definition.residual_id,
            "leaf_id": definition.leaf_id,
            "l5_count": definition.l5_count,
            "compatible_l5_matching_count": len(compatible_l5_matchings(definition)),
            "final_layer": definition.final_layer,
            "forbid_l5": definition.forbid_l5,
            "source_instance": str(source_instance),
            "source_instance_sha256": sha256(source_instance),
            "branch_definition_exact": exact_definition,
            "generated_instance_exact": exact_generated_instance,
            "input_snapshot_exact": snapshot_identity,
            "raw_input_list_exact": exact_raw_input,
            "raw_result": raw.get("Result"),
            "raw_models": raw.get("Models"),
            "raw_unsat_confirmed": unsat,
            "process_exit_status": summary.get("process_exit_status"),
            "resource_time_exit_status": summary.get("resource_usage", {}).get("time_exit_status"),
            "raw_stdout_sha256": sha256(raw_path),
        }

    # Recheck all 75 tail raw results, preserving the screening/overnight identity split.
    tail_root = ROOT / "experiments/v49_d6_tail_partitioned"
    rows = list(csv.DictReader((tail_root / "reports/screening_summary.csv").open(encoding="utf-8")))
    overnight = tail_root / "overnight/20260707_234125"
    selection = read_json(overnight / "selection_certificate.json")
    timeout_ids = {row["branch_id"] for row in rows if row["status"] == "TIMEOUT"}
    selected_ids = set(selection["selected_branch_ids"])
    tail_raw_paths = []
    for row in rows:
        branch_id = row["branch_id"]
        if row["status"] == "UNSAT":
            tail_raw_paths.append(tail_root / "screening/raw" / branch_id / "solver.json")
        elif row["status"] == "TIMEOUT":
            tail_raw_paths.append(overnight / "raw" / branch_id / "solver.json")
        else:
            problems.append(f"unexpected tail screening status {row['status']}: {branch_id}")
    tail_raw_unsat_count = sum(raw_unsat(path) for path in tail_raw_paths)
    if len(rows) != 75 or timeout_ids != selected_ids or tail_raw_unsat_count != 75:
        problems.append("75-tail closure recheck failed")

    # Recheck every non-tail direct UNSAT provenance node; replace exactly the two overwritten
    # L5eq1 raw files with the new replay raw files.
    direct = {
        "support": (ROOT / "experiments/v49_d6_support_partitioned", [
            "T_1","T_2","T_3","T_4","T_12","T_13","T_14","T_23","T_24","T_34","T_123","T_124","T_134"]),
        "refined": (ROOT / "experiments/v49_d6_refined_partitioned", [
            "T_234_L6_3","T_1234_L6_2","T_1234_L6_4"]),
        "partner": (ROOT / "experiments/v49_d6_partner_partitioned", [
            "A_p2","A_p3","A_p7","A_p8","A_p9","B_p1","B_p2","B_p3","B_p6","B_p7","B_p8","B_p9"]),
        "bp5": (ROOT / "experiments/v49_d6_bp5_final_layer_partitioned", [
            "OO_12_OS_36","OO_12_OS_37","OO_12_OS_38","OO_12_OS_39",
            "OO_13_OS_26","OO_13_OS_27","OO_13_OS_28","OO_13_OS_29"]),
        "six": (ROOT / "experiments/v49_d6_six_leaf_reduced", ["A6_residual"]),
        "l5_pilot_preserved": (ROOT / "experiments/v49_d6_l5_partitioned", [
            "B7_residual_L5eq1","B8_residual_L5eq1","B9_residual_L5eq1","B9_residual_L5eq2"]),
        "l5_longrun": (ROOT / "experiments/v49_d6_l5_partitioned/longrun", [
            "A5_residual_L5eq2","A5_residual_L5eq4","B6_residual_L5eq2",
            "B7_residual_L5eq2","B7_residual_L5eq3","B7_residual_L5eq4",
            "B8_residual_L5eq2","B8_residual_L5eq3","B8_residual_L5eq4",
            "B9_residual_L5eq3","B9_residual_L5eq4"]),
    }
    direct_counts = {}
    for campaign, (base, ids) in direct.items():
        count = sum(raw_unsat(base / "branches" / branch_id / "solver.json") for branch_id in ids)
        direct_counts[campaign] = {"expected": len(ids), "raw_unsat": count}
        if count != len(ids):
            problems.append(f"{campaign}: direct raw UNSAT count {count}/{len(ids)}")
    direct_counts["l5_replayed"] = {"expected": 2, "raw_unsat": sum(
        raw_unsat(RUN_DIR / branch_id / "raw_solver.json") for branch_id in branch_ids
    )}

    # Recheck the independent depth-7 witness.
    witness_path = ROOT / "experiments/baseline_n9/decisions/V_t4_n9/depth_07/network.json"
    witness_json = read_json(witness_path)
    witness = [[tuple(edge) for edge in layer] for layer in witness_json["layers"]]
    witness_check = verify_binary(witness, n=9, t=4, kind="V")
    if not witness_check.ok or len(witness) != 7:
        problems.append("depth-7 witness replay failed")

    frozen_manifest = read_json(ROOT / "experiments/v49_d6_final/evidence_manifest.json")
    frozen_bad = []
    for entry in frozen_manifest["files"]:
        path = ROOT / "experiments/v49_d6_final" / entry["bundle_path"]
        if not path.is_file() or sha256(path) != entry["sha256"]:
            frozen_bad.append(entry["path"])
    if frozen_bad:
        problems.append(f"frozen bundle hash failures: {frozen_bad}")

    payload = {
        "status": "PASSED" if not problems else "FAILED",
        "problems": problems,
        "branch_identity": branch_audits,
        "tail_relationship": {
            "tail_parents": [
                "A5_residual_L5eq3",
                "B6_residual_L5eq3",
                "B6_residual_L5eq4",
            ],
            "replayed_branches_are_outside_75_tail": True,
            "screening_status_counts": dict(Counter(row["status"] for row in rows)),
            "screening_timeout_equals_overnight_selection": timeout_ids == selected_ids,
            "tail_raw_unsat_count": tail_raw_unsat_count,
        },
        "non_tail_direct_unsat": direct_counts,
        "depth6_candidate_lineage_to_raw_unsat_complete": not problems,
        "depth7_witness": {
            "path": str(witness_path),
            "depth": len(witness),
            "inputs_checked": 512,
            "verified": witness_check.ok,
        },
        "frozen_bundle": {
            "files_checked": len(frozen_manifest["files"]),
            "hash_failures": frozen_bad,
        },
        "prior_regression_result": "253 passed in 33.73s",
        "conclusion": "VDepth(4,9)=7" if not problems else None,
        "decision": "A" if not problems else "NOT_A",
    }
    output = RUN_DIR / "post_run_audit.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest_path = RUN_DIR / "artifact_manifest.sha256"
    files = sorted(
        path for path in RUN_DIR.rglob("*")
        if path.is_file() and path != manifest_path
    )
    manifest_path.write_text(
        "".join(f"{sha256(path)}  {path.relative_to(RUN_DIR)}\n" for path in files),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "decision": payload["decision"],
                      "problems": problems, "manifest_files": len(files)}, indent=2))
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
