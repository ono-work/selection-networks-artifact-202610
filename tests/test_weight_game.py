import math
import random

import pytest

from src.weight_game import (
    compute_A,
    dominates,
    target_counts,
    u_dominates_target,
    v_dominates_target,
)

# Exact VDepth(t, n) and UDepth(t, n) for 1 <= t <= n <= 10, from Table II
# and Table III of the manuscript. Used as ground truth: Theorem
# "A_U(t,n) <= UDepth(t,n), A_V(t,n) <= VDepth(t,n)" must never be violated
# here, and any cell where equality holds is a case where the weight game
# alone supplies the lower-bound half of the exact value.
V_TABLE = {
    1: {1: 0},
    2: {1: 1, 2: 1},
    3: {1: 2, 2: 3, 3: 3},
    4: {1: 2, 2: 3, 3: 3, 4: 3},
    5: {1: 3, 2: 4, 3: 5, 4: 5, 5: 5},
    6: {1: 3, 2: 4, 3: 5, 4: 5, 5: 5, 6: 5},
    7: {1: 3, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 6},
    8: {1: 3, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 6, 8: 6},
    9: {1: 4, 2: 6, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7},
    10: {1: 4, 2: 6, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7},
}
U_TABLE = {
    1: {1: 0},
    2: {1: 1, 2: 0},
    3: {1: 2, 2: 2, 3: 0},
    4: {1: 2, 2: 2, 3: 2, 4: 0},
    5: {1: 3, 2: 3, 3: 3, 4: 3, 5: 0},
    6: {1: 3, 2: 4, 3: 3, 4: 4, 5: 3, 6: 0},
    7: {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 3, 7: 0},
    8: {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 0},
    9: {1: 4, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 4, 9: 0},
    10: {1: 4, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 4, 10: 0},
}


def _cells():
    for n in range(1, 11):
        for t in range(1, n + 1):
            yield n, t


@pytest.mark.parametrize(("n", "t"), list(_cells()))
def test_soundness_against_exact_n10_tables(n, t):
    """A_kind(t,n) must never exceed the true (independently established)
    depth: this is the paper's Theorem "A_U <= UDepth, A_V <= VDepth"."""
    true_v = V_TABLE[n][t]
    true_u = U_TABLE[n][t]
    if true_v > 0:
        a_v, _ = compute_A("V", t, n, max_rounds=true_v + 1)
        assert a_v is not None and a_v <= true_v
    if true_u > 0:
        a_u, _ = compute_A("U", t, n, max_rounds=true_u + 1)
        assert a_u is not None and a_u <= true_u


def test_udepth_4_6_stays_below_four():
    """Regression guard: UDepth(4,6)=4 is a known, independently verified
    computational value. The weight game must NOT be able to reach 4 here
    (it reaches only 3): this cell's provenance stays computational, and a
    future change to the game must not silently claim it as analytic."""
    a, _ = compute_A("U", 4, 6, max_rounds=6)
    assert a == 3


@pytest.mark.parametrize(
    ("label", "t", "n", "target"),
    [
        ("UDepth(2,9)=5", 2, 9, 5),
        ("UDepth(2,10)=5", 2, 10, 5),
        ("UDepth(3,9)=5", 3, 9, 5),
        ("UDepth(4,9)=5", 4, 9, 5),
        ("UDepth(3,6)=3", 3, 6, 3),
        ("UDepth(3,7)=4", 3, 7, 4),
        ("UDepth(3,8)=4", 3, 8, 4),
        ("UDepth(4,8)=4", 4, 8, 4),
    ],
)
def test_eight_cells_are_theory_derived(label, t, n, target):
    """These eight cells are the ones the paper reports as newly
    theory-derived: the game value equals the known exact depth exactly."""
    a, _ = compute_A("U", t, n, max_rounds=target + 1)
    assert a == target, label


@pytest.mark.parametrize("n", range(1, 18))
def test_t_equals_1_matches_ceil_log2(n):
    """t=1 boundary sanity check: A_U(1,n) = A_V(1,n) = ceil(log2 n), the
    known exact value of VDepth(1,n) = UDepth(1,n) (Corollary 1)."""
    expected = math.ceil(math.log2(n)) if n > 1 else 0
    a_u, _ = compute_A("U", 1, n, max_rounds=expected + 1)
    a_v, _ = compute_A("V", 1, n, max_rounds=expected + 1)
    assert a_u == expected
    assert a_v == expected


@pytest.mark.parametrize(
    ("kind", "t", "n"),
    [
        ("U", 2, 4), ("U", 2, 5), ("U", 2, 6), ("V", 2, 5), ("V", 2, 6),
        ("U", 3, 6), ("V", 3, 6), ("U", 3, 7), ("V", 3, 7), ("U", 4, 8),
        ("V", 2, 8), ("U", 2, 7), ("U", 4, 6), ("V", 4, 6),
    ],
)
def test_dominance_pruning_matches_unpruned_search(kind, t, n):
    """The dominance-pruning optimization must never change the computed
    game value versus an unpruned breadth-first search."""
    pruned, _ = compute_A(kind, t, n, max_rounds=10, prune=True)
    unpruned, _ = compute_A(kind, t, n, max_rounds=10, prune=False)
    assert pruned == unpruned


def test_domination_target_formulas_match_generic_tail_count_check():
    """Cross-validate the specialized O(T) domination formulas against the
    generic sorted-tail-count characterization, on random states."""
    rng = random.Random(0)
    for _ in range(2000):
        n = rng.randint(1, 17)
        t = rng.randint(1, n)
        T = t + 1
        counts = [0] * T
        rem = n
        for i in range(T - 1):
            c = rng.randint(0, rem)
            counts[i] = c
            rem -= c
        counts[T - 1] = rem
        counts = tuple(counts)
        assert dominates(counts, target_counts("U", t, n, T)) == u_dominates_target(counts, t, n, T)
        assert dominates(counts, target_counts("V", t, n, T)) == v_dominates_target(counts, t, n, T)
