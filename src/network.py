"""Direct simulator for comparator networks."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypeAlias

Comparator: TypeAlias = tuple[int, int]
Layer: TypeAlias = Sequence[Comparator]
Network: TypeAlias = Sequence[Layer]


def _validate_n(n: int) -> None:
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"n must be a nonnegative integer, got {n!r}")


def validate_comparator(comparator: Comparator, n: int | None = None) -> None:
    """Validate one 1-indexed comparator."""
    if not isinstance(comparator, tuple) or len(comparator) != 2:
        raise ValueError(f"comparator must be a pair, got {comparator!r}")

    i, j = comparator
    if not isinstance(i, int) or not isinstance(j, int):
        raise ValueError(f"comparator endpoints must be integers, got {comparator!r}")
    if i >= j:
        raise ValueError(f"comparator must satisfy i < j, got {comparator!r}")
    if i < 1:
        raise ValueError(f"wire numbers are 1-indexed, got {comparator!r}")
    if n is not None:
        _validate_n(n)
        if j > n:
            raise ValueError(f"comparator {comparator!r} references wire > n={n}")


def validate_layer(layer: Iterable[Comparator], n: int | None = None) -> None:
    """Validate that a layer is a matching of valid comparators."""
    used: set[int] = set()
    for comparator in layer:
        validate_comparator(comparator, n)
        i, j = comparator
        overlap = used.intersection((i, j))
        if overlap:
            wires = ", ".join(str(wire) for wire in sorted(overlap))
            raise ValueError(
                f"layer is not a matching; wire(s) {wires} appear more than once"
            )
        used.update((i, j))


def validate_network(network: Network, n: int) -> None:
    """Validate all layers in a network."""
    _validate_n(n)
    for index, layer in enumerate(network):
        try:
            validate_layer(layer, n)
        except ValueError as exc:
            raise ValueError(f"invalid layer {index}: {exc}") from exc


def mirror_dual(network: Network, n: int) -> list[list[Comparator]]:
    """Return the mirror-dual network on ``n`` wires.

    Each comparator ``(i, j)`` is replaced layer-by-layer by
    ``(n + 1 - j, n + 1 - i)``.
    """
    validate_network(network, n)
    return [
        [(n + 1 - j, n + 1 - i) for i, j in layer]
        for layer in network
    ]


def apply_comparator(values: Sequence[int], comparator: Comparator) -> list[int]:
    """Apply one comparator to a copy of values and return the result."""
    output = list(values)
    validate_comparator(comparator, len(output))
    i, j = comparator
    left = i - 1
    right = j - 1
    if output[left] > output[right]:
        output[left], output[right] = output[right], output[left]
    return output


def apply_layer(values: Sequence[int], layer: Layer) -> list[int]:
    """Apply one matching layer to a copy of values and return the result."""
    output = list(values)
    validate_layer(layer, len(output))
    for i, j in layer:
        left = i - 1
        right = j - 1
        if output[left] > output[right]:
            output[left], output[right] = output[right], output[left]
    return output


def simulate(network: Network, input_values: Sequence[int]) -> list[int]:
    """Run a comparator network on input values."""
    output = list(input_values)
    validate_network(network, len(output))
    for layer in network:
        output = apply_layer(output, layer)
    return output


def depth(network: Network) -> int:
    """Return the number of layers in a network."""
    return len(network)
