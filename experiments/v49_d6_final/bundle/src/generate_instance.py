"""Generate explicit ASP facts for fixed selection-network instances."""

from __future__ import annotations

import argparse
from itertools import product
from typing import Literal

InputMode = Literal["full", "v_boundary"]


def generate_instance(n: int, t: int, depth: int, *, input_mode: InputMode = "full") -> str:
    """Return ASP facts for a fixed ``(n,t,depth)`` input mode."""
    if n < 0:
        raise ValueError(f"n must be nonnegative, got {n}")
    if not 0 <= t <= n:
        raise ValueError(f"t must satisfy 0 <= t <= n, got t={t}, n={n}")
    if depth < 0:
        raise ValueError(f"depth must be nonnegative, got {depth}")

    lines = [
        f"n({n}).",
        f"t({t}).",
        f"depth({depth}).",
    ]

    if input_mode not in {"full", "v_boundary"}:
        raise ValueError(f"unknown input_mode {input_mode!r}")

    bit_vectors = product((0, 1), repeat=n)
    if input_mode == "v_boundary":
        bit_vectors = (bits for bits in bit_vectors if bits.count(0) <= t)

    for input_id, bits in enumerate(bit_vectors):
        lines.append(f"input({input_id}).")
        lines.append(f"zero_count({input_id},{bits.count(0)}).")
        for wire, bit in enumerate(bits, start=1):
            lines.append(f"bit({input_id},{wire},{bit}).")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", type=int)
    parser.add_argument("t", type=int)
    parser.add_argument("depth", type=int)
    parser.add_argument("--input-mode", choices=("full", "v_boundary"), default="full")
    args = parser.parse_args()
    print(generate_instance(args.n, args.t, args.depth, input_mode=args.input_mode), end="")


if __name__ == "__main__":
    main()
