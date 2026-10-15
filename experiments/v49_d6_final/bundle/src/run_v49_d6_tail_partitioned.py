"""Tail-category partition runner for the remaining V(4,9), depth-6 branches."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import signal
import subprocess
import sys
import time
from collections import Counter, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.benchmark_v49_d6_solver_config import _environment_metadata, _extract_stats, _fmt, _process_snapshot
from src.experiment import COMMON, TARGET_V, solver_version
from src.parse_model import network_to_json, parse_selected_network
from src.run_v49_d6_l5_partitioned import L5BranchDefinition, generate_branch_instance
from src.solver import CLINGO_COMMAND
from src.v49_d6_l5_tail_census import build_all_censuses
from src.v49_d6_topology_pruning import VALIDATION_JSON, topology_pruning_asp_constraints
from src.verify import verify_binary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_tail_partitioned"
DEFAULT_TIMEOUT_SECONDS = 1800
SCREENING_TIMEOUT_SECONDS = 600
SCREENING_WORKERS = 18
OVERNIGHT_TIMEOUT_SECONDS = 14400
OVERNIGHT_WORKERS = 18
SEED = 1
PARENT_FAMILIES = ("A5_residual_L5eq3", "B6_residual_L5eq3", "B6_residual_L5eq4")
WORKLOAD_CLASSES: dict[str, tuple[str, ...]] = {
    "A5_near": ("A5_residual_L5eq3__wire1_partner_2", "A5_residual_L5eq3__wire1_partner_3"),
    "A5_tail": ("A5_residual_L5eq3__wire1_partner_6", "A5_residual_L5eq3__wire1_partner_7", "A5_residual_L5eq3__wire1_partner_8", "A5_residual_L5eq3__wire1_partner_9"),
    "A5_unused": ("A5_residual_L5eq3__wire1_unused",),
    "B6eq3_both_used": ("B6_residual_L5eq3__p1_2__p6_4", "B6_residual_L5eq3__p1_2__p6_5", "B6_residual_L5eq3__p1_3__p6_5"),
    "B6eq3_one_idle_near": ("B6_residual_L5eq3__p1_0__p6_2", "B6_residual_L5eq3__p1_0__p6_5", "B6_residual_L5eq3__p1_2__p6_0", "B6_residual_L5eq3__p1_3__p6_0"),
    "B6eq3_one_idle_tail": ("B6_residual_L5eq3__p1_0__p6_7", "B6_residual_L5eq3__p1_0__p6_8", "B6_residual_L5eq3__p1_0__p6_9", "B6_residual_L5eq3__p1_7__p6_0", "B6_residual_L5eq3__p1_8__p6_0", "B6_residual_L5eq3__p1_9__p6_0"),
    "B6eq3_both_idle": ("B6_residual_L5eq3__p1_0__p6_0",),
    "B6eq4_unused_final_endpoint": ("B6_residual_L5eq4__unused_wire_1", "B6_residual_L5eq4__unused_wire_6"),
    "B6eq4_unused_tail": ("B6_residual_L5eq4__unused_wire_7", "B6_residual_L5eq4__unused_wire_8", "B6_residual_L5eq4__unused_wire_9"),
}

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"]


@dataclass(frozen=True)
class TailBranchDefinition:
    branch_id: str
    parent_branch_id: str
    residual_id: str
    leaf_id: str
    category: str
    category_matching_count: int
    final_layer: tuple[tuple[int, int], ...]
    forbid_l5: tuple[tuple[int, int], ...]
    l5_count: int
    category_constraints: str


@dataclass(frozen=True)
class TailBranchResult:
    branch_id: str
    status: BranchStatus
    runtime_seconds: float
    timeout_seconds: int
    command: list[str]
    peak_rss_kb: int | None
    clingo_result: str | None
    verifier_ok: bool | None
    error_message: str | None = None


@dataclass(frozen=True)
class ScreeningJob:
    queue_position: int
    definition: TailBranchDefinition


@dataclass(frozen=True)
class ScreeningResult:
    queue_position: int
    dispatch_time: str | None
    branch_id: str
    parent_family: str
    census_matching_count: int
    status: BranchStatus
    runtime_seconds: float | None
    timeout_seconds: int
    command: list[str]
    peak_rss_kb: int | None
    cpu_snapshots: int
    clingo_result: str | None
    verifier_ok: bool | None
    instance_path: str
    raw_json_path: str
    stderr_path: str
    resource_log_path: str
    metadata_path: str
    branch_definition_path: str
    result_path: str
    network_path: str | None
    stats: dict[str, Any] | None
    choices: float | None
    conflicts: float | None
    restarts: float | None
    solving_time: float | None
    error_message: str | None = None


@dataclass(frozen=True)
class OvernightJob:
    queue_position: int
    workload_class: str
    definition: TailBranchDefinition


@dataclass(frozen=True)
class OvernightResult:
    queue_position: int
    dispatch_time: str | None
    branch_id: str
    parent_family: str
    workload_class: str
    census_matching_count: int
    status: BranchStatus
    runtime_seconds: float | None
    timeout_seconds: int
    command: list[str]
    solver_options: list[str]
    peak_rss_kb: int | None
    cpu_snapshots: int
    clingo_result: str | None
    verifier_ok: bool | None
    instance_path: str
    raw_json_path: str
    stdout_path: str
    stderr_path: str
    resource_log_path: str
    metadata_path: str
    branch_definition_path: str
    result_path: str
    network_path: str | None
    verifier_path: str | None
    stats: dict[str, Any] | None
    choices: float | None
    conflicts: float | None
    restarts: float | None
    solving_time: float | None
    error_message: str | None = None


def topology_pruning_validated() -> bool:
    if not VALIDATION_JSON.exists():
        return False
    data = json.loads(VALIDATION_JSON.read_text(encoding="utf-8"))
    return data.get("status") == "PASSED"


def category_constraint(parent: L5BranchDefinition, category: str) -> str:
    lines = [f"% Tail category for {parent.branch_id}: {category}"]
    if parent.branch_id == "A5_residual_L5eq3":
        if category == "wire1_unused":
            lines.append(":- selected(5,1,J).")
        else:
            partner = int(category.removeprefix("wire1_partner_"))
            lines.append(f":- not selected(5,1,{partner}).")
    elif parent.branch_id == "B6_residual_L5eq3":
        left, right = category.split("__")
        p1 = int(left.removeprefix("p1_"))
        p6 = int(right.removeprefix("p6_"))
        if p1 == 0:
            lines.append(":- selected(5,1,J).")
        else:
            lines.append(f":- not selected(5,{min(1, p1)},{max(1, p1)}).")
        if p6 == 0:
            lines.append(":- selected(5,I,6).")
            lines.append(":- selected(5,6,J).")
        else:
            lines.append(f":- not selected(5,{min(6, p6)},{max(6, p6)}).")
    elif parent.branch_id == "B6_residual_L5eq4":
        unused = int(category.removeprefix("unused_wire_"))
        lines.append(f":- selected(5,{unused},J).")
        lines.append(f":- selected(5,I,{unused}).")
    else:
        raise ValueError(f"unsupported parent {parent.branch_id!r}")
    return "\n".join(lines) + "\n"


def branch_definitions() -> list[TailBranchDefinition]:
    definitions: list[TailBranchDefinition] = []
    for census in build_all_censuses():
        parent = L5BranchDefinition(
            branch_id=census.branch_id,
            residual_id=census.residual_id,
            leaf_id=census.leaf_id,
            final_layer=census.final_layer,
            forbid_l5=census.forbid_l5,
            l5_count=census.l5_count,
            constraints="",
        )
        for category, count in census.category_counts.items():
            definitions.append(
                TailBranchDefinition(
                    branch_id=f"{census.branch_id}__{category}",
                    parent_branch_id=census.branch_id,
                    residual_id=census.residual_id,
                    leaf_id=census.leaf_id,
                    category=category,
                    category_matching_count=count,
                    final_layer=census.final_layer,
                    forbid_l5=census.forbid_l5,
                    l5_count=census.l5_count,
                    category_constraints=category_constraint(parent, category),
                )
            )
    return definitions


def generate_tail_instance(definition: TailBranchDefinition, *, enable_topology_pruning: bool = False) -> str:
    if enable_topology_pruning and not topology_pruning_validated():
        raise RuntimeError("topology pruning requested before Phase-1 validation passed")
    instance = generate_branch_instance(definition.final_layer, definition.forbid_l5, definition.l5_count)
    instance += "\n" + definition.category_constraints
    if enable_topology_pruning:
        instance += "\n" + topology_pruning_asp_constraints()
    return instance


def materialize(output_dir: Path = DEFAULT_OUTPUT_DIR, *, enable_topology_pruning: bool = False) -> list[TailBranchDefinition]:
    definitions = branch_definitions()
    for name in ("branches", "logs", "reports", "pilot"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)
    for definition in definitions:
        branch_dir = output_dir / "branches" / definition.branch_id
        branch_dir.mkdir(parents=True, exist_ok=True)
        (branch_dir / "branch_definition.json").write_text(json.dumps(asdict(definition), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (branch_dir / "instance.lp").write_text(generate_tail_instance(definition, enable_topology_pruning=enable_topology_pruning), encoding="utf-8")
    write_partition_plan(output_dir / "reports" / "partition_plan.md", definitions)
    return definitions


def run_solver_branches(
    *,
    output_dir: Path,
    timeout_seconds: int,
    workers: int,
    clingo_threads: int,
    enable_topology_pruning: bool,
) -> list[TailBranchResult]:
    definitions = materialize(output_dir, enable_topology_pruning=enable_topology_pruning)
    pending = list(definitions)
    active: list[tuple[TailBranchDefinition, subprocess.Popen[str], float, Path, list[str]]] = []
    results: list[TailBranchResult] = []
    while pending or active:
        while pending and len(active) < workers:
            definition = pending.pop(0)
            branch_dir = output_dir / "branches" / definition.branch_id
            raw_path = branch_dir / "solver.json"
            err_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
            options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={timeout_seconds}"]
            if clingo_threads != 1:
                options.append(f"--parallel-mode={clingo_threads},split")
            command = [*CLINGO_COMMAND, *options, str(COMMON), str(TARGET_V), str(branch_dir / "instance.lp")]
            with raw_path.open("w", encoding="utf-8") as stdout, err_path.open("w", encoding="utf-8") as stderr:
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr, text=True)
            active.append((definition, process, time.perf_counter(), branch_dir, [str(part) for part in command]))
        time.sleep(1.0)
        still_active = []
        for definition, process, started, branch_dir, command in active:
            elapsed = time.perf_counter() - started
            if process.poll() is None and elapsed < timeout_seconds:
                still_active.append((definition, process, started, branch_dir, command))
                continue
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
            results.append(_finalize(definition, branch_dir, command, elapsed, timeout_seconds))
        active = still_active
    (output_dir / "pilot" / "results.json").write_text(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


def _finalize(definition: TailBranchDefinition, branch_dir: Path, command: list[str], elapsed: float, timeout_seconds: int) -> TailBranchResult:
    raw_path = branch_dir / "solver.json"
    clingo_result = None
    verifier_ok = None
    error = None
    try:
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        clingo_result = payload.get("Result")
        if clingo_result == "SATISFIABLE":
            network = parse_selected_network(raw_path.read_text(encoding="utf-8"), n=9, depth=6)
            verifier = verify_binary(network, n=9, t=4, kind="V")
            verifier_ok = verifier.ok
            (branch_dir / "network.json").write_text(json.dumps(network_to_json(network, n=9, t=4, kind="V"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            status: BranchStatus = "SAT" if verifier.ok else "VERIFICATION_FAILED"
        elif clingo_result == "UNSATISFIABLE":
            status = "UNSAT"
        elif clingo_result == "UNKNOWN":
            status = "TIMEOUT"
        else:
            status = "ERROR"
            error = f"unexpected clingo result {clingo_result!r}"
    except Exception as exc:  # noqa: BLE001
        status = "ERROR"
        error = str(exc)
    result = TailBranchResult(definition.branch_id, status, elapsed, timeout_seconds, command, None, clingo_result, verifier_ok, error)
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_screening_queue(definitions: list[TailBranchDefinition]) -> list[ScreeningJob]:
    queues: dict[str, deque[TailBranchDefinition]] = {}
    for parent in PARENT_FAMILIES:
        rows = [definition for definition in definitions if definition.parent_branch_id == parent]
        rows.sort(key=lambda definition: (definition.category_matching_count, definition.branch_id))
        queues[parent] = deque(rows)
    unknown = sorted({definition.parent_branch_id for definition in definitions} - set(PARENT_FAMILIES))
    if unknown:
        raise ValueError(f"unsupported parent families in screening queue: {unknown}")
    jobs: list[ScreeningJob] = []
    while any(queues.values()):
        for parent in PARENT_FAMILIES:
            if queues[parent]:
                jobs.append(ScreeningJob(len(jobs) + 1, queues[parent].popleft()))
    return jobs


def screening_command(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[str]:
    return ["./scripts/run_v49_d6_tail_partitioned.sh", "--mode", "screening", "--enable-topology-pruning", "--output-dir", str(output_dir)]


def run_screening(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[ScreeningResult]:
    screening_dir = output_dir / "screening"
    for name in ("raw", "branches", "logs", "reports"):
        (screening_dir / name).mkdir(parents=True, exist_ok=True)
    (output_dir / "reports").mkdir(parents=True, exist_ok=True)
    definitions = materialize(screening_dir, enable_topology_pruning=True)
    jobs = build_screening_queue(definitions)
    if len(jobs) != 75:
        raise RuntimeError(f"screening expects exactly 75 child branches, got {len(jobs)}")
    metadata = _screening_metadata(output_dir)
    (screening_dir / "reports" / "screening_metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending = deque(jobs)
    active: dict[int, dict[str, Any]] = {}
    results: list[ScreeningResult] = []
    stop_reason: str | None = None
    while pending or active:
        while pending and len(active) < SCREENING_WORKERS and stop_reason is None:
            job = pending.popleft()
            info = _dispatch_screening_job(screening_dir, job, metadata)
            active[info["process"].pid] = info
            print(f"DISPATCH {job.queue_position:02d} {job.definition.branch_id}", flush=True)
        time.sleep(1.0)
        for pid, info in list(active.items()):
            process = info["process"]
            snapshot = _process_snapshot(pid)
            if snapshot is not None:
                info["cpu_snapshots"] += 1
                rss = snapshot.get("rss_kb")
                if isinstance(rss, int):
                    info["peak_rss_kb"] = rss if info["peak_rss_kb"] is None else max(info["peak_rss_kb"], rss)
                with info["resource_log_path"].open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"elapsed_seconds": time.perf_counter() - info["started"], **snapshot}, sort_keys=True) + "\n")
            elapsed = time.perf_counter() - info["started"]
            timed_out = process.poll() is None and elapsed >= SCREENING_TIMEOUT_SECONDS
            if process.poll() is None and not timed_out:
                continue
            if timed_out:
                _terminate_process(process)
            result = _finalize_screening_job(info, timed_out=timed_out)
            results.append(result)
            del active[pid]
            print(f"COMPLETE {result.queue_position:02d} {result.branch_id} {result.status} {_fmt_runtime(result.runtime_seconds)}s", flush=True)
            if result.status == "SAT" and result.verifier_ok:
                stop_reason = "VERIFIED_SAT"
                print(f"VERIFIED_SAT {result.network_path}", flush=True)
                break
            if result.status in {"ERROR", "VERIFICATION_FAILED"}:
                stop_reason = result.status
                print(f"STOPPING_AFTER_{result.status} {result.branch_id}", flush=True)
                break
        if stop_reason is not None:
            results.extend(_cancel_active_jobs(active))
            active.clear()
            results.extend(_cancel_pending_jobs(screening_dir, pending, metadata))
            pending.clear()
            break
    results.sort(key=lambda result: result.queue_position)
    _write_screening_artifacts(output_dir, screening_dir, jobs, results, metadata, stop_reason)
    return results


def _dispatch_screening_job(screening_dir: Path, job: ScreeningJob, metadata: dict[str, Any]) -> dict[str, Any]:
    definition = job.definition
    branch_dir = screening_dir / "branches" / definition.branch_id
    raw_dir = screening_dir / "raw" / definition.branch_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_json_path = raw_dir / "solver.json"
    stderr_path = screening_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = screening_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    metadata_path = raw_dir / "metadata.json"
    result_path = branch_dir / "screening_result.json"
    resource_log_path.write_text("", encoding="utf-8")
    options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={SCREENING_TIMEOUT_SECONDS}", f"--seed={SEED}"]
    command = [*CLINGO_COMMAND, *options, str(COMMON), str(TARGET_V), str(branch_dir / "instance.lp")]
    dispatch_time = _utc_timestamp()
    metadata_path.write_text(json.dumps({"branch": asdict(definition), "queue_position": job.queue_position, "dispatch_time": dispatch_time, "command": [str(part) for part in command], "solver_options": options, "screening": metadata, "raw_json_path": str(raw_json_path), "stderr_path": str(stderr_path), "resource_log_path": str(resource_log_path)}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with raw_json_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, text=True, start_new_session=True)
    return {"job": job, "process": process, "started": time.perf_counter(), "dispatch_time": dispatch_time, "command": [str(part) for part in command], "branch_dir": branch_dir, "raw_json_path": raw_json_path, "stderr_path": stderr_path, "resource_log_path": resource_log_path, "metadata_path": metadata_path, "result_path": result_path, "peak_rss_kb": None, "cpu_snapshots": 0}


def _finalize_screening_job(info: dict[str, Any], *, timed_out: bool) -> ScreeningResult:
    job: ScreeningJob = info["job"]
    definition = job.definition
    raw_json_path: Path = info["raw_json_path"]
    branch_dir: Path = info["branch_dir"]
    runtime = time.perf_counter() - info["started"]
    clingo_result = None
    verifier_ok = None
    error = None
    stats = None
    network_path = None
    try:
        stdout_text = raw_json_path.read_text(encoding="utf-8")
        payload = json.loads(stdout_text) if stdout_text.strip() else {}
        raw_result = payload.get("Result")
        clingo_result = raw_result if isinstance(raw_result, str) else None
        stats = payload.get("Stats") if isinstance(payload.get("Stats"), dict) else None
        if timed_out or clingo_result == "UNKNOWN":
            status: BranchStatus = "TIMEOUT"
        elif clingo_result == "SATISFIABLE":
            network = parse_selected_network(stdout_text, n=9, depth=6)
            verifier = verify_binary(network, n=9, t=4, kind="V")
            verifier_ok = verifier.ok
            network_path_obj = branch_dir / "network.json"
            network_path_obj.write_text(json.dumps(network_to_json(network, n=9, t=4, kind="V"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            network_path = str(network_path_obj)
            status = "SAT" if verifier.ok else "VERIFICATION_FAILED"
            if not verifier.ok:
                error = "independent Python verifier rejected SAT witness"
        elif clingo_result == "UNSATISFIABLE":
            status = "UNSAT"
        else:
            status = "ERROR"
            error = f"unexpected clingo result {clingo_result!r}"
    except Exception as exc:  # noqa: BLE001
        status = "ERROR"
        error = str(exc)
    choices, conflicts, restarts, solving_time = _extract_stats(stats)
    result = _screening_result(info, status, runtime, clingo_result, verifier_ok, stats, choices, conflicts, restarts, solving_time, network_path, error)
    info["result_path"].write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _screening_result(info: dict[str, Any], status: BranchStatus, runtime: float | None, clingo_result: str | None, verifier_ok: bool | None, stats: dict[str, Any] | None, choices: float | None, conflicts: float | None, restarts: float | None, solving_time: float | None, network_path: str | None, error: str | None) -> ScreeningResult:
    job: ScreeningJob = info["job"]
    definition = job.definition
    return ScreeningResult(job.queue_position, info.get("dispatch_time"), definition.branch_id, definition.parent_branch_id, definition.category_matching_count, status, runtime, SCREENING_TIMEOUT_SECONDS, info.get("command", []), info.get("peak_rss_kb"), info.get("cpu_snapshots", 0), clingo_result, verifier_ok, str(info["branch_dir"] / "instance.lp"), str(info["raw_json_path"]), str(info["stderr_path"]), str(info["resource_log_path"]), str(info["metadata_path"]), str(info["branch_dir"] / "branch_definition.json"), str(info["result_path"]), network_path, stats, choices, conflicts, restarts, solving_time, error)


def _cancel_active_jobs(active: dict[int, dict[str, Any]]) -> list[ScreeningResult]:
    results = []
    for info in active.values():
        runtime = time.perf_counter() - info["started"]
        _terminate_process(info["process"])
        info["runtime_seconds"] = runtime
        results.append(_cancel_result(info))
    return results


def _cancel_pending_jobs(screening_dir: Path, pending: deque[ScreeningJob], metadata: dict[str, Any]) -> list[ScreeningResult]:
    return [_cancel_result(_undispatched_info(screening_dir, job, metadata)) for job in pending]


def _undispatched_info(screening_dir: Path, job: ScreeningJob, metadata: dict[str, Any]) -> dict[str, Any]:
    definition = job.definition
    branch_dir = screening_dir / "branches" / definition.branch_id
    raw_dir = screening_dir / "raw" / definition.branch_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = raw_dir / "metadata.json"
    raw_json_path = raw_dir / "solver.json"
    stderr_path = screening_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = screening_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    result_path = branch_dir / "screening_result.json"
    metadata_path.write_text(json.dumps({"branch": asdict(definition), "queue_position": job.queue_position, "screening": metadata, "cancelled_before_dispatch": True}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raw_json_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    resource_log_path.write_text("", encoding="utf-8")
    return {"job": job, "dispatch_time": None, "command": [], "branch_dir": branch_dir, "raw_json_path": raw_json_path, "stderr_path": stderr_path, "resource_log_path": resource_log_path, "metadata_path": metadata_path, "result_path": result_path, "peak_rss_kb": None, "cpu_snapshots": 0, "runtime_seconds": None}


def _cancel_result(info: dict[str, Any]) -> ScreeningResult:
    result = _screening_result(info, "CANCELLED_AFTER_VERIFIED_SAT", info.get("runtime_seconds"), None, None, None, None, None, None, None, None, "cancelled after a verified SAT witness in another branch")
    info["result_path"].write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)


def _write_screening_artifacts(output_dir: Path, screening_dir: Path, jobs: list[ScreeningJob], results: list[ScreeningResult], metadata: dict[str, Any], stop_reason: str | None) -> None:
    (screening_dir / "reports" / "screening_results.json").write_text(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_summary_csv(output_dir / "reports" / "screening_summary.csv", results)
    _write_timeouts_csv(output_dir / "reports" / "screening_timeouts.csv", results)
    write_screening_report(output_dir / "reports" / "screening_report.md", jobs, results, metadata, stop_reason)


def _write_summary_csv(path: Path, results: list[ScreeningResult]) -> None:
    fields = ["queue_position", "branch_id", "parent_family", "census_matching_count", "status", "runtime_seconds", "peak_rss_kb", "cpu_snapshots", "raw_json_path", "stderr_path", "resource_log_path", "metadata_path", "network_path"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({field: getattr(result, field) for field in fields})


def _write_timeouts_csv(path: Path, results: list[ScreeningResult]) -> None:
    fields = ["branch_id", "parent_family", "census_matching_count", "runtime_seconds", "choices_per_second", "conflicts_per_second", "restarts_per_second", "raw_json_path", "stderr_path", "resource_log_path"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in sorted((row for row in results if row.status == "TIMEOUT"), key=_timeout_sort_key):
            writer.writerow({"branch_id": result.branch_id, "parent_family": result.parent_family, "census_matching_count": result.census_matching_count, "runtime_seconds": result.runtime_seconds, "choices_per_second": _rate(result.choices, result.runtime_seconds), "conflicts_per_second": _rate(result.conflicts, result.runtime_seconds), "restarts_per_second": _rate(result.restarts, result.runtime_seconds), "raw_json_path": result.raw_json_path, "stderr_path": result.stderr_path, "resource_log_path": result.resource_log_path})


def write_screening_report(path: Path, jobs: list[ScreeningJob], results: list[ScreeningResult], metadata: dict[str, Any], stop_reason: str | None) -> None:
    counts = Counter(result.status for result in results)
    by_branch = {result.branch_id: result for result in results}
    completed_unsat = [result for result in results if result.status == "UNSAT"]
    timeouts = sorted([result for result in results if result.status == "TIMEOUT"], key=_timeout_sort_key)
    recommendation = _screening_recommendation(results)
    lines = ["# V(4,9), Depth-6 Tail Screening Report", "", "## Reproducibility", "", f"Exact command line: `{' '.join(metadata['command_line'])}`", "", f"Clingo version: `{metadata['clingo_version'].strip()}`", "", f"Host metadata: `{json.dumps(metadata['host'], sort_keys=True)}`", "", f"Git HEAD: `{metadata['git_head']}`", "", f"Dirty worktree state: `{metadata['dirty_worktree_state']}`", "", "## Scheduler Policy", "", "Dynamic worker-pool scheduling with 18 outer workers, one clingo thread per branch, 600 second per-branch timeout, no internal clingo parallel mode, no GPU use, and topology pruning enabled. Within each parent family, children are sorted by ascending census matching count and then stable branch identifier. Dispatch uses parent-family round-robin while multiple queues remain nonempty; workers take the next queued job immediately when free.", "", "## Queue Order", "", "| queue | parent | census | branch | status |", "| ---: | --- | ---: | --- | --- |"]
    for job in jobs:
        result = by_branch.get(job.definition.branch_id)
        lines.append(f"| {job.queue_position} | {job.definition.parent_branch_id} | {job.definition.category_matching_count} | `{job.definition.branch_id}` | {result.status if result else ''} |")
    lines.extend(["", "## Outcome Counts", "", "| status | count |", "| --- | ---: |"])
    for status in ("SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"):
        lines.append(f"| {status} | {counts.get(status, 0)} |")
    lines.extend(["", "## Completed UNSAT Branches", "", "| queue | parent | census | branch | runtime s | peak RSS KB |", "| ---: | --- | ---: | --- | ---: | ---: |"])
    for result in sorted(completed_unsat, key=lambda row: row.queue_position):
        lines.append(f"| {result.queue_position} | {result.parent_family} | {result.census_matching_count} | `{result.branch_id}` | {_fmt_runtime(result.runtime_seconds)} | {result.peak_rss_kb or ''} |")
    lines.extend(["", "## Timeout Branches", "", "Ranked by parent family, census matching count, choices/sec, conflicts/sec, and restarts/sec when available; blank rate fields mean the ranking metric is unavailable for that branch.", "", "| parent | census | branch | runtime s | choices/s | conflicts/s | restarts/s |", "| --- | ---: | --- | ---: | ---: | ---: | ---: |"])
    for result in timeouts:
        lines.append(f"| {result.parent_family} | {result.census_matching_count} | `{result.branch_id}` | {_fmt_runtime(result.runtime_seconds)} | {_fmt(_rate(result.choices, result.runtime_seconds))} | {_fmt(_rate(result.conflicts, result.runtime_seconds))} | {_fmt(_rate(result.restarts, result.runtime_seconds))} |")
    if not timeouts:
        lines.append("|  |  | No timeout branches. Ranking metric is unavailable. |  |  |  |  |")
    lines.extend(["", "## Coverage Accounting", "", "| category | count |", "| --- | ---: |", "| prior closed branches | 0 |", f"| new screening UNSAT branches | {counts.get('UNSAT', 0)} |", f"| remaining timed-out branches | {counts.get('TIMEOUT', 0)} |", "", "## Final Recommendation", "", recommendation, "", "## Stop State", "", f"Stop reason: `{stop_reason or 'completed_all_jobs'}`."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _screening_recommendation(results: list[ScreeningResult]) -> str:
    timeouts = [result for result in results if result.status == "TIMEOUT"]
    if timeouts:
        named = ", ".join(f"`{result.branch_id}`" for result in sorted(timeouts, key=_timeout_sort_key)[:10])
        return f"run a longer wave on specifically named timeout branches: {named}."
    completed = [result for result in results if result.status in {"UNSAT", "SAT"}]
    if completed:
        named = ", ".join(f"`{result.branch_id}`" for result in completed[:3])
        return f"benchmark one-thread versus four-thread solving on specifically named timeout branches: {named}."
    return "add an independent CNF/SAT encoding."


def _timeout_sort_key(result: ScreeningResult) -> tuple[Any, ...]:
    return (result.parent_family, result.census_matching_count, _none_last(_rate(result.choices, result.runtime_seconds)), _none_last(_rate(result.conflicts, result.runtime_seconds)), _none_last(_rate(result.restarts, result.runtime_seconds)), result.branch_id)


def _none_last(value: float | None) -> tuple[int, float]:
    return (1, 0.0) if value is None else (0, value)


def _rate(value: float | None, runtime_seconds: float | None) -> float | None:
    if value is None or runtime_seconds is None or runtime_seconds <= 0:
        return None
    return value / runtime_seconds


def _fmt_runtime(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def _screening_metadata(output_dir: Path) -> dict[str, Any]:
    return {"command_line": screening_command(output_dir), "clingo_version": solver_version(), "host": {**_environment_metadata(), "node": platform.node()}, "git_head": _git(["rev-parse", "HEAD"]), "dirty_worktree_state": _git_dirty_state(), "timeout_seconds": SCREENING_TIMEOUT_SECONDS, "workers": SCREENING_WORKERS, "clingo_threads_per_branch": 1, "internal_clingo_parallel_mode": "none", "topology_pruning": True, "seed": SEED, "output_dir": str(output_dir)}


def _git(args: list[str]) -> str:
    completed = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    return completed.stdout.strip() if completed.returncode == 0 else f"unavailable: {completed.stderr.strip()}"


def _git_dirty_state() -> str:
    status = _git(["status", "--short"])
    return "clean" if not status else status


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def overnight_command(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[str]:
    return ["./scripts/run_v49_d6_tail_partitioned.sh", "--mode", "overnight", "--enable-topology-pruning", "--output-dir", str(output_dir)]


def _screening_rows(output_dir: Path) -> list[dict[str, str]]:
    path = output_dir / "reports" / "screening_summary.csv"
    if not path.exists():
        raise RuntimeError(f"missing screening summary: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _workload_class_for(branch_id: str) -> str | None:
    matches = [name for name, branch_ids in WORKLOAD_CLASSES.items() if branch_id in branch_ids]
    if len(matches) > 1:
        raise RuntimeError(f"branch belongs to multiple workload classes: {branch_id}: {matches}")
    return matches[0] if matches else None


def overnight_selection(output_dir: Path = DEFAULT_OUTPUT_DIR) -> tuple[list[OvernightJob], dict[str, Any]]:
    rows = _screening_rows(output_dir)
    if len(rows) != 75:
        raise RuntimeError(f"screening summary must contain 75 rows, got {len(rows)}")
    status_counts = Counter(row["status"] for row in rows)
    timeout_rows = [row for row in rows if row["status"] == "TIMEOUT"]
    unsat_rows = [row for row in rows if row["status"] == "UNSAT"]
    if len(unsat_rows) != 49 or len(timeout_rows) != 26:
        raise RuntimeError(f"expected 49 screening UNSAT and 26 TIMEOUT rows, got {dict(status_counts)}")
    expected = {branch_id for branch_ids in WORKLOAD_CLASSES.values() for branch_id in branch_ids}
    selected = {row["branch_id"] for row in timeout_rows}
    if selected != expected:
        raise RuntimeError(f"screening TIMEOUT set differs from workload list; missing={sorted(expected - selected)} extra={sorted(selected - expected)}")
    definitions_by_id = {definition.branch_id: definition for definition in branch_definitions()}
    by_id = {row["branch_id"]: row for row in timeout_rows}
    queues: dict[str, deque[TailBranchDefinition]] = {}
    class_members: dict[str, list[str]] = {}
    for class_name, branch_ids in WORKLOAD_CLASSES.items():
        rows_for_class = []
        for branch_id in branch_ids:
            if _workload_class_for(branch_id) != class_name:
                raise RuntimeError(f"workload class membership is not unique for {branch_id}")
            if branch_id not in definitions_by_id:
                raise RuntimeError(f"workload branch not in current 75 child definitions: {branch_id}")
            if branch_id not in by_id:
                raise RuntimeError(f"workload branch was not selected from screening TIMEOUT rows: {branch_id}")
            rows_for_class.append(definitions_by_id[branch_id])
        rows_for_class.sort(key=lambda definition: (definition.category_matching_count, definition.branch_id))
        queues[class_name] = deque(rows_for_class)
        class_members[class_name] = [definition.branch_id for definition in rows_for_class]
    jobs: list[OvernightJob] = []
    while any(queues.values()):
        for class_name in WORKLOAD_CLASSES:
            if queues[class_name]:
                jobs.append(OvernightJob(len(jobs) + 1, class_name, queues[class_name].popleft()))
    if len(jobs) != 26:
        raise RuntimeError(f"overnight selection must contain 26 jobs, got {len(jobs)}")
    certificate = {
        "screening_summary_path": str(output_dir / "reports" / "screening_summary.csv"),
        "screening_status_counts": dict(status_counts),
        "screening_unsat_excluded_count": len(unsat_rows),
        "screening_timeout_selected_count": len(timeout_rows),
        "selected_branch_ids": [job.definition.branch_id for job in jobs],
        "workload_classes": class_members,
        "every_selected_branch_belongs_to_exactly_one_class": True,
        "selection_matches_declared_workload_classes": True,
    }
    return jobs, certificate


def run_overnight(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[OvernightResult]:
    jobs, certificate = overnight_selection(output_dir)
    run_id = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    run_dir = output_dir / "overnight" / run_id
    for name in ("raw", "branches", "logs"):
        (run_dir / name).mkdir(parents=True, exist_ok=False)
    metadata = _overnight_metadata(output_dir, run_dir)
    _materialize_overnight_jobs(run_dir, jobs)
    (run_dir / "selection_certificate.json").write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_overnight_plan(run_dir / "overnight_plan.md", jobs, metadata, certificate)
    pending = deque(jobs)
    active: dict[int, dict[str, Any]] = {}
    results: list[OvernightResult] = []
    stop_reason: str | None = None
    while pending or active:
        while pending and len(active) < OVERNIGHT_WORKERS and stop_reason is None:
            job = pending.popleft()
            info = _dispatch_overnight_job(run_dir, job, metadata)
            active[info["process"].pid] = info
            print(f"DISPATCH {job.queue_position:02d} {job.workload_class} {job.definition.branch_id}", flush=True)
        time.sleep(1.0)
        for pid, info in list(active.items()):
            process = info["process"]
            snapshot = _process_snapshot(pid)
            if snapshot is not None:
                info["cpu_snapshots"] += 1
                rss = snapshot.get("rss_kb")
                if isinstance(rss, int):
                    info["peak_rss_kb"] = rss if info["peak_rss_kb"] is None else max(info["peak_rss_kb"], rss)
                with info["resource_log_path"].open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"elapsed_seconds": time.perf_counter() - info["started"], **snapshot}, sort_keys=True) + "\n")
            elapsed = time.perf_counter() - info["started"]
            timed_out = process.poll() is None and elapsed >= OVERNIGHT_TIMEOUT_SECONDS
            if process.poll() is None and not timed_out:
                continue
            if timed_out:
                _terminate_process(process)
            result = _finalize_overnight_job(info, timed_out=timed_out)
            results.append(result)
            del active[pid]
            print(f"COMPLETE {result.queue_position:02d} {result.branch_id} {result.status} {_fmt_runtime(result.runtime_seconds)}s", flush=True)
            if result.status == "SAT" and result.verifier_ok:
                stop_reason = "VERIFIED_SAT"
                print(f"V49_DEPTH6_SAT_VERIFIED {result.network_path}", flush=True)
                break
            if result.status in {"ERROR", "VERIFICATION_FAILED"}:
                stop_reason = result.status
                print(f"STOPPING_AFTER_{result.status} {result.branch_id}", flush=True)
                break
        if stop_reason is not None:
            results.extend(_cancel_overnight_active(active))
            active.clear()
            results.extend(_cancel_overnight_pending(run_dir, pending, metadata))
            pending.clear()
            break
    results.sort(key=lambda result: result.queue_position)
    outcome = _overnight_outcome(run_dir, results)
    _write_overnight_artifacts(run_dir, jobs, results, metadata, certificate, stop_reason, outcome)
    print(outcome, flush=True)
    print("overnight_report", run_dir / "overnight_report.md", flush=True)
    return results


def _materialize_overnight_jobs(run_dir: Path, jobs: list[OvernightJob]) -> None:
    for job in jobs:
        branch_dir = run_dir / "branches" / job.definition.branch_id
        branch_dir.mkdir(parents=True, exist_ok=True)
        payload = {**asdict(job.definition), "workload_class": job.workload_class, "queue_position": job.queue_position}
        (branch_dir / "branch_definition.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (branch_dir / "instance.lp").write_text(generate_tail_instance(job.definition, enable_topology_pruning=True), encoding="utf-8")


def _dispatch_overnight_job(run_dir: Path, job: OvernightJob, metadata: dict[str, Any]) -> dict[str, Any]:
    definition = job.definition
    branch_dir = run_dir / "branches" / definition.branch_id
    raw_dir = run_dir / "raw" / definition.branch_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_json_path = raw_dir / "solver.json"
    stdout_path = raw_json_path
    stderr_path = run_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = run_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    metadata_path = raw_dir / "metadata.json"
    result_path = branch_dir / "overnight_result.json"
    resource_log_path.write_text("", encoding="utf-8")
    options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={OVERNIGHT_TIMEOUT_SECONDS}", f"--seed={SEED}"]
    command = [*CLINGO_COMMAND, *options, str(COMMON), str(TARGET_V), str(branch_dir / "instance.lp")]
    dispatch_time = _utc_timestamp()
    metadata_path.write_text(json.dumps({"branch": asdict(definition), "workload_class": job.workload_class, "queue_position": job.queue_position, "dispatch_time": dispatch_time, "command": [str(part) for part in command], "solver_options": options, "overnight": metadata, "relevant_hashes": _relevant_hashes(branch_dir / "instance.lp")}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with raw_json_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, text=True, start_new_session=True)
    return {"job": job, "process": process, "started": time.perf_counter(), "dispatch_time": dispatch_time, "solver_options": options, "command": [str(part) for part in command], "branch_dir": branch_dir, "raw_json_path": raw_json_path, "stdout_path": stdout_path, "stderr_path": stderr_path, "resource_log_path": resource_log_path, "metadata_path": metadata_path, "result_path": result_path, "peak_rss_kb": None, "cpu_snapshots": 0}


def _finalize_overnight_job(info: dict[str, Any], *, timed_out: bool) -> OvernightResult:
    raw_json_path: Path = info["raw_json_path"]
    branch_dir: Path = info["branch_dir"]
    runtime = time.perf_counter() - info["started"]
    clingo_result = None
    verifier_ok = None
    error = None
    stats = None
    network_path = None
    verifier_path = None
    try:
        stdout_text = raw_json_path.read_text(encoding="utf-8")
        payload = json.loads(stdout_text) if stdout_text.strip() else {}
        raw_result = payload.get("Result")
        clingo_result = raw_result if isinstance(raw_result, str) else None
        stats = payload.get("Stats") if isinstance(payload.get("Stats"), dict) else None
        if timed_out or clingo_result == "UNKNOWN":
            status: BranchStatus = "TIMEOUT"
        elif clingo_result == "SATISFIABLE":
            network = parse_selected_network(stdout_text, n=9, depth=6)
            verifier = verify_binary(network, n=9, t=4, kind="V")
            verifier_ok = verifier.ok
            network_path_obj = branch_dir / "network.json"
            verifier_path_obj = branch_dir / "verifier.json"
            network_path_obj.write_text(json.dumps(network_to_json(network, n=9, t=4, kind="V"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            verifier_path_obj.write_text(json.dumps(asdict(verifier), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            network_path = str(network_path_obj)
            verifier_path = str(verifier_path_obj)
            status = "SAT" if verifier.ok else "VERIFICATION_FAILED"
            if not verifier.ok:
                error = "independent Python verifier rejected SAT witness"
        elif clingo_result == "UNSATISFIABLE":
            status = "UNSAT"
        else:
            status = "ERROR"
            error = f"unexpected clingo result {clingo_result!r}"
    except Exception as exc:  # noqa: BLE001
        status = "ERROR"
        error = str(exc)
    choices, conflicts, restarts, solving_time = _extract_stats(stats)
    result = _overnight_result(info, status, runtime, clingo_result, verifier_ok, stats, choices, conflicts, restarts, solving_time, network_path, verifier_path, error)
    info["result_path"].write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _overnight_result(info: dict[str, Any], status: BranchStatus, runtime: float | None, clingo_result: str | None, verifier_ok: bool | None, stats: dict[str, Any] | None, choices: float | None, conflicts: float | None, restarts: float | None, solving_time: float | None, network_path: str | None, verifier_path: str | None, error: str | None) -> OvernightResult:
    job: OvernightJob = info["job"]
    definition = job.definition
    return OvernightResult(job.queue_position, info.get("dispatch_time"), definition.branch_id, definition.parent_branch_id, job.workload_class, definition.category_matching_count, status, runtime, OVERNIGHT_TIMEOUT_SECONDS, info.get("command", []), info.get("solver_options", []), info.get("peak_rss_kb"), info.get("cpu_snapshots", 0), clingo_result, verifier_ok, str(info["branch_dir"] / "instance.lp"), str(info["raw_json_path"]), str(info["stdout_path"]), str(info["stderr_path"]), str(info["resource_log_path"]), str(info["metadata_path"]), str(info["branch_dir"] / "branch_definition.json"), str(info["result_path"]), network_path, verifier_path, stats, choices, conflicts, restarts, solving_time, error)


def _cancel_overnight_active(active: dict[int, dict[str, Any]]) -> list[OvernightResult]:
    results = []
    for info in active.values():
        runtime = time.perf_counter() - info["started"]
        _terminate_process(info["process"])
        info["runtime_seconds"] = runtime
        results.append(_cancel_overnight_result(info))
    return results


def _cancel_overnight_pending(run_dir: Path, pending: deque[OvernightJob], metadata: dict[str, Any]) -> list[OvernightResult]:
    return [_cancel_overnight_result(_undispatched_overnight_info(run_dir, job, metadata)) for job in pending]


def _undispatched_overnight_info(run_dir: Path, job: OvernightJob, metadata: dict[str, Any]) -> dict[str, Any]:
    definition = job.definition
    branch_dir = run_dir / "branches" / definition.branch_id
    raw_dir = run_dir / "raw" / definition.branch_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_json_path = raw_dir / "solver.json"
    stderr_path = run_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = run_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    metadata_path = raw_dir / "metadata.json"
    result_path = branch_dir / "overnight_result.json"
    metadata_path.write_text(json.dumps({"branch": asdict(definition), "workload_class": job.workload_class, "queue_position": job.queue_position, "overnight": metadata, "cancelled_before_dispatch": True}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raw_json_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    resource_log_path.write_text("", encoding="utf-8")
    return {"job": job, "dispatch_time": None, "solver_options": [], "command": [], "branch_dir": branch_dir, "raw_json_path": raw_json_path, "stdout_path": raw_json_path, "stderr_path": stderr_path, "resource_log_path": resource_log_path, "metadata_path": metadata_path, "result_path": result_path, "peak_rss_kb": None, "cpu_snapshots": 0, "runtime_seconds": None}


def _cancel_overnight_result(info: dict[str, Any]) -> OvernightResult:
    result = _overnight_result(info, "CANCELLED_AFTER_VERIFIED_SAT", info.get("runtime_seconds"), None, None, None, None, None, None, None, None, None, "cancelled after a verified SAT witness in another branch")
    info["result_path"].write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _write_overnight_artifacts(run_dir: Path, jobs: list[OvernightJob], results: list[OvernightResult], metadata: dict[str, Any], certificate: dict[str, Any], stop_reason: str | None, outcome: str) -> None:
    (run_dir / "overnight_results.json").write_text(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_overnight_summary_csv(run_dir / "overnight_summary.csv", results)
    _write_overnight_timeouts_csv(run_dir / "overnight_timeouts.csv", results)
    write_overnight_report(run_dir / "overnight_report.md", jobs, results, metadata, certificate, stop_reason, outcome)


def _write_overnight_summary_csv(path: Path, results: list[OvernightResult]) -> None:
    fields = ["queue_position", "branch_id", "parent_family", "workload_class", "census_matching_count", "status", "runtime_seconds", "peak_rss_kb", "cpu_snapshots", "raw_json_path", "stdout_path", "stderr_path", "resource_log_path", "metadata_path", "network_path", "verifier_path"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({field: getattr(result, field) for field in fields})


def _write_overnight_timeouts_csv(path: Path, results: list[OvernightResult]) -> None:
    fields = ["branch_id", "workload_class", "parent_family", "census_matching_count", "runtime_seconds", "choices_per_second", "conflicts_per_second", "restarts_per_second", "raw_json_path", "stderr_path", "resource_log_path"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in sorted((row for row in results if row.status == "TIMEOUT"), key=lambda row: (row.workload_class, row.census_matching_count, row.branch_id)):
            writer.writerow({"branch_id": result.branch_id, "workload_class": result.workload_class, "parent_family": result.parent_family, "census_matching_count": result.census_matching_count, "runtime_seconds": result.runtime_seconds, "choices_per_second": _rate(result.choices, result.runtime_seconds), "conflicts_per_second": _rate(result.conflicts, result.runtime_seconds), "restarts_per_second": _rate(result.restarts, result.runtime_seconds), "raw_json_path": result.raw_json_path, "stderr_path": result.stderr_path, "resource_log_path": result.resource_log_path})


def write_overnight_plan(path: Path, jobs: list[OvernightJob], metadata: dict[str, Any], certificate: dict[str, Any]) -> None:
    lines = ["# V(4,9), Depth-6 Tail Overnight Plan", "", f"Exact command: `{' '.join(metadata['command_line'])}`", "", "Configuration: topology pruning enabled; 18 outer workers; one clingo thread per branch; no internal clingo parallel mode; 14,400 second per-branch timeout; no GPU use; fixed seed recorded in metadata.", "", f"Worker calculation: host logical CPUs {metadata['host']['cpu_count']}; reserved logical CPUs 2; outer workers {OVERNIGHT_WORKERS}.", "", f"Selection: excluded {certificate['screening_unsat_excluded_count']} screening UNSAT branches and selected {certificate['screening_timeout_selected_count']} screening TIMEOUT branches.", "", "| queue | workload class | parent | census | branch |", "| ---: | --- | --- | ---: | --- |"]
    for job in jobs:
        lines.append(f"| {job.queue_position} | {job.workload_class} | {job.definition.parent_branch_id} | {job.definition.category_matching_count} | `{job.definition.branch_id}` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_overnight_report(path: Path, jobs: list[OvernightJob], results: list[OvernightResult], metadata: dict[str, Any], certificate: dict[str, Any], stop_reason: str | None, outcome: str) -> None:
    counts = Counter(result.status for result in results)
    runtimes = [result.runtime_seconds for result in results if result.runtime_seconds is not None]
    rss_values = [result.peak_rss_kb for result in results if result.peak_rss_kb is not None]
    newly_closed = counts.get("UNSAT", 0)
    remaining = sum(counts.get(status, 0) for status in ("TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"))
    lines = ["# V(4,9), Depth-6 Tail Overnight Report", "", "## Metadata", "", f"Exact launch command: `{' '.join(metadata['command_line'])}`", "", f"Clingo version: `{metadata['clingo_version'].strip()}`", "", f"Host metadata: `{json.dumps(metadata['host'], sort_keys=True)}`", "", f"Git HEAD: `{metadata['git_head']}`", "", f"Dirty worktree state: `{metadata['dirty_worktree_state']}`", "", f"Relevant hashes: `{json.dumps(metadata['relevant_hashes'], sort_keys=True)}`", "", "## Worker Calculation", "", f"Host logical CPUs: {metadata['host']['cpu_count']}; reserved for OS: 2; outer workers: {OVERNIGHT_WORKERS}; clingo threads per branch: 1; internal clingo parallel mode: none; GPU use: none.", "", "## Scheduling Policy", "", "Dynamic worker-pool scheduling. Dispatch one branch from each nonempty operational workload class in round-robin order. When a worker becomes free, dispatch the next branch from the next nonempty class. Within a class, branches are sorted by census matching count and stable branch ID. Exhausted classes are skipped. No artificial waves are imposed.", "", "## Selection Certificate", "", f"49 screening UNSAT excluded: {certificate['screening_unsat_excluded_count'] == 49}.", "", f"26 screening TIMEOUT selected: {certificate['screening_timeout_selected_count'] == 26}.", "", f"Each selected branch belongs to exactly one class: {certificate['every_selected_branch_belongs_to_exactly_one_class']}.", "", "## Status Table", "", "| queue | workload class | parent | census | branch | status | runtime s | peak RSS KB |", "| ---: | --- | --- | ---: | --- | --- | ---: | ---: |"]
    by_branch = {result.branch_id: result for result in results}
    for job in jobs:
        result = by_branch.get(job.definition.branch_id)
        lines.append(f"| {job.queue_position} | {job.workload_class} | {job.definition.parent_branch_id} | {job.definition.category_matching_count} | `{job.definition.branch_id}` | {result.status if result else ''} | {_fmt_runtime(result.runtime_seconds) if result else ''} | {result.peak_rss_kb if result and result.peak_rss_kb is not None else ''} |")
    lines.extend(["", "## Status Counts", "", "| status | count |", "| --- | ---: |"])
    for status in ("SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"):
        lines.append(f"| {status} | {counts.get(status, 0)} |")
    lines.extend(["", "## Runtime And RSS Summary", "", f"Runtime seconds: `{_summary(runtimes)}`", "", f"Peak RSS KB: `{_summary(rss_values)}`", "", "## Remaining Timeout Branches", "", "| workload class | branch | runtime s |", "| --- | --- | ---: |"])
    timeouts = [result for result in results if result.status == "TIMEOUT"]
    if timeouts:
        for result in timeouts:
            lines.append(f"| {result.workload_class} | `{result.branch_id}` | {_fmt_runtime(result.runtime_seconds)} |")
    else:
        lines.append("|  | No timeout branches. |  |")
    lines.extend(["", "## Tail-Partition Coverage Accounting", "", "| category | count |", "| --- | ---: |", "| branches closed in screening | 49 |", f"| branches newly closed overnight | {newly_closed} |", f"| remaining timeout/error/cancelled branches | {remaining} |", "", "## Outcome", "", outcome, "", f"Stop reason: `{stop_reason or 'completed_all_jobs'}`."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _overnight_outcome(run_dir: Path, results: list[OvernightResult]) -> str:
    counts = Counter(result.status for result in results)
    if counts.get("SAT", 0) and any(result.status == "SAT" and result.verifier_ok for result in results):
        return "V49_DEPTH6_SAT_VERIFIED"
    if len(results) == 26 and counts.get("UNSAT", 0) == 26:
        audit = _run_post_unsat_audits(run_dir)
        if audit.get("tail_children_all_closed") and audit.get("closure_audit_returncode") == 0:
            return "V49_DEPTH6_UNSAT_COVERAGE_COMPLETE"
    return "V49_DEPTH6_INCONCLUSIVE"


def _run_post_unsat_audits(run_dir: Path) -> dict[str, Any]:
    audit_path = run_dir / "post_unsat_audit.json"
    closure = subprocess.run([sys.executable, "-m", "src.v49_d6_closure_audit"], check=False, capture_output=True, text=True)
    census_count = len(branch_definitions())
    payload = {"closure_audit_returncode": closure.returncode, "closure_audit_stdout": closure.stdout, "closure_audit_stderr": closure.stderr, "tail_child_count": census_count, "tail_children_all_closed": census_count == 75}
    audit_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _summary(values: list[float | int]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {"count": len(values), "min": min(values), "max": max(values), "mean": sum(values) / len(values)}


def _overnight_metadata(output_dir: Path, run_dir: Path) -> dict[str, Any]:
    return {"command_line": overnight_command(output_dir), "run_dir": str(run_dir), "clingo_version": solver_version(), "host": {**_environment_metadata(), "node": platform.node()}, "git_head": _git(["rev-parse", "HEAD"]), "dirty_worktree_state": _git_dirty_state(), "timeout_seconds": OVERNIGHT_TIMEOUT_SECONDS, "workers": OVERNIGHT_WORKERS, "reserved_logical_cpus": 2, "clingo_threads_per_branch": 1, "internal_clingo_parallel_mode": "none", "topology_pruning": True, "seed": SEED, "relevant_hashes": _relevant_hashes()}


def _relevant_hashes(*extra_paths: Path) -> dict[str, str | None]:
    paths = [Path("src/run_v49_d6_tail_partitioned.py"), Path("src/v49_d6_topology_pruning.py"), Path("src/verify.py"), COMMON, TARGET_V, VALIDATION_JSON, *extra_paths]
    return {str(path): _sha256(path) for path in paths}


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_partition_plan(path: Path, definitions: list[TailBranchDefinition]) -> None:
    validation = "PASSED" if topology_pruning_validated() else "NOT_PASSED"
    nproc = os.cpu_count() or 1
    lines = [
        "# V(4,9), Depth-6 Tail Partition Plan",
        "",
        f"Phase-1 topology-pruning validation: `{validation}`.",
        "",
        "## Child Categories",
        "",
        "| parent | child category | matching count | branch id |",
        "| --- | --- | ---: | --- |",
    ]
    for definition in definitions:
        lines.append(f"| {definition.parent_branch_id} | {definition.category} | {definition.category_matching_count} | `{definition.branch_id}` |")
    lines.extend(
        [
            "",
            f"Total solver branches: {len(definitions)}.",
            "",
            "## Proposed Pilot Scheduling",
            "",
            f"Thor logical CPUs observed by Python: {nproc}. A conservative pilot plan is 6 workers, one clingo thread per worker, with the existing per-branch timeout policy chosen by the operator.",
            "",
            "## Recommendation",
            "",
            "pilot all categories directly. Do not merge categories without a proved transformation preserving V-type output positions.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("census", "pilot", "longrun", "screening", "overnight"), default="census")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--clingo-threads", type=int, default=1)
    parser.add_argument("--enable-topology-pruning", action="store_true")
    args = parser.parse_args()
    if args.mode == "census":
        definitions = materialize(args.output_dir, enable_topology_pruning=args.enable_topology_pruning)
        print(f"materialized {len(definitions)} branches")
        print(args.output_dir / "reports" / "partition_plan.md")
        return
    if args.mode == "screening":
        if not args.enable_topology_pruning:
            raise SystemExit("screening mode requires --enable-topology-pruning")
        if args.timeout_seconds != DEFAULT_TIMEOUT_SECONDS or args.workers != 1 or args.clingo_threads != 1:
            print("screening mode ignores generic timeout/workers/thread flags and uses 18 outer workers, 1 clingo thread, 600s timeout", file=sys.stderr)
        results = run_screening(args.output_dir)
        counts = Counter(result.status for result in results)
        print("screening_report", args.output_dir / "reports" / "screening_report.md")
        print("screening_summary", args.output_dir / "reports" / "screening_summary.csv")
        print("screening_timeouts", args.output_dir / "reports" / "screening_timeouts.csv")
        print("counts", dict(sorted(counts.items())))
        for result in results:
            if result.status == "SAT" and result.verifier_ok:
                print("verified_sat_witness", result.network_path)
        return
    if args.mode == "overnight":
        if not args.enable_topology_pruning:
            raise SystemExit("overnight mode requires --enable-topology-pruning")
        if args.timeout_seconds != DEFAULT_TIMEOUT_SECONDS or args.workers != 1 or args.clingo_threads != 1:
            print("overnight mode ignores generic timeout/workers/thread flags and uses 18 outer workers, 1 clingo thread, 14400s timeout", file=sys.stderr)
        results = run_overnight(args.output_dir)
        counts = Counter(result.status for result in results)
        print("counts", dict(sorted(counts.items())))
        for result in results:
            if result.status == "SAT" and result.verifier_ok:
                print("verified_sat_witness", result.network_path)
        return
    results = run_solver_branches(
        output_dir=args.output_dir,
        timeout_seconds=args.timeout_seconds,
        workers=args.workers,
        clingo_threads=args.clingo_threads,
        enable_topology_pruning=args.enable_topology_pruning,
    )
    for result in results:
        print(result.branch_id, result.status, f"{result.runtime_seconds:.3f}s")


if __name__ == "__main__":
    main()
