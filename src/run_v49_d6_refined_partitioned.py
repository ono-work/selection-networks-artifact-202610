"""Refined runner for the V(4,9), depth-6 hard instance.

This runner refines only the two timed-out support classes from the completed
support-partitioned pilot.  It adds generated branch constraints to fresh
instances and does not modify the baseline ASP model, verifier, ordinary
experiment driver, or prior experiment artifacts.
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
from src.network import Layer, Network, validate_layer, validate_network
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

N = 9
T = 4
DEPTH = 6
OUTPUT_WIRES = frozenset(range(1, T + 1))
SUFFIX_WIRES = frozenset(range(T + 1, N + 1))
SURVIVING_SUPPORTS = ((2, 3, 4), (1, 2, 3, 4))
REFINED_BRANCHES = (
    ((2, 3, 4), 2),
    ((2, 3, 4), 3),
    ((1, 2, 3, 4), 2),
    ((1, 2, 3, 4), 3),
    ((1, 2, 3, 4), 4),
)
PRIOR_SUPPORT_BRANCHES = (
    (1,),
    (2,),
    (3,),
    (4,),
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 3),
    (2, 4),
    (3, 4),
    (1, 2, 3),
    (1, 2, 4),
    (1, 3, 4),
)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_refined_partitioned"
PRIOR_SUPPORT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_support_partitioned"
PILOT_TIMEOUT_SECONDS = 1800
V_BOUNDARY_VALIDATED = True

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class RefinedBranchDefinition:
    branch_id: str
    support: tuple[int, ...]
    final_layer_comparator_count: int
    constraints: str


@dataclass(frozen=True)
class RefinedBranchResult:
    branch_id: str
    support: tuple[int, ...]
    final_layer_comparator_count: int
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


def branch_id_for(support: tuple[int, ...], final_layer_count: int) -> str:
    return "T_" + "".join(str(wire) for wire in support) + f"_L6_{final_layer_count}"


def branch_definitions() -> list[RefinedBranchDefinition]:
    return [
        RefinedBranchDefinition(
            branch_id=branch_id_for(support, count),
            support=support,
            final_layer_comparator_count=count,
            constraints=refined_branch_constraints(support, count),
        )
        for support, count in REFINED_BRANCHES
    ]


def all_layers_nonempty_constraint(*, hard_instance_mode: bool) -> str:
    if not hard_instance_mode:
        return ""
    return ":- layer(L), not active(L).\n"


def forbid_suffix_only_final_comparators_constraint() -> str:
    return ":- depth(D), selected(D,I,J), I >= 5, J >= 5.\n"


def final_layer_size_constraint(count: int) -> str:
    if count not in {2, 3, 4}:
        raise ValueError("refined final-layer count must be one of 2, 3, 4")
    return f":- depth(D), {count} != #count {{ I,J : selected(D,I,J) }}.\n"


def support_constraints(support: tuple[int, ...]) -> str:
    support_set = set(support)
    if support not in SURVIVING_SUPPORTS:
        raise ValueError("support must be one of the two surviving support classes")
    lines = []
    for wire in sorted(OUTPUT_WIRES):
        if wire in support_set:
            lines.append(f":- depth(D), not touched(D,{wire}).")
        else:
            lines.append(f":- depth(D), touched(D,{wire}).")
    return "\n".join(lines) + "\n"


def refined_branch_constraints(support: tuple[int, ...], final_layer_count: int) -> str:
    if (support, final_layer_count) not in REFINED_BRANCHES:
        raise ValueError("not one of the five refined branches")
    return (
        "% V(4,9), depth-6 refined support/size hard-instance constraints.\n"
        "% Baseline solver/common.lp and solver/target_v.lp are not modified.\n"
        f"{all_layers_nonempty_constraint(hard_instance_mode=True)}"
        f"{forbid_suffix_only_final_comparators_constraint()}"
        f"{support_constraints(support)}"
        f"{final_layer_size_constraint(final_layer_count)}"
    )


def generate_branch_instance(
    support: tuple[int, ...],
    final_layer_count: int,
    *,
    input_mode: str = "v_boundary",
    v_boundary_validated: bool = V_BOUNDARY_VALIDATED,
) -> str:
    if input_mode == "v_boundary" and not v_boundary_validated:
        raise RuntimeError("v_boundary input mode requires the existing validation guard to pass")
    return generate_instance(N, T, DEPTH, input_mode=input_mode) + "\n" + refined_branch_constraints(
        support, final_layer_count
    )


def final_layer_prefix_support(layer: Layer) -> tuple[int, ...]:
    validate_layer(layer, N)
    touched: set[int] = set()
    for i, j in layer:
        if i in OUTPUT_WIRES:
            touched.add(i)
        if j in OUTPUT_WIRES:
            touched.add(j)
    return tuple(sorted(touched))


def final_layer_has_no_suffix_only_comparator(layer: Layer) -> bool:
    validate_layer(layer, N)
    return all(not (i in SUFFIX_WIRES and j in SUFFIX_WIRES) for i, j in layer)


def branch_for_final_layer(layer: Layer) -> tuple[tuple[int, ...], int] | None:
    validate_layer(layer, N)
    if not final_layer_has_no_suffix_only_comparator(layer):
        return None
    support = final_layer_prefix_support(layer)
    count = len(layer)
    if (support, count) in REFINED_BRANCHES:
        return support, count
    return None


def branch_for_network(network: Network) -> tuple[tuple[int, ...], int] | None:
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    return branch_for_final_layer(network[-1])


def default_worker_count() -> int:
    return 5


def run_partitioned(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int = PILOT_TIMEOUT_SECONDS,
    workers: int | None = None,
    clingo_threads_per_branch: int = 1,
) -> list[RefinedBranchResult]:
    if clingo_threads_per_branch != 1:
        raise ValueError("refined pilot uses one clingo thread per branch")
    worker_count = default_worker_count() if workers is None else workers
    if worker_count != 5:
        raise ValueError("refined pilot requires outer parallelism of exactly 5 branch processes")
    _ensure_layout(output_dir)

    version = solver_version()
    pending = branch_definitions()
    active: list[RunningBranch] = []
    results: list[RefinedBranchResult] = []

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

    results.sort(key=lambda result: (result.support, result.final_layer_comparator_count))
    _write_summary(output_dir / "reports" / "summary.csv", results)
    _write_pilot_json(output_dir / "pilot" / "results.json", results, timeout_seconds)
    write_pilot_report(output_dir / "reports" / "pilot_report.md", results)
    return results


class RunningBranch:
    def __init__(
        self,
        definition: RefinedBranchDefinition,
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


def _start_branch(
    definition: RefinedBranchDefinition,
    output_dir: Path,
    timeout_seconds: int,
    version: str,
) -> RunningBranch:
    branch_dir = output_dir / "branches" / definition.branch_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    instance_path = branch_dir / "instance.lp"
    raw_solver_path = branch_dir / "solver.json"
    branch_definition_path = branch_dir / "branch_definition.json"
    metadata_path = branch_dir / "reproducibility.json"
    stderr_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"

    instance_path.write_text(
        generate_branch_instance(definition.support, definition.final_layer_comparator_count),
        encoding="utf-8",
    )
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


def _finalize_branch(running: RunningBranch) -> RefinedBranchResult:
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

    result = RefinedBranchResult(
        branch_id=running.definition.branch_id,
        support=running.definition.support,
        final_layer_comparator_count=running.definition.final_layer_comparator_count,
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
                "final_layer_comparator_count": result.final_layer_comparator_count,
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
        )
        + "\n",
        encoding="utf-8",
    )
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def load_existing_results(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[RefinedBranchResult]:
    results: list[RefinedBranchResult] = []
    for definition in branch_definitions():
        path = output_dir / "branches" / definition.branch_id / "result.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["support"] = tuple(payload["support"])
            results.append(RefinedBranchResult(**payload))
    return results


def write_pilot_report(path: Path, results: list[RefinedBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    result_by_branch = {result.branch_id: result for result in results}
    prior_rows = _prior_support_rows()
    conclusion = _conclusion(results, prior_rows)
    lines = [
        "# V(4,9), Depth-6 Refined Support/Size Pilot Report",
        "",
        "This report records branch results only. TIMEOUT rows are not UNSAT evidence, and this report does not make a final exactness claim automatically.",
        "",
        "## Branch Definitions",
        "",
        "| branch | T(L6) | |L6| | exact constraints |",
        "| --- | --- | ---: | --- |",
    ]
    for definition in branch_definitions():
        constraints = "<br>".join(
            line.replace("|", "\\|")
            for line in definition.constraints.strip().splitlines()
            if line and not line.startswith("%")
        )
        lines.append(
            f"| {definition.branch_id} | {definition.support} | {definition.final_layer_comparator_count} | `{constraints}` |"
        )

    lines.extend(
        [
            "",
            "## Completeness And Disjointness",
            "",
            "The previous support-partitioned pilot completed every support class except T(L6)=(2,3,4) and T(L6)=(1,2,3,4). This refined run partitions exactly those two surviving classes.",
            "",
            "For T=(2,3,4), a matching that touches exactly those three output wires and contains no suffix-only comparator has size 2 or 3. Size 1 cannot touch three distinct output wires, and size 4 would need four non-suffix comparators touching only three matched output wires, impossible in a matching.",
            "",
            "For T=(1,2,3,4), the corresponding size is 2, 3, or 4. Size 1 cannot touch four distinct output wires, and size 4 is the maximum because every non-suffix final comparator must be incident to at least one of the four output wires in a matching.",
            "",
            "The five branches are pairwise disjoint because each branch fixes the exact pair (T(L6), |L6|); two different supports or two different final-layer sizes cannot hold for the same final layer.",
            "",
            "If all five refined branches are UNSAT and the prior thirteen support-pilot UNSAT artifacts are present and verified, then the full depth-6 hard-instance space is UNSAT. If any refined branch is SAT and independently verified, then V(4,9) has a depth-6 witness.",
            "",
            "## New Refined Branch Results",
            "",
            "| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for definition in branch_definitions():
        result = result_by_branch.get(definition.branch_id)
        if result is None:
            lines.append(f"| {definition.branch_id} | NOT_RUN |  |  |  |  |  |")
            continue
        verifier = "" if result.verifier_ok is None else ("OK" if result.verifier_ok else "FAILED")
        lines.append(
            f"| {result.branch_id} | {result.status} | {result.runtime_seconds:.3f} | "
            f"{'' if result.peak_rss_kb is None else result.peak_rss_kb} | {result.cpu_snapshots} | "
            f"{_stats_summary(result.solver_statistics)} | {verifier} |"
        )

    sat = [result for result in results if result.status == "SAT"]
    lines.extend(["", "## SAT Witnesses", ""])
    if sat:
        for result in sat:
            lines.append(
                f"- {result.branch_id}: witness={result.network_json_path}; verifier={result.verifier_json_path}; verifier_ok={result.verifier_ok}"
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Combined Support Table",
            "",
            "| source | branch | support | |L6| | status | artifact |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in prior_rows:
        lines.append(
            f"| prior support pilot | {row['branch']} | {row['support']} |  | {row['status']} | {row['artifact']} |"
        )
    for definition in branch_definitions():
        result = result_by_branch.get(definition.branch_id)
        status = "NOT_RUN" if result is None else result.status
        artifact = "" if result is None else result.parsed_status_path
        lines.append(
            f"| refined pilot | {definition.branch_id} | {definition.support} | {definition.final_layer_comparator_count} | {status} | {artifact} |"
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            conclusion,
            "",
            "## Recommendation",
            "",
            _recommendation(results),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prior_support_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for support in PRIOR_SUPPORT_BRANCHES:
        branch = "T_" + "".join(str(wire) for wire in support)
        artifact = PRIOR_SUPPORT_OUTPUT_DIR / "branches" / branch / "parsed_status.json"
        status = "MISSING"
        if artifact.exists():
            try:
                status = json.loads(artifact.read_text(encoding="utf-8")).get("status", "UNKNOWN")
            except json.JSONDecodeError:
                status = "ERROR"
        rows.append(
            {
                "branch": branch,
                "support": str(support),
                "status": status,
                "artifact": str(artifact),
            }
        )
    return rows


def _conclusion(results: list[RefinedBranchResult], prior_rows: list[dict[str, str]]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        return "ERROR_OR_VERIFICATION_FAILURE"
    if any(result.status == "SAT" and result.verifier_ok for result in results):
        return "DEPTH_6_SAT_FOUND"
    all_refined_unsat = len(results) == len(REFINED_BRANCHES) and all(result.status == "UNSAT" for result in results)
    all_prior_unsat = len(prior_rows) == len(PRIOR_SUPPORT_BRANCHES) and all(row["status"] == "UNSAT" for row in prior_rows)
    if all_refined_unsat and all_prior_unsat:
        return "ALL_15_SUPPORT_CLASSES_UNSAT_CONFIRMED"
    return "INCONCLUSIVE_REMAINING_BRANCHES"


def _recommendation(results: list[RefinedBranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        failed = next(result.branch_id for result in results if result.status in {"ERROR", "VERIFICATION_FAILED"})
        return f"switch the remaining branch to an independent CNF/SAT encoding: {failed}"
    remaining = [result for result in results if result.status == "TIMEOUT"]
    if remaining:
        branch = sorted(remaining, key=lambda result: (-result.runtime_seconds, result.branch_id))[0].branch_id
        return f"split one named remaining branch by the exact comparator incident to output wire 4: {branch}"
    missing = {definition.branch_id for definition in branch_definitions()} - {result.branch_id for result in results}
    if missing:
        return f"longer run for one named remaining branch: {sorted(missing)[0]}"
    return "longer run for one named remaining branch: none; all refined branches resolved"


def _write_summary(path: Path, results: list[RefinedBranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _write_pilot_json(path: Path, results: list[RefinedBranchResult], timeout_seconds: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "pilot",
        "timeout_seconds": timeout_seconds,
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
