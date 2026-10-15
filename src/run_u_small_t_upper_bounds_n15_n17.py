#!/usr/bin/env python3
"""Scout U-type small-t upper bounds for n=15,16,17.

Uses the existing ASP encoding, parser, and independent verifier. No reduction,
symmetry breaking, or pruning rule is introduced.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.generate_instance import generate_instance
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "solver" / "common.lp"
TARGET = ROOT / "solver" / "target_u.lp"
BASE = ROOT / "experiments" / "baseline_n11_17"
DOC_DIR = ROOT / "docs" / "n11_17"
CASES = [
    (15, 2, 8), (15, 3, 8), (15, 4, 8),
    (16, 2, 8), (16, 3, 8), (16, 4, 8),
    (17, 2, 8), (17, 3, 8), (17, 4, 9),
]
SORTING_FALLBACK = {15: 9, 16: 9, 17: 10}
SUMMARY_JSON = BASE / "u_small_t_upper_bounds_n15_n17.json"
SUMMARY_CSV = BASE / "u_small_t_upper_bounds_n15_n17.csv"
PREFLIGHT_JSON = BASE / "u_small_t_upper_bounds_n15_n17_preflight.json"
PREFLIGHT_MD = BASE / "u_small_t_upper_bounds_n15_n17_preflight.md"
REPORT_MD = DOC_DIR / "u_small_t_upper_bounds_n15_n17.md"
SOURCE_REPORTS = [
    DOC_DIR / "u_upper_bounds_n13_n14_depth7.md",
    DOC_DIR / "u_upper_bounds_n13_n14_depth8.md",
    DOC_DIR / "selection_bounds_summary.md",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clingo_version() -> str:
    result = subprocess.run([*CLINGO_COMMAND, "--version"], cwd=ROOT, check=False, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def out_dir(n: int, t: int, depth: int) -> Path:
    return BASE / "decisions" / f"U_t{t}_n{n}" / f"depth_{depth:02d}"


def mirror_t(n: int, t: int) -> int:
    return n - t


def load_bounds_lower(n: int, t: int) -> tuple[int | None, str]:
    path = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    if not path.exists():
        return None, "bounds table missing"
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "U" and int(row["n"]) == n and int(row["t"]) == t:
                return int(row["lower_bound"]), row.get("lower_bound_sources", "")
    return None, "entry missing from bounds table"


def sorting_citation_status() -> str:
    notes = ROOT / "docs" / "n11_17" / "selection_bounds_notes.md"
    summary = ROOT / "docs" / "n11_17" / "selection_bounds_summary.md"
    if notes.exists():
        text = notes.read_text(errors="ignore")
        if "n=17" in text and "TODO_SORTING_DEPTH_CITATION" in text:
            return f"local note candidate: {rel(notes)}; n=17 remains TODO_SORTING_DEPTH_CITATION"
    if summary.exists():
        return f"local note candidate: {rel(summary)}"
    return "sorting-depth citation TODO"


def write_preflight() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    verifier_smoke = []
    for n, t, depth in CASES:
        result = verify_binary([], n=n, t=t, kind="U")
        verifier_smoke.append({
            "n": n,
            "t": t,
            "depth": depth,
            "kind": "U",
            "accepts_parameters": result.n == n and result.t == t and result.kind == "U",
            "smoke_result": asdict(result),
        })
    output_dirs = []
    for n, t, depth in CASES:
        d = out_dir(n, t, depth)
        output_dirs.append({"path": rel(d), "exists": d.exists(), "nonempty": d.exists() and any(d.iterdir())})
    payload = {
        "binary_input_counts": {"n15": 2**15, "n16": 2**16, "n17": 2**17},
        "cases": [{"kind": "U", "n": n, "t": t, "depth": depth, "mirror_t_by_duality": mirror_t(n, t)} for n, t, depth in CASES],
        "clingo_command": list(CLINGO_COMMAND),
        "clingo_version": clingo_version(),
        "common_encoding": rel(COMMON),
        "target_encoding": rel(TARGET),
        "decision_runner": "src.run_u_small_t_upper_bounds_n15_n17",
        "gpu_use": "none",
        "light_regression_command": ".venv/bin/python -m pytest tests/test_verifier.py tests/test_selection_u_asp.py tests/test_parse_model.py tests/test_selection_bounds.py",
        "source_reports": [{"path": rel(path), "exists": path.exists()} for path in SOURCE_REPORTS],
        "duality_scope": "U-duality is used only for report consequences: n=15 t=2,3,4 mirror 13,12,11; n=16 mirror 14,13,12; n=17 mirror 15,14,13.",
        "sorting_fallback_upper_bounds": SORTING_FALLBACK,
        "sorting_depth_citation_status": sorting_citation_status(),
        "output_directories": output_dirs,
        "verifier": "src.verify.verify_binary",
        "verifier_smoke": verifier_smoke,
    }
    write_json(PREFLIGHT_JSON, payload)
    lines = [
        "# U-side small-t upper-bound preflight for n=15,16,17",
        "",
        f"- pyclingo/libclingo version: `{clingo_version().splitlines()[0]}`.",
        "- Existing `solver/common.lp` and `solver/target_u.lp` are used.",
        "- Existing instance generator, parser, and independent verifier are used.",
        "- Exhaustive verification sizes: `2^15 = 32768`, `2^16 = 65536`, `2^17 = 131072` binary inputs.",
        "- Targets are exactly `U(2..4,15)` at depth 8, `U(2..4,16)` at depth 8, `U(2,17)` and `U(3,17)` at depth 8, and `U(4,17)` at depth 9.",
        "- GPU use: none.",
        f"- Sorting-depth citation status: `{payload['sorting_depth_citation_status']}`.",
    ]
    for source in payload["source_reports"]:
        lines.append(f"- Source report exists: `{source['exists']}` at `{source['path']}`.")
    for output in payload["output_directories"]:
        lines.append(f"- Output directory nonempty: `{output['nonempty']}` at `{output['path']}`.")
    PREFLIGHT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(n: int, t: int, depth: int, timeout_seconds: int) -> dict[str, Any]:
    out = out_dir(n, t, depth)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"refusing to overwrite existing artifact directory: {rel(out)}")
    out.mkdir(parents=True, exist_ok=True)
    instance = out / "instance.lp"
    instance.write_text(generate_instance(n, t, depth), encoding="utf-8")
    command = [*CLINGO_COMMAND, "--outf=2", f"--time-limit={timeout_seconds}", "-n", "1", str(COMMON), str(TARGET), str(instance)]
    (out / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")

    started = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    runtime = time.perf_counter() - started
    (out / "solver_raw.json").write_text(completed.stdout, encoding="utf-8")
    (out / "solver.json").write_text(completed.stdout, encoding="utf-8")

    parse_error = None
    try:
        raw = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        raw = {}
        parse_error = str(exc)
    solver_status = raw.get("Result")
    status = "ERROR"
    verifier_payload = None
    network_path = verifier_path = trace_path = None

    if solver_status == "SATISFIABLE":
        network = parse_selected_network(completed.stdout, n=n, depth=depth)
        network_path = out / "network.json"
        write_json(network_path, network_to_json(network, n=n, t=t, kind="U"))
        verifier = verify_binary(network, n=n, t=t, kind="U")
        verifier_payload = asdict(verifier)
        verifier_path = out / "verifier.json"
        write_json(verifier_path, verifier_payload)
        trace_path = out / "verifier_trace_summary.json"
        write_json(trace_path, {"checked_binary_inputs": 2**n, "kind": "U", "n": n, "ok": verifier.ok, "t": t})
        status = "VERIFIED_SAT" if verifier.ok else "VERIFICATION_FAILED"
    elif solver_status == "UNSATISFIABLE":
        status = "UNSAT"
    elif solver_status == "UNKNOWN":
        status = "TIMEOUT"

    lower_bound, lower_source = load_bounds_lower(n, t)
    upper_bound_established = status == "VERIFIED_SAT"
    if upper_bound_established:
        interval = f"[{lower_bound},{depth}]" if lower_bound is not None else f"[?,{depth}]"
        conclusion = f"UDepth({t},{n}) <= {depth}" if lower_bound is None else f"{lower_bound} <= UDepth({t},{n}) <= {depth}"
        upper_bound_value = depth
    elif status == "UNSAT":
        interval = f"[{max(lower_bound or 0, depth + 1)},?]"
        conclusion = f"depth {depth} UNSAT; requires follow-up"
        upper_bound_value = None
    elif status == "TIMEOUT":
        interval = f"[{lower_bound},?]" if lower_bound is not None else "[?,?]"
        conclusion = f"upper bound {depth} not established"
        upper_bound_value = None
    else:
        interval = f"[{lower_bound},?]" if lower_bound is not None else "[?,?]"
        conclusion = "solver result error; requires follow-up"
        upper_bound_value = None

    metadata = {
        "clingo_version": clingo_version(),
        "command": command,
        "gpu_use": "none",
        "parse_error": parse_error,
        "returncode": completed.returncode,
        "runtime_seconds": runtime,
        "stderr": completed.stderr,
        "timeout_seconds": timeout_seconds,
    }
    write_json(out / "solver_metadata.json", metadata)
    result = {
        "artifact_directory": rel(out),
        "case": f"U_t{t}_n{n}_depth{depth}",
        "current_interval": interval,
        "depth": depth,
        "kind": "U",
        "lower_bound": lower_bound,
        "lower_bound_source": lower_source,
        "mirror_t_by_duality": mirror_t(n, t),
        "n": n,
        "network_json_path": None if network_path is None else rel(network_path),
        "notes": conclusion,
        "runtime_seconds": runtime,
        "solver_status": solver_status,
        "sorting_fallback_upper_bound": SORTING_FALLBACK[n],
        "status": status,
        "t": t,
        "upper_bound": upper_bound_value,
        "upper_bound_established": upper_bound_established,
        "verifier": verifier_payload,
        "verifier_json_path": None if verifier_path is None else rel(verifier_path),
        "verifier_status": status if status == "VERIFIED_SAT" else "n/a",
        "verifier_trace_summary_path": None if trace_path is None else rel(trace_path),
    }
    write_json(out / "result.json", result)

    lines = [
        f"# U_t{t}_n{n}_depth{depth}",
        "",
        f"- Problem: U({t},{n}) at depth {depth}",
        f"- Status: `{status}`",
        f"- Solver status: `{solver_status}`",
        f"- Runtime seconds: `{runtime:.6f}`",
        f"- Upper-bound conclusion: `{conclusion}`",
        "- Command: `command.txt`",
        "- Solver input: `instance.lp`",
        "- Raw solver JSON: `solver_raw.json`",
        "- Parsed solver result: `result.json`",
        "- Solver metadata: `solver_metadata.json`",
    ]
    if network_path:
        lines.extend(["- Network: `network.json`", "- Verifier result: `verifier.json`", "- Verifier trace summary: `verifier_trace_summary.json`"])
    lines.extend(["", "This is small-t upper-bound scouting. It is not an exact-depth certificate.", "A SAT witness is accepted only after independent exhaustive binary verification."])
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_summary(results: list[dict[str, Any]]) -> None:
    citation_status = sorting_citation_status()
    payload = {
        "kind": "U",
        "cases": results,
        "provenance": {
            "runner": "src.run_u_small_t_upper_bounds_n15_n17",
            "common_encoding": rel(COMMON),
            "target_encoding": rel(TARGET),
            "sorting_fallback_upper_bounds": SORTING_FALLBACK,
            "sorting_depth_citation_status": citation_status,
            "scope": "small-t upper-bound scouting only; no exact-depth certificate",
        },
    }
    write_json(SUMMARY_JSON, payload)
    fieldnames = ["kind", "n", "t", "depth", "solver_status", "verifier_status", "upper_bound_established", "upper_bound", "current_interval", "runtime_seconds", "artifact_directory", "mirror_t_by_duality", "sorting_fallback_upper_bound", "notes"]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    def row(r: dict[str, Any]) -> str:
        return f"| `U({r['t']},{r['n']})` | {r['depth']} | `{r.get('solver_status')}` | `{r.get('verifier_status')}` | `{r.get('notes')}` | `{r.get('current_interval')}` | `{r.get('artifact_directory')}` | {r.get('runtime_seconds', 0):.3f} s | `U({r.get('mirror_t_by_duality')},{r['n']})` | operational only |"

    md = [
        "# U-side small-t upper-bound scouting for n=15,16,17",
        "",
        "## Scope",
        "",
        "This report records the 9 listed U-type small-t upper-bound scouting runs for n=15,16,17. Only these 9 listed instances were solved. Central t values are not treated here. No new reduction, symmetry breaking, pruning rule, or exact-depth certificate is introduced.",
        "",
        "Targets: `U(2..4,15)` at depth 8, `U(2..4,16)` at depth 8, `U(2,17)` and `U(3,17)` at depth 8, and `U(4,17)` at depth 9. U-duality is used only for U-type consequences.",
        "",
        "## Summary table",
        "",
        "| problem | depth | solver status | verifier status | upper-bound conclusion | current interval | artifact directory | runtime | mirror target by U-duality | notes |",
        "| --- | ---: | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    md.extend(row(r) for r in results)

    for n in [15, 16, 17]:
        md.extend(["", f"## Consequences for n={n}", ""])
        for r in [item for item in results if item["n"] == n]:
            t = r["t"]
            depth = r["depth"]
            m = r["mirror_t_by_duality"]
            if r.get("upper_bound_established"):
                md.append(f"- `U({t},{n})`: depth {depth} is `VERIFIED_SAT`, so `UDepth({t},{n}) <= {depth}`; by U-duality, `UDepth({m},{n}) <= {depth}`.")
            elif r.get("status") == "UNSAT":
                md.append(f"- `U({t},{n})`: depth {depth} is `UNSAT`; requires follow-up.")
            else:
                md.append(f"- `U({t},{n})`: `{r.get('status')}`; upper bound {depth} not established from this run.")
        endpoint_depth = 5 if n == 17 else 4
        md.append(f"- Endpoints: `UDepth(1,{n})={endpoint_depth}`, `UDepth({n-1},{n})={endpoint_depth}` by U-duality, and `UDepth({n},{n})=0`.")

    md.extend([
        "",
        "## Comparison with sorting upper bounds",
        "",
        "Planning sorting upper bounds used here: `SortDepth(15)=9`, `SortDepth(16)=9`, and `SortDepth(17)=10`.",
        "",
        "- For n=15,16, depth 8 `VERIFIED_SAT` entries are one layer shallower than sorting upper bound 9.",
        "- For n=17, depth 8 `VERIFIED_SAT` entries are two layers shallower than planning sorting upper bound 10.",
        "- For `U(4,17)`, depth 9 `VERIFIED_SAT`, if obtained, is one layer shallower than planning sorting upper bound 10.",
        f"- Sorting-depth citation status: `{citation_status}`.",
        "",
        "## Updated small-t upper-bound rows",
        "",
    ])
    for n in [15, 16, 17]:
        cells = []
        for t in range(1, n + 1):
            explicit = next((r for r in results if r["n"] == n and (r["t"] == t or r["mirror_t_by_duality"] == t) and r.get("upper_bound_established")), None)
            if t == 1 or t == n - 1:
                cells.append("5" if n == 17 else "4")
            elif t == n:
                cells.append("0")
            elif explicit is not None:
                cells.append(str(explicit["depth"]))
            else:
                cells.append("?")
        md.append(f"- n={n} non-sorting U upper-bound row after U-duality: `{cells}`; sorting/planning fallback is `{SORTING_FALLBACK[n]}` for unresolved entries.")

    md.extend([
        "",
        "## Next-step interpretation",
        "",
        "- If many depth 8 witnesses are verified, continue with `U(2,n)` and `U(3,n)` for larger n only if desired, or switch to V-side small-t.",
        "- If `U(4,15)` or `U(4,16)` times out at depth 8, record sorting upper bound 9 as fallback and do not deepen automatically.",
        "- If `U(4,17)` times out at depth 9, record sorting/planning upper bound 10 as fallback.",
        "- Exact values require separate lower-bound or UNSAT certificate work.",
        "",
        "## Artifact ledger",
        "",
    ])
    for r in results:
        d = r["artifact_directory"]
        md.extend([
            f"### U({r['t']},{r['n']}), depth {r['depth']}",
            "",
            f"- Command: `{d}/command.txt`",
            f"- Solver input: `{d}/instance.lp`",
            f"- Raw solver JSON: `{d}/solver_raw.json`",
            f"- Parsed result: `{d}/result.json`",
            f"- Solver metadata: `{d}/solver_metadata.json`",
        ])
        if r.get("network_json_path"):
            md.extend([
                f"- Network: `{r['network_json_path']}`",
                f"- Verifier result: `{r['verifier_json_path']}`",
                f"- Verifier trace summary: `{r['verifier_trace_summary_path']}`",
            ])
        md.append("")
    md.extend([
        "## Caveats",
        "",
        "- SAT witnesses are accepted only after independent exhaustive binary simulation.",
        "- TIMEOUT does not imply UNSAT.",
        "- UNSAT, if any, is only a solver artifact for the encoded ASP instance.",
        "- Runtime is operational only.",
        "- This is upper-bound scouting, not an exact-depth certificate.",
        "- U-duality is used only for U-type consequences.",
        "- No new reduction or symmetry argument is introduced.",
        "- n=17 sorting-depth citation status should remain explicit if it is still TODO.",
    ])
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    write_preflight()
    if args.preflight_only:
        return
    results = [run_case(n, t, depth, args.timeout_seconds) for n, t, depth in CASES]
    write_summary(results)
    print(json.dumps({"cases": results, "summary_json": rel(SUMMARY_JSON), "summary_csv": rel(SUMMARY_CSV), "report": rel(REPORT_MD)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
