"""Serial solver-configuration benchmark for representative V(4,9) branches."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.experiment import COMMON, TARGET_V, solver_version
from src.run_v49_d6_l5_partitioned import branch_definitions, generate_branch_instance
from src.solver import CLINGO_COMMAND

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "v49_d6_solver_config_benchmark"
REPRESENTATIVE_BRANCHES = ("A5_residual_L5eq2", "B9_residual_L5eq3")
TIMEOUT_SECONDS = 600
SEED = 1


@dataclass(frozen=True)
class SolverConfig:
    config_id: str
    threads: int
    mode: str
    solver_options: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkResult:
    branch_id: str
    config_id: str
    status: str
    clingo_result: str | None
    runtime_seconds: float
    peak_rss_kb: int | None
    cpu_snapshots: int
    command: list[str]
    solver_options: list[str]
    instance_path: str
    raw_json_path: str
    stderr_path: str
    resource_log_path: str
    stats: dict[str, Any] | None
    choices: float | None
    conflicts: float | None
    restarts: float | None
    solving_time: float | None
    error_message: str | None = None


def clingo_help() -> str:
    return subprocess.run([*CLINGO_COMMAND, "--help=3"], check=True, capture_output=True, text=True).stdout


def supported_configs(help_text: str) -> list[SolverConfig]:
    configs = [SolverConfig("baseline_1thread", 1, "single", ())]
    if "--parallel-mode" in help_text and "compete" in help_text and "split" in help_text:
        configs.extend(
            [
                SolverConfig("split_4thread", 4, "split", ("--parallel-mode=4,split",)),
                SolverConfig("compete_4thread", 4, "compete", ("--parallel-mode=4,compete",)),
            ]
        )
    return configs


def representative_definitions():
    by_id = {definition.branch_id: definition for definition in branch_definitions()}
    return [by_id[branch_id] for branch_id in REPRESENTATIVE_BRANCHES]


def run_benchmark(output_dir: Path = DEFAULT_OUTPUT_DIR, timeout_seconds: int = TIMEOUT_SECONDS) -> list[BenchmarkResult]:
    _ensure_layout(output_dir)
    help_text = clingo_help()
    (output_dir / "reports" / "clingo_help_advanced.txt").write_text(help_text, encoding="utf-8")
    (output_dir / "reports" / "clingo_version.txt").write_text(solver_version(), encoding="utf-8")
    results: list[BenchmarkResult] = []
    for definition in representative_definitions():
        for config in supported_configs(help_text):
            results.append(_run_one(output_dir, definition, config, timeout_seconds))
    _write_summary(output_dir / "reports" / "benchmark_results.json", results, help_text)
    write_report(output_dir / "reports" / "benchmark_report.md", results, help_text)
    return results


def _run_one(output_dir: Path, definition, config: SolverConfig, timeout_seconds: int) -> BenchmarkResult:
    run_id = f"{definition.branch_id}__{config.config_id}"
    raw_dir = output_dir / "raw" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    instance_path = raw_dir / "instance.lp"
    raw_json_path = raw_dir / "solver.json"
    stderr_path = raw_dir / "stderr.log"
    resource_log_path = output_dir / "logs" / f"{run_id}.resources.jsonl"
    metadata_path = raw_dir / "metadata.json"
    instance_path.write_text(generate_branch_instance(definition.final_layer, definition.forbid_l5, definition.l5_count), encoding="utf-8")
    resource_log_path.write_text("", encoding="utf-8")
    solver_options = ["--outf=2", "--stats=2", "-n", "1", f"--time-limit={timeout_seconds}", f"--seed={SEED}", *config.solver_options]
    command = [*CLINGO_COMMAND, *solver_options, str(COMMON), str(TARGET_V), str(instance_path)]
    metadata_path.write_text(
        json.dumps(
            {
                "branch": definition.__dict__,
                "config": asdict(config),
                "command": command,
                "solver_version": solver_version(),
                "environment": _environment_metadata(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    started = time.perf_counter()
    peak_rss: int | None = None
    snapshots = 0
    with raw_json_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, text=True)
        while process.poll() is None:
            snapshot = _process_snapshot(process.pid)
            if snapshot is not None:
                snapshots += 1
                rss = snapshot.get("rss_kb")
                if isinstance(rss, int):
                    peak_rss = rss if peak_rss is None else max(peak_rss, rss)
                with resource_log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"elapsed_seconds": time.perf_counter() - started, **snapshot}, sort_keys=True) + "\n")
            time.sleep(1.0)
    runtime = time.perf_counter() - started
    stdout_text = raw_json_path.read_text(encoding="utf-8") if raw_json_path.exists() else ""
    clingo_result = None
    stats = None
    error_message = None
    try:
        payload = json.loads(stdout_text) if stdout_text.strip() else {}
        raw_result = payload.get("Result")
        clingo_result = raw_result if isinstance(raw_result, str) else None
        stats = payload.get("Stats") if isinstance(payload.get("Stats"), dict) else None
        if clingo_result == "SATISFIABLE":
            status = "SAT"
        elif clingo_result == "UNSATISFIABLE":
            status = "UNSAT"
        elif clingo_result == "UNKNOWN":
            status = "TIMEOUT"
        else:
            status = "ERROR"
            error_message = f"unexpected clingo result {clingo_result!r}"
    except Exception as exc:  # noqa: BLE001
        status = "ERROR"
        error_message = str(exc)
    choices, conflicts, restarts, solving_time = _extract_stats(stats)
    result = BenchmarkResult(
        branch_id=definition.branch_id,
        config_id=config.config_id,
        status=status,
        clingo_result=clingo_result,
        runtime_seconds=runtime,
        peak_rss_kb=peak_rss,
        cpu_snapshots=snapshots,
        command=[str(part) for part in command],
        solver_options=solver_options,
        instance_path=str(instance_path),
        raw_json_path=str(raw_json_path),
        stderr_path=str(stderr_path),
        resource_log_path=str(resource_log_path),
        stats=stats,
        choices=choices,
        conflicts=conflicts,
        restarts=restarts,
        solving_time=solving_time,
        error_message=error_message,
    )
    (raw_dir / "result.json").write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _extract_stats(stats: dict[str, Any] | None) -> tuple[float | None, float | None, float | None, float | None]:
    if not stats:
        return None, None, None, None
    summary = stats.get("Summary") if isinstance(stats.get("Summary"), dict) else {}
    solving = stats.get("Solving") if isinstance(stats.get("Solving"), dict) else {}
    choices = _find_numeric(stats, "Choices")
    conflicts = _find_numeric(stats, "Conflicts")
    restarts = _find_numeric(stats, "Restarts")
    solving_time = None
    times = summary.get("Times") if isinstance(summary, dict) else None
    if isinstance(times, dict):
        solving_time = _coerce_number(times.get("Solve") or times.get("Solving"))
    if solving_time is None:
        solving_time = _find_numeric(solving, "Time")
    return choices, conflicts, restarts, solving_time


def _find_numeric(obj: Any, key: str) -> float | None:
    if isinstance(obj, dict):
        for current_key, value in obj.items():
            if current_key == key:
                found = _coerce_number(value)
                if found is not None:
                    return found
            nested = _find_numeric(value, key)
            if nested is not None:
                return nested
    elif isinstance(obj, list):
        for item in obj:
            nested = _find_numeric(item, key)
            if nested is not None:
                return nested
    return None


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def select_config(results: list[BenchmarkResult]) -> tuple[str, str]:
    by_config: dict[str, list[BenchmarkResult]] = {}
    for result in results:
        by_config.setdefault(result.config_id, []).append(result)
    completions = {config: sum(1 for result in rows if result.status in {"SAT", "UNSAT"}) for config, rows in by_config.items()}
    max_completed = max(completions.values())
    candidates = [config for config, count in completions.items() if count == max_completed]
    if len(candidates) == 1:
        return candidates[0], f"selected by completion count: {completions}"
    if max_completed > 0:
        completed_time = {
            config: sum(result.runtime_seconds for result in by_config[config] if result.status in {"SAT", "UNSAT"})
            for config in candidates
        }
        selected = min(candidates, key=lambda config: completed_time[config])
        return selected, f"completion tie; selected lower completed-job wall time: {completed_time}"
    baseline = "baseline_1thread"
    baseline_rss = max((result.peak_rss_kb or 0) for result in by_config.get(baseline, []))
    for config in candidates:
        if config == baseline:
            continue
        rows = by_config[config]
        ok = True
        for result in rows:
            branch_baseline = next(row for row in by_config[baseline] if row.branch_id == result.branch_id)
            base_rate = _conflict_rate(branch_baseline)
            rate = _conflict_rate(result)
            if base_rate is None or rate is None or rate < 3 * base_rate:
                ok = False
            if result.peak_rss_kb and baseline_rss and result.peak_rss_kb > 1.5 * baseline_rss:
                ok = False
        if ok:
            return config, "no completions; selected multi-thread config by >=3x conflicts/sec without substantially higher RSS"
    return baseline, "no completions; defaulted to one-thread-per-branch outer parallelism"


def _conflict_rate(result: BenchmarkResult) -> float | None:
    if result.conflicts is None or result.runtime_seconds <= 0:
        return None
    return result.conflicts / result.runtime_seconds


def write_report(path: Path, results: list[BenchmarkResult], help_text: str) -> None:
    selected, rationale = select_config(results)
    lines = [
        "# V(4,9), Depth-6 Solver Configuration Benchmark",
        "",
        "## Clingo",
        "",
        solver_version().strip(),
        "",
        "Help-confirmed parallel syntax: `--parallel-mode=<n>[,<mode>]`; supported modes include `compete` and `split`.",
        "",
        "## Tested Configurations",
        "",
        "| config | options |",
        "| --- | --- |",
    ]
    configs = {config.config_id: config for config in supported_configs(help_text)}
    for config in configs.values():
        lines.append(f"| {config.config_id} | {' '.join(config.solver_options) if config.solver_options else 'default single-thread'} --seed={SEED} |")
    lines.extend(
        [
            "",
            "## Results",
            "",
            "| branch | config | status | runtime s | peak RSS KB | choices | conflicts | restarts | solving time |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for result in results:
        lines.append(
            f"| {result.branch_id} | {result.config_id} | {result.status} | {result.runtime_seconds:.3f} | "
            f"{'' if result.peak_rss_kb is None else result.peak_rss_kb} | {_fmt(result.choices)} | {_fmt(result.conflicts)} | "
            f"{_fmt(result.restarts)} | {_fmt(result.solving_time)} |"
        )
    lines.extend(["", "## Heuristic Recommendation", "", f"Selected configuration: `{selected}`.", "", f"Rationale: {rationale}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def _write_summary(path: Path, results: list[BenchmarkResult], help_text: str) -> None:
    selected, rationale = select_config(results)
    payload = {
        "clingo_version": solver_version(),
        "parallel_help_confirmed": "--parallel-mode=<n>[,<mode>]" in help_text or "--parallel-mode,-t <arg>" in help_text,
        "seed": SEED,
        "timeout_seconds": TIMEOUT_SECONDS,
        "selected_config": selected,
        "selection_rationale": rationale,
        "results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _process_snapshot(pid: int) -> dict[str, Any] | None:
    completed = subprocess.run(["ps", "-p", str(pid), "-o", "pid=,etime=,pcpu=,pmem=,rss=,vsz=,stat="], check=False, capture_output=True, text=True)
    line = completed.stdout.strip()
    if completed.returncode != 0 or not line:
        return None
    parts = line.split()
    if len(parts) < 7:
        return {"raw_ps": line}
    return {"pid": int(parts[0]), "etime": parts[1], "cpu_percent": float(parts[2]), "mem_percent": float(parts[3]), "rss_kb": int(parts[4]), "vsz_kb": int(parts[5]), "stat": parts[6]}


def _environment_metadata() -> dict[str, Any]:
    return {"python": platform.python_version(), "platform": platform.platform(), "cpu_count": os.cpu_count(), "gpu_use": "none"}


def _ensure_layout(output_dir: Path) -> None:
    for name in ("raw", "reports", "logs"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout-seconds", type=int, default=TIMEOUT_SECONDS)
    args = parser.parse_args()
    results = run_benchmark(args.output_dir, args.timeout_seconds)
    selected, rationale = select_config(results)
    print(f"selected_config={selected}")
    print(rationale)
    print(args.output_dir / "reports" / "benchmark_report.md")


if __name__ == "__main__":
    main()
