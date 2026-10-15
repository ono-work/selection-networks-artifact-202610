import json
from pathlib import Path

from src.complete_n10_selection_depths import (
    JOBS,
    OUT,
    ROOT,
    audit_new_jobs,
    build_table,
    existing_direct_exact,
    normalized_checkout_sha256,
    validate_table,
)


def test_all_new_jobs_are_unique_conclusive_unsat_decisions():
    assert len(JOBS) == 3
    keys = [(job.kind, job.n, job.t, job.depth) for job in JOBS.values()]
    assert len(keys) == len(set(keys))
    audited = audit_new_jobs()
    assert {item["status"] for item in audited} == {"UNSAT"}
    assert len(audited) == len(JOBS)
    for item in audited:
        assert item["solver_result"] == "UNSATISFIABLE"
        assert Path(ROOT / item["decision"]).is_file()
        assert Path(ROOT / item["raw_solver"]).is_file()
        assert Path(ROOT / item["instance"]).is_file()


def test_all_110_cells_are_exact_and_structurally_consistent():
    table = build_table(existing_direct_exact(), audit_new_jobs())
    result = validate_table(table, require_exact=True)
    assert result == {"errors": [], "unresolved": [], "exact_cells": 110}
    assert table.get("V", 7, 2).lower_bound == 5
    assert table.get("V", 9, 2).lower_bound == 6
    assert table.get("U", 9, 2).lower_bound == 5
    assert table.get("U", 9, 7).lower_bound == 5
    assert table.get("U", 6, 4).lower_bound == 4


def test_every_reused_sat_witness_is_freshly_exhaustive_verified():
    checks = []
    for item in existing_direct_exact():
        for decision in item.get("decisions", []):
            if decision.get("fresh_verification"):
                checks.append(decision["fresh_verification"])
        if item.get("upper_witness"):
            checks.append(item["upper_witness"])
    assert checks
    for check in checks:
        assert check["verifier"]["ok"] is True
        assert check["matching_layers"] is True
        assert check["checked_boolean_inputs"] == 2 ** check["n"]


def test_v3_n7_exact_uses_depth5_unsat_and_depth6_witness():
    case = json.loads(
        (ROOT / "experiments/baseline_n7/decisions/V_t3_n7/case_result.json").read_text(encoding="utf-8")
    )
    by_depth = {decision["depth"]: decision for decision in case["decisions"]}
    assert by_depth[5]["status"] == "UNSAT"
    assert by_depth[6]["status"] == "SAT"
    assert by_depth[6]["verifier_ok"] is True


def test_v49_checkout_relocation_preserves_normalized_certificate():
    current = ROOT / "experiments/v49_d6_closure_audit/coverage_certificate.json"
    frozen = ROOT / "experiments/v49_d6_final/bundle/experiments/v49_d6_closure_audit/coverage_certificate.json"
    assert normalized_checkout_sha256(current) == normalized_checkout_sha256(frozen)


def test_generated_manifest_uses_repository_relative_paths():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        assert not Path(source["path"]).is_absolute()
    for item in manifest["jobs"]:
        for key in ("decision", "raw_solver", "instance"):
            assert not Path(item[key]).is_absolute()
    assert manifest["git"]["dirty"] is True
