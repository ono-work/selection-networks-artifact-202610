"""L5-cardinality partition runner for open V(4,9), depth-6 residual leaves."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.network import Comparator, Network, validate_network
from src.parse_model import network_to_json, parse_selected_network
from src.run_v49_d6_six_leaf_reduced import (
    DEPTH,
    N,
    T,
    V_BOUNDARY_VALIDATED,
    _environment_metadata,
    _process_snapshot,
    _read_metadata_solver_version,
    _stats_summary,
    generate_branch_instance as generate_residual_instance,
)
from src.solver import CLINGO_COMMAND
from src.experiment import COMMON, TARGET_V, solver_version
from src.verify import verify_binary
from src.v49_d6_closure_audit import EXPECTED_OPEN_RESIDUALS
from src.analyze_v49_d6_six_leaf_reductions import LEAVES

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_l5_partitioned"
PILOT_TIMEOUT_SECONDS = 1800
L5_COUNTS = (1, 2, 3, 4)

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class L5BranchDefinition:
    branch_id: str
    residual_id: str
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    forbid_l5: tuple[Comparator, ...]
    l5_count: int
    constraints: str


@dataclass(frozen=True)
class L5BranchResult:
    branch_id: str
    residual_id: str
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    forbid_l5: tuple[Comparator, ...]
    l5_count: int
    status: BranchStatus
    pid: int | None
    command: list[str]
    solver_options: list[str]
    solver_version: str
    runtime_seconds: float
    timeout_seconds: int | None
    worker_count: int
    input_mode: str
    instance_path: str
    raw_solver_json_path: str
    parsed_status_path: str
    metadata_path: str
    resource_log_path: str
    branch_definition_path: str
    peak_rss_kb: int | None
    cpu_snapshots: int
    clingo_result: str | None
    solver_statistics: dict[str, Any] | None
    network_json_path: str | None
    verifier_json_path: str | None
    verifier_ok: bool | None
    comparator_count: int | None
    layer_comparator_counts: list[int] | None
    error_message: str | None = None


def l5_count_constraint(count: int) -> str:
    if count not in L5_COUNTS:
        raise ValueError("L5 count must be 1, 2, 3, or 4")
    return f":- {count} != #count {{ I,J : selected(5,I,J) }}.\n"


def branch_definitions() -> list[L5BranchDefinition]:
    definitions: list[L5BranchDefinition] = []
    for residual_id in EXPECTED_OPEN_RESIDUALS:
        leaf_id = residual_id.removesuffix("_residual")
        leaf = LEAVES[leaf_id]
        for count in L5_COUNTS:
            definitions.append(
                L5BranchDefinition(
                    branch_id=f"{residual_id}_L5eq{count}",
                    residual_id=residual_id,
                    leaf_id=leaf_id,
                    final_layer=leaf.final_layer,
                    forbid_l5=leaf.residual_forbid_l5,
                    l5_count=count,
                    constraints=l5_count_constraint(count),
                )
            )
    return definitions


def generate_branch_instance(
    final_layer: tuple[Comparator, ...],
    forbid_l5: tuple[Comparator, ...],
    l5_count: int,
    *,
    input_mode: str = "v_boundary",
    v_boundary_validated: bool = V_BOUNDARY_VALIDATED,
) -> str:
    return (
        generate_residual_instance(
            final_layer,
            forbid_l5,
            input_mode=input_mode,
            v_boundary_validated=v_boundary_validated,
        )
        + "\n"
        + l5_count_constraint(l5_count)
    )


def branch_for_network(network: Network) -> str | None:
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    final = tuple(sorted(network[-1]))
    l5 = set(network[-2])
    count = len(network[-2])
    for definition in branch_definitions():
        if (
            tuple(sorted(definition.final_layer)) == final
            and set(definition.forbid_l5).isdisjoint(l5)
            and definition.l5_count == count
        ):
            return definition.branch_id
    return None


def default_worker_count() -> int:
    return min(6, max(1, os.cpu_count() or 1))


def run_partitioned(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int = PILOT_TIMEOUT_SECONDS,
    workers: int | None = None,
    clingo_threads_per_branch: int = 1,
) -> list[L5BranchResult]:
    if clingo_threads_per_branch != 1:
        raise ValueError("L5 partition uses one clingo thread per branch")
    worker_count = default_worker_count() if workers is None else workers
    if worker_count < 1 or worker_count > 6:
        raise ValueError("workers must be in 1..6")
    _ensure_layout(output_dir)
    version = solver_version()
    pending = branch_definitions()
    active: list[RunningBranch] = []
    results: list[L5BranchResult] = []
    while pending or active:
        while pending and len(active) < worker_count:
            active.append(_start_branch(pending.pop(0), output_dir, timeout_seconds, version, worker_count))
        time.sleep(1.0)
        next_active: list[RunningBranch] = []
        for running in active:
            running.sample_resources()
            if running.process.poll() is None:
                if running.elapsed() >= timeout_seconds:
                    running.terminate_for_timeout()
                next_active.append(running)
            else:
                results.append(_finalize_branch(running))
        active = []
        for running in next_active:
            if running.process.poll() is None:
                active.append(running)
            else:
                results.append(_finalize_branch(running))
    order = {definition.branch_id: index for index, definition in enumerate(branch_definitions())}
    results.sort(key=lambda result: order[result.branch_id])
    _write_summary(output_dir / "reports" / "summary.csv", results)
    _write_pilot_json(output_dir / "pilot" / "results.json", results, timeout_seconds, worker_count)
    return results


class RunningBranch:
    def __init__(
        self,
        definition: L5BranchDefinition,
        branch_dir: Path,
        command: list[str],
        solver_options: list[str],
        process: subprocess.Popen[str],
        started_at: float,
        timeout_seconds: int,
        resource_log_path: Path,
        worker_count: int,
    ) -> None:
        self.definition = definition
        self.branch_dir = branch_dir
        self.command = command
        self.solver_options = solver_options
        self.process = process
        self.started_at = started_at
        self.timeout_seconds = timeout_seconds
        self.resource_log_path = resource_log_path
        self.worker_count = worker_count
        self.peak_rss_kb: int | None = None
        self.cpu_snapshots = 0
        self.timed_out = False

    def elapsed(self) -> float:
        return time.perf_counter() - self.started_at

    def sample_resources(self) -> None:
        snapshot = _process_snapshot(self.process.pid)
        if snapshot is None:
            return
        rss = snapshot.get("rss_kb")
        if isinstance(rss, int):
            self.peak_rss_kb = rss if self.peak_rss_kb is None else max(self.peak_rss_kb, rss)
        self.cpu_snapshots += 1
        with self.resource_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"elapsed_seconds": self.elapsed(), **snapshot}, sort_keys=True) + "\n")

    def terminate_for_timeout(self) -> None:
        self.timed_out = True
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def _start_branch(
    definition: L5BranchDefinition,
    output_dir: Path,
    timeout_seconds: int,
    version: str,
    worker_count: int,
) -> RunningBranch:
    branch_dir = output_dir / "branches" / definition.branch_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    instance_path = branch_dir / "instance.lp"
    raw_solver_path = branch_dir / "solver.json"
    branch_definition_path = branch_dir / "branch_definition.json"
    metadata_path = branch_dir / "reproducibility.json"
    stderr_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    instance_path.write_text(generate_branch_instance(definition.final_layer, definition.forbid_l5, definition.l5_count), encoding="utf-8")
    resource_log_path.write_text("", encoding="utf-8")
    branch_definition_path.write_text(json.dumps(asdict(definition), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    solver_options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={timeout_seconds}"]
    command = [*CLINGO_COMMAND, *solver_options, str(COMMON), str(TARGET_V), str(instance_path)]
    raw_handle = raw_solver_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=raw_handle, stderr=stderr_handle, text=True)
    raw_handle.close()
    stderr_handle.close()
    metadata = {
        "branch": asdict(definition),
        "pid": process.pid,
        "command": command,
        "solver_options": solver_options,
        "solver_version": version,
        "input_mode": "v_boundary",
        "worker_count": worker_count,
        "environment": _environment_metadata(),
        "started_at_unix": time.time(),
        "paths": {
            "branch_definition": str(branch_definition_path),
            "instance": str(instance_path),
            "raw_solver_json": str(raw_solver_path),
            "stderr": str(stderr_path),
            "resource_log": str(resource_log_path),
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return RunningBranch(definition, branch_dir, [str(part) for part in command], solver_options, process, time.perf_counter(), timeout_seconds, resource_log_path, worker_count)


def _finalize_branch(running: RunningBranch) -> L5BranchResult:
    branch_dir = running.branch_dir
    raw_solver_path = branch_dir / "solver.json"
    parsed_status_path = branch_dir / "parsed_status.json"
    metadata_path = branch_dir / "reproducibility.json"
    network_path = branch_dir / "network.json"
    verifier_path = branch_dir / "verifier.json"
    stdout = raw_solver_path.read_text(encoding="utf-8") if raw_solver_path.exists() else ""
    runtime = running.elapsed()
    clingo_result: str | None = None
    solver_statistics: dict[str, Any] | None = None
    network_json_path: str | None = None
    verifier_json_path: str | None = None
    verifier_ok: bool | None = None
    comparator_count: int | None = None
    layer_counts: list[int] | None = None
    error_message: str | None = None
    try:
        payload: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
        raw_result = payload.get("Result")
        clingo_result = raw_result if isinstance(raw_result, str) else None
        stats = payload.get("Stats")
        solver_statistics = stats if isinstance(stats, dict) else None
        if running.timed_out or clingo_result == "UNKNOWN":
            status: BranchStatus = "TIMEOUT"
        elif clingo_result == "SATISFIABLE":
            network = parse_selected_network(stdout, n=N, depth=DEPTH)
            layer_counts = [len(layer) for layer in network]
            comparator_count = sum(layer_counts)
            network_path.write_text(json.dumps(network_to_json(network, n=N, t=T, kind="V"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            network_json_path = str(network_path)
            verifier = verify_binary(network, n=N, t=T, kind="V")
            verifier_path.write_text(json.dumps(asdict(verifier), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            verifier_json_path = str(verifier_path)
            verifier_ok = verifier.ok
            status = "SAT" if verifier.ok else "VERIFICATION_FAILED"
            if not verifier.ok:
                error_message = verifier.message
        elif clingo_result == "UNSATISFIABLE":
            status = "UNSAT"
        else:
            status = "ERROR"
            error_message = f"unexpected clingo result {clingo_result!r}"
    except Exception as exc:  # noqa: BLE001
        status = "TIMEOUT" if running.timed_out else "ERROR"
        error_message = None if running.timed_out else str(exc)
    result = L5BranchResult(
        branch_id=running.definition.branch_id,
        residual_id=running.definition.residual_id,
        leaf_id=running.definition.leaf_id,
        final_layer=running.definition.final_layer,
        forbid_l5=running.definition.forbid_l5,
        l5_count=running.definition.l5_count,
        status=status,
        pid=running.process.pid,
        command=running.command,
        solver_options=running.solver_options,
        solver_version=_read_metadata_solver_version(metadata_path),
        runtime_seconds=runtime,
        timeout_seconds=running.timeout_seconds,
        worker_count=running.worker_count,
        input_mode="v_boundary",
        instance_path=str(branch_dir / "instance.lp"),
        raw_solver_json_path=str(raw_solver_path),
        parsed_status_path=str(parsed_status_path),
        metadata_path=str(metadata_path),
        resource_log_path=str(running.resource_log_path),
        branch_definition_path=str(branch_dir / "branch_definition.json"),
        peak_rss_kb=running.peak_rss_kb,
        cpu_snapshots=running.cpu_snapshots,
        clingo_result=clingo_result,
        solver_statistics=solver_statistics,
        network_json_path=network_json_path,
        verifier_json_path=verifier_json_path,
        verifier_ok=verifier_ok,
        comparator_count=comparator_count,
        layer_comparator_counts=layer_counts,
        error_message=error_message,
    )
    parsed_status_path.write_text(json.dumps({"branch_id": result.branch_id, "status": result.status, "clingo_result": result.clingo_result, "runtime_seconds": result.runtime_seconds, "timeout_seconds": result.timeout_seconds, "worker_count": result.worker_count, "peak_rss_kb": result.peak_rss_kb, "cpu_snapshots": result.cpu_snapshots, "returncode": running.process.returncode, "error_message": result.error_message}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _write_summary(path: Path, results: list[L5BranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _write_pilot_json(path: Path, results: list[L5BranchResult], timeout_seconds: int, worker_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mode": "pilot", "timeout_seconds": timeout_seconds, "worker_count": worker_count, "input_mode": "v_boundary", "branches": [asdict(result) for result in results]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ensure_layout(output_dir: Path) -> None:
    for relative in ("branches", "logs", "reports", "pilot"):
        path = output_dir / relative
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", choices=("pilot", "full"), default="pilot")
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--clingo-threads-per-branch", type=int, default=1)
    args = parser.parse_args()
    if args.mode != "pilot":
        parser.error("only pilot mode is enabled; do not start longer runs automatically")
    timeout = PILOT_TIMEOUT_SECONDS if args.timeout_seconds is None else args.timeout_seconds
    results = run_partitioned(output_dir=args.output_dir, timeout_seconds=timeout, workers=args.workers, clingo_threads_per_branch=args.clingo_threads_per_branch)
    for result in results:
        print(f"{result.branch_id}: {result.status} in {result.runtime_seconds:.3f}s")


if __name__ == "__main__":
    main()
