#!/usr/bin/env python3
"""Audited witness-only search for U(2,17) at depth 6."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import platform
import resource
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.parse_model import network_to_json, parse_selected_network
from src.verify import verify_binary

N, T, DEPTH = 17, 2, 6
COMMON = ROOT / "solver/common.lp"
TARGET = ROOT / "solver/target_u.lp"
PYTHON = ROOT / ".venv/bin/python"
TIMEOUT_SECONDS = 900


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def reduced_instance() -> str:
    lines = [f"n({N}).", f"t({T}).", f"depth({DEPTH})."]
    input_id = 0
    for zero_count in (1, 2):
        for zero_wires in itertools.combinations(range(1, N + 1), zero_count):
            zeros = set(zero_wires)
            lines.append(f"input({input_id}).")
            lines.append(f"zero_count({input_id},{zero_count}).")
            for wire in range(1, N + 1):
                lines.append(f"bit({input_id},{wire},{0 if wire in zeros else 1}).")
            input_id += 1
    assert input_id == 153
    return "\n".join(lines) + "\n"


def second_verifier(network: list[list[tuple[int, int]]]) -> dict[str, object]:
    failures = []
    checked = 0
    for mask in range(1 << N):
        values = [(mask >> (N - 1 - wire)) & 1 for wire in range(N)]
        zero_count = values.count(0)
        for layer in network:
            for i, j in layer:
                a, b = values[i - 1], values[j - 1]
                values[i - 1], values[j - 1] = min(a, b), max(a, b)
        if values[:T].count(0) != min(T, zero_count):
            failures.append({"mask": mask, "output": values, "zero_count": zero_count})
            break
        checked += 1
    return {"checked": checked, "failures": failures, "ok": not failures}


def main() -> int:
    RUN.mkdir(parents=True, exist_ok=True)
    instance = RUN / "instance.lp"
    instance.write_text(reduced_instance(), encoding="utf-8")
    shutil.copyfile(COMMON, RUN / "common.lp")
    shutil.copyfile(TARGET, RUN / "target_u.lp")

    version = subprocess.run(
        [str(PYTHON), "-m", "clingo", "--version"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    )
    command = [
        str(PYTHON), "-m", "clingo", "--outf=2", "--stats=2", "-n", "1",
        f"--time-limit={TIMEOUT_SECONDS}", str(COMMON), str(TARGET), str(instance),
    ]
    write_json(RUN / "command.json", {"argv": command})
    write_json(RUN / "preflight.json", {
        "scope": "SAT witness search only; UNKNOWN/TIMEOUT is not UNSAT",
        "n": N, "t": T, "depth": DEPTH, "input_count": 153,
        "input_zero_counts": [1, 2],
        "reduction_argument": (
            "zero_count=0 is automatic. For z>2, change all but two zeros to ones; "
            "coordinatewise monotonicity of compare-exchange networks implies that if both "
            "selected outputs are zero for every z=2 input, they remain zero for the smaller "
            "input with additional zeros. Thus z=1 and z=2 are complete for U(2,n)."
        ),
        "normal_forms_used": False,
        "component_canonical_key_used": False,
        "solver_version_stdout": version.stdout,
        "solver_version_stderr": version.stderr,
        "solver_version_exit_status": version.returncode,
        "environment": {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "cwd": str(ROOT), "hostname": socket.gethostname(),
            "platform": platform.platform(), "machine": platform.machine(),
            "python": sys.version, "logical_cpu_count": os.cpu_count(),
        },
    })

    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    wall = time.perf_counter() - started
    finished_utc = datetime.now(timezone.utc).isoformat()
    (RUN / "raw_stdout.json").write_bytes(completed.stdout)
    (RUN / "raw_solver.json").write_bytes(completed.stdout)
    (RUN / "raw_stderr.txt").write_bytes(completed.stderr)

    parse_error = None
    try:
        raw = json.loads(completed.stdout)
    except Exception as exc:
        raw, parse_error = {}, repr(exc)
    result = raw.get("Result")
    network = None
    verification = None
    verification2 = None
    if result == "SATISFIABLE":
        network = parse_selected_network(completed.stdout.decode(), n=N, depth=DEPTH)
        write_json(RUN / "network.json", network_to_json(network, n=N, t=T, kind="U"))
        verification = asdict(verify_binary(network, n=N, t=T, kind="U"))
        write_json(RUN / "verifier_primary.json", verification)
        verification2 = second_verifier(network)
        write_json(RUN / "verifier_independent.json", verification2)

    summary = {
        "started_at_utc": started_utc, "finished_at_utc": finished_utc,
        "wall_seconds": wall,
        "user_cpu_seconds": after.ru_utime - before.ru_utime,
        "system_cpu_seconds": after.ru_stime - before.ru_stime,
        "peak_rss_kbytes": after.ru_maxrss,
        "process_exit_status": completed.returncode,
        "raw_result": result, "raw_models": raw.get("Models"),
        "parse_error": parse_error,
        "verified_sat": bool(result == "SATISFIABLE" and verification and verification["ok"] and verification2 and verification2["ok"]),
        "network_layer_sizes": None if network is None else [len(layer) for layer in network],
        "network_comparator_count": None if network is None else sum(map(len, network)),
        "sha256": {
            "source_common.lp": sha256(COMMON), "snapshot_common.lp": sha256(RUN / "common.lp"),
            "source_target_u.lp": sha256(TARGET), "snapshot_target_u.lp": sha256(RUN / "target_u.lp"),
            "instance.lp": sha256(instance), "raw_stdout.json": sha256(RUN / "raw_stdout.json"),
            "raw_stderr.txt": sha256(RUN / "raw_stderr.txt"),
        },
    }
    write_json(RUN / "run_summary.json", summary)
    manifest_files = sorted(p for p in RUN.iterdir() if p.is_file() and p.name != "artifact_manifest.sha256")
    (RUN / "artifact_manifest.sha256").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in manifest_files), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["verified_sat"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
