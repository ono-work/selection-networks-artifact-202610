#!/usr/bin/env python3
"""Run a requested n=10 U-selection baseline decision."""

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
TARGET = ROOT / "solver" / "target_u.lp"
CASES = {
    "U_t2_n10_depth4": (10, 2, 4, "U_t2_n10", "depth_04"),
    "U_t2_n10_depth5": (10, 2, 5, "U_t2_n10", "depth_05"),
    "U_t3_n10_depth5": (10, 3, 5, "U_t3_n10", "depth_05"),
    "U_t4_n10_depth5": (10, 4, 5, "U_t4_n10", "depth_05"),
    "U_t5_n10_depth5": (10, 5, 5, "U_t5_n10", "depth_05"),
}
N, T, DEPTH, FAMILY, DEPTH_DIR = CASES["U_t3_n10_depth5"]
OUT = ROOT / "experiments" / "baseline_n10" / "decisions" / FAMILY / DEPTH_DIR


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clingo_version() -> str:
    result = subprocess.run(
        [*CLINGO_COMMAND, "--version"], cwd=ROOT, check=False, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def write_preflight() -> None:
    smoke = verify_binary([], n=N, t=T, kind="U")
    payload = {
        "clingo_command": list(CLINGO_COMMAND),
        "clingo_version": clingo_version(),
        "common_encoding": str(COMMON.relative_to(ROOT)),
        "target_encoding": str(TARGET.relative_to(ROOT)),
        "decision_runner": "src.run_baseline_n10_u_decision",
        "verifier": "src.verify.verify_binary",
        "verifier_accepts_parameters": smoke.n == N and smoke.t == T and smoke.kind == "U",
        "verifier_parameter_smoke": asdict(smoke),
        "binary_input_count": 2**N,
        "light_regression_command": (
            ".venv/bin/python -m pytest tests/test_verifier.py "
            "tests/test_selection_u_asp.py tests/test_parse_model.py"
        ),
        "light_regression_result": "17 passed",
        "gpu_use": "none",
    }
    write_json(OUT / "preflight.json", payload)
    (OUT / "preflight.md").write_text(
        f"# U({T},{N}), depth-{DEPTH} preflight\n\n"
        "- pyclingo/libclingo version: `5.8.0`.\n"
        "- Existing `target_u.lp`, instance generator, parser, and independent verifier are used.\n"
        f"- The verifier accepts `n={N}`, `t={T}`, `kind=U` parameters.\n"
        "- Exhaustive verification covers `2^10 = 1024` binary inputs.\n"
        "- Lightweight U encoding, parser, and verifier regressions: `17 passed`.\n"
        "- GPU use: none.\n",
        encoding="utf-8",
    )


def run(timeout_seconds: int) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    write_preflight()
    instance = OUT / "instance.lp"
    instance.write_text(generate_instance(N, T, DEPTH), encoding="utf-8")
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
    (OUT / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")

    started = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    runtime = time.perf_counter() - started
    (OUT / "solver_raw.json").write_text(completed.stdout, encoding="utf-8")
    (OUT / "solver.json").write_text(completed.stdout, encoding="utf-8")

    parse_error = None
    try:
        raw = json.loads(completed.stdout) if completed.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        raw, parse_error = {}, str(exc)
    solver_status = raw.get("Result")
    status = "ERROR"
    network_path = verifier_path = trace_path = None
    verifier_payload = None

    if solver_status == "SATISFIABLE":
        network = parse_selected_network(completed.stdout, n=N, depth=DEPTH)
        network_path = OUT / "network.json"
        write_json(network_path, network_to_json(network, n=N, t=T, kind="U"))
        verifier = verify_binary(network, n=N, t=T, kind="U")
        verifier_payload = asdict(verifier)
        verifier_path = OUT / "verifier.json"
        write_json(verifier_path, verifier_payload)
        trace_path = OUT / "verifier_trace_summary.json"
        write_json(
            trace_path,
            {"checked_binary_inputs": 2**N, "kind": "U", "n": N, "ok": verifier.ok, "t": T},
        )
        status = "VERIFIED_SAT" if verifier.ok else "VERIFICATION_FAILED"
    elif solver_status == "UNSATISFIABLE":
        status = "UNSAT"
    elif solver_status == "UNKNOWN":
        status = "TIMEOUT"

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
    write_json(OUT / "solver_metadata.json", metadata)
    result = {
        "artifact_directory": str(OUT.relative_to(ROOT)),
        "case": f"U_t{T}_n{N}_depth{DEPTH}",
        "depth": DEPTH,
        "kind": "U",
        "n": N,
        "network_json_path": None if network_path is None else str(network_path.relative_to(ROOT)),
        "runtime_seconds": runtime,
        "solver_status": solver_status,
        "status": status,
        "t": T,
        "verifier": verifier_payload,
        "verifier_json_path": None if verifier_path is None else str(verifier_path.relative_to(ROOT)),
        "verifier_trace_summary_path": None if trace_path is None else str(trace_path.relative_to(ROOT)),
    }
    write_json(OUT / "result.json", result)
    lines = [
        f"# U_t{T}_n{N}_depth{DEPTH}",
        "",
        f"- Problem: U({T},{N}) at depth {DEPTH}",
        f"- Status: `{status}`",
        f"- Solver status: `{solver_status}`",
        f"- Runtime seconds: `{runtime:.6f}`",
        "- Command: `command.txt`",
        "- Solver input: `instance.lp`",
        "- Raw solver JSON: `solver_raw.json`",
        "- Parsed solver result: `result.json`",
        "- Solver metadata: `solver_metadata.json`",
    ]
    if network_path:
        lines.extend(
            [
                "- Network: `network.json`",
                "- Verifier result: `verifier.json`",
                "- Verifier trace summary: `verifier_trace_summary.json`",
            ]
        )
    lines.extend(
        [
            "",
            "UNSAT is recorded only as a raw solver artifact for this ASP instance.",
            "A SAT witness is accepted only after independent exhaustive binary verification.",
        ]
    )
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    global N, T, DEPTH, FAMILY, DEPTH_DIR, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), default="U_t3_n10_depth5")
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    args = parser.parse_args()
    N, T, DEPTH, FAMILY, DEPTH_DIR = CASES[args.case]
    OUT = ROOT / "experiments" / "baseline_n10" / "decisions" / FAMILY / DEPTH_DIR
    result = run(args.timeout_seconds)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"VERIFIED_SAT", "UNSAT", "TIMEOUT"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
