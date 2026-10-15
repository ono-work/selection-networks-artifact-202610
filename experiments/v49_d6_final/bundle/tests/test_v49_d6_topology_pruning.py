from itertools import product

from src.network import simulate
from src.v49_d6_topology_pruning import (
    dependency_cones,
    full_dependency_cone_condition,
    single_zero_input,
    topology_pruning_asp_constraints,
    unique_min_condition,
    unique_min_trajectory,
)


def test_unique_min_trajectory_matches_boolean_simulation() -> None:
    network = [[(2, 4)], [(1, 2), (3, 4)], [(1, 3)]]
    for source in range(1, 5):
        trajectory = unique_min_trajectory(network, 4, source)
        output = simulate(network, single_zero_input(4, source))
        assert output[trajectory[-1] - 1] == 0
        assert sum(1 for bit in output if bit == 0) == 1


def test_unique_min_condition_accepts_network_routing_all_single_zeros_to_wire_1() -> None:
    network = [[(1, 2)], [(1, 3)], [(1, 4)]]
    assert unique_min_condition(network, 4)


def test_dependency_cone_propagation() -> None:
    network = [[(1, 2)], [(2, 3)]]
    cones = dependency_cones(network, 3, (2,))
    assert cones[2] == {1, 2, 3}


def test_missing_dependency_cone_is_rejected() -> None:
    network = [[(1, 2)], [(1, 2)]]
    assert not full_dependency_cone_condition(network, 3, 1)


def test_asp_fragment_contains_only_optional_topology_predicates() -> None:
    fragment = topology_pruning_asp_constraints()
    assert "zpos(" in fragment
    assert "depends(" in fragment
    assert "selected(" in fragment


def test_missing_input_dependency_counterexample_for_minimum_output() -> None:
    for x1, x2 in product((0, 1), repeat=2):
        low = (x1, x2, 0)
        high = (x1, x2, 1)
        if min(low) != min(high):
            assert low[:2] == high[:2]
            return
    raise AssertionError("expected an essential-dependency counterexample")
