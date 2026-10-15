from src.selection_bounds import BoundTable, Derivation


def test_v_witness_monotonicity_direction_only():
    table = BoundTable([10])
    table.add_upper_bound("V", 10, 3, 6, Derivation("seed", "V3 witness"))
    table.propagate_v_t_monotonicity()
    assert table.get("V", 10, 2).upper_bound == 6

    table2 = BoundTable([10])
    table2.add_upper_bound("V", 10, 2, 6, Derivation("seed", "V2 witness"))
    table2.propagate_v_t_monotonicity()
    assert table2.get("V", 10, 3).upper_bound is None


def test_v_lower_bound_monotonicity_direction_only():
    table = BoundTable([10])
    table.add_lower_bound("V", 10, 4, 7, Derivation("seed", "V4 lower"))
    table.propagate_v_t_monotonicity()
    assert table.get("V", 10, 5).lower_bound == 7
    assert table.get("V", 10, 10).lower_bound == 7
    assert table.get("V", 10, 3).lower_bound is None


def test_u_duality_propagates_both_bounds():
    table = BoundTable([10])
    table.add_lower_bound("U", 10, 3, 5, Derivation("seed", "U3 lower"))
    table.add_upper_bound("U", 10, 3, 6, Derivation("seed", "U3 upper"))
    table.propagate_u_duality()
    assert table.get("U", 10, 7).lower_bound == 5
    assert table.get("U", 10, 7).upper_bound == 6


def test_u_has_no_t_monotonicity():
    table = BoundTable([10])
    table.add_upper_bound("U", 10, 3, 5, Derivation("seed", "U3 witness"))
    table.propagate_all()
    assert table.get("U", 10, 2).upper_bound is None


def test_u_lower_bound_propagates_to_v_same_cell():
    table = BoundTable(range(1, 8))
    table.add_lower_bound("U", 7, 2, 4, Derivation("TEST", "U lower bound"))
    table.propagate_all()
    assert table.get("V", 7, 2).lower_bound == 4


def test_n_monotonicity_lower_only():
    table = BoundTable([10, 11])
    table.add_lower_bound("V", 10, 3, 6, Derivation("seed", "V(3,10) lower"))
    table.add_upper_bound("V", 10, 3, 6, Derivation("seed", "V(3,10) upper"))
    table.propagate_n_monotonicity()
    assert table.get("V", 11, 3).lower_bound == 6
    assert table.get("V", 11, 3).upper_bound is None


def test_n_monotonicity_upper_propagates_downward_only():
    table = BoundTable([7, 8, 9])
    table.add_upper_bound("U", 8, 2, 4, Derivation("seed", "U(2,8) witness"))
    table.propagate_n_monotonicity()
    assert table.get("U", 7, 2).upper_bound == 4
    assert table.get("U", 9, 2).upper_bound is None


def test_sorting_upper_bound_applies_to_v_and_u():
    table = BoundTable([11])
    table.apply_sorting_upper_bounds({11: 8}, "sorting depth")
    assert table.get("V", 11, 4).upper_bound == 8
    assert table.get("U", 11, 4).upper_bound == 8
    assert table.get("V", 11, 11).status == "EXACT"
    assert table.get("V", 11, 10).status == "EXACT"


def test_conflicting_exact_values_are_errors():
    table = BoundTable([10])
    table.add_exact_value("U", 10, 2, 5, Derivation("seed", "one"))
    table.add_exact_value("U", 10, 2, 6, Derivation("seed", "two"))
    assert table.get("U", 10, 2).status == "ERROR"
