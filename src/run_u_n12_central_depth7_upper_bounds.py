#!/usr/bin/env python3
"""Scout depth-7 U-type upper bounds for central n=12 cases.

This uses the existing ASP encoding, parser, and independent verifier. It does
not introduce reductions, symmetry breaking, or pruning rules.
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
DEPTH = 7
PREVIOUS_DEPTH = 6
CASES = [(12, 5), (12, 6)]
PREVIOUS_SUMMARY = BASE / "u_milestone1_depth6_upper_bounds.json"
PREVIOUS_REPORT = DOC / "u_milestone1_depth6_upper_bounds.md"
SUMMARY_JSON = BASE / "u_n12_central_depth7_upper_bounds.json"
SUMMARY_CSV = BASE / "u_n12_central_depth7_upper_bounds.csv"
PREFLIGHT_JSON = BASE / "u_n12_central_depth7_preflight.json"
PREFLIGHT_MD = BASE / "u_n12_central_depth7_preflight.md"
REPORT_MD = DOC / "u_n12_central_depth7_upper_bounds.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clingo_version() -> str:
    result = subprocess.run([*CLINGO_COMMAND, "--version"], cwd=ROOT, check=False, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def out_dir(n: int, t: int) -> Path:
    return BASE / "decisions" / f"U_t{t}_n{n}" / "depth_07"


def previous_depth6_statuses() -> dict[tuple[int, int], dict[str, Any]]:
    if not PREVIOUS_SUMMARY.exists():
        raise RuntimeError(f"previous summary missing: {rel(PREVIOUS_SUMMARY)}")
    data = json.loads(PREVIOUS_SUMMARY.read_text())
    rows: dict[tuple[int, int], dict[str, Any]] = {}
    for row in data.get("cases", []):
        rows[(int(row["n"]), int(row["t"]))] = row
    missing = [f"U({t},{n})" for n, t in CASES if (n, t) not in rows]
    if missing:
        raise RuntimeError(f"previous summary missing target rows: {', '.join(missing)}")
    not_timeout = [f"U({t},{n})={rows[(n,t)].get('status')}" for n, t in CASES if rows[(n, t)].get("status") != "TIMEOUT"]
    if not_timeout:
        raise RuntimeError("depth-7 scouting is restricted to previous depth-6 TIMEOUT cases; got " + ", ".join(not_timeout))
    return rows


def load_bounds_lower(n: int, t: int) -> tuple[int | None, str]:
    path = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    if not path.exists():
        return None, "bounds table missing"
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "U" and int(row["n"]) == n and int(row["t"]) == t:
                return int(row["lower_bound"]), row.get("lower_bound_sources", "")
    return None, "entry missing from bounds table"


def mirror_t(n: int, t: int) -> int:
    return n - t


def write_preflight(previous: dict[tuple[int, int], dict[str, Any]]) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    DOC.mkdir(parents=True, exist_ok=True)
    verifier_smoke = []
    for n, t in CASES:
        result = verify_binary([], n=n, t=t, kind="U")
        verifier_smoke.append({
            "n": n,
            "t": t,
            "kind": "U",
            "accepts_parameters": result.n == n and result.t == t and result.kind == "U",
            "smoke_result": asdict(result),
        })
    payload = {
        "binary_input_counts": {"n12": 2**12},
        "cases": [{"kind": "U", "n": n, "t": t, "depth": DEPTH, "previous_depth6_status": previous[(n, t)].get("status")} for n, t in CASES],
        "clingo_command": list(CLINGO_COMMAND),
        "clingo_version": clingo_version(),
        "common_encoding": rel(COMMON),
        "target_encoding": rel(TARGET),
        "decision_runner": "src.run_u_n12_central_depth7_upper_bounds",
        "depth6_report_exists": PREVIOUS_REPORT.exists(),
        "depth6_report_path": rel(PREVIOUS_REPORT),
        "depth6_summary_exists": PREVIOUS_SUMMARY.exists(),
        "depth6_summary_path": rel(PREVIOUS_SUMMARY),
        "gpu_use": "none",
        "light_regression_command": ".venv/bin/python -m pytest tests/test_verifier.py tests/test_selection_u_asp.py tests/test_parse_model.py tests/test_selection_bounds.py",
        "purpose": "depth-7 SAT upper-bound scouting only; depth 5 and depth 6 are not rerun",
        "verifier": "src.verify.verify_binary",
        "verifier_smoke": verifier_smoke,
    }
    write_json(PREFLIGHT_JSON, payload)
    lines = [
        "# U-side n=12 central depth-7 preflight",
        "",
        f"- Previous depth-6 report exists: `{PREVIOUS_REPORT.exists()}` at `{rel(PREVIOUS_REPORT)}`.",
        f"- Previous depth-6 summary exists: `{PREVIOUS_SUMMARY.exists()}` at `{rel(PREVIOUS_SUMMARY)}`.",
        "- The two requested targets are confirmed as previous depth-6 `TIMEOUT` rows.",
        f"- pyclingo/libclingo version: `{clingo_version().splitlines()[0]}`.",
        "- Existing `solver/common.lp` and `solver/target_u.lp` are used.",
        "- Existing instance generator, parser, and independent verifier are used.",
        "- Exhaustive verification size: `2^12 = 4096` binary inputs.",
        "- GPU use: none.",
        "- Depth 5 and depth 6 are not rerun by this script.",
    ]
    PREFLIGHT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(n: int, t: int, timeout_seconds: int, previous: dict[str, Any]) -> dict[str, Any]:
    out = out_dir(n, t)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"refusing to overwrite existing artifact directory: {rel(out)}")
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
    upper_bound_7 = status == "VERIFIED_SAT"
    if upper_bound_7:
        conclusion = f"5 <= UDepth({t},{n}) <= 7" if lower_bound and lower_bound >= 5 else f"UDepth({t},{n}) <= 7; lower-bound source needs confirmation"
        interval = "[5,7]" if lower_bound and lower_bound >= 5 else f"[{lower_bound},7]"
    elif status == "UNSAT":
        conclusion = "depth 7 UNSAT; requires follow-up"
        interval = f"[{max(lower_bound or 0, 8)},?]"
    elif status == "TIMEOUT":
        conclusion = "upper bound 7 not established"
        interval = f"[{lower_bound},?]"
    else:
        conclusion = "solver result error; requires follow-up"
        interval = f"[{lower_bound},?]"

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
        "case": f"U_t{t}_n{n}_depth7",
        "current_interval": interval,
        "depth": DEPTH,
        "kind": "U",
        "lower_bound": lower_bound,
        "lower_bound_source": lower_source,
        "n": n,
        "network_json_path": None if network_path is None else rel(network_path),
        "notes": conclusion,
        "previous_depth6_artifact_directory": previous.get("artifact_directory"),
        "previous_depth6_status": previous.get("status"),
        "runtime_seconds": runtime,
        "solver_status": solver_status,
        "status": status,
        "t": t,
        "upper_bound_7_established": upper_bound_7,
        "verifier": verifier_payload,
        "verifier_json_path": None if verifier_path is None else rel(verifier_path),
        "verifier_status": status if status == "VERIFIED_SAT" else "n/a",
        "verifier_trace_summary_path": None if trace_path is None else rel(trace_path),
    }
    write_json(out / "result.json", result)

    lines = [
        f"# U_t{t}_n{n}_depth7",
        "",
        f"- Problem: U({t},{n}) at depth 7",
        f"- Previous depth-6 status: `{previous.get('status')}`",
        f"- Status: `{status}`",
        f"- Solver status: `{solver_status}`",
        f"- Runtime seconds: `{runtime:.6f}`",
        f"- Conclusion: `{conclusion}`",
        "- Command: `command.txt`",
        "- Solver input: `instance.lp`",
        "- Raw solver JSON: `solver_raw.json`",
        "- Parsed solver result: `result.json`",
        "- Solver metadata: `solver_metadata.json`",
    ]
    if network_path:
        lines.extend(["- Network: `network.json`", "- Verifier result: `verifier.json`", "- Verifier trace summary: `verifier_trace_summary.json`"])
    lines.extend([
        "",
        "This depth-7 run is upper-bound scouting. It does not rerun depth 5 or depth 6 and does not create a depth-5/6 UNSAT certificate.",
        "A SAT witness is accepted only after independent exhaustive binary verification.",
    ])
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_summary(results: list[dict[str, Any]]) -> None:
    write_json(SUMMARY_JSON, {"kind": "U", "depth": DEPTH, "previous_depth": PREVIOUS_DEPTH, "cases": results})
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["kind", "n", "t", "depth", "previous_depth6_status", "solver_status", "verifier_status", "upper_bound_7_established", "lower_bound", "current_interval", "runtime_seconds", "artifact_directory", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    def row(r: dict[str, Any]) -> str:
        mirror = mirror_t(r["n"], r["t"])
        if r.get("t") == mirror:
            note = "self-dual central case"
        else:
            note = f"U-duality mirror: U({mirror},{r['n']})"
        conclusion = r.get("current_interval") if r.get("upper_bound_7_established") else r.get("notes")
        return f"| `U({r['t']},{r['n']})` | 7 | `{r.get('previous_depth6_status')}` | `{r.get('solver_status')}` | `{r.get('verifier_status')}` | `{conclusion}` | `{r.get('artifact_directory')}` | {r.get('runtime_seconds', 0):.3f} s | {note} |"

    md = [
        "# U-side depth-7 upper-bound scouting for central n=12 cases",
        "",
        "This report records depth-7 upper-bound scouting for the two central U-type n=12 cases that timed out at depth 6. Depth 5 and depth 6 were not rerun. No new encoding, reduction, symmetry breaking, or pruning rule was introduced.",
        "",
        "## Summary table",
        "",
        "| problem | depth | previous depth-6 status | solver status | verifier status | conclusion | artifact directory | runtime | notes |",
        "| --- | ---: | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    md.extend(row(r) for r in results)
    md.extend(["", "## Consequences", ""])
    for r in results:
        n = r["n"]
        t = r["t"]
        m = mirror_t(n, t)
        if r.get("upper_bound_7_established"):
            if t == m:
                md.append(f"- `U({t},{n})`: depth 7 is `VERIFIED_SAT`, so `5 <= UDepth({t},{n}) <= 7`; this is the self-dual central case.")
            else:
                md.append(f"- `U({t},{n})`: depth 7 is `VERIFIED_SAT`, so `5 <= UDepth({t},{n}) <= 7`; by U-duality, `5 <= UDepth({m},{n}) <= 7`.")
        elif r.get("status") == "UNSAT":
            md.append(f"- `U({t},{n})`: depth 7 is `UNSAT`; the depth-7 lower-bound consequence requires follow-up.")
        else:
            if t == m:
                md.append(f"- `U({t},{n})`: depth 7 reached `{r.get('status')}`, so upper bound 7 is not established for this self-dual central case.")
            else:
                md.append(f"- `U({t},{n})`: depth 7 reached `{r.get('status')}`, so upper bound 7 is not established; by U-duality, no upper bound 7 is established for `U({m},{n})` from this run.")
    md.extend([
        "",
        "## Next-step interpretation",
        "",
        "- If a depth-7 upper bound is obtained, the next issue is either depth-6 witness search or a depth-6/depth-5 UNSAT certificate.",
        "- If depth 7 also times out, the standard pipeline is heavy on the central case and a witness construction, hint, or fixed-layer strategy is needed before drawing stronger conclusions.",
        "- This report is upper-bound scouting; it is not a depth-5 UNSAT certificate.",
        "",
        "## Artifact ledger",
        "",
    ])
    for r in results:
        n = r["n"]
        t = r["t"]
        d = r["artifact_directory"]
        md.extend([
            f"### U({t},{n}), depth 7",
            "",
            f"- Command: `{d}/command.txt`",
            f"- Solver input: `{d}/instance.lp`",
            f"- Raw solver JSON: `{d}/solver_raw.json`",
            f"- Parsed solver result: `{d}/result.json`",
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
        "- Runtime is an operational observation only.",
        "- This is upper-bound scouting; it does not rerun depth 5 or depth 6 and does not create a depth-5/6 UNSAT certificate.",
    ])
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    previous_rows = previous_depth6_statuses()
    write_preflight(previous_rows)
    if args.preflight_only:
        return
    results = [run_case(n, t, args.timeout_seconds, previous_rows[(n, t)]) for n, t in CASES]
    write_summary(results)
    print(json.dumps({"cases": results, "summary_json": rel(SUMMARY_JSON), "summary_csv": rel(SUMMARY_CSV), "report": rel(REPORT_MD)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
