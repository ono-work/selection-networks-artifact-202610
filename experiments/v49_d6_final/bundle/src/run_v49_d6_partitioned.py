"""Partitioned runner for the V(4,9), depth-6 hard instance.

This module keeps the baseline ASP files unchanged.  Each branch adds only the
hard-instance nonempty-layer restriction plus one final-layer cardinality
constraint.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.experiment import COMMON, TARGET_V, solver_version
from src.generate_instance import generate_instance
from src.network import Network, validate_network
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

N = 9
T = 4
DEPTH = 6
BRANCH_FINAL_LAYER_COUNTS = (1, 2, 3, 4)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_partitioned"

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class BranchDefinition:
    """One exhaustive branch in the final-layer-size partition."""

    branch_id: str
    final_layer_comparator_count: int
    constraint: str


@dataclass(frozen=True)
class BranchResult:
    """Persisted result for one partition branch."""

    branch_id: str
    final_layer_comparator_count: int
    status: BranchStatus
    pid: int | None
    command: list[str]
    solver_options: list[str]
    solver_version: str
    runtime_seconds: float
    timeout_seconds: int | None
    instance_path: str
    raw_solver_json_path: str
    parsed_status_path: str
    metadata_path: str
    resource_log_path: str
    peak_rss_kb: int | None
    cpu_snapshots: int
    externally_interrupted: bool
    solver_statistics: dict[str, Any] | None
    network_json_path: str | None
    verifier_json_path: str | None
    verifier_ok: bool | None
    comparator_count: int | None
    layer_comparator_counts: list[int] | None
    error_message: str | None = None


def branch_definitions() -> list[BranchDefinition]:
    """Return the four disjoint final-layer-size branch definitions."""
    return [
        BranchDefinition(
            branch_id=f"L6_eq_{count}",
            final_layer_comparator_count=count,
            constraint=final_layer_size_constraint(count),
        )
        for count in BRANCH_FINAL_LAYER_COUNTS
    ]


def final_layer_size_constraint(count: int) -> str:
    """Return the single branch constraint for ``|L6| = count``."""
    _validate_branch_count(count)
    return (
        f":- depth(D), {count} != #count {{ I,J : selected(D,I,J) }}.\n"
    )


def all_layers_nonempty_constraint() -> str:
    """Return the shared hard-instance constraint requiring every layer active."""
    return ":- layer(L), not active(L).\n"


def hard_instance_constraints(final_layer_count: int) -> str:
    """Return all additive constraints for one hard-instance branch."""
    return (
        "% V(4,9), depth-6 hard-instance additive constraints.\n"
        "% Baseline solver/common.lp and solver/target_v.lp are not modified.\n"
        f"{all_layers_nonempty_constraint()}"
        f"{final_layer_size_constraint(final_layer_count)}"
    )


def generate_branch_instance(final_layer_count: int) -> str:
    """Return full 2^9 input facts plus additive constraints for one branch."""
    return generate_instance(N, T, DEPTH) + "\n" + hard_instance_constraints(final_layer_count)


def branch_for_network(network: Network) -> int | None:
    """Return the branch count containing a valid all-nonempty depth-6 network."""
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    final_count = len(network[-1])
    if final_count in BRANCH_FINAL_LAYER_COUNTS:
        return final_count
    return None


def run_partitioned(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int | None = None,
    outer_parallelism: int = 4,
    clingo_threads_per_branch: int = 1,
) -> list[BranchResult]:
    """Run all four branches, with at most ``outer_parallelism`` child processes."""
    if outer_parallelism < 1:
        raise ValueError("outer_parallelism must be positive")
    if clingo_threads_per_branch != 1:
        raise ValueError("initial hard-instance mode uses one clingo thread per branch")
    _ensure_layout(output_dir)

    version = solver_version()
    results: list[BranchResult] = []
    definitions = branch_definitions()
    pending = list(definitions)
    active: list[RunningBranch] = []

    while pending or active:
        while pending and len(active) < outer_parallelism:
            active.append(_start_branch(pending.pop(0), output_dir, timeout_seconds, version))

        time.sleep(1.0)
        still_active: list[RunningBranch] = []
        for running in active:
            running.sample_resources()
            if running.process.poll() is None:
                if timeout_seconds is not None and running.elapsed() >= timeout_seconds:
                    running.terminate_for_timeout()
                still_active.append(running)
                continue
            results.append(_finalize_branch(running, timed_out=running.timed_out))
        active = []
        for running in still_active:
            if running.process.poll() is None:
                active.append(running)
            else:
                results.append(_finalize_branch(running, timed_out=running.timed_out))

    results.sort(key=lambda item: item.final_layer_comparator_count)
    _write_summary(output_dir / "reports" / "summary.csv", results)
    write_pilot_report(output_dir / "reports" / "pilot_report.md", results)
    return results


class RunningBranch:
    """State for one live clingo process."""

    def __init__(
        self,
        definition: BranchDefinition,
        branch_dir: Path,
        command: list[str],
        process: subprocess.Popen[str],
        started_at: float,
        timeout_seconds: int | None,
        resource_log_path: Path,
    ) -> None:
        self.definition = definition
        self.branch_dir = branch_dir
        self.command = command
        self.process = process
        self.started_at = started_at
        self.timeout_seconds = timeout_seconds
        self.resource_log_path = resource_log_path
        self.peak_rss_kb: int | None = None
        self.cpu_snapshots = 0
        self.timed_out = False
        self.externally_interrupted = False

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
    definition: BranchDefinition,
    output_dir: Path,
    timeout_seconds: int | None,
    version: str,
) -> RunningBranch:
    branch_dir = output_dir / "branches" / definition.branch_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    instance_path = branch_dir / "instance.lp"
    raw_solver_path = branch_dir / "solver.json"
    stderr_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    metadata_path = branch_dir / "reproducibility.json"

    instance_path.write_text(
        generate_branch_instance(definition.final_layer_comparator_count),
        encoding="utf-8",
    )
    resource_log_path.write_text("", encoding="utf-8")

    solver_options = ["--outf=2", "--stats=2", "-n", "1"]
    if timeout_seconds is not None:
        solver_options.append(f"--time-limit={timeout_seconds}")
    command = [
        *CLINGO_COMMAND,
        *solver_options,
        str(COMMON),
        str(TARGET_V),
        str(instance_path),
    ]

    raw_handle = raw_solver_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        stdout=raw_handle,
        stderr=stderr_handle,
        text=True,
    )
    raw_handle.close()
    stderr_handle.close()

    metadata = {
        "branch": asdict(definition),
        "pid": process.pid,
        "command": command,
        "solver_options": solver_options,
        "solver_version": version,
        "environment": _environment_metadata(),
        "started_at_unix": time.time(),
        "paths": {
            "instance": str(instance_path),
            "raw_solver_json": str(raw_solver_path),
            "stderr": str(stderr_path),
            "resource_log": str(resource_log_path),
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return RunningBranch(
        definition=definition,
        branch_dir=branch_dir,
        command=[str(part) for part in command],
        process=process,
        started_at=time.perf_counter(),
        timeout_seconds=timeout_seconds,
        resource_log_path=resource_log_path,
    )


def _finalize_branch(running: RunningBranch, *, timed_out: bool) -> BranchResult:
    runtime = running.elapsed()
    branch_dir = running.branch_dir
    raw_solver_path = branch_dir / "solver.json"
    parsed_status_path = branch_dir / "parsed_status.json"
    metadata_path = branch_dir / "reproducibility.json"
    network_path = branch_dir / "network.json"
    verifier_path = branch_dir / "verifier.json"

    stdout = raw_solver_path.read_text(encoding="utf-8") if raw_solver_path.exists() else ""
    status: BranchStatus
    solver_statistics: dict[str, Any] | None = None
    network_json_path: str | None = None
    verifier_json_path: str | None = None
    verifier_ok: bool | None = None
    comparator_count: int | None = None
    layer_counts: list[int] | None = None
    error_message: str | None = None

    try:
        payload: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
        solver_statistics = payload.get("Stats") if isinstance(payload.get("Stats"), dict) else None
        result = payload.get("Result")
        if timed_out or result == "UNKNOWN":
            status = "TIMEOUT"
        elif result == "SATISFIABLE":
            network = parse_selected_network(stdout, n=N, depth=DEPTH)
            layer_counts = [len(layer) for layer in network]
            comparator_count = sum(layer_counts)
            network_payload = network_to_json(network, n=N, t=T, kind="V")
            network_path.write_text(
                json.dumps(network_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            network_json_path = str(network_path)
            verifier = verify_binary(network, n=N, t=T, kind="V")
            verifier_path.write_text(
                json.dumps(asdict(verifier), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            verifier_json_path = str(verifier_path)
            verifier_ok = verifier.ok
            status = "SAT" if verifier.ok else "VERIFICATION_FAILED"
            if not verifier.ok:
                error_message = verifier.message
        elif result == "UNSATISFIABLE":
            status = "UNSAT"
        else:
            status = "ERROR"
            error_message = f"unexpected clingo result {result!r}"
    except Exception as exc:  # noqa: BLE001 - this is persisted experiment metadata
        status = "TIMEOUT" if timed_out else "ERROR"
        error_message = None if timed_out else str(exc)

    externally_interrupted = (
        not timed_out
        and running.process.returncode is not None
        and running.process.returncode < 0
        and running.process.returncode not in {-signal.SIGTERM, -signal.SIGKILL}
    )
    result_payload = {
        "branch_id": running.definition.branch_id,
        "final_layer_comparator_count": running.definition.final_layer_comparator_count,
        "status": status,
        "clingo_result": _safe_json_result(stdout),
        "runtime_seconds": runtime,
        "timeout_seconds": running.timeout_seconds,
        "returncode": running.process.returncode,
        "peak_rss_kb": running.peak_rss_kb,
        "cpu_snapshots": running.cpu_snapshots,
        "externally_interrupted": externally_interrupted,
        "error_message": error_message,
    }
    parsed_status_path.write_text(
        json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = BranchResult(
        branch_id=running.definition.branch_id,
        final_layer_comparator_count=running.definition.final_layer_comparator_count,
        status=status,
        pid=running.process.pid,
        command=running.command,
        solver_options=_solver_options_from_command(running.command),
        solver_version=_read_metadata_solver_version(metadata_path),
        runtime_seconds=runtime,
        timeout_seconds=running.timeout_seconds,
        instance_path=str(branch_dir / "instance.lp"),
        raw_solver_json_path=str(raw_solver_path),
        parsed_status_path=str(parsed_status_path),
        metadata_path=str(metadata_path),
        resource_log_path=str(running.resource_log_path),
        peak_rss_kb=running.peak_rss_kb,
        cpu_snapshots=running.cpu_snapshots,
        externally_interrupted=externally_interrupted,
        solver_statistics=solver_statistics,
        network_json_path=network_json_path,
        verifier_json_path=verifier_json_path,
        verifier_ok=verifier_ok,
        comparator_count=comparator_count,
        layer_comparator_counts=layer_counts,
        error_message=error_message,
    )
    (branch_dir / "result.json").write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def write_pilot_report(path: Path, results: list[BranchResult]) -> None:
    """Write a Markdown pilot report for the current branch results."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V(4,9), Depth-6 Partitioned Pilot Report",
        "",
        "This report records partition-runner outcomes only. TIMEOUT rows are not lower-bound evidence.",
        "",
        "## Branch Definitions",
        "",
        "| branch | constraint | shared hard-mode constraint |",
        "| --- | --- | --- |",
    ]
    for definition in branch_definitions():
        constraint = definition.constraint.strip().replace("|", "\\|")
        lines.append(
            f"| {definition.branch_id} | `{constraint}` | `:- layer(L), not active(L).` |"
        )

    lines.extend(
        [
            "",
            "## Pilot Results",
            "",
            "| branch | status | runtime seconds | peak RSS KB | CPU snapshots | bound readout |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for result in results:
        lines.append(
            f"| {result.branch_id} | {result.status} | {result.runtime_seconds:.3f} | "
            f"{'' if result.peak_rss_kb is None else result.peak_rss_kb} | "
            f"{result.cpu_snapshots} | {_resource_readout(result)} |"
        )

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            _recommendation(results),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_existing_results(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[BranchResult]:
    """Load branch result artifacts from a previous run."""
    results: list[BranchResult] = []
    for definition in branch_definitions():
        path = output_dir / "branches" / definition.branch_id / "result.json"
        if path.exists():
            results.append(BranchResult(**json.loads(path.read_text(encoding="utf-8"))))
    return results


def _write_summary(path: Path, results: list[BranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _process_snapshot(pid: int) -> dict[str, Any] | None:
    try:
        completed = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid=,etime=,pcpu=,pmem=,rss=,vsz=,stat="],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    line = completed.stdout.strip()
    if completed.returncode != 0 or not line:
        return None
    parts = line.split()
    if len(parts) < 7:
        return {"raw_ps": line}
    return {
        "pid": int(parts[0]),
        "etime": parts[1],
        "cpu_percent": float(parts[2]),
        "mem_percent": float(parts[3]),
        "rss_kb": int(parts[4]),
        "vsz_kb": int(parts[5]),
        "stat": parts[6],
    }


def _safe_json_result(stdout: str) -> str | None:
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        return None
    result = payload.get("Result")
    return result if isinstance(result, str) else None


def _solver_options_from_command(command: list[str]) -> list[str]:
    return [part for part in command if part.startswith("-") or part == "1"]


def _read_metadata_solver_version(path: Path) -> str:
    try:
        return json.loads(path.read_text(encoding="utf-8"))["solver_version"]
    except Exception:  # noqa: BLE001
        return ""


def _resource_readout(result: BranchResult) -> str:
    if result.externally_interrupted:
        return "externally interrupted"
    if result.status == "TIMEOUT":
        return "CPU-bound candidate if CPU snapshots are sustained; timeout is not a bound"
    if result.peak_rss_kb is not None and result.peak_rss_kb > 8_000_000:
        return "memory-bound candidate"
    return "CPU-bound candidate"


def _recommendation(results: list[BranchResult]) -> str:
    if any(result.status == "SAT" for result in results):
        return "Recommendation: verify the SAT witness artifacts before changing runtime configuration."
    if any(result.status == "ERROR" for result in results):
        return "Recommendation: inspect branch errors before longer branch runs or encoding changes."
    if results and all(result.status == "TIMEOUT" for result in results):
        return "Recommendation: (a) longer branch runs first; consider (c) finer partitioning if runtimes remain uneven."
    if any(result.status == "TIMEOUT" for result in results):
        return "Recommendation: (a) longer branch runs for unresolved branches; defer internal clingo threads until branch imbalance is known."
    return "Recommendation: no longer run is implied by this pilot; inspect UNSAT/SAT artifacts first."


def _environment_metadata() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "cwd": str(ROOT),
        "gpu_use": "none",
        "internal_clingo_parallel_mode": "disabled",
    }


def _ensure_layout(output_dir: Path) -> None:
    for relative in ("branches", "logs", "reports", "pilot"):
        path = output_dir / relative
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _validate_branch_count(count: int) -> None:
    if count not in BRANCH_FINAL_LAYER_COUNTS:
        raise ValueError(f"final-layer comparator count must be one of {BRANCH_FINAL_LAYER_COUNTS}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", choices=("pilot", "full"))
    parser.add_argument("--pilot", action="store_true", help="run all branches with a 10-minute cap")
    parser.add_argument("--full", action="store_true", help="run all branches without a time cap")
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument("--outer-parallelism", type=int, default=4)
    parser.add_argument("--clingo-threads-per-branch", type=int, default=1)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    _ensure_layout(args.output_dir)
    if args.report_only:
        results = load_existing_results(args.output_dir)
        write_pilot_report(args.output_dir / "reports" / "pilot_report.md", results)
        print(args.output_dir / "reports" / "pilot_report.md")
        return

    if args.mode == "pilot":
        args.pilot = True
    elif args.mode == "full":
        args.full = True

    if args.pilot and args.full:
        parser.error("--pilot and --full are mutually exclusive")
    if not args.pilot and not args.full:
        parser.error("choose --pilot or --full")

    timeout = 600 if args.pilot else args.timeout_seconds
    results = run_partitioned(
        output_dir=args.output_dir,
        timeout_seconds=timeout,
        outer_parallelism=args.outer_parallelism,
        clingo_threads_per_branch=args.clingo_threads_per_branch,
    )
    for result in results:
        print(f"{result.branch_id}: {result.status} in {result.runtime_seconds:.3f}s")
    print(args.output_dir / "reports" / "pilot_report.md")


if __name__ == "__main__":
    main()
