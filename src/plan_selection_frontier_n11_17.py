"""Generate derived V/U selection-depth bounds and a frontier plan for n=11..17.

This script reads existing reports/artifacts only. It does not invoke clingo,
verifiers, or any search routine.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from src.selection_bounds import BoundEntry, BoundTable, Derivation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "selection_bounds_n11_17"
DOC = ROOT / "docs" / "n11_17"

SORT_DEPTH = {
    1: 0,
    2: 1,
    3: 3,
    4: 3,
    5: 5,
    6: 5,
    7: 6,
    8: 6,
    9: 7,
    10: 7,
    11: 8,
    12: 8,
    13: 9,
    14: 9,
    15: 9,
    16: 9,
    17: 10,
}

SOURCE_PATHS = {
    "n10_summary_json": "experiments/baseline_n10/n10_depth_summary.json",
    "n10_summary_csv": "experiments/baseline_n10/n10_depth_table.csv",
    "n10_summary_md": "docs/n10/n10_depth_summary.md",
    "n10_v_report": "docs/n10/n10_v_selection_decisions.md",
    "n10_u_report": "docs/n10/u_selection_decisions.md",
    "v49_certificate": "experiments/v49_d6_final/final_certificate.json",
    "v49_evidence_index": "experiments/v49_d6_final/evidence_index.md",
    "v3n9_d5_decision": "experiments/baseline_n9/decisions/V_t3_n9/depth_05/decision.json",
    "v3n9_d6_verifier": "experiments/baseline_n9/decisions/V_t3_n9/depth_06/verifier.json",
    "u2n8_summary": "experiments/u_calibration/U_t2_n8/summary.csv",
    "u2n8_d4_verifier": "experiments/u_calibration/U_t2_n8/depth_04/verifier.json",
    "u3n9_d4_decision": "experiments/baseline_n9/decisions/U_t3_n9/depth_04/decision.json",
    "u3n9_d5_verifier": "experiments/baseline_n9/decisions/U_t3_n9/depth_05/verifier.json",
    "u4n9_d4_decision": "experiments/baseline_n9/decisions/U_t4_n9/depth_04/decision.json",
    "u4n9_d5_verifier": "experiments/baseline_n9/decisions/U_t4_n9/depth_05/verifier.json",
    "sorting_note": "docs/literature/exact_depth_audit.md",
    "sorting_bib": "docs/literature/references.bib",
}


def read_json(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text())


def source_audit() -> tuple[dict[str, Any], list[str]]:
    checks: dict[str, Any] = {}
    problems: list[str] = []
    for name, rel in SOURCE_PATHS.items():
        exists = (ROOT / rel).exists()
        checks[name] = {"path": rel, "exists": exists}
        if not exists:
            problems.append(f"missing source path: {rel}")

    def set_check(name: str, ok: bool, detail: Any) -> None:
        checks[name] = {"ok": ok, "detail": detail}
        if not ok:
            problems.append(f"source audit failed: {name}: {detail}")

    if (ROOT / SOURCE_PATHS["n10_summary_json"]).exists():
        data = read_json(SOURCE_PATHS["n10_summary_json"])
        v = {e["t"]: e["depth"] for e in data.get("V_table", [])}
        u = {e["t"]: e["depth"] for e in data.get("U_table", [])}
        set_check("n10_V_table_source", v == {1:4,2:6,3:6,4:7,5:7,6:7,7:7,8:7,9:7,10:7}, v)
        set_check("n10_U_table_source", u == {1:4,2:5,3:5,4:5,5:5,6:5,7:5,8:5,9:4,10:0}, u)
    else:
        set_check("n10_integrated_summary", False, "missing integrated summary")

    if (ROOT / SOURCE_PATHS["v49_certificate"]).exists():
        cert = read_json(SOURCE_PATHS["v49_certificate"])
        set_check("VDepth_4_9_certificate", cert.get("status") == "AFFIRMATIVE" and cert.get("result") == "VDepth(4,9)=7", cert)

    if (ROOT / SOURCE_PATHS["v3n9_d5_decision"]).exists() and (ROOT / SOURCE_PATHS["v3n9_d6_verifier"]).exists():
        d5 = read_json(SOURCE_PATHS["v3n9_d5_decision"])
        d6v = read_json(SOURCE_PATHS["v3n9_d6_verifier"])
        set_check("VDepth_3_9_source", d5.get("status") == "UNSAT" and d6v.get("ok") is True, {"d5": d5.get("status"), "d6_verifier_ok": d6v.get("ok")})

    if (ROOT / SOURCE_PATHS["u2n8_d4_verifier"]).exists():
        v = read_json(SOURCE_PATHS["u2n8_d4_verifier"])
        set_check("UDepth_2_8_source", v.get("ok") is True, v)

    if (ROOT / SOURCE_PATHS["u3n9_d4_decision"]).exists() and (ROOT / SOURCE_PATHS["u3n9_d5_verifier"]).exists():
        d4 = read_json(SOURCE_PATHS["u3n9_d4_decision"])
        d5v = read_json(SOURCE_PATHS["u3n9_d5_verifier"])
        set_check("UDepth_3_9_source", d4.get("status") == "UNSAT" and d5v.get("ok") is True, {"d4": d4.get("status"), "d5_verifier_ok": d5v.get("ok")})

    if (ROOT / SOURCE_PATHS["u4n9_d4_decision"]).exists() and (ROOT / SOURCE_PATHS["u4n9_d5_verifier"]).exists():
        d4 = read_json(SOURCE_PATHS["u4n9_d4_decision"])
        d5v = read_json(SOURCE_PATHS["u4n9_d5_verifier"])
        set_check("UDepth_4_9_source", d4.get("status") == "UNSAT" and d5v.get("ok") is True, {"d4": d4.get("status"), "d5_verifier_ok": d5v.get("ok")})

    sorting_status = "TODO_SORTING_DEPTH_CITATION"
    if (ROOT / SOURCE_PATHS["sorting_note"]).exists() and (ROOT / SOURCE_PATHS["sorting_bib"]).exists():
        note = (ROOT / SOURCE_PATHS["sorting_note"]).read_text()
        bib = (ROOT / SOURCE_PATHS["sorting_bib"]).read_text()
        if "n = 6,...,16" in note and "DobbelaereSortingNetworks" in bib:
            sorting_status = "PARTIAL_LOCAL_NOTE_WITH_N17_TODO"
    checks["sorting_depth_citation_status"] = {
        "status": sorting_status,
        "detail": "Local notes cover the sorting-depth row through n=16; n=17 uses the planning assumption and needs a citation check.",
    }
    return checks, problems


def seed_table(audit: dict[str, Any]) -> BoundTable:
    table = BoundTable(range(1, 18))
    table.add_one_selection_exact(17)
    table.add_u_all_wire_trivial()

    sorting_status = audit.get("sorting_depth_citation_status", {}).get("status")
    source_status = "CONFIRMED" if sorting_status == "PARTIAL_LOCAL_NOTE_WITH_N17_TODO" else "MISSING_OR_TODO"
    table.apply_sorting_upper_bounds(
        SORT_DEPTH,
        "planning sorting-depth table; local Dobbelaere/Bundala-Zavodny note through n<=16, n=17 citation TODO",
        source_status=source_status,
    )

    summary = read_json(SOURCE_PATHS["n10_summary_json"])
    for e in summary.get("V_table", []) + summary.get("U_table", []):
        table.add_exact_value(
            e["kind"],
            e["n"],
            e["t"],
            e["depth"],
            Derivation(
                "N10_INTEGRATED_SUMMARY_SEED",
                e.get("derivation_summary", "n=10 integrated summary"),
                artifacts=tuple(e.get("artifact_paths", [])) + (SOURCE_PATHS["n10_summary_json"],),
            ),
        )

    # Older exact seeds improve n>=11 lower bounds and source audit traceability.
    seeds = [
        ("V", 3, 9, 6, "VDepth(3,9)=6", ("experiments/baseline_n9/decisions/V_t3_n9/depth_05/", "experiments/baseline_n9/decisions/V_t3_n9/depth_06/")),
        ("V", 4, 9, 7, "VDepth(4,9)=7 final certificate", (SOURCE_PATHS["v49_certificate"], SOURCE_PATHS["v49_evidence_index"])),
        ("U", 2, 8, 4, "UDepth(2,8)=4 calibration", ("experiments/u_calibration/U_t2_n8/",)),
        ("U", 3, 9, 5, "UDepth(3,9)=5", ("experiments/baseline_n9/decisions/U_t3_n9/",)),
        ("U", 4, 9, 5, "UDepth(4,9)=5", ("experiments/baseline_n9/decisions/U_t4_n9/",)),
    ]
    for kind, t, n, depth, source, artifacts in seeds:
        table.add_exact_value(kind, n, t, depth, Derivation("SOURCE_EXACT_SEED", source, artifacts=artifacts))
    # U(5,9)=5 by U-duality from U(4,9)=5 for lower-bound propagation.
    table.add_exact_value("U", 9, 5, 5, Derivation("U_DUALITY_SEED", "UDepth(5,9)=UDepth(4,9)=5", artifacts=("experiments/baseline_n9/decisions/U_t4_n9/",)))

    table.propagate_all()
    table.detect_exact_entries()
    return table


def next_action(entry: BoundEntry) -> str:
    if entry.status == "EXACT":
        return "none"
    if entry.status == "ERROR":
        return "resolve bound contradiction before planning"
    lb = entry.lower_bound
    ub = entry.upper_bound
    if lb is None:
        return "establish a lower bound source before solver planning"
    if ub is None:
        return "establish an upper bound source before solver planning"
    return f"run {entry.kind}({entry.t},{entry.n}) at depth {lb}"


def entry_to_row(entry: BoundEntry) -> dict[str, Any]:
    return {
        "kind": entry.kind,
        "n": entry.n,
        "t": entry.t,
        "lower_bound": entry.lower_bound,
        "upper_bound": entry.upper_bound,
        "status": entry.status,
        "gap_size": entry.gap_size,
        "lower_bound_sources": entry.lower_sources(),
        "upper_bound_sources": entry.upper_sources(),
        "derivation_summary": entry.derivation_summary(),
        "next_action": next_action(entry),
    }


def propose_frontier(table: BoundTable) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int, int]] = set()

    def milestone(n: int) -> str:
        if n <= 12:
            return "Milestone 1: n=11,12"
        if n <= 14:
            return "Milestone 2: n=13,14"
        return "Milestone 3: n=15,16,17"

    def add(priority: str, kind: str, n: int, t: int, rationale: str) -> None:
        e = table.get(kind, n, t)
        if e.status == "EXACT" or e.lower_bound is None or e.upper_bound is None:
            return
        key = (kind, n, t, e.lower_bound)
        if key in seen:
            return
        seen.add(key)
        proposals.append(
            {
                "milestone": milestone(n),
                "priority": priority,
                "kind": kind,
                "n": n,
                "t": t,
                "depth_to_test": e.lower_bound,
                "current_lower_bound": e.lower_bound,
                "current_upper_bound": e.upper_bound,
                "gap_size": e.gap_size,
                "problem": f"{kind}({t},{n}) at depth {e.lower_bound}",
                "rationale": rationale,
                "expected_conclusion_pattern": "SAT closes the upper side at the tested depth; UNSAT raises the lower bound; TIMEOUT remains inconclusive.",
                "artifact_directory_suggestion": f"experiments/frontier_n11_17/{kind}_t{t}_n{n}/depth_{e.lower_bound:02d}/",
            }
        )

    for n in range(11, 18):
        for t in range(2, n // 2 + 1):
            add("A_U_FIRST", "U", n, t, "U-side first; U-duality removes the mirrored target.")

    for n in range(11, 18):
        for t in (2, 3):
            add("B_V_SMALL_T", "V", n, t, "Small fixed-t V frontier; V witness monotonicity can also improve smaller-t upper bounds.")

    for n in range(11, 18):
        s = SORT_DEPTH[n]
        for t in range(4, n + 1):
            e = table.get("V", n, t)
            if e.status == "EXACT":
                continue
            # Focus on tests at S-1: a single UNSAT at a threshold t closes all larger t.
            if e.lower_bound is not None and e.lower_bound <= s - 1 <= (e.upper_bound or s):
                key = ("V", n, t, s - 1)
                if key not in seen:
                    seen.add(key)
                    proposals.append(
                        {
                            "milestone": milestone(n),
                            "priority": "C_V_SORTING_FRONTIER",
                            "kind": "V",
                            "n": n,
                            "t": t,
                            "depth_to_test": s - 1,
                            "current_lower_bound": e.lower_bound,
                            "current_upper_bound": e.upper_bound,
                            "gap_size": e.gap_size,
                            "problem": f"V({t},{n}) at depth {s - 1}",
                            "rationale": "Find the smallest t whose V-depth reaches SortDepth(n); UNSAT at S-1 propagates to all larger t.",
                            "expected_conclusion_pattern": "UNSAT at S-1 closes this and all larger V targets at S; SAT may move the frontier to a larger t.",
                            "artifact_directory_suggestion": f"experiments/frontier_n11_17/V_t{t}_n{n}/depth_{s - 1:02d}/",
                        }
                    )
                    break
    order = {"Milestone 1: n=11,12": 0, "Milestone 2: n=13,14": 1, "Milestone 3: n=15,16,17": 2}
    priority_order = {"A_U_FIRST": 0, "B_V_SMALL_T": 1, "C_V_SORTING_FRONTIER": 2}
    proposals.sort(key=lambda p: (order[p["milestone"]], priority_order[p["priority"]], p["n"], p["t"]))
    return proposals


def compact_bounds_table(rows: list[dict[str, Any]], kind: str, n: int) -> str:
    cells = [r for r in rows if r["kind"] == kind and r["n"] == n]
    t_row = " | ".join(str(r["t"]) for r in cells)
    b_row = " | ".join(f"{r['lower_bound']}-{r['upper_bound']}" if r["status"] != "EXACT" else str(r["lower_bound"]) for r in cells)
    s_row = " | ".join(r["status"] for r in cells)
    sep = " | ".join(["---:"] * len(cells))
    return f"| t | {t_row} |\n| ---: | {sep} |\n| {kind} bounds | {b_row} |\n| status | {s_row} |"


def write_outputs(table: BoundTable, audit: dict[str, Any], audit_problems: list[str], proposals: list[dict[str, Any]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    rows = [entry_to_row(e) for e in table.rows(11, 17)]
    errors = [r for r in rows if r["status"] == "ERROR"]
    audit_status = "BLOCKED" if errors else ("WARNING" if audit_problems or audit.get("sorting_depth_citation_status", {}).get("status") != "CONFIRMED" else "PASSED")

    summary = {
        "audit_status": audit_status,
        "source_audit": audit,
        "audit_problems": audit_problems,
        "sorting_depths": SORT_DEPTH,
        "sorting_depth_citation_status": audit.get("sorting_depth_citation_status", {}).get("status"),
        "exact_seed_count": len([e for e in table.rows(1, 10) if e.status == "EXACT"]),
        "n11_17_gap_counts_by_kind": {
            "V": sum(1 for r in rows if r["kind"] == "V" and r["status"] == "GAP"),
            "U": sum(1 for r in rows if r["kind"] == "U" and r["status"] == "GAP"),
        },
        "n11_17_exact_counts_by_kind": {
            "V": sum(1 for r in rows if r["kind"] == "V" and r["status"] == "EXACT"),
            "U": sum(1 for r in rows if r["kind"] == "U" and r["status"] == "EXACT"),
        },
        "bounds": rows,
        "frontier_experiments": proposals,
    }
    (OUT / "bounds_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    with (OUT / "bounds_table.csv").open("w", newline="") as f:
        fieldnames = ["kind", "n", "t", "lower_bound", "upper_bound", "status", "gap_size", "lower_bound_sources", "upper_bound_sources", "derivation_summary", "next_action"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            rr = dict(r)
            rr["lower_bound_sources"] = " || ".join(rr["lower_bound_sources"])
            rr["upper_bound_sources"] = " || ".join(rr["upper_bound_sources"])
            writer.writerow(rr)

    with (OUT / "frontier_experiments.csv").open("w", newline="") as f:
        fieldnames = ["milestone", "priority", "kind", "n", "t", "depth_to_test", "current_lower_bound", "current_upper_bound", "gap_size", "problem", "rationale", "expected_conclusion_pattern", "artifact_directory_suggestion"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(proposals)

    (OUT / "derivation_graph.json").write_text(json.dumps({"nodes": rows, "edges": table.derivations}, indent=2, sort_keys=True) + "\n")

    first10 = proposals[:10]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for p in proposals:
        grouped.setdefault(p["milestone"], []).append(p)

    frontier_md_lines = [
        "# Frontier experiments for n=11..17",
        "",
        "No solver command is run by this planning step. The list below is derived from current bounds only.",
        "",
        "## Recommended order",
        "",
        "1. U side first: U-duality halves the targets, and the n=10 U cases closed at depth 5.",
        "2. V small-t second: V(2,n) and V(3,n) are isolated from the t>=4 sorting frontier.",
        "3. V sorting-frontier third: test S(n)-1 to find where V-depth reaches full sorting depth.",
        "",
        "## First 10 experiments",
        "",
    ]
    for i, p in enumerate(first10, 1):
        frontier_md_lines.append(f"{i}. `{p['problem']}` ({p['milestone']}, {p['priority']})")
    frontier_md_lines.extend(["", "## Milestones", ""])
    for m in ["Milestone 1: n=11,12", "Milestone 2: n=13,14", "Milestone 3: n=15,16,17"]:
        frontier_md_lines.extend([f"### {m}", ""])
        for p in grouped.get(m, []):
            frontier_md_lines.append(f"- `{p['problem']}`: {p['rationale']}")
        frontier_md_lines.append("")
    frontier_md_lines.extend([
        "## Expected conclusion patterns",
        "",
        "- SAT at the current lower-bound depth closes the upper side for that entry.",
        "- UNSAT at the current lower-bound depth raises the lower bound by one.",
        "- For V sorting-frontier tests at S(n)-1, UNSAT closes that target and all larger V targets at S(n) by V lower-bound monotonicity plus sorting upper bound.",
        "- TIMEOUT must be recorded honestly and must not be treated as UNSAT; only then consider partition or certificate strategies.",
    ])
    (OUT / "frontier_experiments.md").write_text("\n".join(frontier_md_lines) + "\n")

    sort_rows = "\n".join(f"| {n} | {SORT_DEPTH[n]} |" for n in range(1, 18))
    summary_lines = [
        "# Selection bounds summary for n=11..17",
        "",
        "This report propagates existing V/U selection-depth results and sorting upper bounds. It does not run a solver, verifier replay, additional reduction, or new symmetry argument.",
        "",
        f"Audit status: `{audit_status}`.",
        "",
        "## Propagation rules",
        "",
        "- One-selection: `VDepth(1,n)=UDepth(1,n)=ceil(log2 n)`.",
        "- U all-wire case: `UDepth(n,n)=0`.",
        "- Sorting upper bounds apply to both V and U, with full sorting exact for `VDepth(n,n)` and `VDepth(n-1,n)`.",
        "- Lower bounds propagate upward in n; upper bounds do not.",
        "- V witnesses propagate from larger t to smaller t; V lower bounds propagate from smaller t to larger t.",
        "- U-duality is valid only for U. No U t-monotonicity is assumed.",
        "- V-to-U upper bounds apply for the same `(t,n)` only.",
        "",
        "## Sorting-depth table",
        "",
        f"Citation status: `{audit.get('sorting_depth_citation_status', {}).get('status')}`. Local notes cover n<=16; n=17 remains a citation TODO under the planning assumption.",
        "",
        "| n | SortDepth(n) |",
        "| ---: | ---: |",
        sort_rows,
        "",
        "## Compact bounds tables",
        "",
    ]
    for n in range(11, 18):
        summary_lines.extend([f"### n={n}", "", "V-type:", "", compact_bounds_table(rows, "V", n), "", "U-type:", "", compact_bounds_table(rows, "U", n), ""])
    summary_lines.extend([
        "## Exact entries already derived",
        "",
        f"- V exact entries for n=11..17: {summary['n11_17_exact_counts_by_kind']['V']}.",
        f"- U exact entries for n=11..17: {summary['n11_17_exact_counts_by_kind']['U']}.",
        "",
        "## Major gaps",
        "",
        f"- V GAP entries: {summary['n11_17_gap_counts_by_kind']['V']}.",
        f"- U GAP entries: {summary['n11_17_gap_counts_by_kind']['U']}.",
        "- The most actionable gaps are listed in `experiments/selection_bounds_n11_17/frontier_experiments.csv`.",
        "",
        "## Direction warnings",
        "",
        "- Do not use U-duality for V.",
        "- Do not infer U(2,n) from a U(3,n) witness.",
        "- For V, a witness for larger t gives an upper bound for smaller t; a lower bound for smaller t gives lower bounds for larger t.",
    ])
    (DOC / "selection_bounds_summary.md").write_text("\n".join(summary_lines) + "\n")

    (DOC / "selection_frontier_plan.md").write_text("\n".join(frontier_md_lines) + "\n")

    notes = [
        "# Selection bounds notes for n=11..17",
        "",
        "## Values inherited from n=10",
        "",
        "The seed exact values are read from `experiments/baseline_n10/n10_depth_summary.json` and checked against the expected V/U rows.",
        "",
        "## Values derived by monotonicity in n",
        "",
        "Only lower bounds propagate from smaller n to larger n. This is used for V(2), V(3), V(t>=4), and U lower bounds inherited from n<=10.",
        "",
        "## Values derived by V t-monotonicity",
        "",
        "V upper bounds propagate from larger t to smaller t. V lower bounds propagate from smaller t to larger t. The tests assert that the opposite directions are not applied.",
        "",
        "## Values derived by U-duality",
        "",
        "U-duality fills mirrored U entries only. It is not applied to V. It is used to avoid duplicate frontier experiments for t and n-t.",
        "",
        "## Values using sorting upper bounds",
        "",
        "Sorting upper bounds use the planning table supplied for n=1..17. Local notes cite Dobbelaere/Bundala-Zavodny support through n<=16; n=17 remains `TODO_SORTING_DEPTH_CITATION`/planning assumption until a local citation is added.",
        "",
        "## Implementation assumptions",
        "",
        "- Bounds are integer comparator-layer depths.",
        "- Missing lower or upper sources are represented as gaps, not exact values.",
        "- Runtime is not used as evidence.",
        "- The plan does not create solver instances or launch clingo.",
        "",
        "## Next concrete Codex commands",
        "",
        "After this planning step, choose one milestone and ask Codex to run only the listed experiment(s), for example:",
        "",
        "```text",
        "Run the Milestone 1 U-side frontier experiments for n=11,12 in order, using the existing ASP pipeline, saving artifacts separately, and stop on TIMEOUT.",
        "```",
    ]
    (DOC / "selection_bounds_notes.md").write_text("\n".join(notes) + "\n")


def main() -> int:
    audit, audit_problems = source_audit()
    table = seed_table(audit)
    proposals = propose_frontier(table)
    write_outputs(table, audit, audit_problems, proposals)
    summary = json.loads((OUT / "bounds_summary.json").read_text())
    print(json.dumps({
        "audit_status": summary["audit_status"],
        "gap_counts": summary["n11_17_gap_counts_by_kind"],
        "frontier_count": len(proposals),
        "sorting_depth_citation_status": summary["sorting_depth_citation_status"],
    }, indent=2, sort_keys=True))
    return 0 if summary["audit_status"] in {"PASSED", "WARNING"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
