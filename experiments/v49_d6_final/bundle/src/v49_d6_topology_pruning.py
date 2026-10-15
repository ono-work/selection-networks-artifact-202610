"""Optional topology-only pruning checks for the V(4,9), depth-6 hard mode.

The constraints here are necessary conditions for V-type selection networks.
They are disabled unless a special runner explicitly appends their ASP fragment.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.network import Comparator, Network, simulate, validate_network
from src.verify import verify_binary

ROOT = Path(__file__).resolve().parents[1]
REGRESSION_REPORT = ROOT / "experiments" / "v49_d6_topology_pruning" / "regression_report.md"
VALIDATION_JSON = ROOT / "experiments" / "v49_d6_topology_pruning" / "validation.json"


@dataclass(frozen=True)
class TopologyValidation:
    status: str
    checked_cases: int
    checked_sat_witnesses: int
    failures: tuple[str, ...]


def single_zero_input(n: int, source: int) -> tuple[int, ...]:
    return tuple(0 if wire == source else 1 for wire in range(1, n + 1))


def unique_min_trajectory(network: Network, n: int, source: int) -> list[int]:
    validate_network(network, n)
    if not 1 <= source <= n:
        raise ValueError(f"source must be in 1..{n}")
    position = source
    trajectory = [position]
    for layer in network:
        for i, j in layer:
            if position == j:
                position = i
                break
            if position == i:
                break
        trajectory.append(position)
    return trajectory


def unique_min_condition(network: Network, n: int) -> bool:
    return all(unique_min_trajectory(network, n, source)[-1] == 1 for source in range(1, n + 1))


def dependency_cones(network: Network, n: int, outputs: tuple[int, ...]) -> dict[int, set[int]]:
    validate_network(network, n)
    cones: dict[int, set[int]] = {output: {output} for output in outputs}
    for layer in reversed(network):
        comparator_by_wire: dict[int, Comparator] = {}
        for i, j in layer:
            comparator_by_wire[i] = (i, j)
            comparator_by_wire[j] = (i, j)
        for output, cone in cones.items():
            expanded = set(cone)
            for wire in tuple(cone):
                comparator = comparator_by_wire.get(wire)
                if comparator is not None:
                    expanded.update(comparator)
            cones[output] = expanded
    return cones


def full_dependency_cone_condition(network: Network, n: int, t: int) -> bool:
    all_inputs = set(range(1, n + 1))
    return all(cone == all_inputs for cone in dependency_cones(network, n, tuple(range(1, t + 1))).values())


def topology_pruning_condition(network: Network, n: int, t: int) -> bool:
    return unique_min_condition(network, n) and full_dependency_cone_condition(network, n, t)


def topology_pruning_asp_constraints() -> str:
    return """\
% Optional topology-only pruning for special hard-mode V selection.
% This fragment is not part of the ordinary baseline encoding.
source(1..N) :- n(N).
zpos(S,0,S) :- source(S).
zpos(S,L,I) :- source(S), layer(L), selected(L,I,J), zpos(S,L - 1,I).
zpos(S,L,I) :- source(S), layer(L), selected(L,I,J), zpos(S,L - 1,J).
zpos(S,L,W) :- source(S), layer(L), wire(W), zpos(S,L - 1,W), not touched(L,W).
:- source(S), depth(D), not zpos(S,D,1).

depends(R,D,R) :- rank(R), depth(D).
depends(R,L - 1,W) :- rank(R), layer(L), wire(W), depends(R,L,W), not touched(L,W).
depends(R,L - 1,I) :- rank(R), layer(L), selected(L,I,J), depends(R,L,I).
depends(R,L - 1,J) :- rank(R), layer(L), selected(L,I,J), depends(R,L,I).
depends(R,L - 1,I) :- rank(R), layer(L), selected(L,I,J), depends(R,L,J).
depends(R,L - 1,J) :- rank(R), layer(L), selected(L,I,J), depends(R,L,J).
:- rank(R), wire(W), not depends(R,0,W).
"""


def network_from_json(path: Path) -> tuple[int, int, str, list[list[Comparator]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    layers = [[(int(i), int(j)) for i, j in layer] for layer in data["layers"]]
    return int(data["n"]), int(data["t"]), str(data["kind"]), layers


def validate_existing_v_artifacts(root: Path = ROOT) -> TopologyValidation:
    failures: list[str] = []
    checked_cases = 0
    checked_sat = 0
    for case_path in sorted(root.glob("experiments/baseline_n*/decisions/V_t*_n*/case_result.json")):
        data = json.loads(case_path.read_text(encoding="utf-8"))
        n = int(data["n"])
        t = int(data["t"])
        if n > 8 or t > 4:
            continue
        checked_cases += 1
        decisions = data.get("decisions", [])
        for decision in decisions:
            if decision.get("status") != "SAT":
                continue
            checked_sat += 1
            network_path = decision.get("network_json_path")
            verifier_path = decision.get("verifier_json_path")
            if not network_path or not verifier_path:
                failures.append(f"{case_path}: SAT decision lacks witness or verifier path")
                continue
            witness_n, witness_t, kind, network = network_from_json(Path(network_path))
            verifier = json.loads(Path(verifier_path).read_text(encoding="utf-8"))
            if kind != "V" or witness_n != n or witness_t != t:
                failures.append(f"{case_path}: witness metadata mismatch")
            if verifier.get("ok") is not True:
                failures.append(f"{case_path}: verifier not OK")
            verification = verify_binary(network, n=n, t=t, kind="V")
            if not verification.ok:
                failures.append(f"{case_path}: fresh verifier failed: {verification.message}")
            if not topology_pruning_condition(network, n, t):
                failures.append(f"{case_path}: SAT witness violates topology pruning")
    status = "PASSED" if checked_cases > 0 and not failures else "FAILED"
    return TopologyValidation(status, checked_cases, checked_sat, tuple(failures))


def write_regression_report(path: Path = REGRESSION_REPORT) -> TopologyValidation:
    result = validate_existing_v_artifacts()
    path.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_JSON.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_JSON.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# V(4,9) Topology Pruning Regression",
        "",
        f"Status: `{result.status}`",
        "",
        f"- checked V decision cases with n <= 8, t <= 4: {result.checked_cases}",
        f"- checked SAT witnesses: {result.checked_sat_witnesses}",
        "- UNSAT baseline decisions remain UNSAT under added pruning by monotonicity of adding constraints.",
        "- SAT baseline decisions are preserved by the listed verified witnesses satisfying both topology conditions.",
        "",
        "## Failures",
        "",
    ]
    if result.failures:
        lines.extend(f"- {failure}" for failure in result.failures)
    else:
        lines.append("None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    result = write_regression_report()
    print(result.status)
    print(REGRESSION_REPORT)


if __name__ == "__main__":
    main()
