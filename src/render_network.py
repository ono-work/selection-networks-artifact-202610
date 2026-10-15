"""Human-readable rendering for canonical selection-network JSON witnesses."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from src.network import apply_layer, validate_network
from src.verify import verify_binary

SelectionKind = Literal["V", "U"]


@dataclass(frozen=True)
class Witness:
    """Canonical network witness plus its metadata."""

    kind: SelectionKind
    n: int
    t: int
    depth: int
    network: list[list[tuple[int, int]]]


@dataclass(frozen=True)
class TraceResult:
    """Layer-by-layer simulation trace for one explicit input."""

    input_values: tuple[int, ...]
    states: tuple[tuple[int, ...], ...]
    final_output: tuple[int, ...]
    target_satisfied: bool


@dataclass(frozen=True)
class Provenance:
    """Exact-depth provenance reconstructed from experiment summaries."""

    shorter_unsat_depths: tuple[int, ...]
    sat_depth: int | None
    verified_sat: bool


def load_witness(path: Path | str) -> Witness:
    """Load and validate a canonical network JSON witness."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    kind = data["kind"]
    if kind not in {"V", "U"}:
        raise ValueError(f"kind must be 'V' or 'U', got {kind!r}")
    n = int(data["n"])
    t = int(data["t"])
    layers = [
        [(_as_int_pair(comparator)) for comparator in layer]
        for layer in data["layers"]
    ]
    depth = int(data["depth"])
    if depth != len(layers):
        raise ValueError(f"declared depth {depth} does not match {len(layers)} layers")
    validate_network(layers, n)
    return Witness(kind=kind, n=n, t=t, depth=depth, network=layers)


def load_verifier_result(path: Path | str | None) -> dict[str, Any] | None:
    """Load verifier JSON when available."""
    if path is None:
        return None
    verifier_path = Path(path)
    if not verifier_path.exists():
        return None
    return json.loads(verifier_path.read_text(encoding="utf-8"))


def load_provenance(path: Path | str | None, witness: Witness) -> Provenance | None:
    """Load exactness provenance from an experiment summary CSV when available."""
    if path is None:
        return None
    summary_path = Path(path)
    if not summary_path.exists():
        return None

    shorter_unsat: list[int] = []
    sat_depth: int | None = None
    verified_sat = False
    with summary_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("kind") != witness.kind:
                continue
            if int(row["n"]) != witness.n or int(row["t"]) != witness.t:
                continue
            depth = int(row["depth"])
            status = row["status"]
            if depth < witness.depth and status == "UNSAT":
                shorter_unsat.append(depth)
            if depth == witness.depth and status == "SAT":
                sat_depth = depth
                verified_sat = row.get("verifier_ok") == "True"

    return Provenance(tuple(sorted(shorter_unsat)), sat_depth, verified_sat)


def parse_input_vector(text: str, *, n: int) -> tuple[int, ...]:
    """Parse either a binary string or comma-separated integers."""
    stripped = text.strip()
    if not stripped:
        raise ValueError("input vector must not be empty")
    if "," in stripped:
        values = tuple(int(part.strip()) for part in stripped.split(","))
    elif set(stripped) <= {"0", "1"}:
        values = tuple(int(char) for char in stripped)
    else:
        raise ValueError("input must be a binary string or comma-separated integers")
    if len(values) != n:
        raise ValueError(f"input length must be {n}, got {len(values)}")
    return values


def trace_network(witness: Witness, input_values: tuple[int, ...]) -> TraceResult:
    """Return the input, each post-layer state, final output, and target result."""
    if len(input_values) != witness.n:
        raise ValueError(f"input length must be {witness.n}, got {len(input_values)}")
    state = list(input_values)
    states: list[tuple[int, ...]] = [tuple(state)]
    for layer in witness.network:
        state = apply_layer(state, layer)
        states.append(tuple(state))
    final_output = states[-1]
    return TraceResult(
        input_values=tuple(input_values),
        states=tuple(states),
        final_output=final_output,
        target_satisfied=target_satisfied(
            witness.kind,
            witness.t,
            tuple(input_values),
            final_output,
        ),
    )


def target_satisfied(
    kind: SelectionKind,
    t: int,
    input_values: tuple[int, ...],
    output_values: tuple[int, ...],
) -> bool:
    """Check the V- or U-type target for one concrete input/output pair."""
    expected = tuple(sorted(input_values)[:t])
    prefix = output_values[:t]
    if kind == "V":
        return prefix == expected
    return tuple(sorted(prefix)) == expected


def render_markdown(
    witness: Witness,
    *,
    verifier: dict[str, Any] | None = None,
    provenance: Provenance | None = None,
    traces: list[tuple[str, TraceResult]] | None = None,
) -> str:
    """Render a deterministic Markdown witness dossier."""
    counts = [len(layer) for layer in witness.network]
    lines = [
        f"# {witness.kind}-type witness n={witness.n}, t={witness.t}, depth={witness.depth}",
        "",
        "This is one depth-optimal witness selected from a SAT model. It is not "
        "claimed to be canonical, comparator-count optimal, or minimum-size.",
        "",
        "## Metadata",
        "",
        f"- kind: {witness.kind}",
        f"- n: {witness.n}",
        f"- t: {witness.t}",
        f"- depth: {witness.depth}",
        f"- total comparator count: {sum(counts)}",
        f"- layer comparator counts: {', '.join(str(count) for count in counts)}",
        "",
        "Wire numbers increase from top to bottom. Layers progress left to right.",
        "",
        "## Layers",
        "",
    ]
    for index, layer in enumerate(witness.network, start=1):
        lines.append(f"- Layer {index}: {_format_layer(layer)}")

    lines.extend(["", "## Verification", ""])
    if verifier is None:
        independent = verify_binary(witness.network, witness.n, witness.t, witness.kind)
        lines.append(f"- independent verifier result: {independent.ok} ({independent.message})")
    else:
        lines.append(
            "- independent verifier result: "
            f"{verifier.get('ok')} ({verifier.get('message')})"
        )

    lines.extend(["", "## Exactness Provenance", ""])
    if provenance is None:
        lines.append("- exactness provenance: unavailable")
    else:
        if provenance.shorter_unsat_depths:
            depths = ", ".join(str(depth) for depth in provenance.shorter_unsat_depths)
            lines.append(f"- shorter depths checked UNSAT: {depths}")
        else:
            lines.append("- shorter depths checked UNSAT: none recorded")
        sat_status = "verified SAT" if provenance.verified_sat else "SAT"
        lines.append(f"- depth {provenance.sat_depth}: {sat_status}")

    if traces:
        lines.extend(["", "## Traces", ""])
        for label, trace in traces:
            lines.extend([f"### {label}", "", render_trace_markdown(trace), ""])
        while lines and lines[-1] == "":
            lines.pop()

    return "\n".join(lines) + "\n"


def render_trace_markdown(trace: TraceResult) -> str:
    """Render one compact Markdown table for a trace."""
    lines = [
        "| step | values |",
        "| --- | --- |",
        f"| input | {_format_values(trace.states[0])} |",
    ]
    for index, state in enumerate(trace.states[1:], start=1):
        lines.append(f"| after layer {index} | {_format_values(state)} |")
    lines.append(f"| final output | {_format_values(trace.final_output)} |")
    lines.append(f"| target satisfied | {trace.target_satisfied} |")
    return "\n".join(lines)


def render_tikz(witness: Witness) -> str:
    """Render a standalone deterministic TikZ snippet."""
    lines = [
        "\\begin{tikzpicture}[x=1.15cm,y=0.55cm,line cap=round]",
        f"  \\node[anchor=west] at (0,1) {{{witness.kind}-type $n={witness.n}$, $t={witness.t}$, depth {witness.depth}}};",
    ]
    right = witness.depth + 1
    for wire in range(1, witness.n + 1):
        y = -wire
        lines.append(f"  \\draw (0,{y}) -- ({right},{y});")
        lines.append(f"  \\node[anchor=east] at (-0.15,{y}) {{{wire}}};")
    for layer_index, layer in enumerate(witness.network, start=1):
        x = layer_index
        lines.append(f"  \\node[anchor=south] at ({x},-0.5) {{L{layer_index}}};")
        for i, j in layer:
            y_i = -i
            y_j = -j
            lines.append(f"  \\draw ({x},{y_i}) -- ({x},{y_j});")
            lines.append(f"  \\fill ({x},{y_i}) circle (0.07);")
            lines.append(f"  \\fill ({x},{y_j}) circle (0.07);")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines) + "\n"


def write_witness_files(
    *,
    network_json: Path | str,
    markdown_path: Path | str,
    tikz_path: Path | str,
    summary_csv: Path | str | None = None,
    verifier_json: Path | str | None = None,
    traces: list[tuple[str, str]] | None = None,
) -> tuple[Path, Path]:
    """Write Markdown and TikZ files for one witness."""
    witness = load_witness(network_json)
    trace_results = [
        (label, trace_network(witness, parse_input_vector(text, n=witness.n)))
        for label, text in (traces or [])
    ]
    markdown = render_markdown(
        witness,
        verifier=load_verifier_result(verifier_json),
        provenance=load_provenance(summary_csv, witness),
        traces=trace_results,
    )
    tikz = render_tikz(witness)

    md_output = Path(markdown_path)
    tex_output = Path(tikz_path)
    md_output.parent.mkdir(parents=True, exist_ok=True)
    tex_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.write_text(markdown, encoding="utf-8")
    tex_output.write_text(tikz, encoding="utf-8")
    return md_output, tex_output


def main(argv: list[str] | None = None) -> int:
    """CLI for rendering one canonical network JSON witness."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("network_json", type=Path)
    parser.add_argument("--summary-csv", type=Path)
    parser.add_argument("--verifier-json", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--tikz-output", type=Path)
    parser.add_argument(
        "--trace",
        action="append",
        default=[],
        metavar="LABEL=INPUT",
        help="Add a trace from a binary string or comma-separated integers.",
    )
    args = parser.parse_args(argv)

    witness = load_witness(args.network_json)
    traces = [_parse_trace_arg(item) for item in args.trace]
    markdown = render_markdown(
        witness,
        verifier=load_verifier_result(args.verifier_json),
        provenance=load_provenance(args.summary_csv, witness),
        traces=[
            (label, trace_network(witness, parse_input_vector(text, n=witness.n)))
            for label, text in traces
        ],
    )
    tikz = render_tikz(witness)

    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    if args.tikz_output:
        args.tikz_output.parent.mkdir(parents=True, exist_ok=True)
        args.tikz_output.write_text(tikz, encoding="utf-8")

    return 0


def _as_int_pair(value: Any) -> tuple[int, int]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"comparator must be a two-item list, got {value!r}")
    return int(value[0]), int(value[1])


def _format_layer(layer: list[tuple[int, int]]) -> str:
    if not layer:
        return "(empty)"
    return ", ".join(f"({i},{j})" for i, j in layer)


def _format_values(values: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in values)


def _parse_trace_arg(text: str) -> tuple[str, str]:
    if "=" not in text:
        raise ValueError(f"trace must be LABEL=INPUT, got {text!r}")
    label, values = text.split("=", 1)
    if not label:
        raise ValueError("trace label must not be empty")
    return label, values


if __name__ == "__main__":
    raise SystemExit(main())
