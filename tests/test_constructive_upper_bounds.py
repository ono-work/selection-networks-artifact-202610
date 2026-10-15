from src.constructive_upper_bounds import Closure, apply_initial_facts, ceil_log2, iterate_closure, u2_power_depth


def test_u2_power_formula_values():
    assert u2_power_depth(2) == 0
    assert u2_power_depth(4) == 2
    assert u2_power_depth(8) == 4
    assert u2_power_depth(16) == 5


def test_padding_restriction_rule_arithmetic():
    c = Closure(max_n=6)
    c.add_bound("U", 6, 2, 4, "seed")
    iterate_closure(c)
    assert c.best("U", 5, 2) <= 4


def test_u_duality_not_applied_to_v():
    c = Closure(max_n=8)
    c.add_bound("V", 8, 3, 5, "seed")
    iterate_closure(c)
    assert c.best("V", 8, 5) is None


def test_v_t_monotonicity_not_applied_to_u():
    c = Closure(max_n=8)
    c.add_bound("U", 8, 4, 4, "seed")
    iterate_closure(c)
    assert c.best("U", 8, 3) != 4
    assert all(c.derivations[d].rule != "V_T_MONOTONICITY" for d in c.entries[("U", 8, 3)].derivations)


def test_u_binary_merge_depth_calculation():
    c = Closure(max_n=6)
    c.add_bound("U", 3, 2, 2, "left")
    c.add_bound("U", 4, 2, 2, "final")
    iterate_closure(c)
    assert c.best("U", 6, 2) <= 4


def test_u_to_v_binary_merge_depth_calculation():
    c = Closure(max_n=6)
    c.add_bound("U", 3, 2, 2, "left")
    c.add_bound("V", 4, 2, 3, "final")
    iterate_closure(c)
    assert c.best("V", 6, 2) <= 5


def test_ceil_log2():
    assert ceil_log2(1) == 0
    assert ceil_log2(17) == 5
