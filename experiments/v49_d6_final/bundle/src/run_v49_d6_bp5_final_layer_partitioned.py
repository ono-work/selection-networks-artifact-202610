"""B_p5 final-layer partition runner for V(4,9), depth 6.

This runner refines only the previously timed-out B_p5 child:
T(L6)=(1,2,3,4), |L6|=3, and final comparator (4,5).
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
BP5_SUPPORT = (1, 2, 3, 4)
BP5_FINAL_LAYER_COUNT = 3
BP5_FIXED_COMPARATOR = (4, 5)
BRANCH_SPECS = (
    ((1, 2), (3, 6)),
    ((1, 2), (3, 7)),
    ((1, 2), (3, 8)),
    ((1, 2), (3, 9)),
    ((1, 3), (2, 6)),
    ((1, 3), (2, 7)),
    ((1, 3), (2, 8)),
    ((1, 3), (2, 9)),
    ((2, 3), (1, 6)),
    ((2, 3), (1, 7)),
    ((2, 3), (1, 8)),
    ((2, 3), (1, 9)),
)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_bp5_final_layer_partitioned"
PARENT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_partner_partitioned"
PILOT_TIMEOUT_SECONDS = 1800
V_BOUNDARY_VALIDATED = True

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]


@dataclass(frozen=True)
class BP5BranchDefinition:
    branch_id: str
    output_output_comparator: tuple[int, int]
    output_suffix_comparator: tuple[int, int]
    fixed_comparator: tuple[int, int]
    final_layer_comparators: tuple[tuple[int, int], ...]
    parent_constraints: str
    final_layer_constraints: str
    constraints: str


@dataclass(frozen=True)
class BP5BranchResult:
    branch_id: str
    output_output_comparator: tuple[int, int]
    output_suffix_comparator: tuple[int, int]
    fixed_comparator: tuple[int, int]
    final_layer_comparators: tuple[tuple[int, int], ...]
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


def branch_id_for(output_output: tuple[int, int], output_suffix: tuple[int, int]) -> str:
    return f"OO_{output_output[0]}{output_output[1]}_OS_{output_suffix[0]}{output_suffix[1]}"


def normalize_comparator(comparator: tuple[int, int]) -> tuple[int, int]:
    i, j = comparator
    if i == j or i < 1 or j < 1 or i > N or j > N:
        raise ValueError("invalid comparator")
    return (i, j) if i < j else (j, i)


def branch_definitions() -> list[BP5BranchDefinition]:
    return [
        BP5BranchDefinition(
            branch_id=branch_id_for(output_output, output_suffix),
            output_output_comparator=normalize_comparator(output_output),
            output_suffix_comparator=normalize_comparator(output_suffix),
            fixed_comparator=BP5_FIXED_COMPARATOR,
            final_layer_comparators=final_layer_comparators(output_output, output_suffix),
            parent_constraints=parent_constraints(),
            final_layer_constraints=final_layer_constraints(final_layer_comparators(output_output, output_suffix)),
            constraints=bp5_branch_constraints(output_output, output_suffix),
        )
        for output_output, output_suffix in BRANCH_SPECS
    ]


def final_layer_comparators(
    output_output: tuple[int, int],
    output_suffix: tuple[int, int],
) -> tuple[tuple[int, int], ...]:
    comparators = tuple(sorted((BP5_FIXED_COMPARATOR, normalize_comparator(output_output), normalize_comparator(output_suffix))))
    if len(set(comparators)) != 3:
        raise ValueError("branch must fix three distinct final comparators")
    touched = {wire for comparator in comparators for wire in comparator}
    if len(touched) != 6 or not set(BP5_SUPPORT) <= touched:
        raise ValueError("branch comparators do not form the requested B_p5 final matching")
    return comparators


def all_layers_nonempty_constraint(*, hard_instance_mode: bool) -> str:
    if not hard_instance_mode:
        return ""
    return ":- layer(L), not active(L).\n"


def forbid_suffix_only_final_comparators_constraint() -> str:
    return ":- depth(D), selected(D,I,J), I >= 5, J >= 5.\n"


def support_constraints() -> str:
    return "".join(f":- depth(D), not touched(D,{wire}).\n" for wire in sorted(BP5_SUPPORT))


def final_layer_size_constraint() -> str:
    return f":- depth(D), {BP5_FINAL_LAYER_COUNT} != #count {{ I,J : selected(D,I,J) }}.\n"


def parent_constraints() -> str:
    return (
        f"{all_layers_nonempty_constraint(hard_instance_mode=True)}"
        f"{forbid_suffix_only_final_comparators_constraint()}"
        f"{support_constraints()}"
        f"{final_layer_size_constraint()}"
        f":- depth(D), not selected(D,4,5).\n"
    )


def final_layer_constraints(comparators: tuple[tuple[int, int], ...]) -> str:
    return "".join(f":- depth(D), not selected(D,{i},{j}).\n" for i, j in comparators)


def bp5_branch_constraints(output_output: tuple[int, int], output_suffix: tuple[int, int]) -> str:
    if (output_output, output_suffix) not in BRANCH_SPECS:
        raise ValueError("not one of the 12 B_p5 final-layer branches")
    comparators = final_layer_comparators(output_output, output_suffix)
    return (
        "% V(4,9), depth-6 B_p5 final-layer partition constraints.\n"
        "% Baseline solver/common.lp and solver/target_v.lp are not modified.\n"
        "% No suffix-wire symmetry or canonical suffix partner is assumed.\n"
        f"{parent_constraints()}"
        f"{final_layer_constraints(comparators)}"
    )


def generate_branch_instance(
    output_output: tuple[int, int],
    output_suffix: tuple[int, int],
    *,
    input_mode: str = "v_boundary",
    v_boundary_validated: bool = V_BOUNDARY_VALIDATED,
) -> str:
    if input_mode == "v_boundary" and not v_boundary_validated:
        raise RuntimeError("v_boundary input mode requires the existing validation guard to pass")
    return generate_instance(N, T, DEPTH, input_mode=input_mode) + "\n" + bp5_branch_constraints(
        output_output, output_suffix
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


def is_bp5_final_layer(layer: Layer) -> bool:
    validate_layer(layer, N)
    return (
        len(layer) == BP5_FINAL_LAYER_COUNT
        and BP5_FIXED_COMPARATOR in layer
        and final_layer_prefix_support(layer) == BP5_SUPPORT
        and final_layer_has_no_suffix_only_comparator(layer)
    )


def branch_for_final_layer(layer: Layer) -> str | None:
    validate_layer(layer, N)
    if not is_bp5_final_layer(layer):
        return None
    layer_set = set(layer)
    for definition in branch_definitions():
        if set(definition.final_layer_comparators) == layer_set:
            return definition.branch_id
    return None


def branch_for_network(network: Network) -> str | None:
    validate_network(network, N)
    if len(network) != DEPTH or any(len(layer) == 0 for layer in network):
        return None
    return branch_for_final_layer(network[-1])


def default_worker_count() -> int:
    return min(8, max(1, (os.cpu_count() or 1) - 2))


def run_partitioned(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int = PILOT_TIMEOUT_SECONDS,
    workers: int | None = None,
    clingo_threads_per_branch: int = 1,
) -> list[BP5BranchResult]:
    if clingo_threads_per_branch != 1:
        raise ValueError("B_p5 pilot uses one clingo thread per child")
    worker_count = default_worker_count() if workers is None else workers
    if worker_count < 1 or worker_count > 8:
        raise ValueError("workers must be in 1..8")
    _ensure_layout(output_dir)

    version = solver_version()
    pending = branch_definitions()
    active: list[RunningBranch] = []
    results: list[BP5BranchResult] = []

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
        definition: BP5BranchDefinition,
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
    definition: BP5BranchDefinition,
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

    instance_path.write_text(
        generate_branch_instance(definition.output_output_comparator, definition.output_suffix_comparator),
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
        "parent": {
            "branch_id": "B_p5",
            "support": BP5_SUPPORT,
            "final_layer_comparator_count": BP5_FINAL_LAYER_COUNT,
            "fixed_comparator": BP5_FIXED_COMPARATOR,
        },
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


def _finalize_branch(running: RunningBranch) -> BP5BranchResult:
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
    except Exception as exc:  # noqa: BLE001
        status = "TIMEOUT" if running.timed_out else "ERROR"
        error_message = None if running.timed_out else str(exc)

    result = BP5BranchResult(
        branch_id=running.definition.branch_id,
        output_output_comparator=running.definition.output_output_comparator,
        output_suffix_comparator=running.definition.output_suffix_comparator,
        fixed_comparator=running.definition.fixed_comparator,
        final_layer_comparators=running.definition.final_layer_comparators,
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
    parsed_status_path.write_text(
        json.dumps(
            {
                "branch_id": result.branch_id,
                "output_output_comparator": result.output_output_comparator,
                "output_suffix_comparator": result.output_suffix_comparator,
                "fixed_comparator": result.fixed_comparator,
                "final_layer_comparators": result.final_layer_comparators,
                "status": result.status,
                "clingo_result": result.clingo_result,
                "runtime_seconds": result.runtime_seconds,
                "timeout_seconds": result.timeout_seconds,
                "worker_count": result.worker_count,
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


def load_existing_results(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[BP5BranchResult]:
    results: list[BP5BranchResult] = []
    for definition in branch_definitions():
        path = output_dir / "branches" / definition.branch_id / "result.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            for key in ("output_output_comparator", "output_suffix_comparator", "fixed_comparator"):
                payload[key] = tuple(payload[key])
            payload["final_layer_comparators"] = tuple(tuple(item) for item in payload["final_layer_comparators"])
            results.append(BP5BranchResult(**payload))
    return results


def write_pilot_report(path: Path, results: list[BP5BranchResult], worker_count: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    definitions = branch_definitions()
    result_by_branch = {result.branch_id: result for result in results}
    actual_worker_count = worker_count if worker_count is not None else (results[0].worker_count if results else default_worker_count())
    parent_row = _parent_bp5_row()
    conclusion = _conclusion(results)
    lines = [
        "# V(4,9), Depth-6 B_p5 Final-Layer Pilot Report",
        "",
        "This report refines only the prior B_p5 TIMEOUT branch. TIMEOUT rows are not UNSAT evidence.",
        "",
        f"Actual worker count: {actual_worker_count}.",
        "",
        "## Proof Summary",
        "",
        "B_p5 fixes T(L6)=(1,2,3,4), |L6|=3, and final comparator (4,5). Since final layers are matchings, wires 4 and 5 cannot appear in the other two final comparators.",
        "",
        "The remaining output wires 1,2,3 must all be touched by the two remaining comparators. Therefore exactly one remaining comparator is an output-output pair among {1,2,3}, and the third output wire is paired with one suffix wire in {6,7,8,9}. This gives 3 output-output choices times 4 suffix choices, exactly 12 branches.",
        "",
        "The branches are pairwise disjoint because each fixes a distinct exact final-layer comparator set. Their union covers B_p5 because every B_p5 final matching has exactly one of those output-output pairs and exactly one suffix partner for the remaining output wire. No suffix-wire symmetry or canonicalization is used.",
        "",
        "## Branch Definitions",
        "",
        "| branch | fixed final layer | exact constraints |",
        "| --- | --- | --- |",
    ]
    for definition in definitions:
        constraints = "<br>".join(
            line.replace("|", "\\|")
            for line in definition.constraints.strip().splitlines()
            if line and not line.startswith("%")
        )
        lines.append(f"| {definition.branch_id} | {definition.final_layer_comparators} | `{constraints}` |")

    lines.extend(
        [
            "",
            "## Branch Results",
            "",
            "| branch | status | runtime seconds | peak RSS KB | CPU snapshots | statistics summary | verifier |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for definition in definitions:
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
            "## Combined Parent/Child Table",
            "",
            "| source | branch | fixed final layer | status | artifact |",
            "| --- | --- | --- | --- | --- |",
            f"| prior partner pilot parent | B_p5 | T(L6)=(1,2,3,4), |L6|=3, (4,5) | {parent_row['status']} | {parent_row['artifact']} |",
        ]
    )
    for definition in definitions:
        result = result_by_branch.get(definition.branch_id)
        status = "NOT_RUN" if result is None else result.status
        artifact = "" if result is None else result.parsed_status_path
        lines.append(f"| current B_p5 split | {definition.branch_id} | {definition.final_layer_comparators} | {status} | {artifact} |")

    lines.extend(["", "## Conclusion", "", conclusion, "", "## Recommendation", "", _recommendation(results)])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parent_bp5_row() -> dict[str, str]:
    artifact = PARENT_OUTPUT_DIR / "branches" / "B_p5" / "parsed_status.json"
    status = "MISSING"
    if artifact.exists():
        try:
            status = str(json.loads(artifact.read_text(encoding="utf-8")).get("status", "UNKNOWN"))
        except json.JSONDecodeError:
            status = "ERROR"
    return {"status": status, "artifact": str(artifact)}


def _conclusion(results: list[BP5BranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        return "ERROR_OR_VERIFICATION_FAILURE"
    if any(result.status == "SAT" and result.verifier_ok for result in results):
        return "DEPTH_6_SAT_FOUND"
    if len(results) == len(BRANCH_SPECS) and all(result.status == "UNSAT" for result in results):
        return "BP5_ALL_CHILDREN_UNSAT_CONFIRMED"
    return "BP5_INCONCLUSIVE_REMAINING_CHILDREN"


def _recommendation(results: list[BP5BranchResult]) -> str:
    if any(result.status in {"ERROR", "VERIFICATION_FAILED"} for result in results):
        failed = [result.branch_id for result in results if result.status in {"ERROR", "VERIFICATION_FAILED"}]
        return "further exact split of named children: " + ", ".join(failed)
    timed_out = [result for result in results if result.status == "TIMEOUT"]
    if timed_out:
        names = ", ".join(result.branch_id for result in sorted(timed_out, key=lambda r: (-r.runtime_seconds, r.branch_id)))
        return f"longer runs for named children: {names}"
    missing = sorted({definition.branch_id for definition in branch_definitions()} - {result.branch_id for result in results})
    if missing:
        return f"longer runs for named children: {', '.join(missing)}"
    return "return to the A_p5/A_p6 branches"


def _write_summary(path: Path, results: list[BP5BranchResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def _write_pilot_json(path: Path, results: list[BP5BranchResult], timeout_seconds: int, worker_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": "pilot",
        "timeout_seconds": timeout_seconds,
        "worker_count": worker_count,
        "input_mode": "v_boundary",
        "parent": "B_p5",
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
