"""Support-partitioned runner for the V(4,9), depth-6 hard instance.

This runner is special-purpose.  It does not modify the baseline ASP model; it
adds only optional boundary input facts and hard-instance constraints in the
generated branch instances.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Literal

from src.experiment import COMMON, TARGET_V, solver_version
from src.generate_instance import generate_instance
from src.network import Comparator, Layer, Network, validate_layer, validate_network
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

N = 9
T = 4
DEPTH = 6
OUTPUT_WIRES = frozenset(range(1, T + 1))
SUFFIX_WIRES = frozenset(range(T + 1, N + 1))
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_support_partitioned"
PILOT_TIMEOUT_SECONDS = 900

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class SupportBranchDefinition:
    branch_id: str
    support: tuple[int, ...]
    constraints: str


@dataclass(frozen=True)
class SupportBranchResult:
    branch_id: str
    support: tuple[int, ...]
    status: BranchStatus
    pid: int | None
    command: list[str]
    solver_options: list[str]
    solver_version: str
    runtime_seconds: float
    timeout_seconds: int | None
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


def support_subsets() -> list[tuple[int, ...]]:
    subsets: list[tuple[int, ...]] = []
    for size in range(1, T + 1):
        subsets.extend(combinations(range(1, T + 1), size))
    return subsets


def branch_definitions() -> list[SupportBranchDefinition]:
    return [
        SupportBranchDefinition(
            branch_id="T_" + "".join(str(wire) for wire in support),
            support=support,
            constraints=support_branch_constraints(support),
        )
        for support in support_subsets()
    ]


def all_layers_nonempty_constraint() -> str:
    return ":- layer(L), not active(L).\n"


def forbid_suffix_only_final_comparators_constraint() -> str:
    return ":- depth(D), selected(D,I,J), I >= 5, J >= 5.\n"


def support_branch_constraints(support: tuple[int, ...]) -> str:
    support_set = set(support)
    if not support_set or not support_set <= set(OUTPUT_WIRES):
        raise ValueError("support must be a nonempty subset of {1,2,3,4}")
    lines = [
        "% V(4,9), depth-6 support-partition hard-instance constraints.",
        "% Baseline solver/common.lp and solver/target_v.lp are not modified.",
        all_layers_nonempty_constraint().strip(),
        forbid_suffix_only_final_comparators_constraint().strip(),
    ]
    for wire in sorted(OUTPUT_WIRES):
        if wire in support_set:
            lines.append(f":- depth(D), not touched(D,{wire}).")
        else:
            lines.append(f":- depth(D), touched(D,{wire}).")
    return "\n".join(lines) + "\n"


def generate_branch_instance(support: tuple[int, ...], *, input_mode: str = "v_boundary") -> str:
    return generate_instance(N, T, DEPTH, input_mode=input_mode) + "\n" + support_branch_constraints(support)


def final_layer_prefix_support(layer: Layer) -> tuple[int, ...]:
    validate_layer(layer, N)
    touched: set[int] = set()
    for i, j in layer:
        if i in OUTPUT_WIRES:
            touched.add(i)
        if j in OUTPUT_WIRES:
            touched.add(j)
    return tuple(sorted(touched))


def final_layer_satisfies_normal_form(layer: Layer) -> bool:
    validate_layer(layer, N)
    return bool(final_layer_prefix_support(layer)) and all(
        not (i in SUFFIX_WIRES and j in SUFFIX_WIRES) for i, j in layer
    )


def branch_for_final_layer(layer: Layer) -> tuple[int, ...] | None:
    if not final_layer_satisfies_normal_form(layer):
        return None
    return final_layer_prefix_support(layer)


def branch_for_network(network: Network) -> tuple[int, ...] | None:
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    return branch_for_final_layer(network[-1])


def default_worker_count() -> int:
    return min(16, max(1, (os.cpu_count() or 1) - 2))


def run_partitioned(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int = PILOT_TIMEOUT_SECONDS,
    workers: int | None = None,
    clingo_threads_per_branch: int = 1,
) -> list[SupportBranchResult]:
    if clingo_threads_per_branch != 1:
        raise ValueError("support pilot uses one clingo thread per branch")
    worker_count = default_worker_count() if workers is None else workers
    if worker_count < 1:
        raise ValueError("workers must be positive")
    _ensure_layout(output_dir)

    version = solver_version()
    pending = branch_definitions()
    active: list[RunningBranch] = []
    results: list[SupportBranchResult] = []

    while pending or active:
        while pending and len(active) < worker_count:
            active.append(_start_branch(pending.pop(0), output_dir, timeout_seconds, version))
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

    results.sort(key=lambda result: (len(result.support), result.support))
    _write_summary(output_dir / "reports" / "summary.csv", results)
    _write_pilot_json(output_dir / "pilot" / "results.json", results)
    write_pilot_report(output_dir / "reports" / "pilot_report.md", results)
    return results


class RunningBranch:
    def __init__(
        self,
        definition: SupportBranchDefinition,
        branch_dir: Path,
        command: list[str],
        solver_options: list[str],
        process: subprocess.Popen[str],
        started_at: float,
        timeout_seconds: int,
        resource_log_path: Path,
    ) -> None:
        self.definition = definition
        self.branch_dir = branch_dir
        self.command = command
        self.solver_options = solver_options
        self.process = process
        self.started_at = started_at
        self.timeout_seconds = timeout_seconds
        self.resource_log_path = resource_log_path
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


def _start_branch(definition: SupportBranchDefinition, output_dir: Path, timeout_seconds: int, version: str) -> RunningBranch:
    branch_dir = output_dir / "branches" / definition.branch_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    instance_path = branch_dir / "instance.lp"
    raw_solver_path = branch_dir / "solver.json"
    branch_definition_path = branch_dir / "branch_definition.json"
    metadata_path = branch_dir / "reproducibility.json"
    stderr_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"

    instance_path.write_text(generate_branch_instance(definition.support), encoding="utf-8")
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
    )


def _finalize_branch(running: RunningBranch) -> SupportBranchResult:
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
            network_path.write_text(
                json.dumps(network_to_json(network, n=N, t=T, kind="V"), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
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
    except Exception as exc:  # noqa: BLE001 - experiment artifact captures failure
        status = "TIMEOUT" if running.timed_out else "ERROR"
        error_message = None if running.timed_out else str(exc)

    result = SupportBranchResult(
        branch_id=running.definition.branch_id,
        support=running.definition.support,
        status=status,
        pid=running.process.pid,
        command=running.command,
        solver_options=running.solver_options,
        solver_version=_read_metadata_solver_version(metadata_path),
        runtime_seconds=runtime,
        timeout_seconds=running.timeout_seconds,
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
    parsed_status_path.write_text(
        json.dumps(
            {
                "branch_id": result.branch_id,
                "support": result.support,
                "status": result.status,
                "clingo_result": result.clingo_result,
                "runtime_seconds": result.runtime_seconds,
                "timeout_seconds": result.timeout_seconds,
                "peak_rss_kb": result.peak_rss_kb,
                "cpu_snapshots": result.cpu_snapshots,
                "returncode": running.process.returncode,
                "error_message": result.error_message,
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def write_pilot_report(path: Path, results: list[SupportBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sat = [r for r in results if r.status == "SAT"]
    unsat = [r for r in results if r.status == "UNSAT"]
    timed_out = sorted([r for r in results if r.status == "TIMEOUT"], key=lambda r: (-r.runtime_seconds, r.branch_id))
    lines = [
        "# V(4,9), Depth-6 Support-Partitioned Pilot Report",
        "",
        "This report records pilot outcomes only. TIMEOUT rows are not lower-bound evidence.",
        "",
        "## Proof Summaries",
        "",
        "Boundary inputs: for V-type rank r, the target bit changes only between inputs with r-1 and r zeros. Comparator-network output bits are monotone Boolean functions, so checking the boundary layers with at most t zeros is equivalent to checking all binary inputs for V-type t-selection.",
        "",
        "Last-layer normal form: a final comparator wholly in wires 5..9 cannot affect output wires 1..4 and can be deleted. If deletion emptied layer 6, the network would have effective depth at most 5 while still solving V(3,9), contradicting the confirmed V(3,9)=6 fact. Therefore the special hard mode forbids suffix-only final comparators without excluding a depth-6 V(4,9) solution.",
        "",
        "## Branch Definitions",
        "",
        "| branch | T(L6) | exact constraints |",
        "| --- | --- | --- |",
    ]
    for definition in branch_definitions():
        constraints = "<br>".join(line.replace("|", "\\|") for line in definition.constraints.strip().splitlines() if line and not line.startswith("%"))
        lines.append(f"| {definition.branch_id} | {definition.support} | `{constraints}` |")

    lines.extend([
        "",
        "## Branch Results",
        "",
        "| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ])
    for result in results:
        lines.append(
            f"| {result.branch_id} | {result.status} | {result.runtime_seconds:.3f} | "
            f"{'' if result.peak_rss_kb is None else result.peak_rss_kb} | {result.cpu_snapshots} | {_stats_summary(result.solver_statistics)} |"
        )

    lines.extend([
        "",
        "## SAT Branches",
        "",
        ", ".join(r.branch_id for r in sat) if sat else "None.",
        "",
        "## UNSAT Branches",
        "",
        ", ".join(r.branch_id for r in unsat) if unsat else "None.",
        "",
        "## Timed-Out Branches Ranked",
        "",
        "| rank | branch | runtime seconds | peak RSS KB | statistics summary |",
        "| ---: | --- | ---: | ---: | --- |",
    ])
    for rank, result in enumerate(timed_out, start=1):
        lines.append(
            f"| {rank} | {result.branch_id} | {result.runtime_seconds:.3f} | "
            f"{'' if result.peak_rss_kb is None else result.peak_rss_kb} | {_stats_summary(result.solver_statistics)} |"
        )

    lines.extend(["", "## Recommendation", "", _recommendation(results)])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_existing_results(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[SupportBranchResult]:
    results: list[SupportBranchResult] = []
    for definition in branch_definitions():
        path = output_dir / "branches" / definition.branch_id / "result.json"
        if path.exists():
            results.append(SupportBranchResult(**json.loads(path.read_text(encoding="utf-8"))))
    return results


def _write_summary(path: Path, results: list[SupportBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _write_pilot_json(path: Path, results: list[SupportBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "pilot",
        "timeout_seconds": PILOT_TIMEOUT_SECONDS,
        "input_mode": "v_boundary",
        "branches": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _recommendation(results: list[SupportBranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        return "Recommendation: inspect failed branch artifacts before changing the partition."
    timed_out = [result for result in results if result.status == "TIMEOUT"]
    if timed_out:
        largest = ", ".join(result.branch_id for result in sorted(timed_out, key=lambda r: (-r.runtime_seconds, r.branch_id))[:5])
        return f"Recommendation: (b) refine specific timed-out branches by final-layer comparator count first, starting with {largest}; if still uneven, use (c) exact comparator incident to a designated output wire."
    if any(result.status == "SAT" for result in results):
        return "Recommendation: verify SAT artifacts independently before any longer run."
    return "Recommendation: all branches resolved in pilot; no longer automatic run is implied."


def _environment_metadata() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
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
    results = run_partitioned(
        output_dir=args.output_dir,
        timeout_seconds=timeout,
        workers=args.workers,
        clingo_threads_per_branch=args.clingo_threads_per_branch,
    )
    for result in results:
        print(f"{result.branch_id}: {result.status} in {result.runtime_seconds:.3f}s")
    print(args.output_dir / "reports" / "pilot_report.md")


if __name__ == "__main__":
    main()
