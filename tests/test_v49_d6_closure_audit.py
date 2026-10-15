from itertools import product

from src.network import apply_comparator, apply_layer
from src.v49_d6_closure_audit import (
    EXPECTED_OPEN_RESIDUALS,
    build_certificate,
    graph_is_acyclic,
    repeated_comparator_redundant,
)


def test_compare_exchange_idempotent_exhaustive_small_n():
    for n in range(2, 7):
        for i in range(1, n):
            edge = (i, i + 1)
            for state in product((0, 1), repeat=n):
                once = apply_comparator(state, edge)
                twice = apply_comparator(once, edge)
                assert twice == once


def test_repeated_comparator_redundant_representative_matchings():
    examples = [
        ([(1, 4), (2, 3), (5, 6)], [(2, 3), (7, 8)], (2, 3)),
        ([(1, 6), (2, 3), (4, 5)], [(1, 6), (2, 3), (4, 5)], (1, 6)),
        ([(1, 9), (2, 8), (4, 5)], [(2, 3), (4, 5)], (4, 5)),
    ]
    for l5, l6, edge in examples:
        for state in product((0, 1), repeat=9):
            assert repeated_comparator_redundant(l5, l6, edge, tuple(state))


def test_deleting_repeated_comparator_can_empty_l6_effective_depth_note():
    l5 = [(2, 3)]
    l6 = [(2, 3)]
    for state in product((0, 1), repeat=4):
        assert apply_layer(apply_layer(state, l5), l6) == apply_layer(state, l5)


def test_closure_certificate_passes_and_has_expected_open_residuals():
    payload = build_certificate()

    assert payload["status"] == "COVERAGE_AUDIT_PASSED"
    assert tuple(payload["scope"]["open_residuals_after_prior_unsat"]) == EXPECTED_OPEN_RESIDUALS
    assert payload["uncovered"] == []
    assert payload["dependency_graph"]["acyclic"]
    assert graph_is_acyclic([tuple(edge) for edge in payload["dependency_graph"]["edges"]])


def test_non_residual_classifications_have_provenance_or_explicit_a5_dependency():
    payload = build_certificate()
    for item in payload["classifications"]:
        if item["class_id"] == "C":
            assert item["provenance"]["status"] == "UNSAT"
            assert item["provenance"]["artifact"].endswith("parsed_status.json")
            assert item["dependency_path"][-1] == item["destination"]
        if item["class_id"] == "B":
            assert item["destination"] == "A5"
            assert tuple(item["dependency_path"]) == (item["leaf"], "A5", "A5_residual")
