from src.run_v49_d6_tail_partitioned import branch_definitions, generate_tail_instance
from src.v49_d6_l5_tail_census import (
    UNRESOLVED_BRANCHES,
    build_all_censuses,
    category_for,
    compatible_l5_matchings,
    unresolved_definitions,
)


def test_unresolved_parent_definitions_are_recovered_from_l5_runner() -> None:
    assert [definition.branch_id for definition in unresolved_definitions()] == list(UNRESOLVED_BRANCHES)
    by_id = {definition.branch_id: definition for definition in unresolved_definitions()}
    assert by_id["A5_residual_L5eq3"].final_layer == ((2, 3), (4, 5))
    assert by_id["B6_residual_L5eq3"].final_layer == ((1, 6), (2, 3), (4, 5))
    assert by_id["B6_residual_L5eq4"].final_layer == ((1, 6), (2, 3), (4, 5))


def test_census_categories_cover_each_matching_exactly_once() -> None:
    for definition in unresolved_definitions():
        matchings = compatible_l5_matchings(definition)
        classified = [category_for(definition, matching)[0] for matching in matchings]
        assert len(classified) == len(matchings)
        assert all(category for category in classified)


def test_census_counts_are_consistent() -> None:
    for census in build_all_censuses():
        assert census.entries
        assert sum(census.category_counts.values()) == len(census.entries)
        assert len({entry.matching for entry in census.entries}) == len(census.entries)


def test_tail_runner_child_branches_equal_nonempty_census_categories() -> None:
    expected = {
        (census.branch_id, category)
        for census in build_all_censuses()
        for category, count in census.category_counts.items()
        if count > 0
    }
    actual = {(definition.parent_branch_id, definition.category) for definition in branch_definitions()}
    assert actual == expected


def test_tail_instance_does_not_include_topology_pruning_by_default() -> None:
    definition = branch_definitions()[0]
    instance = generate_tail_instance(definition)
    assert "zpos(" not in instance
    assert "depends(" not in instance
    assert definition.category_constraints in instance
