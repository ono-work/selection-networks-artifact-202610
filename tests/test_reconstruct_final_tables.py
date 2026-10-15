"""Tests for scripts/reconstruct_final_tables.py.

The reconstruction script is itself a verification program (it exits
nonzero on any disagreement with the manuscript tables). These tests run
it end to end and additionally pin the properties the paper states.
"""
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reconstruct_final_tables.py"


def load_module():
    spec = importlib.util.spec_from_file_location("rft", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_end_to_end_reconstruction_succeeds(tmp_path):
    proc = subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "RECONSTRUCTION OK" in proc.stdout
    for name in ("final_bounds_n11_17.csv", "final_bounds_n11_17.json",
                 "final_tables_n11_17.tex", "weight_game_improvements.csv"):
        assert (ROOT / "generated" / name).exists()


def test_improvement_list_matches_paper():
    rows = list(csv.DictReader(open(ROOT / "generated" /
                                    "weight_game_improvements.csv")))
    assert len(rows) == 44
    u = [r for r in rows if r["kind"] == "U"]
    v = [r for r in rows if r["kind"] == "V"]
    assert len(u) == 42 and len(v) == 2
    assert sorted((int(r["n"]), int(r["t"])) for r in v) == [(17, 8), (17, 9)]
    # the exact cell list stated in the paper
    expected_u = ([(13, t) for t in (4, 6, 7, 9)]
                  + [(14, t) for t in range(4, 11)]
                  + [(15, t) for t in range(4, 12)]
                  + [(16, t) for t in range(4, 13)]
                  + [(17, t) for t in range(2, 16)])
    assert sorted((int(r["n"]), int(r["t"])) for r in u) == sorted(expected_u)
    for r in rows:
        assert int(r["after_lower"]) - int(r["before_lower"]) == 1


def test_u2_n17_and_dual_exact_depth_6():
    data = json.load(open(ROOT / "generated" / "final_bounds_n11_17.json"))
    cells = {(r["kind"], r["t"], r["n"]): r for r in data["bounds"]}
    for t in (2, 15):
        r = cells[("U", t, 17)]
        assert r["lower"] == r["upper"] == 6 and r["exact"]


def test_tables_match_manuscript_transcription():
    data = json.load(open(ROOT / "generated" / "final_bounds_n11_17.json"))
    cells = {(r["kind"], r["t"], r["n"]): (r["lower"], r["upper"])
             for r in data["bounds"]}
    expected = json.load(open(ROOT / "scripts" /
                              "expected_paper_tables_n11_17.json"))
    for kind in ("U", "V"):
        for n in range(11, 18):
            row = expected[kind][str(n)]
            assert len(row) == n
            for t in range(1, n + 1):
                assert cells[(kind, t, n)] == tuple(row[t - 1]), (kind, t, n)


def test_u5_14_and_u9_14_need_propagation():
    """The two cells whose raw game value does not reach the final bound."""
    mod = load_module()
    A = mod.load_game()
    assert mod.game_bound(A, "U", 5, 14) == 5
    assert mod.game_bound(A, "U", 9, 14) == 5
    # but the game-improved U(4,13)=U(9,13) cell propagates:
    assert mod.game_bound(A, "U", 4, 13) == 6
    exact10 = mod.load_exact_n10()
    seeds = {k: g for k in [("U", t, n) for n in range(11, 18)
                            for t in range(1, n + 1)]
             if (g := mod.game_bound(A, *k)) is not None}
    final = mod.compute_lower_fixpoint(exact10, extra_seeds=seeds)
    assert final[("U", 5, 14)] == 6
    assert final[("U", 9, 14)] == 6


def test_base_lower_matches_stored_column():
    mod = load_module()
    exact10 = mod.load_exact_n10()
    _, stored = mod.load_paper_ready()
    base = mod.compute_lower_fixpoint(exact10)
    for key, v in stored.items():
        assert base[key] == v, key


def test_structural_constants():
    mod = load_module()
    assert mod.SDEPTH == {11: 8, 12: 8, 13: 9, 14: 9, 15: 9, 16: 9, 17: 10}
    assert mod.nakano_v2_lower(16) == 6
    assert mod.nakano_v2_lower(17) == 6
    assert mod.ceil_log2(17) == 5
