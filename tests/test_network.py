import pytest

from src.network import apply_comparator, depth, mirror_dual, simulate, validate_layer


@pytest.mark.parametrize(
    ("input_values", "expected"),
    [
        ([0, 0], [0, 0]),
        ([0, 1], [0, 1]),
        ([1, 0], [0, 1]),
        ([1, 1], [1, 1]),
    ],
)
def test_one_comparator_binary_cases(input_values, expected):
    assert apply_comparator(input_values, (1, 2)) == expected


def test_invalid_non_matching_layer_rejected():
    with pytest.raises(ValueError, match="not a matching"):
        validate_layer([(1, 2), (2, 3)], n=3)


def test_depth_zero_simulation_is_identity():
    assert depth([]) == 0
    assert simulate([], [3, 1, 2]) == [3, 1, 2]


def test_small_hand_written_network_sorts_three_values():
    network = [[(1, 2)], [(2, 3)], [(1, 2)]]
    assert simulate(network, [2, 0, 1]) == [0, 1, 2]


def test_mirror_dual_transforms_comparators_layer_by_layer():
    network = [[(1, 4), (2, 3)], [(1, 2)]]

    assert mirror_dual(network, n=5) == [[(2, 5), (3, 4)], [(4, 5)]]
    assert depth(mirror_dual(network, n=5)) == depth(network)


def test_mirror_dual_is_an_involution():
    network = [[(1, 6), (2, 4)], [(3, 5)]]

    assert mirror_dual(mirror_dual(network, n=6), n=6) == network
