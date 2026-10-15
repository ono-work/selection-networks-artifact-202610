#!/usr/bin/env python3
"""Run the two requested n=10 V-selection depth decisions.

This script uses the existing ASP encoding, clingo command, parser, and
independent Python verifier. It does not change existing artifacts.
"""

from __future__ import annotations

import argparse
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
TARGET_V = ROOT / "solver" / "target_v.lp"
BASE = ROOT / "experiments" / "baseline_n10"

CASES = {
    "V_t2_n10_depth5": {
        "n": 10,
        "t": 2,
        "depth": 5,
        "out": BASE / "decisions" / "V_t2_n10" / "depth_05",
    },
    "V_t3_n10_depth6": {
        "n": 10,
        "t": 3,
        "depth": 6,
        "out": BASE / "decisions" / "V_t3_n10" / "depth_06",
    },
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clingo_version() -> str:
    completed = subprocess.run([*CLINGO_COMMAND, "--version"], cwd=ROOT, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return completed.stderr.strip()
    return completed.stdout.strip()


def preflight() -> dict[str, Any]:
    BASE.mkdir(parents=True, exist_ok=True)
    version = clingo_version()
    verifier_checks = []
    for t in (2, 3):
        result = verify_binary([], n=10, t=t, kind="V")
        verifier_checks.append(asdict(result))
    payload = {
        "clingo_version": version,
        "clingo_command": list(CLINGO_COMMAND),
        "cases": {
            name: {k: str(v) if isinstance(v, Path) else v for k, v in case.items()}
            for name, case in CASES.items()
        },
        "existing_pipeline": {
            "generate_instance": "src.generate_instance.generate_instance",
            "parser": "src.parse_model.parse_selected_network",
            "verifier": "src.verify.verify_binary",
            "target": str(TARGET_V.relative_to(ROOT)),
            "common": str(COMMON.relative_to(ROOT)),
        },
        "n10_binary_input_count": 2**10,
        "verifier_accepts_n10_parameters": all(check["n"] == 10 and check["kind"] == "V" for check in verifier_checks),
        "verifier_parameter_smoke": verifier_checks,
        "runner_accepts_n10_cases": all(case["n"] == 10 for case in CASES.values()),
    }
    write_json(BASE / "preflight.json", payload)
    lines = [
        "# n=10 V-selection preflight",
        "",
        f"- clingo command: `{' '.join(CLINGO_COMMAND)}`",
        f"- clingo version: `{version.splitlines()[0] if version else 'unavailable'}`",
        "- existing verifier accepts `n=10`, `t=2,3`, `kind=V` parameters.",
        "- exhaustive binary verification size: `2^10 = 1024` inputs.",
        "- existing decision components used: `generate_instance`, `target_v.lp`, `parse_selected_network`, `verify_binary`.",
        "- GPU use: none.",
    ]
    (BASE / "preflight.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def run_case(name: str, *, timeout_seconds: int) -> dict[str, Any]:
    case = CASES[name]
    n = int(case["n"])
    t = int(case["t"])
    depth = int(case["depth"])
    out = Path(case["out"])
    out.mkdir(parents=True, exist_ok=True)
    instance = out / "instance.lp"
    solver_raw = out / "solver_raw.json"
    solver_json = out / "solver.json"
    metadata = out / "solver_metadata.json"
    command_path = out / "command.txt"
    result_path = out / "result.json"
    readme_path = out / "README.md"

    instance.write_text(generate_instance(n, t, depth), encoding="utf-8")
    command = [
        *CLINGO_COMMAND,
        "--outf=2",
        f"--time-limit={timeout_seconds}",
        "-n",
        "1",
        str(COMMON),
        str(TARGET_V),
        str(instance),
    ]
    command_path.write_text(" ".join(command) + "\n", encoding="utf-8")

    start = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    runtime = time.perf_counter() - start
    solver_raw.write_text(completed.stdout, encoding="utf-8")
    solver_json.write_text(completed.stdout, encoding="utf-8")

    parsed: dict[str, Any] = {}
    parse_error = None
    try:
        parsed = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    raw_result = parsed.get("Result")
    status = "ERROR"
    verifier_payload = None
    network_path = None
    verifier_path = None
    verifier_trace_path = None
    if raw_result == "SATISFIABLE":
        network = parse_selected_network(completed.stdout, n=n, depth=depth)
        network_payload = network_to_json(network, n=n, t=t, kind="V")
        network_path = out / "network.json"
        write_json(network_path, network_payload)
        verifier = verify_binary(network, n=n, t=t, kind="V")
        verifier_payload = asdict(verifier)
        verifier_path = out / "verifier.json"
        write_json(verifier_path, verifier_payload)
        verifier_trace_path = out / "verifier_trace_summary.json"
        write_json(verifier_trace_path, {"checked_binary_inputs": 2**n, "ok": verifier.ok, "kind": "V", "n": n, "t": t})
        status = "VERIFIED_SAT" if verifier.ok else "VERIFICATION_FAILED"
    elif raw_result == "UNSATISFIABLE":
        status = "UNSAT"
    elif raw_result == "UNKNOWN":
        status = "TIMEOUT"
    elif completed.returncode != 0:
        status = "ERROR"
    elif parse_error:
        status = "ERROR"

    meta = {
        "case": name,
        "command": command,
        "returncode": completed.returncode,
        "runtime_seconds": runtime,
        "timeout_seconds": timeout_seconds,
        "stderr": completed.stderr,
        "clingo_version": clingo_version(),
        "gpu_use": "none",
        "parse_error": parse_error,
    }
    write_json(metadata, meta)
    result = {
        "case": name,
        "kind": "V",
        "n": n,
        "t": t,
        "depth": depth,
        "status": status,
        "solver_status": raw_result,
        "runtime_seconds": runtime,
        "artifact_directory": str(out.relative_to(ROOT)),
        "instance_path": str(instance.relative_to(ROOT)),
        "command_path": str(command_path.relative_to(ROOT)),
        "solver_json_path": str(solver_json.relative_to(ROOT)),
        "solver_raw_json_path": str(solver_raw.relative_to(ROOT)),
        "solver_metadata_path": str(metadata.relative_to(ROOT)),
        "network_json_path": None if network_path is None else str(network_path.relative_to(ROOT)),
        "verifier_json_path": None if verifier_path is None else str(verifier_path.relative_to(ROOT)),
        "verifier_trace_summary_path": None if verifier_trace_path is None else str(verifier_trace_path.relative_to(ROOT)),
        "verifier": verifier_payload,
    }
    write_json(result_path, result)
    readme_path.write_text(readme_for(result), encoding="utf-8")
    return result


def readme_for(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['case']}",
        "",
        f"- Problem: V({result['t']},{result['n']}) at depth {result['depth']}",
        f"- Status: `{result['status']}`",
        f"- Solver status: `{result['solver_status']}`",
        f"- Runtime seconds: `{result['runtime_seconds']:.6f}`",
        f"- Command: `{result['command_path']}`",
        f"- Raw solver JSON: `{result['solver_raw_json_path']}`",
        f"- Parsed solver JSON: `{result['solver_json_path']}`",
        f"- Solver metadata: `{result['solver_metadata_path']}`",
    ]
    if result["network_json_path"]:
        lines.append(f"- Network: `{result['network_json_path']}`")
    if result["verifier_json_path"]:
        lines.append(f"- Verifier: `{result['verifier_json_path']}`")
    lines += [
        "",
        "UNSAT is recorded only as a raw solver artifact for this constrained ASP instance.",
        "SAT witnesses are accepted only when the independent verifier checks all 2^10 binary inputs.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--case", choices=sorted(CASES))
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), indent=2, sort_keys=True))
        return 0
    if args.case is None:
        parser.error("--case is required unless --preflight is used")
    result = run_case(args.case, timeout_seconds=args.timeout_seconds)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"VERIFIED_SAT", "UNSAT", "TIMEOUT"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
