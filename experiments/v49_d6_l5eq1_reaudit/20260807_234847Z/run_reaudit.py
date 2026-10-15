#!/usr/bin/env python3
"""Replay exactly the two missing V(4,9) depth-6 L5eq1 instances."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv/bin/python"
COMMON = ROOT / "solver/common.lp"
TARGET = ROOT / "solver/target_v.lp"
BRANCHES = {
    "A5_residual_L5eq1": ROOT / "experiments/v49_d6_l5_partitioned/branches/A5_residual_L5eq1/instance.lp",
    "B6_residual_L5eq1": ROOT / "experiments/v49_d6_l5_partitioned/branches/B6_residual_L5eq1/instance.lp",
}
EXPECTED_HASHES = {
    str(COMMON): "2cebdc5d3107f09b77e3ebeaf554b39f25212dbe7a1fb9bd78fa933e0b990fc0",
    str(TARGET): "ddae98e3a4bd702b9d97342ab558f7a4670eb7c7caf5dd726e28aef7cfe77f1a",
    str(BRANCHES["A5_residual_L5eq1"]): "50f49de2e87d3d35bf1f2cd77544ccdc3c39d839f277558dbece979f4648aa20",
    str(BRANCHES["B6_residual_L5eq1"]): "6cebc8627592dcf0de1722834ff0c4925f524d6e1291edd6b61c93dc475a6b69",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time_report(path: Path) -> dict[str, str | int | float | None]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ": " in line:
            key, value = line.strip().split(": ", 1)
            fields[key] = value
    def number(key: str, cast):
        try:
            return cast(fields[key])
        except (KeyError, ValueError):
            return None
    return {
        "user_cpu_seconds": number("User time (seconds)", float),
        "system_cpu_seconds": number("System time (seconds)", float),
        "cpu_percent": fields.get("Percent of CPU this job got"),
        "elapsed_wall_clock": fields.get("Elapsed (wall clock) time (h:mm:ss or m:ss)"),
        "maximum_resident_set_kbytes": number("Maximum resident set size (kbytes)", int),
        "time_exit_status": number("Exit status", int),
    }


def main() -> int:
    input_hashes = {path: sha256(Path(path)) for path in EXPECTED_HASHES}
    if input_hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hash mismatch: {input_hashes!r}")

    snapshot = RUN_DIR / "input_snapshot"
    snapshot.mkdir(exist_ok=True)
    shutil.copy2(COMMON, snapshot / "common.lp")
    shutil.copy2(TARGET, snapshot / "target_v.lp")
    for branch_id, instance in BRANCHES.items():
        shutil.copy2(instance, snapshot / f"{branch_id}.instance.lp")

    version_result = subprocess.run(
        [str(PYTHON), "-m", "clingo", "--version"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    environment = {
        "started_at_utc": utc_now(),
        "cwd": str(ROOT),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "python_executable": str(PYTHON),
        "python_version": sys.version,
        "solver_name": "pyclingo",
        "solver_version_stdout": version_result.stdout,
        "solver_version_stderr": version_result.stderr,
        "input_hashes_sha256": input_hashes,
    }
    (RUN_DIR / "environment.json").write_text(
        json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    running = []
    for branch_id, instance in BRANCHES.items():
        branch_dir = RUN_DIR / branch_id
        raw_stdout = branch_dir / "raw_stdout.json"
        raw_stderr = branch_dir / "raw_stderr.txt"
        time_report = branch_dir / "resource_usage.txt"
        solver_command = [
            str(PYTHON), "-m", "clingo", "--outf=2", "--stats=2", "-n", "1",
            "--time-limit=900", str(COMMON), str(TARGET), str(instance),
        ]
        wrapped_command = ["/usr/bin/time", "-v", "-o", str(time_report), *solver_command]
        started_at = utc_now()
        started = time.perf_counter()
        stdout_handle = raw_stdout.open("wb")
        stderr_handle = raw_stderr.open("wb")
        process = subprocess.Popen(
            wrapped_command,
            cwd=ROOT,
            stdout=stdout_handle,
            stderr=stderr_handle,
            start_new_session=True,
        )
        running.append({
            "branch_id": branch_id,
            "instance": instance,
            "process": process,
            "stdout_handle": stdout_handle,
            "stderr_handle": stderr_handle,
            "raw_stdout": raw_stdout,
            "raw_stderr": raw_stderr,
            "time_report": time_report,
            "solver_command": solver_command,
            "wrapped_command": wrapped_command,
            "started_at": started_at,
            "started": started,
        })

    summaries = []
    for item in running:
        process = item["process"]
        returncode = process.wait()
        wall_seconds = time.perf_counter() - item["started"]
        item["stdout_handle"].close()
        item["stderr_handle"].close()
        raw_bytes = item["raw_stdout"].read_bytes()
        raw_json_path = RUN_DIR / item["branch_id"] / "raw_solver.json"
        raw_json_path.write_bytes(raw_bytes)
        try:
            raw_json = json.loads(raw_bytes)
            parse_error = None
        except Exception as exc:
            raw_json = None
            parse_error = repr(exc)
        summary = {
            "branch_id": item["branch_id"],
            "source_instance_path": str(item["instance"]),
            "solver_command": item["solver_command"],
            "wrapped_command": item["wrapped_command"],
            "started_at_utc": item["started_at"],
            "finished_at_utc": utc_now(),
            "wrapper_wall_seconds": wall_seconds,
            "process_exit_status": returncode,
            "raw_json_parse_error": parse_error,
            "raw_clingo_result": raw_json.get("Result") if isinstance(raw_json, dict) else None,
            "raw_models": raw_json.get("Models") if isinstance(raw_json, dict) else None,
            "raw_stdout_sha256": sha256(item["raw_stdout"]),
            "raw_stderr_sha256": sha256(item["raw_stderr"]),
            "raw_stderr_bytes": item["raw_stderr"].stat().st_size,
            "input_hashes_sha256": {
                "instance.lp": sha256(item["instance"]),
                "common.lp": sha256(COMMON),
                "target_v.lp": sha256(TARGET),
            },
            "resource_usage": parse_time_report(item["time_report"]),
            "artifact_paths": {
                "raw_stdout": str(item["raw_stdout"]),
                "raw_json": str(raw_json_path),
                "raw_stderr": str(item["raw_stderr"]),
                "resource_usage": str(item["time_report"]),
            },
        }
        summary_path = RUN_DIR / item["branch_id"] / "run_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (RUN_DIR / item["branch_id"] / "command.json").write_text(
            json.dumps({"solver_command": item["solver_command"], "wrapped_command": item["wrapped_command"]}, indent=2) + "\n",
            encoding="utf-8",
        )
        summaries.append(summary)

    completed = {
        "run_directory": str(RUN_DIR),
        "started_at_utc": environment["started_at_utc"],
        "finished_at_utc": utc_now(),
        "parallel_jobs": 2,
        "results": summaries,
        "all_raw_unsat": all(
            row["process_exit_status"] == 0 and row["raw_clingo_result"] == "UNSATISFIABLE"
            for row in summaries
        ),
    }
    (RUN_DIR / "run_manifest.json").write_text(
        json.dumps(completed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if completed["all_raw_unsat"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
