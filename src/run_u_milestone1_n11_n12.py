#!/usr/bin/env python3
"""Run U-side Milestone 1 decisions for n=11,12 at depth 5.

Uses the existing ASP encoding and independent verifier. No reduction,
symmetry breaking, or pruning rule is introduced here.
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
DOC = ROOT / "docs" / "n11_17"
DEPTH = 5
CASES = [
    (11, 2), (11, 3), (11, 4), (11, 5),
    (12, 2), (12, 3), (12, 4), (12, 5), (12, 6),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clingo_version() -> str:
    result = subprocess.run([*CLINGO_COMMAND, "--version"], cwd=ROOT, check=False, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def out_dir(n: int, t: int) -> Path:
    return BASE / "decisions" / f"U_t{t}_n{n}" / "depth_05"


def load_bounds_lower(n: int, t: int) -> tuple[int | None, str]:
    path = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    if not path.exists():
        return None, "bounds table missing"
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "U" and int(row["n"]) == n and int(row["t"]) == t:
                return int(row["lower_bound"]), row.get("lower_bound_sources", "")
    return None, "entry missing from bounds table"


def write_preflight() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    smoke = []
    for n, t in CASES:
        result = verify_binary([], n=n, t=t, kind="U")
        smoke.append({"n": n, "t": t, "kind": "U", "accepts_parameters": result.n == n and result.t == t and result.kind == "U", "smoke_result": asdict(result)})
    n10_summary = ROOT / "experiments" / "baseline_n10" / "n10_depth_summary.json"
    bounds_table = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    payload = {
        "binary_input_counts": {"n11": 2**11, "n12": 2**12},
        "cases": [{"kind": "U", "n": n, "t": t, "depth": DEPTH} for n, t in CASES],
        "clingo_command": list(CLINGO_COMMAND),
        "clingo_version": clingo_version(),
        "common_encoding": rel(COMMON),
        "target_encoding": rel(TARGET),
        "decision_runner": "src.run_u_milestone1_n11_n12",
        "gpu_use": "none",
        "light_regression_command": ".venv/bin/python -m pytest tests/test_verifier.py tests/test_selection_u_asp.py tests/test_parse_model.py tests/test_selection_bounds.py",
        "n10_depth_summary_exists": n10_summary.exists(),
        "n10_depth_summary_path": rel(n10_summary),
        "selection_bounds_table_exists": bounds_table.exists(),
        "selection_bounds_table_path": rel(bounds_table),
        "u_duality_report_use": "U-duality will be used only for report consequences and mirrored U entries.",
        "verifier": "src.verify.verify_binary",
        "verifier_smoke": smoke,
    }
    write_json(BASE / "u_milestone1_preflight.json", payload)
    lines = [
        "# U-side Milestone 1 preflight for n=11,12",
        "",
        f"- pyclingo/libclingo version: `{clingo_version().splitlines()[0]}`.",
        "- Existing `solver/common.lp` and `solver/target_u.lp` are used.",
        "- Existing instance generator, parser, and independent verifier are used.",
        "- Exhaustive verification sizes: `2^11 = 2048`, `2^12 = 4096` binary inputs.",
        f"- n=10 integrated summary exists: `{n10_summary.exists()}` at `{rel(n10_summary)}`.",
        f"- selection bounds table exists: `{bounds_table.exists()}` at `{rel(bounds_table)}`.",
        "- U-duality is used only for report consequences, not as a solver shortcut.",
        "- GPU use: none.",
    ]
    (BASE / "u_milestone1_preflight.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(n: int, t: int, timeout_seconds: int, skip_existing: bool) -> dict[str, Any]:
    out = out_dir(n, t)
    result_path = out / "result.json"
    if skip_existing and result_path.exists():
        return json.loads(result_path.read_text())
    if any(out.glob("*")):
        raise RuntimeError(f"refusing to overwrite existing partial artifact directory: {rel(out)}")
    out.mkdir(parents=True, exist_ok=True)
    instance = out / "instance.lp"
    instance.write_text(generate_instance(n, t, DEPTH), encoding="utf-8")
    command = [
        *CLINGO_COMMAND,
        "--outf=2",
        f"--time-limit={timeout_seconds}",
        "-n",
        "1",
        str(COMMON),
        str(TARGET),
        str(instance),
    ]
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
        network = parse_selected_network(completed.stdout, n=n, depth=DEPTH)
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
    exact_conclusion = None
    if status == "VERIFIED_SAT" and lower_bound == DEPTH:
        exact_conclusion = f"UDepth({t},{n})=5"
    elif status == "VERIFIED_SAT":
        exact_conclusion = "VERIFIED_SAT upper bound 5; lower-bound source needs confirmation"
    elif status == "UNSAT":
        exact_conclusion = f"UDepth({t},{n})>=6; exact value unresolved in this run"
    elif status == "TIMEOUT":
        exact_conclusion = "unresolved due to TIMEOUT"

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
        "case": f"U_t{t}_n{n}_depth5",
        "depth": DEPTH,
        "exact_conclusion": exact_conclusion,
        "kind": "U",
        "lower_bound_at_depth": lower_bound,
        "lower_bound_source": lower_source,
        "n": n,
        "network_json_path": None if network_path is None else rel(network_path),
        "runtime_seconds": runtime,
        "solver_status": solver_status,
        "status": status,
        "t": t,
        "verifier": verifier_payload,
        "verifier_json_path": None if verifier_path is None else rel(verifier_path),
        "verifier_trace_summary_path": None if trace_path is None else rel(trace_path),
    }
    write_json(result_path, result)

    lines = [
        f"# U_t{t}_n{n}_depth5",
        "",
        f"- Problem: U({t},{n}) at depth 5",
        f"- Status: `{status}`",
        f"- Solver status: `{solver_status}`",
        f"- Runtime seconds: `{runtime:.6f}`",
        f"- Exact conclusion: `{exact_conclusion}`",
        "- Command: `command.txt`",
        "- Solver input: `instance.lp`",
        "- Raw solver JSON: `solver_raw.json`",
        "- Parsed solver result: `result.json`",
        "- Solver metadata: `solver_metadata.json`",
    ]
    if network_path:
        lines.extend(["- Network: `network.json`", "- Verifier result: `verifier.json`", "- Verifier trace summary: `verifier_trace_summary.json`"])
    lines.extend(["", "UNSAT is recorded only as a raw solver artifact for this ASP instance.", "A SAT witness is accepted only after independent exhaustive binary verification."])
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_summary(results: list[dict[str, Any]]) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    summary_path = BASE / "u_milestone1_n11_n12_summary.json"
    write_json(summary_path, {"kind": "U", "depth": 5, "cases": results})
    csv_path = BASE / "u_milestone1_n11_n12_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["kind", "n", "t", "depth", "solver_status", "verifier_status", "exact_conclusion", "runtime_seconds", "artifact_directory", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "kind": "U",
                "n": r["n"],
                "t": r["t"],
                "depth": r["depth"],
                "solver_status": r.get("solver_status"),
                "verifier_status": r.get("status") if r.get("status") == "VERIFIED_SAT" else "n/a",
                "exact_conclusion": r.get("exact_conclusion"),
                "runtime_seconds": f"{r.get('runtime_seconds', 0):.6f}",
                "artifact_directory": r.get("artifact_directory"),
                "notes": "lower bound 5 from generated bounds table" if r.get("lower_bound_at_depth") == 5 else "lower-bound source needs confirmation",
            })

    def status_line(r: dict[str, Any]) -> str:
        verifier = r.get("status") if r.get("status") == "VERIFIED_SAT" else "n/a"
        return f"| `U({r['t']},{r['n']})` | 5 | `{r.get('solver_status')}` | `{verifier}` | `{r.get('exact_conclusion')}` | `{r.get('artifact_directory')}` | {r.get('runtime_seconds', 0):.3f} s | lower bound source: bounds table |"

    by_n = {11: [r for r in results if r["n"] == 11], 12: [r for r in results if r["n"] == 12]}
    md = [
        "# U-side Milestone 1 for n=11,12",
        "",
        "This report records the nine requested U-type depth-5 frontier decisions. No new encoding, reduction, symmetry breaking, or pruning rule was introduced.",
        "",
        "## Summary table",
        "",
        "| problem | depth | solver status | verifier status | conclusion | artifact directory | runtime | notes |",
        "| --- | ---: | --- | --- | --- | --- | ---: | --- |",
    ]
    md.extend(status_line(r) for r in results)
    md.extend(["", "## Consequences", ""])
    for n in (11, 12):
        exact_ts = sorted(r["t"] for r in by_n[n] if str(r.get("exact_conclusion", "")).startswith("UDepth"))
        md.extend([f"### n={n}", ""])
        if exact_ts == ([2, 3, 4, 5] if n == 11 else [2, 3, 4, 5, 6]):
            row = [None] * (n + 1)
            row[1] = 4
            row[n] = 0
            for t in exact_ts:
                row[t] = 5
                mirror = n - t
                if 1 <= mirror <= n:
                    row[mirror] = 5
            if n - 1 >= 1:
                row[n - 1] = 4
            md.append(f"The tested central representatives are all exact at depth 5. U-duality fills the mirrored targets for n={n}.")
            md.append("")
            md.append("```text")
            md.append("t:            " + " ".join(f"{t:>2}" for t in range(1, n + 1)))
            md.append("UDepth:       " + " ".join(f"{row[t]:>2}" if row[t] is not None else " ?" for t in range(1, n + 1)))
            md.append("```")
        else:
            md.append("The table is not complete from this milestone alone; see the per-case status rows above.")
        md.append("")
    md.extend(["## Artifact ledger", ""])
    for r in results:
        d = r["artifact_directory"]
        md.extend([
            f"### U({r['t']},{r['n']}), depth 5",
            "",
            f"- Command: `{d}/command.txt`",
            f"- Solver input: `{d}/instance.lp`",
            f"- Raw solver JSON: `{d}/solver_raw.json`",
            f"- Parsed solver result: `{d}/result.json`",
            f"- Solver metadata: `{d}/solver_metadata.json`",
        ])
        if r.get("network_json_path"):
            md.extend([f"- Network: `{r['network_json_path']}`", f"- Verifier result: `{r['verifier_json_path']}`", f"- Verifier trace summary: `{r['verifier_trace_summary_path']}`"])
        md.extend([f"- README: `{d}/README.md`", ""])
    md.extend([
        "## Caveats",
        "",
        "- UNSAT is based on solver artifacts for the encoded ASP instances.",
        "- SAT witnesses are accepted only after independent exhaustive binary simulation.",
        "- Runtime is an operational observation only.",
        "- U-duality is used only for U-type consequences.",
        "- Depth 6 and later were not run in this milestone.",
    ])
    (DOC / "u_milestone1_n11_n12.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--case", choices=[f"U_t{t}_n{n}_depth5" for n, t in CASES] + ["all"], default="all")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    args = parser.parse_args()
    write_preflight()
    selected = CASES if args.case == "all" else [(int(args.case.split("_n")[1].split("_")[0]), int(args.case.split("_t")[1].split("_n")[0]))]
    results = [run_case(n, t, args.timeout_seconds, args.skip_existing) for n, t in selected]
    # Include prior completed results if a subset was requested, so the summary remains complete when possible.
    if args.case != "all":
        complete = []
        for n, t in CASES:
            p = out_dir(n, t) / "result.json"
            if p.exists():
                complete.append(json.loads(p.read_text()))
        results = complete
    results.sort(key=lambda r: (r["n"], r["t"]))
    write_summary(results)
    print(json.dumps({"cases": results, "summary_json": rel(BASE / "u_milestone1_n11_n12_summary.json"), "report": rel(DOC / "u_milestone1_n11_n12.md")}, indent=2, sort_keys=True))
    bad = [r for r in results if r.get("status") not in {"VERIFIED_SAT", "UNSAT", "TIMEOUT"}]
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
