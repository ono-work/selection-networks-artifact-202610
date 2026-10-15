"""Independent verifier for V-type and U-type selection networks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product
from random import Random
from typing import Literal, TypeAlias

Comparator: TypeAlias = tuple[int, int]
Layer: TypeAlias = Sequence[Comparator]
Network: TypeAlias = Sequence[Layer]
SelectionKind: TypeAlias = Literal["V", "U"]


@dataclass(frozen=True)
class VerificationResult:
    """Structured verifier result."""

    ok: bool
    kind: str
    n: int
    t: int
    message: str
    counterexample: tuple[int, ...] | None = None
    output: tuple[int, ...] | None = None
    expected: tuple[int, ...] | int | None = None


def _validate_parameters(n: int, t: int, kind: str) -> None:
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"n must be a nonnegative integer, got {n!r}")
    if not isinstance(t, int) or not 0 <= t <= n:
        raise ValueError(f"t must satisfy 0 <= t <= n, got t={t!r}, n={n!r}")
    if kind not in {"V", "U"}:
        raise ValueError(f"kind must be 'V' or 'U', got {kind!r}")


def _validate_network(network: Network, n: int) -> None:
    for layer_index, layer in enumerate(network):
        used: set[int] = set()
        for comparator in layer:
            if not isinstance(comparator, tuple) or len(comparator) != 2:
                raise ValueError(
                    f"invalid layer {layer_index}: comparator must be a pair, "
                    f"got {comparator!r}"
                )
            i, j = comparator
            if not isinstance(i, int) or not isinstance(j, int):
                raise ValueError(
                    f"invalid layer {layer_index}: endpoints must be integers, "
                    f"got {comparator!r}"
                )
            if not 1 <= i < j <= n:
                raise ValueError(
                    f"invalid layer {layer_index}: comparator must satisfy "
                    f"1 <= i < j <= n, got {comparator!r} with n={n}"
                )
            overlap = used.intersection((i, j))
            if overlap:
                wires = ", ".join(str(wire) for wire in sorted(overlap))
                raise ValueError(
                    f"invalid layer {layer_index}: not a matching; wire(s) "
                    f"{wires} appear more than once"
                )
            used.update((i, j))


def _run_network(network: Network, input_values: tuple[int, ...]) -> tuple[int, ...]:
    output = list(input_values)
    for layer in network:
        next_output = output.copy()
        for i, j in layer:
            left = i - 1
            right = j - 1
            if output[left] <= output[right]:
                next_output[left] = output[left]
                next_output[right] = output[right]
            else:
                next_output[left] = output[right]
                next_output[right] = output[left]
        output = next_output
    return tuple(output)


def _v_expected_prefix(zero_count: int, t: int) -> tuple[int, ...]:
    return tuple(0 if zero_count >= r else 1 for r in range(1, t + 1))


def verify_binary(network: Network, n: int, t: int, kind: SelectionKind) -> VerificationResult:
    """Exhaustively verify a network on all binary inputs of length n."""
    try:
        _validate_parameters(n, t, kind)
        _validate_network(network, n)
    except ValueError as exc:
        return VerificationResult(False, kind, n, t, str(exc))

    for bits in product((0, 1), repeat=n):
        output = _run_network(network, bits)
        zero_count = bits.count(0)
        prefix = output[:t]

        if kind == "V":
            expected_prefix = _v_expected_prefix(zero_count, t)
            if prefix != expected_prefix:
                return VerificationResult(
                    False,
                    kind,
                    n,
                    t,
                    "V-type verification failed",
                    counterexample=bits,
                    output=output,
                    expected=expected_prefix,
                )
        else:
            expected_zeros = min(t, zero_count)
            actual_zeros = prefix.count(0)
            if actual_zeros != expected_zeros:
                return VerificationResult(
                    False,
                    kind,
                    n,
                    t,
                    "U-type verification failed",
                    counterexample=bits,
                    output=output,
                    expected=expected_zeros,
                )

    return VerificationResult(True, kind, n, t, "verified all binary inputs")


def randomized_integer_sanity(
    network: Network,
    n: int,
    t: int,
    kind: SelectionKind,
    *,
    trials: int = 100,
    value_range: tuple[int, int] = (0, 9),
    seed: int | None = None,
) -> VerificationResult:
    """Run optional randomized integer-input sanity checks."""
    try:
        _validate_parameters(n, t, kind)
        _validate_network(network, n)
    except ValueError as exc:
        return VerificationResult(False, kind, n, t, str(exc))
    if trials < 0:
        return VerificationResult(False, kind, n, t, f"trials must be >= 0, got {trials}")

    low, high = value_range
    if low > high:
        return VerificationResult(
            False,
            kind,
            n,
            t,
            f"value_range must satisfy low <= high, got {value_range!r}",
        )

    rng = Random(seed)
    for _ in range(trials):
        values = tuple(rng.randint(low, high) for _ in range(n))
        output = _run_network(network, values)
        expected = tuple(sorted(values)[:t])
        prefix = output[:t]
        if kind == "V":
            ok = prefix == expected
        else:
            ok = tuple(sorted(prefix)) == expected
        if not ok:
            return VerificationResult(
                False,
                kind,
                n,
                t,
                "randomized integer sanity check failed",
                counterexample=values,
                output=output,
                expected=expected,
            )

    return VerificationResult(True, kind, n, t, "passed randomized integer sanity checks")
