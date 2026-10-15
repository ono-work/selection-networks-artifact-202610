#!/usr/bin/env python3
"""Scout U-type depth-8 upper bounds for n=13,14 depth-7 TIMEOUT cases.

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
DEPTH = 8
CASES = [(13, 4), (13, 5), (13, 6), (14, 3), (14, 4), (14, 5), (14, 6), (14, 7)]
EXCLUDED_DEPTH7_VERIFIED = [(13, 2), (13, 3), (14, 2)]
PREVIOUS_SUMMARY_JSON = BASE / "u_upper_bounds_n13_n14_depth7.json"
PREVIOUS_REPORT_MD = DOC_DIR / "u_upper_bounds_n13_n14_depth7.md"
SUMMARY_JSON = BASE / "u_upper_bounds_n13_n14_depth8.json"
SUMMARY_CSV = BASE / "u_upper_bounds_n13_n14_depth8.csv"
PREFLIGHT_JSON = BASE / "u_upper_bounds_n13_n14_depth8_preflight.json"
PREFLIGHT_MD = BASE / "u_upper_bounds_n13_n14_depth8_preflight.md"
REPORT_MD = DOC_DIR / "u_upper_bounds_n13_n14_depth8.md"
SOURCE_REPORTS = [
    ROOT / "experiments" / "baseline_n10" / "n10_depth_summary.json",
    ROOT / "docs" / "n11_17" / "u_milestone1_depth6_upper_bounds.md",
    ROOT / "docs" / "n11_17" / "u_n12_central_depth7_upper_bounds.md",
    ROOT / "docs" / "n11_17" / "residual_reuse_n11_u_depth5_depth6.md",
    PREVIOUS_REPORT_MD,
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
    return BASE / "decisions" / f"U_t{t}_n{n}" / "depth_08"


def mirror_t(n: int, t: int) -> int:
    return n - t


def load_bounds_lower(n: int, t: int) -> tuple[int | None, str]:
    path = ROOT / "experiments" / "selection_bounds_n11_17" / "bounds_table.csv"
    if not path.exists():
        return None, "bounds table missing"
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "U" and int(row["n"]) == n and int(row["t"]) == t:
                return int(row["lower_bound"]), row.get("lower_bound_sources", "")
    return None, "entry missing from bounds table"


def sorting_citation_status() -> str:
    preferred = ROOT / "docs" / "n11_17" / "selection_bounds_summary.md"
    if preferred.exists():
        return f"local note candidate: {rel(preferred)}"
    candidates = list((ROOT / "docs").glob("**/*")) if (ROOT / "docs").exists() else []
    for path in candidates:
        if path.is_file() and path.suffix.lower() in {".md", ".tex", ".bib", ".txt"}:
            try:
                text = path.read_text(errors="ignore").lower()
            except Exception:
                continue
            if "sortdepth" in text or "sorting-depth" in text or "sorting network" in text:
                if "todo-sorting" in text or "todo_sorting" in text:
                    continue
                return f"local note candidate: {rel(path)}"
    return "sorting-depth citation TODO"



def load_previous_depth7_statuses() -> tuple[dict[tuple[int, int], dict[str, Any]], list[str]]:
    errors: list[str] = []
    rows: dict[tuple[int, int], dict[str, Any]] = {}
    if not PREVIOUS_SUMMARY_JSON.exists():
        return rows, [f"missing previous summary: {rel(PREVIOUS_SUMMARY_JSON)}"]
    try:
        payload = json.loads(PREVIOUS_SUMMARY_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        return rows, [f"failed to parse previous summary: {exc}"]
    for row in payload.get("cases", []):
        try:
            rows[(int(row["n"]), int(row["t"]))] = row
        except Exception as exc:
            errors.append(f"malformed previous row: {exc}: {row!r}")
    for n, t in CASES:
        row = rows.get((n, t))
        if row is None:
            errors.append(f"missing previous depth-7 row for U({t},{n})")
        elif row.get("status") != "TIMEOUT":
            errors.append(f"expected previous depth-7 TIMEOUT for U({t},{n}), got {row.get('status')}")
    for n, t in EXCLUDED_DEPTH7_VERIFIED:
        row = rows.get((n, t))
        if row is None:
            errors.append(f"missing previous depth-7 excluded row for U({t},{n})")
        elif row.get("status") != "VERIFIED_SAT":
            errors.append(f"expected previous depth-7 VERIFIED_SAT for excluded U({t},{n}), got {row.get('status')}")
    return rows, errors

def write_preflight() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    DOC_DIR.mkdir(parents=True, exist_ok=True)
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
    output_dirs = []
    for n, t in CASES:
        d = out_dir(n, t)
        output_dirs.append({"path": rel(d), "exists": d.exists(), "nonempty": d.exists() and any(d.iterdir())})
    previous_rows, previous_errors = load_previous_depth7_statuses()
    previous_statuses = {f"U({t},{n})": previous_rows.get((n, t), {}).get("status") for n, t in CASES}
    excluded_statuses = {f"U({t},{n})": previous_rows.get((n, t), {}).get("status") for n, t in EXCLUDED_DEPTH7_VERIFIED}
    payload = {
        "binary_input_counts": {"n13": 2**13, "n14": 2**14},
        "cases": [{"kind": "U", "n": n, "t": t, "depth": DEPTH, "mirror_t_by_duality": mirror_t(n, t)} for n, t in CASES],
        "clingo_command": list(CLINGO_COMMAND),
        "clingo_version": clingo_version(),
        "common_encoding": rel(COMMON),
        "target_encoding": rel(TARGET),
        "decision_runner": "src.run_u_upper_bounds_n13_n14_depth8",
        "gpu_use": "none",
        "light_regression_command": ".venv/bin/python -m pytest tests/test_verifier.py tests/test_selection_u_asp.py tests/test_parse_model.py tests/test_selection_bounds.py",
        "source_reports": [{"path": rel(path), "exists": path.exists()} for path in SOURCE_REPORTS],
        "duality_scope": "n=13 uses t=2..6; n=14 uses t=2..7, with U(t,n)=U(n-t,n) for report consequences only.",
        "sorting_depth_n13_n14": 9,
        "sorting_depth_citation_status": sorting_citation_status(),
        "previous_depth7_summary": {"path": rel(PREVIOUS_SUMMARY_JSON), "exists": PREVIOUS_SUMMARY_JSON.exists(), "target_statuses": previous_statuses, "excluded_depth7_verified_statuses": excluded_statuses, "errors": previous_errors},
        "output_directories": output_dirs,
        "verifier": "src.verify.verify_binary",
        "verifier_smoke": verifier_smoke,
    }
    write_json(PREFLIGHT_JSON, payload)
    lines = [
        "# U-side depth-8 upper-bound preflight for n=13,14",
        "",
        f"- pyclingo/libclingo version: `{clingo_version().splitlines()[0]}`.",
        f"- Previous depth-7 TIMEOUT check errors: `{len(previous_errors)}`.",
        "- Existing `solver/common.lp` and `solver/target_u.lp` are used.",
        "- Existing instance generator, parser, and independent verifier are used.",
        "- Exhaustive verification sizes: `2^13 = 8192`, `2^14 = 16384` binary inputs.",
        "- Only previous depth-7 TIMEOUT rows are raised to depth 8: `U(4..6,13)` and `U(3..7,14)`.",
        "- GPU use: none.",
        f"- Sorting-depth citation status: `{payload['sorting_depth_citation_status']}`.",
    ]
    for source in payload["source_reports"]:
        lines.append(f"- Source report exists: `{source['exists']}` at `{source['path']}`.")
    PREFLIGHT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(n: int, t: int, timeout_seconds: int) -> dict[str, Any]:
    out = out_dir(n, t)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"refusing to overwrite existing artifact directory: {rel(out)}")
    out.mkdir(parents=True, exist_ok=True)
    instance = out / "instance.lp"
    instance.write_text(generate_instance(n, t, DEPTH), encoding="utf-8")
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
    upper_bound = status == "VERIFIED_SAT"
    if upper_bound:
        interval = f"[{lower_bound},8]" if lower_bound is not None else "[?,8]"
        conclusion = f"UDepth({t},{n}) <= 8" if lower_bound is None else f"{lower_bound} <= UDepth({t},{n}) <= 8"
    elif status == "UNSAT":
        interval = f"[{max(lower_bound or 0, 9)},?]"
        conclusion = "depth 8 UNSAT; requires follow-up"
    elif status == "TIMEOUT":
        interval = f"[{lower_bound},?]" if lower_bound is not None else "[?,?]"
        conclusion = "upper bound 8 not established"
    else:
        interval = f"[{lower_bound},?]" if lower_bound is not None else "[?,?]"
        conclusion = "solver result error; requires follow-up"

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
        "case": f"U_t{t}_n{n}_depth8",
        "current_interval": interval,
        "depth": DEPTH,
        "kind": "U",
        "previous_depth7_status": load_previous_depth7_statuses()[0].get((n, t), {}).get("status", "UNKNOWN"),
        "lower_bound": lower_bound,
        "lower_bound_source": lower_source,
        "mirror_t_by_duality": mirror_t(n, t),
        "n": n,
        "network_json_path": None if network_path is None else rel(network_path),
        "notes": conclusion,
        "runtime_seconds": runtime,
        "solver_status": solver_status,
        "status": status,
        "t": t,
        "upper_bound_established": upper_bound,
        "verifier": verifier_payload,
        "verifier_json_path": None if verifier_path is None else rel(verifier_path),
        "verifier_status": status if status == "VERIFIED_SAT" else "n/a",
        "verifier_trace_summary_path": None if trace_path is None else rel(trace_path),
    }
    write_json(out / "result.json", result)

    lines = [
        f"# U_t{t}_n{n}_depth8",
        "",
        f"- Problem: U({t},{n}) at depth 8",
        f"- Status: `{status}`",
        f"- Solver status: `{solver_status}`",
        f"- Runtime seconds: `{runtime:.6f}`",
        f"- Previous depth-7 status: `{result.get("previous_depth7_status", "UNKNOWN")}`",
        f"- Upper-bound conclusion: `{conclusion}`",
        "- Command: `command.txt`",
        "- Solver input: `instance.lp`",
        "- Raw solver JSON: `solver_raw.json`",
        "- Parsed solver result: `result.json`",
        "- Solver metadata: `solver_metadata.json`",
    ]
    if network_path:
        lines.extend(["- Network: `network.json`", "- Verifier result: `verifier.json`", "- Verifier trace summary: `verifier_trace_summary.json`"])
    lines.extend(["", "This is depth-8 upper-bound scouting. It is not an exact-depth certificate.", "A SAT witness is accepted only after independent exhaustive binary verification."])
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_summary(results: list[dict[str, Any]]) -> None:
    citation_status = sorting_citation_status()
    payload = {
        "kind": "U",
        "depth": DEPTH,
        "cases": results,
        "provenance": {
            "runner": "src.run_u_upper_bounds_n13_n14_depth8",
            "common_encoding": rel(COMMON),
            "target_encoding": rel(TARGET),
            "sorting_depth_n13_n14": 9,
            "sorting_depth_citation_status": citation_status,
        },
    }
    write_json(SUMMARY_JSON, payload)
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["kind", "n", "t", "depth", "previous_depth7_status", "solver_status", "verifier_status", "upper_bound_established", "current_interval", "runtime_seconds", "artifact_directory", "mirror_t_by_duality", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in fieldnames})

    def summary_row(r: dict[str, Any]) -> str:
        return f"| `U({r['t']},{r['n']})` | 8 | `{r.get('previous_depth7_status')}` | `{r.get('solver_status')}` | `{r.get('verifier_status')}` | `{r.get('notes')}` | `{r.get('current_interval')}` | `{r.get('artifact_directory')}` | {r.get('runtime_seconds', 0):.3f} s | mirror `U({r.get('mirror_t_by_duality')},{r['n']})` |"

    md = [
        "# U-side depth-8 upper-bound scouting for n=13,14",
        "",
        "## Scope",
        "",
        "This report records the 8 U-type depth-8 upper-bound scouting runs for n=13,14 that were TIMEOUT at depth 7. Only these 8 listed instances were solved. No depth-7 VERIFIED_SAT row was rerun, and no new reduction, symmetry breaking, pruning rule, or exact-depth certificate is introduced.",
        "",
        "Targets: `U(4..6,13)` and `U(3..7,14)`. U-duality is used only for U-type consequences.",
        "",
        "## Summary table",
        "",
        "| problem | depth | previous depth-7 status | solver status | verifier status | upper-bound conclusion | current interval | artifact directory | runtime | notes |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    md.extend(summary_row(r) for r in results)
    for n in [13, 14]:
        md.extend(["", f"## Consequences for n={n}", ""])
        for r in [row for row in results if row["n"] == n]:
            t = r["t"]
            m = r["mirror_t_by_duality"]
            if r.get("upper_bound_established"):
                if t == m:
                    md.append(f"- `U({t},{n})`: depth 8 is `VERIFIED_SAT`, so `UDepth({t},{n}) <= 8`; this is the self-dual central case.")
                else:
                    md.append(f"- `U({t},{n})`: depth 8 is `VERIFIED_SAT`, so `UDepth({t},{n}) <= 8`; by U-duality, `UDepth({m},{n}) <= 8`.")
            elif r.get("status") == "UNSAT":
                md.append(f"- `U({t},{n})`: depth 8 is `UNSAT`; requires follow-up.")
            else:
                md.append(f"- `U({t},{n})`: `{r.get('status')}`; upper bound 8 not established from this run.")
        endpoint = n - 1
        md.append(f"- Standard endpoints: `UDepth(1,{n})=4`, `UDepth({endpoint},{n})=4` by U-duality, and `UDepth({n},{n})=0`.")
    md.extend([
        "",
        "## Comparison with sorting depth",
        "",
        f"For planning, the sorting-depth upper bound used for n=13,14 is 9. Entries with depth-8 `VERIFIED_SAT` therefore have U-type selection upper bounds one layer shallower than this sorting upper bound. Sorting-depth citation status: `{citation_status}`.",
        "",
        "## Next-step interpretation",
        "",
        "- If many depth-8 witnesses are verified, the n=13,14 U-side upper bounds are substantially improved relative to sorting depth 9.",
        "- TIMEOUT rows should be recorded as unresolved upper-bound searches; do not infer UNSAT.",
        "- Any depth-8 UNSAT row would require separate follow-up.",
        "- Exact values still require separate lower-bound or UNSAT certificate work for shallower depths.",
        "",
        "## Artifact ledger",
        "",
    ])
    for r in results:
        d = r["artifact_directory"]
        md.extend([
            f"### U({r['t']},{r['n']}), depth 8",
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
    ])
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    write_preflight()
    _, previous_errors = load_previous_depth7_statuses()
    if previous_errors:
        raise RuntimeError("previous depth-7 status audit failed: " + "; ".join(previous_errors))
    if args.preflight_only:
        return
    results = [run_case(n, t, args.timeout_seconds) for n, t in CASES]
    write_summary(results)
    print(json.dumps({"cases": results, "summary_json": rel(SUMMARY_JSON), "summary_csv": rel(SUMMARY_CSV), "report": rel(REPORT_MD)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
