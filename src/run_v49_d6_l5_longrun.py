"""One-hour long-run wave for open V(4,9) L5-cardinality branches."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.benchmark_v49_d6_solver_config import DEFAULT_OUTPUT_DIR as BENCHMARK_DIR
from src.experiment import COMMON, TARGET_V, solver_version
from src.network import Comparator
from src.parse_model import network_to_json, parse_selected_network
from src.run_v49_d6_l5_partitioned import L5BranchDefinition, branch_definitions, generate_branch_instance
from src.solver import CLINGO_COMMAND
from src.verify import verify_binary

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_l5_partitioned" / "longrun"
REPORT_PATH = ROOT / "experiments" / "v49_d6_l5_partitioned" / "reports" / "longrun_report.md"
TIMEOUT_SECONDS = 3600
SEED = 1
OPEN_BRANCHES = (
    "A5_residual_L5eq2",
    "A5_residual_L5eq3",
    "A5_residual_L5eq4",
    "B6_residual_L5eq2",
    "B6_residual_L5eq3",
    "B6_residual_L5eq4",
    "B7_residual_L5eq2",
    "B7_residual_L5eq3",
    "B7_residual_L5eq4",
    "B8_residual_L5eq2",
    "B8_residual_L5eq3",
    "B8_residual_L5eq4",
    "B9_residual_L5eq3",
    "B9_residual_L5eq4",
)
CLOSED_UNSAT = (
    "A5_residual_L5eq1",
    "B6_residual_L5eq1",
    "B7_residual_L5eq1",
    "B8_residual_L5eq1",
    "B9_residual_L5eq1",
    "B9_residual_L5eq2",
)

BranchStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"]


@dataclass(frozen=True)
class LongrunConfig:
    selected_config: str
    threads_per_branch: int
    parallel_options: tuple[str, ...]
    nproc: int
    workers: int
    worker_formula: str
    benchmark_summary_path: str


@dataclass(frozen=True)
class LongrunResult:
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


def load_config(benchmark_dir: Path = BENCHMARK_DIR) -> LongrunConfig:
    summary_path = benchmark_dir / "reports" / "benchmark_results.json"
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    selected = data["selected_config"]
    if selected == "baseline_1thread":
        threads, options = 1, ()
    elif selected == "split_4thread":
        threads, options = 4, ("--parallel-mode=4,split",)
    elif selected == "compete_4thread":
        threads, options = 4, ("--parallel-mode=4,compete",)
    else:
        raise ValueError(f"unknown selected config {selected!r}")
    nproc = int(subprocess.run(["nproc"], check=True, capture_output=True, text=True).stdout.strip())
    workers = min(14, max(1, (nproc - 2) // threads))
    return LongrunConfig(
        selected_config=selected,
        threads_per_branch=threads,
        parallel_options=options,
        nproc=nproc,
        workers=workers,
        worker_formula=f"min(14, max(1, floor(({nproc} - 2) / {threads})))",
        benchmark_summary_path=str(summary_path),
    )


def open_definitions() -> list[L5BranchDefinition]:
    by_id = {definition.branch_id: definition for definition in branch_definitions()}
    return [by_id[branch_id] for branch_id in OPEN_BRANCHES]


def run_longrun(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    timeout_seconds: int = TIMEOUT_SECONDS,
    config: LongrunConfig | None = None,
) -> list[LongrunResult]:
    cfg = load_config() if config is None else config
    _ensure_layout(output_dir)
    metadata = _run_metadata()
    definitions = open_definitions()
    pending = list(definitions)
    active: list[RunningBranch] = []
    results: list[LongrunResult] = []
    cancelled = False
    for definition in definitions:
        _materialize_branch(output_dir, definition, cfg, timeout_seconds, metadata)
    version = solver_version()
    while (pending or active) and not cancelled:
        while pending and len(active) < cfg.workers:
            active.append(_start_branch(pending.pop(0), output_dir, cfg, timeout_seconds, version, metadata))
        time.sleep(1.0)
        next_active: list[RunningBranch] = []
        for running in active:
            running.sample_resources()
            if running.process.poll() is None:
                if running.elapsed() >= timeout_seconds:
                    running.terminate_for_timeout()
                next_active.append(running)
                continue
            result = _finalize_branch(running)
            results.append(result)
            if result.status == "SAT" and result.verifier_ok:
                cancelled = True
        active = []
        for running in next_active:
            if cancelled:
                running.terminate_for_cancel()
                results.append(_cancelled_result(running, "verified SAT in sibling branch"))
            elif running.process.poll() is None:
                active.append(running)
            else:
                result = _finalize_branch(running)
                results.append(result)
                if result.status == "SAT" and result.verifier_ok:
                    cancelled = True
        if cancelled:
            for definition in pending:
                results.append(_cancelled_pending_result(output_dir, definition, cfg, timeout_seconds, version, metadata))
            pending = []
    order = {definition.branch_id: index for index, definition in enumerate(definitions)}
    results.sort(key=lambda result: order[result.branch_id])
    _write_json(output_dir / "results.json", {"config": asdict(cfg), "results": [asdict(result) for result in results]})
    write_report(REPORT_PATH, results, cfg)
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
        self.cancelled = False

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
        self._terminate()

    def terminate_for_cancel(self) -> None:
        self.cancelled = True
        self._terminate()

    def _terminate(self) -> None:
        if self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def _materialize_branch(output_dir: Path, definition: L5BranchDefinition, cfg: LongrunConfig, timeout_seconds: int, metadata: dict[str, Any]) -> None:
    branch_dir = output_dir / "branches" / definition.branch_id
    branch_dir.mkdir(parents=True, exist_ok=True)
    (branch_dir / "instance.lp").write_text(generate_branch_instance(definition.final_layer, definition.forbid_l5, definition.l5_count), encoding="utf-8")
    (branch_dir / "branch_definition.json").write_text(json.dumps(asdict(definition), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "logs" / f"{definition.branch_id}.resources.jsonl").write_text("", encoding="utf-8")
    _write_metadata(branch_dir / "reproducibility.json", definition, cfg, timeout_seconds, metadata, None, None)


def _start_branch(
    definition: L5BranchDefinition,
    output_dir: Path,
    cfg: LongrunConfig,
    timeout_seconds: int,
    version: str,
    metadata: dict[str, Any],
) -> RunningBranch:
    branch_dir = output_dir / "branches" / definition.branch_id
    instance_path = branch_dir / "instance.lp"
    raw_solver_path = branch_dir / "solver.json"
    stderr_path = output_dir / "logs" / f"{definition.branch_id}.stderr.log"
    resource_log_path = output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"
    solver_options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={timeout_seconds}", f"--seed={SEED}", *cfg.parallel_options]
    command = [*CLINGO_COMMAND, *solver_options, str(COMMON), str(TARGET_V), str(instance_path)]
    _write_metadata(branch_dir / "reproducibility.json", definition, cfg, timeout_seconds, metadata, command, version)
    raw_handle = raw_solver_path.open("w", encoding="utf-8")
    stderr_handle = stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=raw_handle, stderr=stderr_handle, text=True)
    raw_handle.close()
    stderr_handle.close()
    return RunningBranch(definition, branch_dir, [str(part) for part in command], solver_options, process, time.perf_counter(), timeout_seconds, resource_log_path, cfg.workers)


def _finalize_branch(running: RunningBranch) -> LongrunResult:
    branch_dir = running.branch_dir
    raw_solver_path = branch_dir / "solver.json"
    parsed_status_path = branch_dir / "parsed_status.json"
    network_path = branch_dir / "network.json"
    verifier_path = branch_dir / "verifier.json"
    stdout = raw_solver_path.read_text(encoding="utf-8") if raw_solver_path.exists() else ""
    clingo_result = None
    stats = None
    network_json_path = None
    verifier_json_path = None
    verifier_ok = None
    comparator_count = None
    layer_counts = None
    error_message = None
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
        raw_result = payload.get("Result")
        clingo_result = raw_result if isinstance(raw_result, str) else None
        stats = payload.get("Stats") if isinstance(payload.get("Stats"), dict) else None
        if running.timed_out or clingo_result == "UNKNOWN":
            status: BranchStatus = "TIMEOUT"
        elif clingo_result == "SATISFIABLE":
            network = parse_selected_network(stdout, n=9, depth=6)
            layer_counts = [len(layer) for layer in network]
            comparator_count = sum(layer_counts)
            network_path.write_text(json.dumps(network_to_json(network, n=9, t=4, kind="V"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            network_json_path = str(network_path)
            verifier = verify_binary(network, n=9, t=4, kind="V")
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
    result = _make_result(
        running.definition,
        status,
        running.process.pid,
        running.command,
        running.solver_options,
        running.elapsed(),
        running.timeout_seconds,
        running.worker_count,
        str(branch_dir / "instance.lp"),
        str(raw_solver_path),
        str(parsed_status_path),
        str(branch_dir / "reproducibility.json"),
        str(running.resource_log_path),
        str(branch_dir / "branch_definition.json"),
        running.peak_rss_kb,
        running.cpu_snapshots,
        clingo_result,
        stats,
        network_json_path,
        verifier_json_path,
        verifier_ok,
        comparator_count,
        layer_counts,
        error_message,
    )
    _write_result(branch_dir, result)
    return result


def _cancelled_result(running: RunningBranch, message: str) -> LongrunResult:
    result = _make_result(
        running.definition,
        "CANCELLED_AFTER_VERIFIED_SAT",
        running.process.pid,
        running.command,
        running.solver_options,
        running.elapsed(),
        running.timeout_seconds,
        running.worker_count,
        str(running.branch_dir / "instance.lp"),
        str(running.branch_dir / "solver.json"),
        str(running.branch_dir / "parsed_status.json"),
        str(running.branch_dir / "reproducibility.json"),
        str(running.resource_log_path),
        str(running.branch_dir / "branch_definition.json"),
        running.peak_rss_kb,
        running.cpu_snapshots,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        message,
    )
    _write_result(running.branch_dir, result)
    return result


def _cancelled_pending_result(output_dir: Path, definition: L5BranchDefinition, cfg: LongrunConfig, timeout_seconds: int, version: str, metadata: dict[str, Any]) -> LongrunResult:
    branch_dir = output_dir / "branches" / definition.branch_id
    solver_options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={timeout_seconds}", f"--seed={SEED}", *cfg.parallel_options]
    command = [*CLINGO_COMMAND, *solver_options, str(COMMON), str(TARGET_V), str(branch_dir / "instance.lp")]
    _write_metadata(branch_dir / "reproducibility.json", definition, cfg, timeout_seconds, metadata, command, version)
    result = _make_result(
        definition,
        "CANCELLED_AFTER_VERIFIED_SAT",
        None,
        [str(part) for part in command],
        solver_options,
        0.0,
        timeout_seconds,
        cfg.workers,
        str(branch_dir / "instance.lp"),
        str(branch_dir / "solver.json"),
        str(branch_dir / "parsed_status.json"),
        str(branch_dir / "reproducibility.json"),
        str(output_dir / "logs" / f"{definition.branch_id}.resources.jsonl"),
        str(branch_dir / "branch_definition.json"),
        None,
        0,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "verified SAT in sibling branch before launch",
    )
    _write_result(branch_dir, result)
    return result


def _make_result(definition: L5BranchDefinition, status: BranchStatus, pid: int | None, command: list[str], solver_options: list[str], runtime_seconds: float, timeout_seconds: int | None, worker_count: int, instance_path: str, raw_solver_json_path: str, parsed_status_path: str, metadata_path: str, resource_log_path: str, branch_definition_path: str, peak_rss_kb: int | None, cpu_snapshots: int, clingo_result: str | None, solver_statistics: dict[str, Any] | None, network_json_path: str | None, verifier_json_path: str | None, verifier_ok: bool | None, comparator_count: int | None, layer_comparator_counts: list[int] | None, error_message: str | None) -> LongrunResult:
    return LongrunResult(definition.branch_id, definition.residual_id, definition.leaf_id, definition.final_layer, definition.forbid_l5, definition.l5_count, status, pid, command, solver_options, solver_version(), runtime_seconds, timeout_seconds, worker_count, "v_boundary", instance_path, raw_solver_json_path, parsed_status_path, metadata_path, resource_log_path, branch_definition_path, peak_rss_kb, cpu_snapshots, clingo_result, solver_statistics, network_json_path, verifier_json_path, verifier_ok, comparator_count, layer_comparator_counts, error_message)


def _write_result(branch_dir: Path, result: LongrunResult) -> None:
    (branch_dir / "parsed_status.json").write_text(json.dumps({"branch_id": result.branch_id, "status": result.status, "clingo_result": result.clingo_result, "runtime_seconds": result.runtime_seconds, "timeout_seconds": result.timeout_seconds, "peak_rss_kb": result.peak_rss_kb, "cpu_snapshots": result.cpu_snapshots, "error_message": result.error_message}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (branch_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, results: list[LongrunResult], cfg: LongrunConfig) -> None:
    by_status = {status: [r.branch_id for r in results if r.status == status] for status in ["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED", "CANCELLED_AFTER_VERIFIED_SAT"]}
    rss = [r.peak_rss_kb for r in results if r.peak_rss_kb is not None]
    runtimes = [r.runtime_seconds for r in results]
    if any(r.status == "SAT" and r.verifier_ok for r in results):
        conclusion = "V49_DEPTH6_SAT_VERIFIED"
    elif len(by_status["UNSAT"]) == len(OPEN_BRANCHES):
        conclusion = "V49_DEPTH6_UNSAT_COVERAGE_COMPLETE"
    else:
        conclusion = "V49_DEPTH6_INCONCLUSIVE"
    lines = [
        "# V(4,9), Depth-6 L5 Long-Run Report",
        "",
        f"Benchmark-selected solver configuration: {cfg.selected_config}; options: {' '.join(cfg.parallel_options) if cfg.parallel_options else 'single-thread baseline'}.",
        f"Worker calculation: {cfg.worker_formula} = {cfg.workers}.",
        "",
        "## Status Table",
        "",
        "| branch | status | runtime seconds | peak RSS KB | verifier |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for r in results:
        verifier = "" if r.verifier_ok is None else ("OK" if r.verifier_ok else "FAILED")
        lines.append(f"| {r.branch_id} | {r.status} | {r.runtime_seconds:.3f} | {'' if r.peak_rss_kb is None else r.peak_rss_kb} | {verifier} |")
    lines.extend(["", "## Status Lists", ""])
    for status, names in by_status.items():
        lines.append(f"- {status}: {', '.join(names) if names else 'None'}")
    lines.extend([
        "",
        "## Runtime And RSS",
        "",
        f"- runtime min/max seconds: {min(runtimes):.3f} / {max(runtimes):.3f}" if runtimes else "- runtime: unavailable",
        f"- peak RSS min/max KB: {min(rss)} / {max(rss)}" if rss else "- peak RSS: unavailable",
        "",
        "## Coverage Accounting",
        "",
        f"- prior closed L5 branches: {', '.join(CLOSED_UNSAT)}",
        f"- newly closed UNSAT branches: {', '.join(by_status['UNSAT']) if by_status['UNSAT'] else 'None'}",
        f"- still-open branches: {', '.join(by_status['TIMEOUT'] + by_status['ERROR'] + by_status['VERIFICATION_FAILED']) if (by_status['TIMEOUT'] + by_status['ERROR'] + by_status['VERIFICATION_FAILED']) else 'None'}",
        "",
        "## Conclusion",
        "",
        conclusion,
        "",
        "## Recommended Next Action",
        "",
        _recommendation(conclusion, by_status),
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _recommendation(conclusion: str, by_status: dict[str, list[str]]) -> str:
    remaining = by_status["TIMEOUT"] + by_status["ERROR"] + by_status["VERIFICATION_FAILED"]
    if conclusion == "V49_DEPTH6_INCONCLUSIVE" and remaining:
        return "run a longer wave on specifically named remaining branches: " + ", ".join(remaining)
    if conclusion == "V49_DEPTH6_UNSAT_COVERAGE_COMPLETE":
        return "move to n = 10"
    return "add an independent CNF/SAT encoding"


def _run_metadata() -> dict[str, Any]:
    return {
        "git_head": _cmd(["git", "rev-parse", "HEAD"]),
        "git_status_short": _cmd(["git", "status", "--short"]),
        "file_hashes": {str(path): _sha256(path) for path in [Path("src/run_v49_d6_l5_longrun.py"), Path("src/run_v49_d6_l5_partitioned.py"), COMMON, TARGET_V]},
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "gpu_use": "none",
    }


def _write_metadata(path: Path, definition: L5BranchDefinition, cfg: LongrunConfig, timeout_seconds: int, metadata: dict[str, Any], command: list[str] | None, version: str | None) -> None:
    path.write_text(json.dumps({"branch": asdict(definition), "config": asdict(cfg), "timeout_seconds": timeout_seconds, "command": command, "solver_version": version, "run_metadata": metadata}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _cmd(command: list[str]) -> str:
    return subprocess.run(command, check=False, capture_output=True, text=True).stdout.strip()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _process_snapshot(pid: int) -> dict[str, Any] | None:
    completed = subprocess.run(["ps", "-p", str(pid), "-o", "pid=,etime=,pcpu=,pmem=,rss=,vsz=,stat="], check=False, capture_output=True, text=True)
    line = completed.stdout.strip()
    if completed.returncode != 0 or not line:
        return None
    parts = line.split()
    if len(parts) < 7:
        return {"raw_ps": line}
    return {"pid": int(parts[0]), "etime": parts[1], "cpu_percent": float(parts[2]), "mem_percent": float(parts[3]), "rss_kb": int(parts[4]), "vsz_kb": int(parts[5]), "stat": parts[6]}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ensure_layout(output_dir: Path) -> None:
    for name in ("branches", "logs"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout-seconds", type=int, default=TIMEOUT_SECONDS)
    args = parser.parse_args()
    cfg = load_config()
    print(f"selected_config={cfg.selected_config}")
    print(f"workers={cfg.workers}")
    results = run_longrun(output_dir=args.output_dir, timeout_seconds=args.timeout_seconds, config=cfg)
    for result in results:
        print(f"{result.branch_id}: {result.status} in {result.runtime_seconds:.3f}s")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
