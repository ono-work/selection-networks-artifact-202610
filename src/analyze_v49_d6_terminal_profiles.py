"""Terminal profile predicates for the six remaining V(4,9), depth-6 leaves."""

from __future__ import annotations

from itertools import product
from typing import NamedTuple

from src.network import Layer, apply_layer

N = 9
T = 4

LEAVES: dict[str, Layer] = {
    "A5": ((2, 3), (4, 5)),
    "A6": ((2, 3), (4, 6)),
    "B6": ((1, 6), (2, 3), (4, 5)),
    "B7": ((1, 7), (2, 3), (4, 5)),
    "B8": ((1, 8), (2, 3), (4, 5)),
    "B9": ((1, 9), (2, 3), (4, 5)),
}


class TerminalProfile(NamedTuple):
    leaf: str
    final_layer: Layer
    clauses: tuple[str, ...]


def zero_count(state: tuple[int, ...]) -> int:
    return sum(1 for bit in state if bit == 0)


def v49_output_condition(state: list[int] | tuple[int, ...]) -> bool:
    z = zero_count(tuple(state))
    return all((state[index - 1] == 0) == (z >= index) for index in range(1, T + 1))


def comparator_23_profile(state: tuple[int, ...]) -> bool:
    z = zero_count(state)
    y2, y3 = state[1], state[2]
    if z <= 1:
        return y2 == 1 and y3 == 1
    if z == 2:
        return (y2, y3).count(0) == 1
    return y2 == 0 and y3 == 0


def comparator_4q_profile(state: tuple[int, ...], q: int) -> bool:
    z = zero_count(state)
    y4, yq = state[3], state[q - 1]
    if z <= 3:
        return y4 == 1 and yq == 1
    return y4 == 0 or yq == 0


def untouched_wire1_profile(state: tuple[int, ...]) -> bool:
    z = zero_count(state)
    y1 = state[0]
    if z == 0:
        return y1 == 1
    return y1 == 0


def comparator_1s_profile(state: tuple[int, ...], s: int) -> bool:
    z = zero_count(state)
    y1, ys = state[0], state[s - 1]
    if z == 0:
        return y1 == 1 and ys == 1
    return y1 == 0 or ys == 0


def terminal_predicate(leaf: str, state: tuple[int, ...]) -> bool:
    if leaf == "A5":
        return comparator_23_profile(state) and comparator_4q_profile(state, 5) and untouched_wire1_profile(state)
    if leaf == "A6":
        return comparator_23_profile(state) and comparator_4q_profile(state, 6) and untouched_wire1_profile(state)
    if leaf in {"B6", "B7", "B8", "B9"}:
        s = int(leaf[1])
        return comparator_23_profile(state) and comparator_4q_profile(state, 5) and comparator_1s_profile(state, s)
    raise ValueError(f"unknown leaf {leaf!r}")


def direct_final_layer_condition(leaf: str, state: tuple[int, ...]) -> bool:
    return v49_output_condition(apply_layer(state, LEAVES[leaf]))


def all_binary_states() -> list[tuple[int, ...]]:
    return [tuple(bits) for bits in product((0, 1), repeat=N)]


def profiles() -> list[TerminalProfile]:
    return [
        TerminalProfile(
            leaf="A5",
            final_layer=LEAVES["A5"],
            clauses=(
                "(2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0",
                "(4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0",
                "wire 1 untouched: z=0 -> y1=1; z>=1 -> y1=0",
            ),
        ),
        TerminalProfile(
            leaf="A6",
            final_layer=LEAVES["A6"],
            clauses=(
                "(2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0",
                "(4,6): z<=3 -> y4=y6=1; z>=4 -> y4=0 or y6=0",
                "wire 1 untouched: z=0 -> y1=1; z>=1 -> y1=0",
            ),
        ),
        *[
            TerminalProfile(
                leaf=f"B{s}",
                final_layer=LEAVES[f"B{s}"],
                clauses=(
                    "(2,3): z<=1 -> y2=y3=1; z=2 -> exactly one zero; z>=3 -> y2=y3=0",
                    "(4,5): z<=3 -> y4=y5=1; z>=4 -> y4=0 or y5=0",
                    f"(1,{s}): z=0 -> y1=y{s}=1; z>=1 -> y1=0 or y{s}=0",
                ),
            )
            for s in (6, 7, 8, 9)
        ],
    ]


def equivalence_summary() -> dict[str, bool]:
    states = all_binary_states()
    return {
        leaf: all(terminal_predicate(leaf, state) == direct_final_layer_condition(leaf, state) for state in states)
        for leaf in LEAVES
    }


def main() -> None:
    for profile in profiles():
        print(profile.leaf, profile.final_layer)
        for clause in profile.clauses:
            print("  -", clause)
        print("  exhaustive_equivalence:", equivalence_summary()[profile.leaf])


if __name__ == "__main__":
    main()
