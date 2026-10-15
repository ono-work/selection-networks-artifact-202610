"""Reduced six-leaf runner for the V(4,9), depth-6 hard instance."""

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

from src.analyze_v49_d6_six_leaf_reductions import LEAVES
from src.analyze_v49_d6_terminal_profiles import profiles
from src.experiment import COMMON, TARGET_V, solver_version
from src.generate_instance import generate_instance
from src.network import Comparator, Network, validate_network
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

N = 9
T = 4
DEPTH = 6
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_six_leaf_reduced"
PILOT_TIMEOUT_SECONDS = 1800
V_BOUNDARY_VALIDATED = True

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class ReducedBranchDefinition:
    branch_id: str
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    forbid_l5: tuple[Comparator, ...]
    constraints: str


@dataclass(frozen=True)
class ReducedBranchResult:
    branch_id: str
    leaf_id: str
    final_layer: tuple[Comparator, ...]
    forbid_l5: tuple[Comparator, ...]
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


def branch_definitions() -> list[ReducedBranchDefinition]:
    return [
        ReducedBranchDefinition(
            branch_id=f"{leaf_id}_residual",
            leaf_id=leaf_id,
            final_layer=leaf.final_layer,
            forbid_l5=leaf.residual_forbid_l5,
            constraints=reduced_branch_constraints(leaf.final_layer, leaf.residual_forbid_l5),
        )
        for leaf_id, leaf in LEAVES.items()
    ]


def all_layers_nonempty_constraint() -> str:
    return ":- layer(L), not active(L).\n"


def forbid_suffix_only_final_comparators_constraint() -> str:
    return ":- depth(D), selected(D,I,J), I >= 5, J >= 5.\n"


def final_layer_exact_constraints(final_layer: tuple[Comparator, ...]) -> str:
    lines = [f":- depth(D), {len(final_layer)} != #count {{ I,J : selected(D,I,J) }}."]
    lines.extend(f":- depth(D), not selected(D,{i},{j})." for i, j in final_layer)
    return "\n".join(lines) + "\n"


def forbid_l5_constraints(forbid_l5: tuple[Comparator, ...]) -> str:
    return "".join(f":- selected(5,{i},{j}).\n" for i, j in forbid_l5)


def reduced_branch_constraints(final_layer: tuple[Comparator, ...], forbid_l5: tuple[Comparator, ...]) -> str:
    return (
        "% V(4,9), depth-6 six-leaf reduced hard-instance constraints.\n"
        "% Baseline solver/common.lp and solver/target_v.lp are not modified.\n"
        f"{all_layers_nonempty_constraint()}"
        f"{forbid_suffix_only_final_comparators_constraint()}"
        f"{final_layer_exact_constraints(final_layer)}"
        f"{forbid_l5_constraints(forbid_l5)}"
    )


def generate_branch_instance(
    final_layer: tuple[Comparator, ...],
    forbid_l5: tuple[Comparator, ...],
    *,
    input_mode: str = "v_boundary",
    v_boundary_validated: bool = V_BOUNDARY_VALIDATED,
) -> str:
    if input_mode == "v_boundary" and not v_boundary_validated:
        raise RuntimeError("v_boundary input mode requires the existing validation guard to pass")
    return generate_instance(N, T, DEPTH, input_mode=input_mode) + "\n" + reduced_branch_constraints(final_layer, forbid_l5)


def branch_for_network(network: Network) -> str | None:
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    final = tuple(sorted(network[-1]))
    l5 = set(network[-2])
    for definition in branch_definitions():
        if tuple(sorted(definition.final_layer)) == final and set(definition.forbid_l5).isdisjoint(l5):
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
) -> list[ReducedBranchResult]:
    if clingo_threads_per_branch != 1:
        raise ValueError("six-leaf reduced pilot uses one clingo thread per branch")
    worker_count = default_worker_count() if workers is None else workers
    if worker_count < 1 or worker_count > 6:
        raise ValueError("workers must be in 1..6")
    _ensure_layout(output_dir)

    version = solver_version()
    pending = branch_definitions()
    active: list[RunningBranch] = []
    results: list[ReducedBranchResult] = []
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
    write_pilot_report(output_dir / "reports" / "pilot_report.md", results, worker_count)
    return results


class RunningBranch:
    def __init__(
        self,
        definition: ReducedBranchDefinition,
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
    definition: ReducedBranchDefinition,
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

    instance_path.write_text(generate_branch_instance(definition.final_layer, definition.forbid_l5), encoding="utf-8")
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
    return RunningBranch(
        definition=definition,
        branch_dir=branch_dir,
        command=[str(part) for part in command],
        solver_options=solver_options,
        process=process,
        started_at=time.perf_counter(),
        timeout_seconds=timeout_seconds,
        resource_log_path=resource_log_path,
        worker_count=worker_count,
    )


def _finalize_branch(running: RunningBranch) -> ReducedBranchResult:
    branch_dir = running.branch_dir
    raw_solver_path = branch_dir / "solver.json"
    parsed_status_path = branch_dir / "parsed_status.json"
    metadata_path = branch_dir / "reproducibility.json"
    branch_definition_path = branch_dir / "branch_definition.json"
    network_path = branch_dir / "network.json"
    verifier_path = branch_dir / "verifier.json"
    runtime = running.elapsed()
    stdout = raw_solver_path.read_text(encoding="utf-8") if raw_solver_path.exists() else ""

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
    result = ReducedBranchResult(
        branch_id=running.definition.branch_id,
        leaf_id=running.definition.leaf_id,
        final_layer=running.definition.final_layer,
        forbid_l5=running.definition.forbid_l5,
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
        branch_definition_path=str(branch_definition_path),
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
    parsed_status_path.write_text(json.dumps({
        "branch_id": result.branch_id,
        "leaf_id": result.leaf_id,
        "status": result.status,
        "clingo_result": result.clingo_result,
        "runtime_seconds": result.runtime_seconds,
        "timeout_seconds": result.timeout_seconds,
        "worker_count": result.worker_count,
        "peak_rss_kb": result.peak_rss_kb,
        "cpu_snapshots": result.cpu_snapshots,
        "returncode": running.process.returncode,
        "error_message": result.error_message,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def load_existing_results(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[ReducedBranchResult]:
    results: list[ReducedBranchResult] = []
    for definition in branch_definitions():
        path = output_dir / "branches" / definition.branch_id / "result.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["final_layer"] = tuple(tuple(item) for item in payload["final_layer"])
            payload["forbid_l5"] = tuple(tuple(item) for item in payload["forbid_l5"])
            results.append(ReducedBranchResult(**payload))
    return results


def write_pilot_report(path: Path, results: list[ReducedBranchResult], worker_count: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    result_by_branch = {result.branch_id: result for result in results}
    actual_worker_count = worker_count if worker_count is not None else (results[0].worker_count if results else default_worker_count())
    lines = [
        "# V(4,9), Depth-6 Six-Leaf Reduced Pilot Report",
        "",
        f"Actual worker count: {actual_worker_count}.",
        "",
        "## Terminal Profiles",
        "",
        "| leaf | final layer | profile clauses |",
        "| --- | --- | --- |",
    ]
    for profile in profiles():
        lines.append(f"| {profile.leaf} | {profile.final_layer} | {'; '.join(profile.clauses)} |")
    lines.extend([
        "",
        "## Redundancy Lemma",
        "",
        "If the same comparator e occurs in L5 and L6, the L6 copy is redundant: both layers are matchings, no intervening comparator touches its endpoints, and C_e composed with C_e equals C_e.",
        "",
        "## Reduction Table",
        "",
        "| residual | final layer | forbidden in L5 | coverage note |",
        "| --- | --- | --- | --- |",
    ])
    coverage_notes = {
        "A5_residual": "repeated (2,3) or (4,5) reduces to prior UNSAT T_4 or T_23",
        "A6_residual": "repeated (2,3) or (4,6) reduces to prior UNSAT T_4 or T_23",
        "B6_residual": "repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,6) reduces to A5",
        "B7_residual": "repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,7) reduces to A5",
        "B8_residual": "repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,8) reduces to A5",
        "B9_residual": "repeated (2,3)/(4,5) reduces to prior UNSAT T_14/T_123; repeated (1,9) reduces to A5",
    }
    for definition in branch_definitions():
        lines.append(f"| {definition.branch_id} | {definition.final_layer} | {definition.forbid_l5} | {coverage_notes[definition.branch_id]} |")
    lines.extend([
        "",
        "## Coverage Of Original Six Leaves",
        "",
        "The six residual branches are not a direct partition. A5/A6 omitted cases reduce to prior UNSAT support branches. Bs omitted cases with repeated (2,3) or (4,5) reduce to prior UNSAT support branches; omitted cases with repeated (1,s) reduce to A5. Therefore UNSAT for all six residual branches closes all six original leaves.",
        "",
        "## Branch Results",
        "",
        "| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ])
    for definition in branch_definitions():
        result = result_by_branch.get(definition.branch_id)
        if result is None:
            lines.append(f"| {definition.branch_id} | NOT_RUN |  |  |  |  |  |")
            continue
        verifier = "" if result.verifier_ok is None else ("OK" if result.verifier_ok else "FAILED")
        lines.append(f"| {result.branch_id} | {result.status} | {result.runtime_seconds:.3f} | {'' if result.peak_rss_kb is None else result.peak_rss_kb} | {result.cpu_snapshots} | {_stats_summary(result.solver_statistics)} | {verifier} |")
    sat = [result for result in results if result.status == "SAT"]
    lines.extend(["", "## SAT Witnesses", ""])
    if sat:
        for result in sat:
            lines.append(f"- {result.branch_id}: witness={result.network_json_path}; verifier={result.verifier_json_path}; verifier_ok={result.verifier_ok}")
    else:
        lines.append("None.")
    lines.extend(["", "## Conclusion", "", _conclusion(results), "", "## Recommendation", "", _recommendation(results)])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _conclusion(results: list[ReducedBranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        return "ERROR_OR_VERIFICATION_FAILURE"
    if any(result.status == "SAT" and result.verifier_ok for result in results):
        return "DEPTH_6_SAT_FOUND"
    if len(results) == len(branch_definitions()) and all(result.status == "UNSAT" for result in results):
        return "ALL_SIX_LEAF_REDUCTIONS_CLOSED"
    return "SIX_LEAF_REDUCED_PILOT_INCONCLUSIVE"


def _recommendation(results: list[ReducedBranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        failed = [result.branch_id for result in results if result.status in {"ERROR", "VERIFICATION_FAILED"}]
        return "independent SAT/CNF encoding check: " + ", ".join(failed)
    timed_out = [result for result in results if result.status == "TIMEOUT"]
    if timed_out:
        names = ", ".join(result.branch_id for result in sorted(timed_out, key=lambda r: (-r.runtime_seconds, r.branch_id)))
        return f"longer runs for named residual branches: {names}"
    missing = sorted({definition.branch_id for definition in branch_definitions()} - {result.branch_id for result in results})
    if missing:
        return "one exact layer-5 split for named residual branches: " + ", ".join(missing)
    return "independent SAT/CNF encoding check"


def _write_summary(path: Path, results: list[ReducedBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _write_pilot_json(path: Path, results: list[ReducedBranchResult], timeout_seconds: int, worker_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mode": "pilot", "timeout_seconds": timeout_seconds, "worker_count": worker_count, "input_mode": "v_boundary", "branches": [asdict(result) for result in results]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _process_snapshot(pid: int) -> dict[str, Any] | None:
    try:
        completed = subprocess.run(["ps", "-p", str(pid), "-o", "pid=,etime=,pcpu=,pmem=,rss=,vsz=,stat="], check=False, capture_output=True, text=True)
    except OSError:
        return None
    line = completed.stdout.strip()
    if completed.returncode != 0 or not line:
        return None
    parts = line.split()
    if len(parts) < 7:
        return {"raw_ps": line}
    return {"pid": int(parts[0]), "etime": parts[1], "cpu_percent": float(parts[2]), "mem_percent": float(parts[3]), "rss_kb": int(parts[4]), "vsz_kb": int(parts[5]), "stat": parts[6]}


def _read_metadata_solver_version(path: Path) -> str:
    try:
        return json.loads(path.read_text(encoding="utf-8"))["solver_version"]
    except Exception:  # noqa: BLE001
        return ""


def _stats_summary(stats: dict[str, Any] | None) -> str:
    if not stats:
        return ""
    summary = stats.get("Summary")
    if isinstance(summary, dict):
        parts = []
        for key in ("Times", "Models", "Conflicts", "Choices"):
            if key in summary:
                parts.append(f"{key}={summary[key]}")
        if parts:
            return "; ".join(parts)
    return "stats captured"


def _environment_metadata() -> dict[str, Any]:
    return {"python": platform.python_version(), "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(), "cpu_count": os.cpu_count(), "gpu_use": "none", "internal_clingo_parallel_mode": "disabled"}


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
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    _ensure_layout(args.output_dir)
    if args.report_only:
        results = load_existing_results(args.output_dir)
        write_pilot_report(args.output_dir / "reports" / "pilot_report.md", results)
        print(args.output_dir / "reports" / "pilot_report.md")
        return
    if args.mode != "pilot":
        parser.error("only pilot mode is enabled; do not start longer runs automatically")
    timeout = PILOT_TIMEOUT_SECONDS if args.timeout_seconds is None else args.timeout_seconds
    results = run_partitioned(output_dir=args.output_dir, timeout_seconds=timeout, workers=args.workers, clingo_threads_per_branch=args.clingo_threads_per_branch)
    for result in results:
        print(f"{result.branch_id}: {result.status} in {result.runtime_seconds:.3f}s")
    print(args.output_dir / "reports" / "pilot_report.md")


if __name__ == "__main__":
    main()
