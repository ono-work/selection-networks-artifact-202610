"""Exact-depth experiment driver for V-type and U-type ASP synthesis."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

from src.generate_instance import generate_instance
from src.parse_model import network_to_json, parse_selected_network
from src.solver import CLINGO_COMMAND
from src.verify import VerificationResult, verify_binary

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "solver" / "common.lp"
TARGET_V = ROOT / "solver" / "target_v.lp"
TARGET_U = ROOT / "solver" / "target_u.lp"

DecisionStatus = Literal["SAT", "UNSAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"]
SelectionKind = Literal["V", "U"]
TARGETS: dict[SelectionKind, Path] = {"V": TARGET_V, "U": TARGET_U}


@dataclass(frozen=True)
class DepthDecision:
    """Saved result for one exact-depth feasibility decision."""

    n: int
    t: int
    kind: SelectionKind
    depth: int
    status: DecisionStatus
    command: list[str]
    solver_version: str
    runtime_seconds: float
    instance_path: str
    raw_solver_json_path: str | None
    network_json_path: str | None
    verifier_json_path: str | None
    verifier_ok: bool | None
    comparator_count: int | None
    layer_comparator_counts: list[int] | None
    error_message: str | None = None


@dataclass(frozen=True)
class ExactDepthResult:
    """Complete result for testing depths in increasing order."""

    n: int
    t: int
    kind: SelectionKind
    minimum_depth: int | None
    status: str
    decisions: list[DepthDecision]
    summary_path: str


@dataclass(frozen=True)
class MatrixCase:
    """One exact-depth matrix row specification."""

    kind: SelectionKind
    t: int
    n: int
    depths: tuple[int, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class MatrixResult:
    """One matrix case result, possibly unresolved."""

    kind: SelectionKind
    t: int
    n: int
    tested_depths: list[int]
    timeout_seconds: int
    minimum_depth: int | None
    status: str
    decisions: list[DepthDecision]
    summary_path: str


CALIBRATION_EXPECTED: dict[tuple[SelectionKind, int, int], int] = {
    **{("V", 1, n): math.ceil(math.log2(n)) for n in range(1, 9)},
    **{("U", 1, n): math.ceil(math.log2(n)) for n in range(1, 9)},
    ("V", 2, 2): 1,
    ("V", 2, 4): 3,
    ("V", 2, 8): 5,
    ("U", 2, 2): 0,
    ("U", 2, 4): 2,
    ("U", 2, 8): 4,
}


def solver_version() -> str:
    """Return the clingo version string used by the experiment driver."""
    completed = subprocess.run(
        (*CLINGO_COMMAND, "--version"),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or f"version command failed: {completed.returncode}"
    return completed.stdout.strip()


def run_exact_depth(
    n: int,
    t: int,
    *,
    kind: SelectionKind,
    output_dir: Path | str,
    max_depth: int | None = None,
    time_limit_seconds: int = 10,
) -> ExactDepthResult:
    """Test exact depths ``0,1,2,...`` for one fixed ``(kind,n,t)``.

    A minimum depth is declared only when every smaller tested depth is UNSAT and
    the first SAT network passes the independent Python verifier.
    """
    _validate_case(kind=kind, n=n, t=t, time_limit_seconds=time_limit_seconds)
    stop_depth = max_depth if max_depth is not None else max(0, n)
    case = MatrixCase(
        kind=kind,
        t=t,
        n=n,
        depths=tuple(range(stop_depth + 1)),
        timeout_seconds=time_limit_seconds,
    )
    matrix_result = _run_matrix_case(case, output_dir=Path(output_dir), solver_version_text=solver_version())
    return ExactDepthResult(
        n=n,
        t=t,
        kind=kind,
        minimum_depth=matrix_result.minimum_depth,
        status=matrix_result.status,
        decisions=matrix_result.decisions,
        summary_path=matrix_result.summary_path,
    )


def run_exact_depth_v(
    n: int,
    t: int,
    *,
    output_dir: Path | str,
    max_depth: int | None = None,
    time_limit_seconds: int = 10,
) -> ExactDepthResult:
    """Backward-compatible V-type exact-depth driver."""
    return run_exact_depth(
        n,
        t,
        kind="V",
        output_dir=output_dir,
        max_depth=max_depth,
        time_limit_seconds=time_limit_seconds,
    )


def run_exact_depth_u(
    n: int,
    t: int,
    *,
    output_dir: Path | str,
    max_depth: int | None = None,
    time_limit_seconds: int = 10,
) -> ExactDepthResult:
    """U-type exact-depth driver."""
    return run_exact_depth(
        n,
        t,
        kind="U",
        output_dir=output_dir,
        max_depth=max_depth,
        time_limit_seconds=time_limit_seconds,
    )


def run_v_calibration(
    *,
    output_dir: Path | str,
    time_limit_seconds: int = 10,
) -> list[ExactDepthResult]:
    """Run the V-type calibration subset."""
    return _run_calibration_subset("V", output_dir=Path(output_dir), time_limit_seconds=time_limit_seconds)


def run_u_calibration(
    *,
    output_dir: Path | str,
    time_limit_seconds: int = 10,
) -> list[ExactDepthResult]:
    """Run the U-type calibration subset."""
    return _run_calibration_subset("U", output_dir=Path(output_dir), time_limit_seconds=time_limit_seconds)


def run_calibration_suite(
    *,
    output_dir: Path | str,
    time_limit_seconds: int = 10,
) -> list[ExactDepthResult]:
    """Run all locked-down calibration cells and assert their exact depths."""
    root = Path(output_dir)
    results: list[ExactDepthResult] = []
    for kind, t, n, expected_depth in calibration_cases():
        result = run_exact_depth(
            n,
            t,
            kind=kind,
            output_dir=root / f"{kind}_t{t}_n{n}",
            max_depth=expected_depth,
            time_limit_seconds=time_limit_seconds,
        )
        _assert_expected_depth(result, expected_depth)
        results.append(result)

    write_calibration_markdown(root / "calibration_summary.md", results)
    return results


def calibration_cases() -> list[tuple[SelectionKind, int, int, int]]:
    """Return locked-down calibration cases in stable report order."""
    cases: list[tuple[SelectionKind, int, int, int]] = []
    for kind in ("V", "U"):
        for n in range(1, 9):
            cases.append((kind, 1, n, CALIBRATION_EXPECTED[(kind, 1, n)]))
    for kind in ("V", "U"):
        for n in (2, 4, 8):
            cases.append((kind, 2, n, CALIBRATION_EXPECTED[(kind, 2, n)]))
    return cases


def run_experiment_matrix(
    cases: Iterable[MatrixCase],
    *,
    output_dir: Path | str,
) -> list[MatrixResult]:
    """Run an explicit matrix of exact-depth cases."""
    root = Path(output_dir)
    version = solver_version()
    results: list[MatrixResult] = []
    for case in cases:
        _validate_case(
            kind=case.kind,
            n=case.n,
            t=case.t,
            time_limit_seconds=case.timeout_seconds,
        )
        result = _run_matrix_case(
            case,
            output_dir=root / f"{case.kind}_t{case.t}_n{case.n}",
            solver_version_text=version,
        )
        results.append(result)

    write_matrix_summary(root / "summary.csv", results)
    write_matrix_summary_json(root / "summary.json", results)
    return results


def smoke_matrix_cases(
    *,
    timeout_seconds: int = 10,
    max_n: int = 6,
    include_u_dual_cross_checks: bool = False,
) -> list[MatrixCase]:
    """Return the Milestone 3B smoke matrix, capped at ``n <= 6``.

    By default U-type cases with ``t > n / 2`` are omitted because their
    depths are derived from ``U(n - t, n)`` by mirror duality. Set
    ``include_u_dual_cross_checks`` when those cases are intentionally being
    run as independent cross-checks.
    """
    if max_n > 6:
        raise ValueError("smoke matrix must not run instances with n > 6")
    cases: list[MatrixCase] = []
    for kind in ("V", "U"):
        for n in range(1, max_n + 1):
            for t in range(1, min(4, n) + 1):
                if kind == "U" and t > n // 2 and not include_u_dual_cross_checks:
                    continue
                cases.append(
                    MatrixCase(
                        kind=kind,
                        t=t,
                        n=n,
                        depths=tuple(range(n + 1)),
                        timeout_seconds=timeout_seconds,
                    )
                )
    return cases


def run_smoke_matrix(
    *,
    output_dir: Path | str,
    time_limit_seconds: int = 10,
    max_n: int = 6,
    include_u_dual_cross_checks: bool = False,
) -> list[MatrixResult]:
    """Run the complete small-instance smoke matrix."""
    return run_experiment_matrix(
        smoke_matrix_cases(
            timeout_seconds=time_limit_seconds,
            max_n=max_n,
            include_u_dual_cross_checks=include_u_dual_cross_checks,
        ),
        output_dir=output_dir,
    )


def write_calibration_markdown(path: Path | str, results: list[ExactDepthResult]) -> None:
    """Write a compact Markdown summary table for calibration results."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| kind | t | n | status | minimum depth | tested depths | runtime seconds | comparators | layer counts | summary |",
        "| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for result in results:
        total_runtime = sum(decision.runtime_seconds for decision in result.decisions)
        tested = ",".join(str(decision.depth) for decision in result.decisions)
        sat = _first_verified_sat(result.decisions)
        comparators = "" if sat is None else str(sat.comparator_count)
        layer_counts = "" if sat is None else _format_layer_counts(sat.layer_comparator_counts)
        minimum = "" if result.minimum_depth is None else str(result.minimum_depth)
        lines.append(
            f"| {result.kind} | {result.t} | {result.n} | {result.status} | {minimum} | "
            f"{tested} | {total_runtime:.3f} | {comparators} | {layer_counts} | {result.summary_path} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_matrix_summary(path: Path | str, results: list[MatrixResult]) -> None:
    """Write one summary row per matrix case."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "kind",
        "t",
        "n",
        "tested_depths",
        "timeout_seconds",
        "status",
        "minimum_depth",
        "runtime_seconds",
        "first_sat_depth",
        "comparator_count",
        "layer_comparator_counts",
        "summary_path",
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            sat = _first_verified_sat(result.decisions)
            writer.writerow(
                {
                    "kind": result.kind,
                    "t": result.t,
                    "n": result.n,
                    "tested_depths": ",".join(str(depth) for depth in result.tested_depths),
                    "timeout_seconds": result.timeout_seconds,
                    "status": result.status,
                    "minimum_depth": "" if result.minimum_depth is None else result.minimum_depth,
                    "runtime_seconds": f"{sum(d.runtime_seconds for d in result.decisions):.6f}",
                    "first_sat_depth": "" if sat is None else sat.depth,
                    "comparator_count": "" if sat is None else sat.comparator_count,
                    "layer_comparator_counts": "" if sat is None else _format_layer_counts(sat.layer_comparator_counts),
                    "summary_path": result.summary_path,
                }
            )


def write_matrix_summary_json(path: Path | str, results: list[MatrixResult]) -> None:
    """Write the matrix summary as JSON for downstream tooling."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for result in results:
        sat = _first_verified_sat(result.decisions)
        payload.append(
            {
                "kind": result.kind,
                "t": result.t,
                "n": result.n,
                "tested_depths": result.tested_depths,
                "timeout_seconds": result.timeout_seconds,
                "status": result.status,
                "minimum_depth": result.minimum_depth,
                "runtime_seconds": sum(d.runtime_seconds for d in result.decisions),
                "first_sat_depth": None if sat is None else sat.depth,
                "comparator_count": None if sat is None else sat.comparator_count,
                "layer_comparator_counts": None if sat is None else sat.layer_comparator_counts,
                "summary_path": result.summary_path,
            }
        )
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown_report(
    path: Path | str,
    *,
    calibration_results: list[ExactDepthResult],
    smoke_results: list[MatrixResult],
) -> None:
    """Write a concise calibration and smoke report."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    confirmed = [result for result in smoke_results if result.minimum_depth is not None]
    unresolved = [result for result in smoke_results if result.minimum_depth is None]

    lines = [
        "# Milestone 3B Calibration and Smoke Report",
        "",
        "This report records baseline ASP synthesis outcomes only; it is not a research-results claim.",
        "",
        "## Locked Calibration",
        "",
        "| kind | t | n | exact depth | runtime seconds | comparators | layer counts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in calibration_results:
        sat = _first_verified_sat(result.decisions)
        lines.append(
            f"| {result.kind} | {result.t} | {result.n} | {result.minimum_depth} | "
            f"{sum(d.runtime_seconds for d in result.decisions):.3f} | "
            f"{'' if sat is None else sat.comparator_count} | "
            f"{'' if sat is None else _format_layer_counts(sat.layer_comparator_counts)} |"
        )

    lines.extend(
        [
            "",
            "## Smoke Matrix Confirmed Exact Cells",
            "",
            "| kind | t | n | exact depth | tested depths | runtime seconds | comparators | layer counts |",
            "| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |",
        ]
    )
    for result in confirmed:
        sat = _first_verified_sat(result.decisions)
        lines.append(
            f"| {result.kind} | {result.t} | {result.n} | {result.minimum_depth} | "
            f"{','.join(str(d) for d in result.tested_depths)} | "
            f"{sum(d.runtime_seconds for d in result.decisions):.3f} | "
            f"{'' if sat is None else sat.comparator_count} | "
            f"{'' if sat is None else _format_layer_counts(sat.layer_comparator_counts)} |"
        )

    lines.extend(
        [
            "",
            "## Smoke Matrix Unresolved Cells",
            "",
        ]
    )
    if unresolved:
        lines.extend(
            [
                "| kind | t | n | status | tested depths | runtime seconds |",
                "| --- | ---: | ---: | --- | --- | ---: |",
            ]
        )
        for result in unresolved:
            lines.append(
                f"| {result.kind} | {result.t} | {result.n} | {result.status} | "
                f"{','.join(str(d) for d in result.tested_depths)} | "
                f"{sum(d.runtime_seconds for d in result.decisions):.3f} |"
            )
    else:
        lines.append("No unresolved smoke cells.")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_calibration_subset(
    kind: SelectionKind,
    *,
    output_dir: Path,
    time_limit_seconds: int,
) -> list[ExactDepthResult]:
    results: list[ExactDepthResult] = []
    for case_kind, t, n, expected_depth in calibration_cases():
        if case_kind != kind:
            continue
        result = run_exact_depth(
            n,
            t,
            kind=kind,
            output_dir=output_dir / f"{kind}_t{t}_n{n}",
            max_depth=expected_depth,
            time_limit_seconds=time_limit_seconds,
        )
        _assert_expected_depth(result, expected_depth)
        results.append(result)
    write_calibration_markdown(output_dir / "calibration_summary.md", results)
    return results


def _run_matrix_case(
    case: MatrixCase,
    *,
    output_dir: Path,
    solver_version_text: str,
) -> MatrixResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    decisions: list[DepthDecision] = []
    for depth in case.depths:
        decision = _run_one_depth(
            case.n,
            case.t,
            depth,
            kind=case.kind,
            output_dir=output_dir,
            solver_version_text=solver_version_text,
            time_limit_seconds=case.timeout_seconds,
        )
        decisions.append(decision)
        _write_depth_summary(output_dir / "summary.csv", decisions)
        if decision.status in {"SAT", "TIMEOUT", "ERROR", "VERIFICATION_FAILED"}:
            break

    minimum_depth, status = _classify_matrix_result(decisions)
    result = MatrixResult(
        kind=case.kind,
        t=case.t,
        n=case.n,
        tested_depths=[decision.depth for decision in decisions],
        timeout_seconds=case.timeout_seconds,
        minimum_depth=minimum_depth,
        status=status,
        decisions=decisions,
        summary_path=str(output_dir / "summary.csv"),
    )
    _write_case_result(output_dir / "case_result.json", result)
    return result


def _run_one_depth(
    n: int,
    t: int,
    depth: int,
    *,
    kind: SelectionKind,
    output_dir: Path,
    solver_version_text: str,
    time_limit_seconds: int,
) -> DepthDecision:
    depth_dir = output_dir / f"depth_{depth:02d}"
    depth_dir.mkdir(parents=True, exist_ok=True)
    instance_path = depth_dir / "instance.lp"
    raw_solver_path = depth_dir / "solver.json"
    metadata_path = depth_dir / "decision.json"
    network_path = depth_dir / "network.json"
    verifier_path = depth_dir / "verifier.json"

    instance_path.write_text(generate_instance(n, t, depth), encoding="utf-8")
    command = [
        *CLINGO_COMMAND,
        "--outf=2",
        f"--time-limit={time_limit_seconds}",
        "-n",
        "1",
        str(COMMON),
        str(TARGETS[kind]),
        str(instance_path),
    ]

    start = time.perf_counter()
    stdout = ""
    stderr = ""
    returncode: int | None = None
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=time_limit_seconds + 5,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        timed_out = True
    runtime = time.perf_counter() - start
    raw_solver_path.write_text(stdout, encoding="utf-8")

    status: DecisionStatus
    verifier_result: VerificationResult | None = None
    verifier_json_path: str | None = None
    network_json_path: str | None = None
    comparator_count: int | None = None
    layer_comparator_counts: list[int] | None = None
    error_message: str | None = None

    try:
        payload: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
        result = payload.get("Result")
        if timed_out or result == "UNKNOWN":
            status = "TIMEOUT"
        elif result == "SATISFIABLE":
            network = parse_selected_network(stdout, n=n, depth=depth)
            layer_comparator_counts = [len(layer) for layer in network]
            comparator_count = sum(layer_comparator_counts)
            network_payload = network_to_json(network, n=n, t=t, kind=kind)
            network_path.write_text(
                json.dumps(network_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            network_json_path = str(network_path)
            verifier_result = verify_binary(network, n=n, t=t, kind=kind)
            verifier_path.write_text(
                json.dumps(asdict(verifier_result), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            verifier_json_path = str(verifier_path)
            if verifier_result.ok:
                status = "SAT"
            else:
                status = "VERIFICATION_FAILED"
                error_message = verifier_result.message
        elif result == "UNSATISFIABLE":
            status = "UNSAT"
        else:
            status = "ERROR"
            error_message = f"unexpected clingo result {result!r}"
    except Exception as exc:  # noqa: BLE001 - persisted as experiment artifact
        status = "ERROR"
        error_message = str(exc)

    if status == "ERROR" and stderr and error_message is None:
        error_message = stderr.strip()
    if status == "ERROR" and returncode not in (0, None):
        suffix = f"clingo exited with return code {returncode}"
        error_message = f"{error_message}; {suffix}" if error_message else suffix

    decision = DepthDecision(
        n=n,
        t=t,
        kind=kind,
        depth=depth,
        status=status,
        command=[str(part) for part in command],
        solver_version=solver_version_text,
        runtime_seconds=runtime,
        instance_path=str(instance_path),
        raw_solver_json_path=str(raw_solver_path),
        network_json_path=network_json_path,
        verifier_json_path=verifier_json_path,
        verifier_ok=None if verifier_result is None else verifier_result.ok,
        comparator_count=comparator_count,
        layer_comparator_counts=layer_comparator_counts,
        error_message=error_message,
    )
    metadata_path.write_text(
        json.dumps(asdict(decision), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return decision


def _classify_matrix_result(decisions: list[DepthDecision]) -> tuple[int | None, str]:
    if not decisions:
        return None, "UNRESOLVED"
    for index, decision in enumerate(decisions):
        if decision.status == "SAT":
            shorter_are_unsat = all(item.status == "UNSAT" for item in decisions[:index])
            if shorter_are_unsat and decision.verifier_ok:
                return decision.depth, "MINIMUM_FOUND"
            return None, "SAT_UNVERIFIED"
        if decision.status in {"TIMEOUT", "ERROR", "VERIFICATION_FAILED"}:
            return None, decision.status
    return None, "MAX_DEPTH_REACHED"


def _first_verified_sat(decisions: list[DepthDecision]) -> DepthDecision | None:
    for decision in decisions:
        if decision.status == "SAT" and decision.verifier_ok:
            return decision
    return None


def _write_depth_summary(path: Path, decisions: list[DepthDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(decisions[0]).keys()))
        writer.writeheader()
        for decision in decisions:
            writer.writerow(asdict(decision))


def _write_case_result(path: Path, result: MatrixResult) -> None:
    path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _assert_expected_depth(result: ExactDepthResult, expected_depth: int) -> None:
    if result.status != "MINIMUM_FOUND" or result.minimum_depth != expected_depth:
        raise AssertionError(
            f"{result.kind}({result.t},{result.n}) expected minimum depth "
            f"{expected_depth}, got status={result.status}, depth={result.minimum_depth}"
        )


def _validate_case(*, kind: SelectionKind, n: int, t: int, time_limit_seconds: int) -> None:
    if n < 0:
        raise ValueError(f"n must be nonnegative, got {n}")
    if not 0 <= t <= n:
        raise ValueError(f"t must satisfy 0 <= t <= n, got t={t}, n={n}")
    if kind not in TARGETS:
        raise ValueError(f"kind must be one of {sorted(TARGETS)}, got {kind!r}")
    if time_limit_seconds <= 0:
        raise ValueError("time_limit_seconds must be positive")


def _format_layer_counts(layer_counts: list[int] | None) -> str:
    if layer_counts is None:
        return ""
    return ",".join(str(count) for count in layer_counts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int)
    parser.add_argument("--t", type=int)
    parser.add_argument("--kind", choices=sorted(TARGETS), default="V")
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/v_exact"))
    parser.add_argument("--max-depth", type=int)
    parser.add_argument("--time-limit", type=int, default=10)
    parser.add_argument("--calibration", action="store_true")
    parser.add_argument("--calibration-suite", action="store_true")
    parser.add_argument("--smoke-matrix", action="store_true")
    args = parser.parse_args()

    if args.calibration_suite:
        results = run_calibration_suite(
            output_dir=args.output_dir,
            time_limit_seconds=args.time_limit,
        )
        print(Path(args.output_dir) / "calibration_summary.md")
        for result in results:
            print(f"{result.kind}({result.t},{result.n}): {result.status}, depth={result.minimum_depth}")
        return

    if args.smoke_matrix:
        smoke_results = run_smoke_matrix(
            output_dir=args.output_dir,
            time_limit_seconds=args.time_limit,
        )
        print(Path(args.output_dir) / "summary.csv")
        for result in smoke_results:
            print(f"{result.kind}({result.t},{result.n}): {result.status}, depth={result.minimum_depth}")
        return

    if args.calibration:
        if args.kind == "V":
            results = run_v_calibration(
                output_dir=args.output_dir,
                time_limit_seconds=args.time_limit,
            )
        else:
            results = run_u_calibration(
                output_dir=args.output_dir,
                time_limit_seconds=args.time_limit,
            )
        print(Path(args.output_dir) / "calibration_summary.md")
        for result in results:
            print(f"{result.kind}({result.t},{result.n}): {result.status}, depth={result.minimum_depth}")
        return

    if args.n is None or args.t is None:
        parser.error("--n and --t are required unless a matrix/calibration mode is used")
    result = run_exact_depth(
        args.n,
        args.t,
        kind=args.kind,
        output_dir=args.output_dir,
        max_depth=args.max_depth,
        time_limit_seconds=args.time_limit,
    )
    print(result.summary_path)
    print(f"{result.kind}({result.t},{result.n}): {result.status}, depth={result.minimum_depth}")


if __name__ == "__main__":
    main()
